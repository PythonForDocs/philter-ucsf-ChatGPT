import argparse
from pathlib import Path
import re
import tempfile
from datetime import datetime, timedelta

from philter import Philter
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
    base_opts = cfg.to_philter_options()

    for txt_file in input_dir.rglob("*.txt"):
        original = txt_file.read_text()
        pre_text, wl_map = _apply_whitelist(original, cfg.whitelist)
        pre_text, date_map = _handle_dates(pre_text, cfg.dates)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            temp_file = tmp_path / txt_file.name
            temp_file.write_text(pre_text)
            philter_opts = dict(base_opts)
            philter_opts["finpath"] = str(tmp_path)
            philter_opts["foutpath"] = str(output_dir)
            filterer = Philter(philter_opts)
            filterer.map_coordinates()
            filterer.transform()

            out_file = output_dir / txt_file.name
            filtered = out_file.read_text()
            filtered = _restore_placeholders(filtered, wl_map)
            filtered = _restore_placeholders(filtered, date_map)
            filtered = _apply_blacklist(filtered, cfg.blacklist, cfg.replacement.style)
            out_file.write_text(filtered)


if __name__ == "__main__":
    main()
