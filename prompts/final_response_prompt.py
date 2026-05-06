"""Prompt for user-facing final response."""

from langchain_core.prompts import ChatPromptTemplate

final_response_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Write a short, clear final response to the user.\n"
            "Use risk analysis and context.\n"
            "Respond in plain text only, no markdown.",
        ),
        (
            "human",
            "User input: {user_input}\n"
            "Category: {category}\n"
            "Extracted details: {extracted_details}\n"
            "Context: {context}\n"
            "Risk analysis: {risk_analysis}",
        ),
    ]
)
