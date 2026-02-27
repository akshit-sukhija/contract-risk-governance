"""Deterministic contract keyword risk rule engine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml


@dataclass(frozen=True)
class Rule:
    """Represents a single contract keyword risk rule."""

    id: str
    keywords: List[str]
    weight: int


class RuleEngine:
    """Loads and evaluates deterministic contract keyword rules."""

    def __init__(self, policy_path: str | Path) -> None:
        self.policy_path = Path(policy_path)
        self.rules = self._load_rules(self.policy_path)

    def evaluate(self, document_text: str) -> Dict[str, object]:
        """Evaluate contract text against keyword risk rules."""
        if not isinstance(document_text, str):
            raise TypeError("document_text must be a string.")

        lowered_text = document_text.lower()

        passed_rules: List[str] = []
        failed_rules: List[str] = []
        risk_score = 0

        for rule in self.rules:
            if self._evaluate_rule(rule, lowered_text):
                failed_rules.append(rule.id)
                risk_score += rule.weight
            else:
                passed_rules.append(rule.id)

        label = self._deterministic_label(risk_score)

        return {
            "deterministic_label": label,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "eligibility_score": int(risk_score),
        }

    @staticmethod
    def _load_rules(policy_path: Path) -> List[Rule]:
        if not policy_path.exists():
            raise FileNotFoundError(f"Policy file not found: {policy_path}")

        with policy_path.open("r", encoding="utf-8") as file:
            raw = yaml.safe_load(file) or {}

        if not isinstance(raw, dict):
            raise ValueError("Policy YAML must contain a top-level 'rules' mapping.")

        if "rules" not in raw:
            raise ValueError("Policy YAML must contain the 'rules' key.")

        raw_rules = raw["rules"]
        if not isinstance(raw_rules, list):
            raise ValueError("Policy YAML key 'rules' must be a list.")

        rules: List[Rule] = []
        for index, item in enumerate(raw_rules):
            if not isinstance(item, dict):
                raise ValueError(f"Rule at index {index} must be a mapping.")

            missing = [k for k in ("id", "keywords", "weight") if k not in item]
            if missing:
                raise ValueError(f"Rule at index {index} missing fields: {', '.join(missing)}")

            rule_id = item.get("id", index)
            keywords = item["keywords"]
            if not isinstance(keywords, list) or not keywords:
                raise ValueError(f"Rule '{rule_id}' must have a non-empty keywords list.")
            if not all(isinstance(keyword, str) and keyword.strip() for keyword in keywords):
                raise ValueError(f"Rule '{rule_id}' has invalid keyword entries.")

            weight = item["weight"]
            if not isinstance(weight, int):
                raise ValueError(f"Rule '{rule_id}' has non-integer weight.")

            rules.append(
                Rule(
                    id=str(item["id"]),
                    keywords=[keyword.lower() for keyword in keywords],
                    weight=weight,
                )
            )

        return rules

    @staticmethod
    def _evaluate_rule(rule: Rule, lowered_document_text: str) -> bool:
        return any(keyword in lowered_document_text for keyword in rule.keywords)

    @staticmethod
    def _deterministic_label(risk_score: int) -> str:
        if risk_score == 0:
            return "LOW_RISK"
        if 1 <= risk_score <= 40:
            return "MEDIUM_RISK"
        return "HIGH_RISK"
