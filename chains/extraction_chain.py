"""Extraction chain builder."""

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from config import get_llm
from prompts.extraction_prompt import extraction_prompt


def build_extraction_chain(llm: ChatOpenAI | None = None) -> Runnable:
    parser = JsonOutputParser()
    llm = llm or get_llm()

    chain = extraction_prompt | llm | parser

    def normalize(output: dict) -> dict:
        
        if "missing_fields" not in output or not isinstance(output.get("missing_fields"), list):
            output["missing_fields"] = []
        return output

    return (chain | RunnableLambda(normalize)).with_config(
        {"run_name": "extract_details", "tags": ["extraction"]}
    )
