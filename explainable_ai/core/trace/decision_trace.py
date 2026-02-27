"""Decision trace formatter for governance pipeline outputs."""

from __future__ import annotations

from typing import Any, Dict, List


def generate_decision_trace(
    input_data: dict,
    passed_rules: list,
    failed_rules: list,
    eligibility_score: int,
    confidence_vector: dict,
    governance_decision: str,
) -> list:
    """Generate an ordered, human-readable timeline of decision steps."""
    _validate_inputs(
        input_data=input_data,
        passed_rules=passed_rules,
        failed_rules=failed_rules,
        eligibility_score=eligibility_score,
        confidence_vector=confidence_vector,
        governance_decision=governance_decision,
    )

    timeline: List[Dict[str, Any]] = [
        {
            "step": "Input Received",
            "value": dict(input_data),
        }
    ]

    for rule_id in passed_rules:
        timeline.append(
            {
                "step": "Keyword Risk Scan",
                "rule_id": str(rule_id),
                "result": "PASS",
            }
        )

    for rule_id in failed_rules:
        timeline.append(
            {
                "step": "Keyword Risk Scan",
                "rule_id": str(rule_id),
                "result": "FAIL",
            }
        )

    timeline.append({"step": "Score Computed", "value": int(eligibility_score)})
    timeline.append({"step": "Confidence Vector", "value": dict(confidence_vector)})
    timeline.append({"step": "Governance Decision", "value": governance_decision})
    timeline.append({"step": "Final Decision", "value": governance_decision})

    return timeline


def _validate_inputs(
    input_data: Dict[str, Any],
    passed_rules: List[Any],
    failed_rules: List[Any],
    eligibility_score: int,
    confidence_vector: Dict[str, Any],
    governance_decision: str,
) -> None:
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary.")

    if not isinstance(passed_rules, list):
        raise TypeError("passed_rules must be a list.")

    if not isinstance(failed_rules, list):
        raise TypeError("failed_rules must be a list.")

    if not isinstance(eligibility_score, int):
        raise TypeError("eligibility_score must be an integer.")

    if not isinstance(confidence_vector, dict):
        raise TypeError("confidence_vector must be a dictionary.")

    if not isinstance(governance_decision, str) or not governance_decision.strip():
        raise ValueError("governance_decision must be a non-empty string.")
