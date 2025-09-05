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
`philterx` reads options from a YAML file. The sample `config.yaml` lists every supported key:

- `dates` (default `remove`): how to handle detected dates; may also be `keep` or `shift`.
- `replacement.style` (default `asterisk`): how PHI spans are replaced; options are `asterisk`, `redacted`, or `pseudonym`.
- `filters` (default `config/default_filters.json`): JSON file describing active filter patterns.
- `whitelist` (default `resources/whitelists/whitelist_plus_fps_091718_nonames.json`): JSON files containing terms that should never be filtered.
- `blacklist` (default `resources/blacklists/firstnames_minus_fps.json`): JSON files listing terms that should always be removed.
- `xml` (default `config/phi_notes_i2b2.json`): sample XML notes used when running evaluation.
- `stanford_ner_tagger` (default empty): supply `classifier` and `jar` paths to enable Stanford NER patterns.
- `freq_table` (default `false`): emit token frequency tables after filtering.
- `initials` (default `true`): treat isolated initials as PHI.
- `coords` (default `config/coordinates.json`): coordinate mappings for annotations.
- `eval_out` (default `philter_ucsf/data/phi`): directory for evaluation output files.
- `eval.enabled` (default `false`): run evaluation against gold annotations.
- `eval.gold_dir` (default empty): directory containing gold-standard annotations for evaluation.
- `ucsfformat` (default `false`): enable UCSF-specific output format.
- `cachepos` (default empty): directory for caching part-of-speech tags; blank disables caching.
- `verbose` (default `true`): emit detailed logging information.

All default resource files live within this repository under `config/`, `resources/`, or `philter_ucsf/data/` as noted above.

### Overriding defaults
To customize behavior, copy `config.yaml` and edit the fields you want to change. For example:

```yaml
filters: my_filters.json
replacement:
  style: redacted
whitelist:
  - custom_whitelist.json
blacklist:
  - custom_blacklist.json
eval:
  enabled: true
  gold_dir: /path/to/gold_annotations
```

Run `philterx` with your modified configuration:

```bash
philterx --config my_config.yaml --input ./data/i2b2_notes/ --output ./data/i2b2_results/
```

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
