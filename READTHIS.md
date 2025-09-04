# Quick Start Guide

This guide summarizes the basics of running **Philter** from the command line.

## Installation
- Install the package from PyPI:
  ```bash
  pip3 install philter-ucsf
  ```
- Or work from source by cloning this repository and installing the dependencies:
  ```bash
  git clone https://github.com/.../philter-ucsf-ChatGPT.git
  pip3 install -r requirements.txt
  ```

## Command-line usage
Run Philter against a directory of notes:
```bash
python3 main.py -i ./data/i2b2_notes/ -o ./data/i2b2_results/ -f ./configs/philter_delta.json
```
Key flags:
- `-i` – input note directory or file.
- `-o` – output directory for PHI-reduced notes.
- `-f` – path to the configuration JSON controlling PHI rules.
- `-a` – optional annotation directory when evaluating.

## Editing whitelist and blacklist
Philter ships with JSON files listing terms to always keep or remove:
- Whitelists live under `filters/whitelists/`
- Blacklists live under `filters/blacklists/`
Add or delete entries from these JSON files to customize behavior. The configuration file references these lists when running.

## PHI options
The file `configs/philter_delta.json` defines which PHI filters are active and how they behave. Tweak this file to enable or disable specific PHI categories or to point at different whitelist/blacklist files. Additional flags such as `-n` (include initials) and `-t` (emit word-frequency table) further control PHI reporting.

## Replacement styles
Control how detected PHI appears in the output via `--outputformat`:
- `asterisk` – replaces PHI spans with `*` characters.
- `i2b2` – writes the original text with XML tags around PHI spans.

## Evaluation toggle
To score Philter against ground-truth annotations, supply the annotation directory and enable evaluation:
```bash
python3 main.py -i NOTES -a ANNO -o OUTPUT -x ./data/phi_notes.json -f ./configs/philter_delta.json -e
```
Omit `-e` (or pass `--prod=True`) to skip evaluation and simply generate PHI-reduced text.
