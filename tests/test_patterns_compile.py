from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from philter_ucsf.philter import Philter


def test_default_patterns_compile():
    filters = Path(__file__).resolve().parents[1] / "philter_ucsf" / "configs" / "philter_delta.json"
    philter = Philter({
        "filters": str(filters),
        "finpath": ".",
        "foutpath": ".",
    })
    for pat in philter.patterns:
        if pat["type"] in {"regex", "regex_context"}:
            assert pat.get("data") is not None
