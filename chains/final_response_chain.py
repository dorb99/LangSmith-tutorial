"""Final response generation chain."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from config import get_llm
from prompts.final_response_prompt import final_response_prompt


def build_final_response_chain(llm: ChatOpenAI | None = None) -> Runnable:
    llm = llm or get_llm()
    parser = StrOutputParser()

    chain = final_response_prompt | llm | parser
    return chain.with_config(
        {"run_name": "generate_final_answer", "tags": ["final-response"]}
    )
