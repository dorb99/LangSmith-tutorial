"""Main workflow composition for the lab project."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import (
    Runnable,
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
)

from config import APP_VERSION, MODEL_NAME, PROMPT_VERSION, get_llm
from chains.classification_chain import build_classification_chain
from chains.context_chain import build_context_chain
from chains.extraction_chain import build_extraction_chain
from chains.final_response_chain import build_final_response_chain
from chains.risk_chain import build_risk_chain
from utils.json_utils import safe_category, safe_decision, safe_risk_level


def _safe_fallback(inputs: dict[str, Any]) -> dict[str, Any]:
    user_input = str(inputs.get("user_input", "") or "").strip()
    return {
        "category": "unknown",
        "extracted_details": {
            "reason": "Could not parse model output.",
            "missing_fields": [],
        },
        "context": "If the request type is unclear, ask the user for clarification.",
        "risk_level": "none",
        "decision": "ask_for_more_information",
        "reason": "Could not complete analysis safely.",
        "final_answer": (
            f"I need a bit more detail to help with this request: '{user_input}'. "
            "Please clarify what you need and include key details."
        ),
    }


def _preprocess_user_input(inputs: dict[str, Any]) -> dict[str, Any]:
    """Normalize the incoming payload into a consistent workflow state."""
    user_input = str(inputs.get("user_input", "") or "").strip()
    return {"user_input": user_input, "is_empty": user_input == ""}


def build_workflow(prompt_version: str = PROMPT_VERSION) -> Runnable:
    """Build the full workflow as an LCEL pipeline."""
    llm = get_llm()
    classify = build_classification_chain(llm=llm)
    extract = build_extraction_chain(llm=llm)
    add_context = build_context_chain()
    analyze_risk = build_risk_chain(prompt_version=prompt_version, llm=llm)
    final_response = build_final_response_chain(llm=llm)

    # Main happy-path pipeline operating on a shared state dict.
    normal_pipeline: Runnable = (
        RunnablePassthrough()
        # 1) Classify the request.
        | RunnablePassthrough.assign(
            category=RunnableLambda(
                lambda state: classify.invoke({"user_input": state["user_input"]})[
                    "category"
                ]
            )
        )
        # 2) Extract structured details from the input and category.
        | RunnablePassthrough.assign(
            extracted_details=RunnableLambda(
                lambda state: extract.invoke(
                    {
                        "user_input": state["user_input"],
                        "category": state["category"],
                    }
                )
            )
        )
        # 3) Add fake policy/technical/general context based on category.
        | RunnablePassthrough.assign(
            context=RunnableLambda(
                lambda state: add_context.invoke({"category": state["category"]})[
                    "context"
                ]
            )
        )
        # 4) Run risk analysis using prompt-v1 or prompt-v2.
        | RunnablePassthrough.assign(
            risk_analysis=RunnableLambda(
                lambda state: analyze_risk.invoke(
                    {
                        "user_input": state["user_input"],
                        "category": state["category"],
                        "extracted_details": state["extracted_details"],
                        "context": state["context"],
                    }
                )
            )
        )
        # 5) Generate the final natural-language answer.
        | RunnablePassthrough.assign(
            final_answer=RunnableLambda(
                lambda state: final_response.invoke(
                    {
                        "user_input": state["user_input"],
                        "category": state["category"],
                        "extracted_details": state["extracted_details"],
                        "context": state["context"],
                        "risk_analysis": state["risk_analysis"],
                    }
                )
            )
        )
        # 6) Post-process into the public output schema, applying safety helpers.
        | RunnableLambda(
            lambda state: {
                "category": safe_category(state.get("category")),
                "extracted_details": state.get("extracted_details", {}),
                "context": state.get("context", ""),
                "risk_level": safe_risk_level(
                    state.get("risk_analysis", {}).get("risk_level")
                ),
                "decision": safe_decision(
                    state.get("risk_analysis", {}).get("decision")
                ),
                "reason": state.get("risk_analysis", {}).get(
                    "reason", "No reason provided."
                ),
                "final_answer": (
                    state.get("final_answer", "").strip()
                    if isinstance(state.get("final_answer"), str)
                    and state.get("final_answer", "").strip()
                    else "Please provide more details so I can help."
                ),
            }
        )
    )

    # Route empty-input cases to a safe fallback.
    workflow: Runnable = RunnableLambda(_preprocess_user_input) | RunnableBranch(
        # If the (normalized) user_input is empty, go straight to fallback.
        (lambda state: state.get("is_empty", False), RunnableLambda(_safe_fallback)),
        # Default branch: normal LCEL pipeline.
        normal_pipeline,
    )

    return workflow.with_config(
        {
            "run_name": "full_company_request_workflow",
            "tags": ["workflow", "company-request-assistant", prompt_version],
            "metadata": {
                "app_version": APP_VERSION,
                "prompt_version": prompt_version,
                "model": MODEL_NAME,
                "workflow": "company_request_assistant",
                "environment": "development",
            },
        }
    )
