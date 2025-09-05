from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional

import yaml


_BASE_DIR = Path(__file__).resolve().parent.parent


def _pkg_path(*parts: str) -> Path:
    return _BASE_DIR.joinpath(*parts)


def _default_whitelist() -> List[str]:
    return [
        str(
            _pkg_path(
                "resources",
                "whitelists",
                "whitelist_plus_fps_091718_nonames.json",
            )
        )
    ]


def _default_blacklist() -> List[str]:
    return [
        str(
            _pkg_path(
                "resources",
                "blacklists",
                "firstnames_minus_fps.json",
            )
        )
    ]


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
    whitelist: List[str] = field(default_factory=_default_whitelist)
    blacklist: List[str] = field(default_factory=_default_blacklist)
    eval: Eval = field(default_factory=Eval)
    filters: Path = field(
        default_factory=lambda: _pkg_path("config", "default_filters.json")
    )
    xml: Optional[Path] = None
    stanford_ner_tagger: Optional[Dict[str, Path]] = None
    freq_table: bool = False
    initials: bool = True
    coords: Path = field(default_factory=lambda: _pkg_path("config", "coordinates.json"))
    eval_out: Path = field(
        default_factory=lambda: _pkg_path("philter_ucsf", "data", "phi")
    )
    ucsfformat: bool = False
    cachepos: bool = False
    verbose: bool = True

    def to_philter_options(self) -> dict:
        opts = {
            "outformat": self.replacement.style,
            "filters": str(self.filters),
            "xml": str(self.xml) if self.xml else None,
            "stanford_ner_tagger": {
                k: str(v) for k, v in self.stanford_ner_tagger.items()
            }
            if self.stanford_ner_tagger
            else None,
            "freq_table": self.freq_table,
            "initials": self.initials,
            "coords": str(self.coords),
            "eval_out": str(self.eval_out),
            "ucsfformat": self.ucsfformat,
            "cachepos": self.cachepos,
            "verbose": self.verbose,
        }
        if self.eval.enabled:
            opts["run_eval"] = True
            opts["anno_folder"] = self.eval.gold_dir
        return opts


def load_config(path: str | Path) -> Config:
    data = yaml.safe_load(Path(path).read_text())
    replacement = data.get("replacement", {})
    eval_cfg = data.get("eval", {})
    return Config(
        dates=data.get("dates", "remove"),
        replacement=Replacement(style=replacement.get("style", "asterisk")),
        whitelist=list(data.get("whitelist", _default_whitelist()) or []),
        blacklist=list(data.get("blacklist", _default_blacklist()) or []),
        eval=Eval(
            enabled=eval_cfg.get("enabled", False),
            gold_dir=eval_cfg.get("gold_dir", ""),
        ),
        filters=Path(data["filters"]) if data.get("filters") else _pkg_path("config", "default_filters.json"),
        xml=Path(data["xml"]) if data.get("xml") else None,
        stanford_ner_tagger={k: Path(v) for k, v in data["stanford_ner_tagger"].items()} if data.get("stanford_ner_tagger") else None,
        freq_table=data.get("freq_table", False),
        initials=data.get("initials", True),
        coords=Path(data["coords"]) if data.get("coords") else _pkg_path("config", "coordinates.json"),
        eval_out=Path(data["eval_out"]) if data.get("eval_out") else _pkg_path("philter_ucsf", "data", "phi"),
        ucsfformat=data.get("ucsfformat", False),
        cachepos=data.get("cachepos", False),
        verbose=data.get("verbose", True),
    )
