from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import yaml


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config(config_path: str = "configs/config.yaml") -> dict[str, Any]:
    full_path = get_project_root() / config_path

    if not full_path.exists():
        raise FileNotFoundError(f"Config file not found: {full_path}")

    with full_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def resolve_path(relative_path: str) -> Path:
    return get_project_root() / relative_path


@lru_cache(maxsize=1)
def get_config() -> dict[str, Any]:
    return load_config()


@lru_cache(maxsize=1)
def load_production_model() -> Any:
    config = get_config()
    model_path = resolve_path(config["paths"]["model_dir"]) / "production_model.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Production model not found: {model_path}. "
            "Provide an authorized model artifact at models/production_model.pkl before starting predictions."
        )

    return joblib.load(model_path)


def load_metrics() -> dict[str, Any] | None:
    config = get_config()
    metrics_path = resolve_path(config["paths"]["report_dir"]) / "metrics.json"

    if not metrics_path.exists():
        return None

    with metrics_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_model_version() -> str:
    config = get_config()
    model_path = resolve_path(config["paths"]["model_dir"]) / "production_model.pkl"

    if not model_path.exists():
        return "model-not-found"

    modified_timestamp = int(model_path.stat().st_mtime)
    return f"local-production-{modified_timestamp}"
