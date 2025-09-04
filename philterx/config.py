from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal

import importlib.resources as pkg_resources
import yaml


def _pkg_path(*parts: str) -> str:
    return str(pkg_resources.files("philter_ucsf").joinpath(*parts))


def _default_filters() -> str:
    return _pkg_path("configs", "philter_delta.json")


def _default_xml() -> str:
    return _pkg_path("data", "phi_notes_i2b2.json")


def _default_coords() -> str:
    return _pkg_path("data", "coordinates.json")


def _default_eval_out() -> str:
    return _pkg_path("data", "phi")


@dataclass
class Replacement:
    style: Literal["asterisk", "redacted", "pseudonym"] = "asterisk"


@dataclass
class Eval:
    enabled: bool = False
    gold_dir: str = ""


@dataclass
class Config:
    dates: Literal["keep", "remove", "shift"] = "remove"
    replacement: Replacement = field(default_factory=Replacement)
    whitelist: List[str] = field(default_factory=list)
    blacklist: List[str] = field(default_factory=list)
    eval: Eval = field(default_factory=Eval)
    filters: str = field(default_factory=_default_filters)
    xml: str = field(default_factory=_default_xml)
    stanford_ner_tagger: Dict[str, str | bool] = field(default_factory=dict)
    freq_table: bool = False
    initials: bool = True
    coords: str = field(default_factory=_default_coords)
    eval_out: str = field(default_factory=_default_eval_out)
    ucsfformat: bool = False
    cachepos: str = ""
    verbose: bool = True

    def to_philter_options(self) -> dict:
        opts = {"outformat": self.replacement.style}
        if self.eval.enabled:
            opts["run_eval"] = True
            opts["anno_folder"] = self.eval.gold_dir
        for key in (
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
        ):
            value = getattr(self, key)
            if value:
                opts[key] = value
        return opts


def load_config(path: str | Path) -> Config:
    data = yaml.safe_load(Path(path).read_text())
    replacement = data.get("replacement", {})
    eval_cfg = data.get("eval", {})
    return Config(
        dates=data.get("dates", "remove"),
        replacement=Replacement(style=replacement.get("style", "asterisk")),
        whitelist=list(data.get("whitelist", []) or []),
        blacklist=list(data.get("blacklist", []) or []),
        eval=Eval(
            enabled=eval_cfg.get("enabled", False),
            gold_dir=eval_cfg.get("gold_dir", ""),
        ),
        filters=data.get("filters", _default_filters()),
        xml=data.get("xml", _default_xml()),
        stanford_ner_tagger=dict(data.get("stanford_ner_tagger", {}) or {}),
        freq_table=data.get("freq_table", False),
        initials=data.get("initials", True),
        coords=data.get("coords", _default_coords()),
        eval_out=data.get("eval_out", _default_eval_out()),
        ucsfformat=data.get("ucsfformat", False),
        cachepos=data.get("cachepos", ""),
        verbose=data.get("verbose", True),
    )
