"""Prompt template for request classification."""

from langchain_core.prompts import ChatPromptTemplate

classification_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Classify the user request into exactly one category.\n"
            "Valid categories: expense, technical_support, general_question, unknown.\n"
            "Return only valid JSON with key 'category'.\n"
            "Do not include markdown.",
        ),
        ("human", "User message:\n{user_input}"),
    ]
)
