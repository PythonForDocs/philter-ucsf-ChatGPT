import argparse
from pathlib import Path
import re
import tempfile
from datetime import datetime, timedelta
import json

from philter_ucsf.philter import Philter
from philterx.config import load_config

DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def _restore_placeholders(text: str, mapping: dict[str, str]) -> str:
    for placeholder, value in mapping.items():
        text = text.replace(placeholder, value)
    return text


def _apply_whitelist(text: str, terms: list[str]):
    mapping = {}
    for i, term in enumerate(terms):
        placeholder = f"PHILTERXWL{i}"
        mapping[placeholder] = term
        text = text.replace(term, placeholder)
    return text, mapping


def _apply_blacklist(text: str, terms: list[str], style: str) -> str:
    def repl(term: str) -> str:
        if style == "redacted":
            return "[REDACTED]"
        if style == "pseudonym":
            return "[PSEUDONYM]"
        return "*" * len(term)

    for term in terms:
        text = re.sub(re.escape(term), repl(term), text)
    return text


def _handle_dates(text: str, mode: str):
    mapping = {}
    if mode in {"keep", "shift"}:
        matches = list(DATE_RE.finditer(text))
        for i, m in enumerate(matches):
            original = m.group(1)
            placeholder = f"PHILTERXDATE{i}"
            if mode == "shift":
                try:
                    dt = datetime.strptime(original, "%Y-%m-%d").date()
                    dt = dt + timedelta(days=1)
                    replacement = dt.strftime("%Y-%m-%d")
                except ValueError:
                    replacement = original
            else:
                replacement = original
            mapping[placeholder] = replacement
            text = text.replace(original, placeholder, 1)
    return text, mapping


def main() -> None:
    """Command line interface for running Philter on text files."""
    parser = argparse.ArgumentParser(description="Filter PHI from text files")
    parser.add_argument("--input", required=True, help="Directory containing .txt files to filter")
    parser.add_argument("--output", required=True, help="Directory to write filtered files")
    parser.add_argument("--config", required=True, help="YAML configuration for Philter")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_config(args.config)

    for txt_file in input_dir.rglob("*.txt"):
        original = txt_file.read_text()
        pre_text, wl_map = _apply_whitelist(original, cfg.whitelist)
        pre_text, date_map = _handle_dates(pre_text, cfg.dates)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            temp_file = tmp_path / txt_file.name
            temp_file.write_text(pre_text)
            philter_opts = {
                "finpath": str(tmp_path),
                "foutpath": str(output_dir),
                "filters": cfg.filters,
                "xml": cfg.xml,
                "freq_table": cfg.freq_table,
                "initials": cfg.initials,
                "coords": cfg.coords,
                "eval_out": cfg.eval_out,
                "ucsfformat": cfg.ucsfformat,
                "cachepos": cfg.cachepos,
                "verbose": cfg.verbose,
                "outformat": cfg.replacement.style,
            }
            if cfg.stanford_ner_tagger:
                philter_opts["stanford_ner_tagger"] = cfg.stanford_ner_tagger
            if cfg.eval.enabled:
                philter_opts["run_eval"] = True
                philter_opts["anno_folder"] = cfg.eval.gold_dir
            filterer = Philter(philter_opts)
            filterer.map_coordinates()
            filterer.transform()

            out_file = output_dir / txt_file.name
            filtered = out_file.read_text()
            filtered = _restore_placeholders(filtered, wl_map)
            filtered = _restore_placeholders(filtered, date_map)
            filtered = _apply_blacklist(filtered, cfg.blacklist, cfg.replacement.style)
            out_file.write_text(filtered)

    if cfg.eval.enabled:
        gold_dir = Path(cfg.eval.gold_dir)
        if gold_dir.exists():
            if cfg.replacement.style == "redacted":
                phi_re = re.compile(r"\[REDACTED\]")
            elif cfg.replacement.style == "pseudonym":
                phi_re = re.compile(r"\[PSEUDONYM\]")
            else:
                phi_re = re.compile(r"\*+")

            tp = fp = fn = 0
            for pred_file in output_dir.rglob("*.txt"):
                gold_file = gold_dir / pred_file.relative_to(output_dir)
                if not gold_file.exists():
                    continue
                pred_spans = {(m.start(), m.end()) for m in phi_re.finditer(pred_file.read_text())}
                gold_spans = {(m.start(), m.end()) for m in phi_re.finditer(gold_file.read_text())}
                tp += len(pred_spans & gold_spans)
                fp += len(pred_spans - gold_spans)
                fn += len(gold_spans - pred_spans)

            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
            report = {
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
            report_dir = Path("eval")
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "report.json").write_text(json.dumps(report, indent=2))
            print(
                f"Evaluation - Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}"
            )


if __name__ == "__main__":
    main()
