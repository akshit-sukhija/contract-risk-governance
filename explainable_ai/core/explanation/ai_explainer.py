"""AI-generated explanation helper for governance decision traces.

This module is strictly presentation-only. It must not modify governance
decisions, influence scoring, or alter rule-evaluation outcomes.
"""

from __future__ import annotations

import json
import os
from typing import Any, List

import requests


DEFAULT_MODEL_ID = "google/flan-t5-large"
INFERENCE_API_URL_TEMPLATE = "https://api-inference.huggingface.co/models/{model_id}"
REQUEST_TIMEOUT_SECONDS = 15
MAX_TRACE_ITEMS = 40
MAX_EXPLANATION_CHARS = 1200


def generate_ai_explanation(trace: list, final_decision: str) -> str:
    """Generate a human-readable explanation from trace and final decision.

    This function is fail-safe by design. Any token/API/network/parsing issue
    returns a deterministic fallback explanation and does not raise outward.
    """
    fallback = _fallback_explanation(trace=trace, final_decision=final_decision)

    if not isinstance(trace, list) or not isinstance(final_decision, str) or not final_decision.strip():
        return fallback

    token = os.getenv("HF_API_TOKEN", "").strip()
    if not token:
        return fallback

    model_id = os.getenv("HF_MODEL_ID", DEFAULT_MODEL_ID).strip() or DEFAULT_MODEL_ID
    prompt = _build_prompt(trace=trace, final_decision=final_decision)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 220,
            "temperature": 0.2,
            "return_full_text": False,
        },
    }

    try:
        response = requests.post(
            INFERENCE_API_URL_TEMPLATE.format(model_id=model_id),
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            return fallback

        data = response.json()
        if isinstance(data, dict) and isinstance(data.get("error"), str):
            return fallback

        explanation = _extract_generated_text(data).strip()
        if not explanation:
            return fallback

        return _truncate_explanation(explanation)
    except (requests.RequestException, ValueError, TypeError):
        return fallback


def _build_prompt(trace: List[Any], final_decision: str) -> str:
    trace_lines: List[str] = []
    for index, entry in enumerate(trace[:MAX_TRACE_ITEMS], start=1):
        if not isinstance(entry, dict):
            trace_lines.append(f"{index}. {entry}")
            continue

        step = str(entry.get("step", "Unknown Step"))
        details = []
        for key, value in entry.items():
            if key == "step":
                continue
            details.append(f"{key}={_stringify_value(value)}")

        suffix = f" | {'; '.join(details)}" if details else ""
        trace_lines.append(f"{index}. {step}{suffix}")

    trace_block = "\n".join(trace_lines) if trace_lines else "No trace steps available."

    return (
        "You are generating an audit-friendly explanation for a governance decision.\n"
        "Use only the provided trace and final decision.\n"
        "Do not change the outcome, do not add unsupported claims.\n"
        "Write a concise explanation in 4-6 sentences.\n\n"
        f"Final Decision: {final_decision}\n"
        "Trace Timeline:\n"
        f"{trace_block}\n"
    )


def _extract_generated_text(payload: Any) -> str:
    if isinstance(payload, list) and payload:
        first = payload[0]
        if isinstance(first, dict):
            text = first.get("generated_text")
            if isinstance(text, str):
                return text

    if isinstance(payload, dict):
        text = payload.get("generated_text")
        if isinstance(text, str):
            return text

    return ""


def _fallback_explanation(trace: Any, final_decision: str) -> str:
    passed = 0
    failed = 0
    eligibility_score: Any = "N/A"

    if isinstance(trace, list):
        for item in trace:
            if not isinstance(item, dict):
                continue

            if item.get("step") == "Rule Evaluation":
                result = str(item.get("result", "")).upper()
                if result == "PASS":
                    passed += 1
                elif result == "FAIL":
                    failed += 1

            if item.get("step") == "Score Computed" and "value" in item:
                eligibility_score = item.get("value")

    decision_text = final_decision if isinstance(final_decision, str) and final_decision.strip() else "UNKNOWN"

    return (
        "Automated explanation service is currently unavailable. "
        f"The final governance decision is '{decision_text}'. "
        f"Rule evaluation summary: {passed} passed, {failed} failed. "
        f"Eligibility score: {eligibility_score}. "
        "Please refer to the full decision trace for complete audit details."
    )


def _truncate_explanation(explanation: str) -> str:
    if len(explanation) <= MAX_EXPLANATION_CHARS:
        return explanation
    return explanation[: MAX_EXPLANATION_CHARS - 3].rstrip() + "..."


def _stringify_value(value: Any) -> str:
    try:
        text = json.dumps(value, ensure_ascii=True)
    except (TypeError, ValueError):
        text = str(value)

    if len(text) > 180:
        return text[:177] + "..."
    return text