"""Classification chain builder."""

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from config import get_llm
from prompts.classification_prompt import classification_prompt
from utils.json_utils import safe_category


def build_classification_chain(llm: ChatOpenAI | None = None) -> Runnable:
    parser = JsonOutputParser()
    llm = llm or get_llm()

    chain = classification_prompt | llm | parser

    def normalize(output: dict) -> dict:
        return {"category": safe_category(output.get("category"))}

    return (chain | RunnableLambda(normalize)).with_config(
        {"run_name": "classify_request", "tags": ["classification"]}
    )
