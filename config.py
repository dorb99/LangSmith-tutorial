"""Central configuration for the LangSmith + LangChain lab project."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

LANGSMITH_PROJECT_NAME = os.getenv("LANGSMITH_PROJECT", "langsmith-langchain-lab")
APP_VERSION = os.getenv("APP_VERSION", "v1")
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "prompt-v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))


def _require_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(
            f"Missing required environment variable '{name}'. "
            "Copy .env.example to .env and set the required API keys."
        )
    return value


def validate_environment() -> None:
    """Fail fast with clear messages for missing keys."""
    _require_env_var("OPENAI_API_KEY")
    _require_env_var("LANGSMITH_API_KEY")


def get_llm() -> ChatOpenAI:
    """Build the project LLM instance from environment settings."""
    validate_environment()
    return ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)


def build_run_config(
    *, mode: str, prompt_version: str, extra_tags: list[str] | None = None, extra_metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build a consistent RunnableConfig payload for LangSmith traces."""
    tags = [mode, "langchain", "langsmith", prompt_version]
    if extra_tags:
        tags.extend(extra_tags)

    metadata: dict[str, Any] = {
        "app_version": APP_VERSION,
        "prompt_version": prompt_version,
        "model": MODEL_NAME,
        "workflow": "company_request_assistant",
        "environment": "development",
        "mode": mode,
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    return {"tags": tags, "metadata": metadata}
