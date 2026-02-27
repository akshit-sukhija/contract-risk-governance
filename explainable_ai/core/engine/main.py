"""Core contract evaluation entrypoint for reusable governance decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from explainable_ai.core.engine.rule_engine import RuleEngine
from explainable_ai.core.explanation.ai_explainer import generate_ai_explanation
from explainable_ai.core.governance.governance import apply_governance_layer
from explainable_ai.core.risk.keyword_scanner import scan_for_risks
from explainable_ai.core.scoring.scoring import calculate_confidence_vector
from explainable_ai.core.trace.decision_trace import generate_decision_trace


BASE_DIR = Path(__file__).resolve().parents[2]
POLICY_PATH = BASE_DIR / "policies" / "rules.yaml"


def evaluate_contract(document_text: str, enable_ai: bool = False) -> dict:
    """Evaluate contract text through deterministic governance and optional AI explanation."""
    if not isinstance(document_text, str):
        raise TypeError("document_text must be a string.")

    if not document_text.strip():
        raise ValueError("document_text must be a non-empty string.")

    if not isinstance(enable_ai, bool):
        raise TypeError("enable_ai must be a boolean.")

    rule_engine = RuleEngine(POLICY_PATH)
    rule_result = rule_engine.evaluate(document_text)

    confidence_vector = calculate_confidence_vector(
        passed_rules=rule_result["passed_rules"],
        failed_rules=rule_result["failed_rules"],
        total_rules=len(rule_engine.rules),
        retrieval_similarity=1.0,
        data_completeness=1.0,
    )

    governance_decision = apply_governance_layer(
        deterministic_label=rule_result["deterministic_label"],
        confidence_vector=confidence_vector,
        crag_blocked=False,
    )

    trace = generate_decision_trace(
        input_data={"document_text": document_text},
        passed_rules=rule_result["passed_rules"],
        failed_rules=rule_result["failed_rules"],
        eligibility_score=rule_result["eligibility_score"],
        confidence_vector=confidence_vector,
        governance_decision=governance_decision,
    )

    clauses = _segment_clauses(document_text)
    trace.append(
        {
            "step": "Clause Segmentation",
            "value": clauses,
            "count": len(clauses),
        }
    )

    risk_scan = scan_for_risks(document_text)
    if risk_scan["risk_flag_count"] > 0:
        governance_decision = "REVIEW_REQUIRED"
        trace.append(
            {
                "step": "Keyword Hard Gate",
                "value": risk_scan["risk_keywords_found"],
            }
        )

    ai_explanation = (
        generate_ai_explanation(trace, governance_decision) if enable_ai else None
    )

    return {
        "decision": governance_decision,
        "deterministic_label": rule_result["deterministic_label"],
        "confidence_vector": confidence_vector,
        "trace": trace,
        "ai_explanation": ai_explanation,
    }


def _segment_clauses(document_text: str) -> List[str]:
    """Split contract content into clause-like segments for traceability."""
    segments: List[str] = []
    for raw in document_text.splitlines():
        clause = raw.strip()
        if clause:
            segments.append(clause)

    if not segments:
        text = document_text.strip()
        if text:
            segments = [text]

    return segments
