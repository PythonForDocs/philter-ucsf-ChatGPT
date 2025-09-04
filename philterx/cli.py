import argparse
from pathlib import Path
import shutil
import tempfile
import yaml
from philter import Philter


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

    config_path = Path(args.config)
    config = yaml.safe_load(config_path.read_text())

    for txt_file in input_dir.rglob("*.txt"):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            shutil.copy(txt_file, tmp_path / txt_file.name)
            cfg = dict(config)
            cfg["finpath"] = str(tmp_path)
            cfg["foutpath"] = str(output_dir)
            filterer = Philter(cfg)
            filterer.map_coordinates()
            filterer.transform()


if __name__ == "__main__":
    main()
