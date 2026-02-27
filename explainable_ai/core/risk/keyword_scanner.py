"""Keyword-based risk scanning utilities."""

from __future__ import annotations

from typing import Dict, List


DANGEROUS_KEYWORDS = [
    "indemnification",
    "non-compete",
    "exclusivity",
    "net 90",
    "unlimited liability",
    "work for hire",
    "perpetual license",
]


def scan_for_risks(text: str) -> dict:
    """Scan input text for predefined risky contract keywords."""
    source_text = text.lower() if isinstance(text, str) else ""
    found_keywords: List[str] = [
        keyword for keyword in DANGEROUS_KEYWORDS if keyword in source_text
    ]

    result: Dict[str, List[str] | int] = {
        "risk_keywords_found": found_keywords,
        "risk_flag_count": len(found_keywords),
    }
    return result
