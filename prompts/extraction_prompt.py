"""Prompt template for category-aware extraction."""

from langchain_core.prompts import ChatPromptTemplate

extraction_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Extract details from the user request based on category.\n"
            "Input keys: user_input, category.\n"
            "Return only valid JSON. Include 'missing_fields' as a list.\n"
            "Category schemas:\n"
            "- expense: amount(number|null), currency(str|null), vendor(str|null), "
            "receipt_attached(bool|null), number_of_people(number|null), missing_fields(list[str])\n"
            "- technical_support: system(str|null), problem(str|null), urgency(low|medium|high|unknown), "
            "error_message(str|null), missing_fields(list[str])\n"
            "- general_question: topic(str|null), question(str|null), missing_fields(list[str])\n"
            "- unknown: reason(str), missing_fields(list[str])\n"
            "Do not include markdown.",
        ),
        (
            "human",
            "Category: {category}\n"
            "User message: {user_input}",
        ),
    ]
)
