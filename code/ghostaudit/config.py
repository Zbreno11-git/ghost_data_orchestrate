"""Load code/config/default.toml and resolve repo-relative paths."""
from __future__ import annotations

import tomllib
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CODE_DIR.parent
DEFAULT_CONFIG = CODE_DIR / "config" / "default.toml"


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def price_for(config: dict, model: str) -> tuple[float, float]:
    """(input_per_m, output_per_m). Unknown models are an error, never a free call."""
    try:
        m = config["models"][model]
    except KeyError as exc:
        raise KeyError(f"no price configured for model {model!r}; add it to default.toml") from exc
    return float(m["input_per_m"]), float(m["output_per_m"])
