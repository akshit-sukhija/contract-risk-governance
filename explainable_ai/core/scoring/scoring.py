"""Confidence scoring utilities for the governance engine."""

from __future__ import annotations

from typing import Any, Dict, List


def calculate_confidence_vector(
    passed_rules: list,
    failed_rules: list,
    total_rules: int,
    retrieval_similarity: float,
    data_completeness: float,
) -> dict:
    """Calculate confidence components for governance decisions.

    Returns a structured dictionary with independent confidence values
    (0-100, integer) for rule evaluation coverage, retrieval similarity,
    and data completeness.
    """
    _validate_inputs(
        passed_rules=passed_rules,
        failed_rules=failed_rules,
        total_rules=total_rules,
        retrieval_similarity=retrieval_similarity,
        data_completeness=data_completeness,
    )

    rules_evaluated = len(passed_rules) + len(failed_rules)

    rule_confidence = _to_percentage((rules_evaluated / total_rules) * 100.0)
    retrieval_confidence = _to_percentage(retrieval_similarity * 100.0)
    completeness_confidence = _to_percentage(data_completeness * 100.0)

    return {
        "rule_confidence": rule_confidence,
        "retrieval_confidence": retrieval_confidence,
        "data_completeness": completeness_confidence,
    }


def _validate_inputs(
    passed_rules: List[Any],
    failed_rules: List[Any],
    total_rules: int,
    retrieval_similarity: float,
    data_completeness: float,
) -> None:
    if not isinstance(passed_rules, list):
        raise TypeError("passed_rules must be a list.")

    if not isinstance(failed_rules, list):
        raise TypeError("failed_rules must be a list.")

    if not isinstance(total_rules, int):
        raise TypeError("total_rules must be an integer.")

    if total_rules <= 0:
        raise ValueError("total_rules must be greater than 0.")

    if len(passed_rules) + len(failed_rules) > total_rules:
        raise ValueError("Evaluated rule count cannot exceed total_rules.")

    if not isinstance(retrieval_similarity, (int, float)):
        raise TypeError("retrieval_similarity must be a number between 0 and 1.")

    if not isinstance(data_completeness, (int, float)):
        raise TypeError("data_completeness must be a number between 0 and 1.")

    if not (0.0 <= float(retrieval_similarity) <= 1.0):
        raise ValueError("retrieval_similarity must be between 0 and 1.")

    if not (0.0 <= float(data_completeness) <= 1.0):
        raise ValueError("data_completeness must be between 0 and 1.")


def _to_percentage(value: float) -> int:
    """Round to nearest integer and bound output to 0-100."""
    return max(0, min(100, int(round(value))))
