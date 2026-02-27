"""Governance decision layer for deterministic contract risk outputs."""

from __future__ import annotations

from typing import Any, Dict


_VALID_LABELS = {"LOW_RISK", "MEDIUM_RISK", "HIGH_RISK"}


def apply_governance_layer(
    deterministic_label: str,
    confidence_vector: dict,
    crag_blocked: bool,
) -> str:
    """Map deterministic risk label and confidence controls to a governance action."""
    _validate_inputs(
        deterministic_label=deterministic_label,
        confidence_vector=confidence_vector,
    )

    if crag_blocked is True:
        return "ESCALATE"

    label_map = {
        "LOW_RISK": "APPROVED",
        "MEDIUM_RISK": "REVIEW_REQUIRED",
        "HIGH_RISK": "ESCALATE",
    }
    action = label_map[deterministic_label]

    if float(confidence_vector["rule_confidence"]) < 50:
        return "REVIEW_REQUIRED"

    return action


def _validate_inputs(deterministic_label: str, confidence_vector: Dict[str, Any]) -> None:
    if deterministic_label not in _VALID_LABELS:
        allowed = ", ".join(sorted(_VALID_LABELS))
        raise ValueError(
            f"Invalid deterministic_label '{deterministic_label}'. "
            f"Expected one of: {allowed}."
        )

    if not isinstance(confidence_vector, dict):
        raise TypeError("confidence_vector must be a dictionary.")

    if "rule_confidence" not in confidence_vector:
        raise ValueError("confidence_vector must contain 'rule_confidence'.")

    rule_confidence = confidence_vector["rule_confidence"]
    if not isinstance(rule_confidence, (int, float)):
        raise TypeError("confidence_vector['rule_confidence'] must be a number.")
