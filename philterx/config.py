from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal

import yaml


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

    def to_philter_options(self) -> dict:
        opts = {}
        opts["outformat"] = self.replacement.style
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
        whitelist=list(data.get("whitelist", []) or []),
        blacklist=list(data.get("blacklist", []) or []),
        eval=Eval(
            enabled=eval_cfg.get("enabled", False),
            gold_dir=eval_cfg.get("gold_dir", ""),
        ),
    )
