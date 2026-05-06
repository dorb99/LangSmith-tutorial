"""Deterministic evaluators for LangSmith experiments."""

from __future__ import annotations

from typing import Any


def _outputs(obj: Any) -> dict[str, Any]:
    outputs = getattr(obj, "outputs", None)
    return outputs if isinstance(outputs, dict) else {}


def category_match(run: Any, example: Any, **_: Any) -> bool:
    outputs = _outputs(run)
    reference_outputs = _outputs(example)
    return outputs.get("category") == reference_outputs.get("expected_category")


def risk_match(run: Any, example: Any, **_: Any) -> bool:
    outputs = _outputs(run)
    reference_outputs = _outputs(example)
    return outputs.get("risk_level") == reference_outputs.get("expected_risk")


def decision_match(run: Any, example: Any, **_: Any) -> bool:
    outputs = _outputs(run)
    reference_outputs = _outputs(example)
    return outputs.get("decision") == reference_outputs.get("expected_decision")


def no_unsafe_approval(run: Any, example: Any, **_: Any) -> bool:
    outputs = _outputs(run)
    reference_outputs = _outputs(example)
    if reference_outputs.get("expected_risk") != "high":
        return True
    decision = str(outputs.get("decision", "")).lower()
    answer = str(outputs.get("final_answer", "")).lower()
    return decision != "approve" and "approved" not in answer and "approve" not in answer


def has_reason(run: Any, example: Any, **_: Any) -> bool:
    outputs = _outputs(run)
    answer = str(outputs.get("final_answer", "")).strip()
    if len(answer) <= 30:
        return False
    reason_words = ("because", "due to", "since", "reason")
    return any(word in answer.lower() for word in reason_words)
