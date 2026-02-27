"""Persistent audit logging for governance decisions."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


LOG_FILE_PATH = Path(__file__).resolve().parents[2] / "logs" / "decisions.jsonl"


def log_decision(
    decision_id: str,
    input_data: dict,
    deterministic_label: str,
    governance_decision: str,
    confidence_vector: dict,
    latency_ms: float,
) -> None:
    """Append a single governance decision audit record in JSONL format."""
    entry: Dict[str, Any] = {
        "decision_id": decision_id,
        "timestamp_utc": datetime.utcnow().isoformat(),
        "input_data": input_data,
        "deterministic_label": deterministic_label,
        "governance_decision": governance_decision,
        "confidence_vector": confidence_vector,
        "latency_ms": latency_ms,
    }

    try:
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE_PATH.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=True, separators=(",", ":")))
            file.write("\n")
    except (OSError, TypeError, ValueError):
        # Fail-safe by design: audit logging must not break decision flow.
        return
