"""Utility helpers for robust JSON-like workflow outputs."""

from __future__ import annotations

from typing import Any


def safe_category(value: Any) -> str:
    allowed = {"expense", "technical_support", "general_question", "unknown"}
    if isinstance(value, str) and value in allowed:
        return value
    return "unknown"


def safe_risk_level(value: Any) -> str:
    allowed = {"low", "medium", "high", "none"}
    if isinstance(value, str) and value in allowed:
        return value
    return "none"


def safe_decision(value: Any) -> str:
    allowed = {"approve", "needs_human_review", "ask_for_more_information", "answer_directly"}
    if isinstance(value, str) and value in allowed:
        return value
    return "ask_for_more_information"
