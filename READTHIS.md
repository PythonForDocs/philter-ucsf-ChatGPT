# Quick Start Guide

This guide summarizes the basics of running **philterx** from the command line.

## Installation
Install from PyPI:
```bash
pip3 install philter-ucsf
```
or work from source by cloning this repository and installing the dependencies:
```bash
git clone https://github.com/.../philter-ucsf-ChatGPT.git
pip3 install -r requirements.txt
```

## Quick start
This repository provides a sample configuration at `config.yaml`.  
Filter a directory of text files by running:
```bash
philterx --input ./data/i2b2_notes/ --output ./data/i2b2_results/ --config config.yaml
```

## Configuration
`philterx` reads options from a YAML file. Key fields include:

- `dates`: how to treat detected dates – `keep`, `remove` or `shift`.
- `replacement.style`: format used for PHI spans (`asterisk`, `redacted`, or `pseudonym`).
- `filters`: JSON file listing active filters.
- `whitelist` / `blacklist`: lists of JSON files containing terms to always keep or always remove.
- `eval.enabled` and `eval.gold_dir`: enable evaluation and point to gold-standard annotations.
- `xml`, `stanford_ner_tagger`, `freq_table`, `initials`, `coords`, `eval_out`, `ucsfformat`, `cachepos`, `verbose`: advanced options passed directly to the underlying `Philter` engine.

## Default resources
If a path is not provided in `config.yaml`, built‑in resources are used:

- `config/default_filters.json` – default PHI filter definitions.
- `resources/whitelists/whitelist_plus_fps_091718_nonames.json` – default whitelist terms.
- `resources/blacklists/firstnames_minus_fps.json` – default blacklist terms.
- `philter_ucsf/data/phi_notes_i2b2.json` – sample XML notes for evaluation.
- `philter_ucsf/data/coordinates.json` – coordinate mappings for annotations.
- `philter_ucsf/data/phi` – default directory for evaluation outputs.

## Editing whitelist and blacklist
Add or remove entries from the JSON files listed under `whitelist` and `blacklist` in the configuration to customize term handling.

## Replacement styles
The `replacement.style` field determines how detected PHI appears in output:
- `asterisk` – replace spans with `*`.
- `redacted` – insert `[REDACTED]`.
- `pseudonym` – insert `[PSEUDONYM]`.

## Evaluation
Set `eval.enabled: true` and provide `eval.gold_dir` to produce precision/recall metrics.  
Without evaluation, `philterx` simply writes PHI‑reduced text.

## Regex pattern formats
Regular-expression filters may be written in two forms:

- Raw patterns using Python syntax, e.g. `(?i)foo`.
- Delimited form `/pattern/flags`, where trailing flags map to Python's `re` options (`i`, `m`, `s`, `x`).

Inline flag blocks such as `(?im)` can appear anywhere in the pattern; they are stripped and moved to the beginning before compilation. Any regex that fails to compile is skipped with a warning instead of stopping the program.
