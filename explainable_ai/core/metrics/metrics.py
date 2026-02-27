"""In-memory, thread-safe metrics tracking for governance decisions."""

from __future__ import annotations

from threading import Lock
from typing import Dict


class _MetricsTracker:
    """Singleton-style metrics state container."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.total_requests = 0
        self.approved_count = 0
        self.review_required_count = 0
        self.escalate_count = 0
        self.cumulative_latency = 0.0

    def record_decision(self, decision: str, latency_ms: float) -> None:
        """Record one decision event and latency in milliseconds."""
        decision_text = str(decision)
        try:
            latency_value = float(latency_ms)
        except (TypeError, ValueError):
            latency_value = 0.0

        with self._lock:
            self.total_requests += 1

            if decision_text == "APPROVED":
                self.approved_count += 1
            elif decision_text == "REVIEW_REQUIRED":
                self.review_required_count += 1
            elif decision_text == "ESCALATE":
                self.escalate_count += 1

            self.cumulative_latency += latency_value

    def get_metrics(self) -> Dict[str, float | int]:
        """Return a snapshot of current metrics."""
        with self._lock:
            total_requests = self.total_requests
            approved = self.approved_count
            review_required = self.review_required_count
            escalate = self.escalate_count
            cumulative_latency = self.cumulative_latency

        average_latency = (cumulative_latency / total_requests) if total_requests else 0.0
        return {
            "total_requests": total_requests,
            "approved": approved,
            "review_required": review_required,
            "escalate": escalate,
            "average_latency_ms": average_latency,
        }


_TRACKER = _MetricsTracker()


def record_decision(decision: str, latency_ms: float) -> None:
    """Record a governance decision and latency."""
    _TRACKER.record_decision(decision=decision, latency_ms=latency_ms)


def get_metrics() -> dict:
    """Return aggregated metrics as a dictionary."""
    return _TRACKER.get_metrics()
