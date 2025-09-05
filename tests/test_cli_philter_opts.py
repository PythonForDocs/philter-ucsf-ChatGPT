from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from philterx import cli


def test_cli_passes_all_options(tmp_path, monkeypatch):
    # prepare input and output directories
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()

    (in_dir / "note.txt").write_text("dummy text")

    # minimal config
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text("{}")

    captured = {}

    class DummyPhilter:
        def __init__(self, opts):
            captured.update(opts)

        def map_coordinates(self):
            pass

        def transform(self):
            out_file = Path(captured["foutpath"]) / "note.txt"
            out_file.write_text("filtered")

    monkeypatch.setattr(cli, "Philter", lambda opts: DummyPhilter(opts))

    args = [
        "philterx", "--input", str(in_dir), "--output", str(out_dir), "--config", str(cfg_path)
    ]
    monkeypatch.setattr(sys, "argv", args)

    cli.main()

    required = [
        "filters",
        "xml",
        "stanford_ner_tagger",
        "freq_table",
        "initials",
        "coords",
        "eval_out",
        "ucsfformat",
        "cachepos",
        "verbose",
        "finpath",
        "foutpath",
    ]
    for key in required:
        assert key in captured
