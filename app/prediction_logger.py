from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.model_loader import get_config, resolve_path


LOG_COLUMNS = [
    "timestamp_utc",
    "step",
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "fraud_probability",
    "risk_level",
    "decision",
    "model_version",
]


def get_prediction_log_path() -> Path:
    config = get_config()
    log_dir = resolve_path(config["paths"]["log_dir"])
    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir / "predictions.csv"


def log_prediction(
    transaction: dict[str, Any],
    fraud_probability: float,
    risk_level: str,
    decision: str,
    model_version: str,
) -> None:
    log_path = get_prediction_log_path()
    file_exists = log_path.exists()

    row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **transaction,
        "fraud_probability": fraud_probability,
        "risk_level": risk_level,
        "decision": decision,
        "model_version": model_version,
    }

    with log_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=LOG_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)
