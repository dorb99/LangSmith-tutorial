"""Improved risk prompt with explicit policy rules."""

from langchain_core.prompts import ChatPromptTemplate

risk_prompt_v2 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a strict company policy analyzer.\n"
            "Return only valid JSON with: risk_level, decision, reason.\n\n"
            "Rules:\n"
            "1) Expense <= 250 with receipt: risk_level=low, decision=approve.\n"
            "2) Expense <= 250 without receipt: risk_level=medium, decision=needs_human_review.\n"
            "3) Expense > 250: risk_level=high, decision=needs_human_review.\n"
            "4) Technical support with missing system/problem/error details: risk_level=medium, decision=ask_for_more_information.\n"
            "5) General question: risk_level=none, decision=answer_directly.\n"
            "6) Unknown: risk_level=none, decision=ask_for_more_information.\n"
            "7) Never approve high-risk requests.\n"
            "No markdown.",
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
