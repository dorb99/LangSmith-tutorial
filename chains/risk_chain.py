"""Risk analysis chain builder with prompt versioning."""

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from config import get_llm
from prompts.risk_prompt_v1 import risk_prompt_v1
from prompts.risk_prompt_v2 import risk_prompt_v2
from utils.json_utils import safe_decision, safe_risk_level


def build_risk_chain(prompt_version: str, llm: ChatOpenAI | None = None) -> Runnable:
    parser = JsonOutputParser()
    llm = llm or get_llm()
    prompt = risk_prompt_v2 if prompt_version == "prompt-v2" else risk_prompt_v1

    chain = prompt | llm | parser

    def normalize(output: dict) -> dict:
        return {
            "risk_level": safe_risk_level(output.get("risk_level")),
            "decision": safe_decision(output.get("decision")),
            "reason": output.get("reason", "Insufficient information."),
        }

    return (chain | RunnableLambda(normalize)).with_config(
        {"run_name": "analyze_risk", "tags": ["risk-analysis", prompt_version]}
    )
