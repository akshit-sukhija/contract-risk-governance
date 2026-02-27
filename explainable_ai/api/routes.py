"""FastAPI routes for deterministic governance evaluation."""

from __future__ import annotations

import csv
import io
import time
import uuid
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, HTTPException, UploadFile

from explainable_ai.core.audit.audit_logger import log_decision
from explainable_ai.core.engine.main import evaluate_contract
from explainable_ai.core.engine.rule_engine import RuleEngine
from explainable_ai.core.governance.governance import apply_governance_layer
from explainable_ai.core.logging.logger import get_logger
from explainable_ai.core.metrics.metrics import record_decision
from explainable_ai.core.scoring.scoring import calculate_confidence_vector
from explainable_ai.core.trace.decision_trace import generate_decision_trace


app = FastAPI(title="Explainable AI Governance API")
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
POLICY_PATH = BASE_DIR / "policies" / "rules.yaml"


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate")
def evaluate(request_data: Dict[str, Any]) -> Dict[str, Any]:
    start = time.perf_counter()
    decision_id: str | None = None

    enable_ai_explanation = request_data.get("enable_ai_explanation", False)
    if not isinstance(enable_ai_explanation, bool):
        raise HTTPException(
            status_code=400,
            detail="enable_ai_explanation must be a boolean.",
        )

    document_text = request_data.get("document_text")
    if not isinstance(document_text, str) or not document_text.strip():
        raise HTTPException(
            status_code=400,
            detail="document_text must be a non-empty string.",
        )

    applicant_data: Dict[str, Any] = {"document_text": document_text}

    try:
        result = evaluate_contract(
            document_text=document_text,
            enable_ai=enable_ai_explanation,
        )
    except (FileNotFoundError, ValueError, TypeError) as exc:
        logger.error(f"Evaluation error: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    risk_scan = _extract_risk_scan_from_trace(result["trace"])

    latency_ms = (time.perf_counter() - start) * 1000.0
    decision_id = str(uuid.uuid4())

    log_decision(
        decision_id=decision_id,
        input_data=applicant_data,
        deterministic_label=result["deterministic_label"],
        governance_decision=result["decision"],
        confidence_vector=result["confidence_vector"],
        latency_ms=latency_ms,
    )
    record_decision(result["decision"], latency_ms)

    logger.info(f"Decision computed: {result['decision']} | decision_id={decision_id}")

    return {
        "decision_id": decision_id,
        "decision": result["decision"],
        "deterministic_label": result["deterministic_label"],
        "confidence_vector": result["confidence_vector"],
        "trace": result["trace"],
        "risk_keywords_found": risk_scan["risk_keywords_found"],
        "risk_flag_count": risk_scan["risk_flag_count"],
        "ai_explanation": result["ai_explanation"],
        "latency_ms": round(latency_ms, 3),
    }


@app.post("/batch_evaluate")
async def batch_evaluate(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    try:
        contents = await file.read()
        text = contents.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))

        rule_engine = RuleEngine(POLICY_PATH)
        rows = [dict(row) for row in reader]

        if not rows:
            raise HTTPException(status_code=400, detail="CSV file contains no data rows.")

        approved = 0
        review_required = 0
        escalate = 0
        confidence_sum = 0.0

        for row in rows:
            applicant_data = _coerce_row_values(row)
            result = _evaluate_applicant(applicant_data, rule_engine)

            decision = result["decision"]
            if decision == "APPROVED":
                approved += 1
            elif decision == "REVIEW_REQUIRED":
                review_required += 1
            elif decision == "ESCALATE":
                escalate += 1

            confidence_sum += float(result["confidence_vector"]["rule_confidence"])

        total = len(rows)
        average_rule_confidence = confidence_sum / total if total else 0.0

        return {
            "total": total,
            "approved": approved,
            "review_required": review_required,
            "escalate": escalate,
            "average_rule_confidence": round(average_rule_confidence, 3),
        }
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded.") from exc
    except (ValueError, TypeError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/metrics")
def metrics() -> Dict[str, Any]:
    from explainable_ai.core.metrics.metrics import get_metrics

    return get_metrics()


def _evaluate_applicant(applicant_data: Any, rule_engine: RuleEngine) -> Dict[str, Any]:
    rule_result = rule_engine.evaluate(applicant_data)

    if isinstance(applicant_data, dict):
        retrieval_similarity = float(applicant_data.get("retrieval_similarity", 1.0))
        data_completeness = float(applicant_data.get("data_completeness", 1.0))
        crag_blocked = bool(applicant_data.get("crag_blocked", False))
        trace_input_data: Dict[str, Any] = applicant_data
    else:
        retrieval_similarity = 1.0
        data_completeness = 1.0
        crag_blocked = False
        trace_input_data = {"document_text": str(applicant_data)}

    confidence_vector = calculate_confidence_vector(
        passed_rules=rule_result["passed_rules"],
        failed_rules=rule_result["failed_rules"],
        total_rules=len(rule_engine.rules),
        retrieval_similarity=retrieval_similarity,
        data_completeness=data_completeness,
    )

    governance_decision = apply_governance_layer(
        deterministic_label=rule_result["deterministic_label"],
        confidence_vector=confidence_vector,
        crag_blocked=crag_blocked,
    )

    trace = generate_decision_trace(
        input_data=trace_input_data,
        passed_rules=rule_result["passed_rules"],
        failed_rules=rule_result["failed_rules"],
        eligibility_score=rule_result["eligibility_score"],
        confidence_vector=confidence_vector,
        governance_decision=governance_decision,
    )

    return {
        "decision": governance_decision,
        "deterministic_label": rule_result["deterministic_label"],
        "confidence_vector": confidence_vector,
        "trace": trace,
    }


def _coerce_row_values(row: Dict[str, Any]) -> Dict[str, Any]:
    coerced: Dict[str, Any] = {}
    for key, value in row.items():
        coerced[key] = _coerce_value(value)
    return coerced


def _coerce_value(value: Any) -> Any:
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    text = value.strip()
    if text == "":
        return ""

    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False

    try:
        if any(ch in text for ch in (".", "e", "E")):
            return float(text)
        return int(text)
    except ValueError:
        return text


def _extract_risk_scan_from_trace(trace: Any) -> Dict[str, Any]:
    if not isinstance(trace, list):
        return {"risk_keywords_found": [], "risk_flag_count": 0}

    for item in trace:
        if not isinstance(item, dict):
            continue

        if item.get("step") != "Keyword Hard Gate":
            continue

        value = item.get("value", [])
        if not isinstance(value, list):
            value = []

        keywords = [str(entry) for entry in value]
        return {
            "risk_keywords_found": keywords,
            "risk_flag_count": len(keywords),
        }

    return {"risk_keywords_found": [], "risk_flag_count": 0}
