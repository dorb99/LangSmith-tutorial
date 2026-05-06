"""Basic risk prompt (intentionally weaker)."""

from langchain_core.prompts import ChatPromptTemplate

risk_prompt_v1 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Analyze risk and decision for a company request.\n"
            "Use category, extracted details, and context.\n"
            "Return only JSON with keys: risk_level, decision, reason.\n"
            "Allowed risk_level: low, medium, high, none.\n"
            "Allowed decision: approve, needs_human_review, ask_for_more_information, answer_directly.",
        ),
        (
            "human",
            "User input: {user_input}\n"
            "Category: {category}\n"
            "Extracted details: {extracted_details}\n"
            "Policy context: {context}",
        ),
    ]
)
