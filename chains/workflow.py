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


EMPTY_INPUT_RESPONSE: dict[str, Any] = {
    "category": "unknown",
    "extracted_details": {
        "reason": "Could not parse model output.",
        "missing_fields": [],
    },
    "context": "If the request type is unclear, ask the user for clarification.",
    "risk_level": "none",
    "decision": "ask_for_more_information",
    "reason": "Could not complete analysis safely.",
    "final_answer": "I need a bit more detail to help. Please clarify what you need and include key details.",
}


def build_workflow(prompt_version: str = PROMPT_VERSION) -> Runnable:
    """Build the full workflow as a simple step-by-step pipeline."""
    llm = get_llm()
    classify = build_classification_chain(llm=llm)
    extract = build_extraction_chain(llm=llm)
    add_context = build_context_chain()
    analyze_risk = build_risk_chain(prompt_version=prompt_version, llm=llm)
    final_response = build_final_response_chain(llm=llm)

    def run(inputs: dict[str, Any]) -> dict[str, Any]:
        # 0) Read and clean the user's input.
        user_input = str(inputs.get("user_input", "") or "").strip()
        if not user_input:
            return EMPTY_INPUT_RESPONSE

        # 1) Classify the request (e.g. policy / technical / general).
        category = classify.invoke({"user_input": user_input})["category"]

        # 2) Extract structured details from the input.
        extracted_details = extract.invoke(
            {"user_input": user_input, "category": category}
        )

        # 3) Add helpful context based on the category.
        context = add_context.invoke({"category": category})["context"]

        # 4) Analyze risk and decide what to do.
        risk_analysis = analyze_risk.invoke(
            {
                "user_input": user_input,
                "category": category,
                "extracted_details": extracted_details,
                "context": context,
            }
        )

        # 5) Generate the final answer for the user.
        final_answer = final_response.invoke(
            {
                "user_input": user_input,
                "category": category,
                "extracted_details": extracted_details,
                "context": context,
                "risk_analysis": risk_analysis,
            }
        )

        # 6) Package the public response.
        clean_answer = final_answer.strip() if isinstance(final_answer, str) else ""
        return {
            "category": safe_category(category),
            "extracted_details": extracted_details,
            "context": context,
            "risk_level": safe_risk_level(risk_analysis.get("risk_level")),
            "decision": safe_decision(risk_analysis.get("decision")),
            "reason": risk_analysis.get("reason", "No reason provided."),
            "final_answer": clean_answer or "Please provide more details so I can help.",
        }

    workflow = RunnableLambda(run)
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


def build_workflow_LCEL(prompt_version: str = PROMPT_VERSION) -> Runnable:
    """Same workflow as build_workflow, but written in LCEL style."""
    llm = get_llm()
    classify = build_classification_chain(llm=llm)
    extract = build_extraction_chain(llm=llm)
    add_context = build_context_chain()
    analyze_risk = build_risk_chain(prompt_version=prompt_version, llm=llm)
    final_response = build_final_response_chain(llm=llm)

    # 0) Read and clean user input.
    preprocess = RunnableLambda(
        lambda inputs: {
            "user_input": str(inputs.get("user_input", "") or "").strip(),
            "is_empty": str(inputs.get("user_input", "") or "").strip() == "",
        }
    )

    # 1-6) Same steps as build_workflow, but composed with LCEL operators.
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
        # 2) Extract structured details from the input.
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
        # 3) Add helpful context based on category.
        | RunnablePassthrough.assign(
            context=RunnableLambda(
                lambda state: add_context.invoke({"category": state["category"]})[
                    "context"
                ]
            )
        )
        # 4) Analyze risk and decide what to do.
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
        # 5) Generate the final answer for the user.
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
        # 6) Package the public response.
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

    workflow: Runnable = preprocess | RunnableBranch(
        (lambda state: state.get("is_empty", False), RunnableLambda(lambda _: EMPTY_INPUT_RESPONSE)),
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
