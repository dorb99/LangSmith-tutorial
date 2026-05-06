"""Policy context chain builder using RunnableLambda."""

from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnableLambda

POLICY_CONTEXT = {
    "expense": (
        "Team meals are allowed up to $250. A receipt is required. "
        "Missing receipts require human review. Expenses above $250 require manager review."
    ),
    "technical_support": (
        "Technical support requests should include the affected system, urgency, "
        "problem description, and error message if available."
    ),
    "general_question": (
        "General company questions should be answered briefly and clearly using available policy context."
    ),
    "unknown": "If the request type is unclear, ask the user for clarification.",
}


def build_context_chain() -> Runnable:
    def add_context(inputs: dict) -> dict:
        category = inputs.get("category", "unknown")
        return {"context": POLICY_CONTEXT.get(category, POLICY_CONTEXT["unknown"])}

    return RunnableLambda(add_context).with_config(
        {"run_name": "add_policy_context", "tags": ["policy-context"]}
    )
