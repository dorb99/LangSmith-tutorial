"""CLI entrypoint for the LangSmith + LangChain lab workflow."""

from __future__ import annotations

import argparse
from typing import Any

from chains.workflow import build_workflow
from config import (
    LANGSMITH_PROJECT_NAME,
    PROMPT_VERSION,
    build_run_config,
    validate_environment,
)
from data.examples import EXAMPLES
from evaluation.evaluators import (
    category_match,
    decision_match,
    has_reason,
    no_unsafe_approval,
    risk_match,
)
from langsmith import Client, evaluate

DATASET_NAME = "company-request-assistant-dataset"


def run_workflow(message: str, prompt_version: str) -> None:
    validate_environment()
    workflow = build_workflow(prompt_version=prompt_version)
    config = build_run_config(mode="lesson", prompt_version=prompt_version)
    result = workflow.invoke({"user_input": message}, config=config)

    print(f"LangSmith project: {LANGSMITH_PROJECT_NAME}")
    print(f"Prompt version: {prompt_version}")
    print()
    _print_result(result)
    print()
    print("Final answer:")
    print(result.get("final_answer", ""))


def create_dataset(reset: bool = False) -> None:
    validate_environment()
    client = Client()
    existing = next((ds for ds in client.list_datasets(dataset_name=DATASET_NAME)), None)

    if existing and reset:
        client.delete_dataset(dataset_id=existing.id)
        existing = None

    if existing:
        print(f"Created/reused dataset: {DATASET_NAME}")
        print(f"Examples: {len(EXAMPLES)}")
        return

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Training dataset for company request assistant LangSmith lab.",
    )
    for example in EXAMPLES:
        client.create_example(
            dataset_id=dataset.id,
            inputs=example["inputs"],
            outputs=example["outputs"],
            metadata=example["metadata"],
        )
    print(f"Created/reused dataset: {DATASET_NAME}")
    print(f"Examples: {len(EXAMPLES)}")


def run_experiment(prompt_version: str) -> None:
    validate_environment()
    client = Client()
    workflow = build_workflow(prompt_version=prompt_version)
    run_config = build_run_config(
        mode="evaluation",
        prompt_version=prompt_version,
        extra_metadata={"dataset": DATASET_NAME},
    )

    def target(inputs: dict[str, Any]) -> dict[str, Any]:
        return workflow.invoke(inputs, config=run_config)

    experiment = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[category_match, risk_match, decision_match, no_unsafe_approval, has_reason],
        experiment_prefix=f"company-request-assistant-{prompt_version}",
        client=client,
    )
    print(f"Experiment complete for {prompt_version}.")
    print(f"Results: {experiment}")


def _print_result(result: dict[str, Any]) -> None:
    print(f"Category: {result.get('category', 'unknown')}")
    print(f"Risk level: {result.get('risk_level', 'none')}")
    print(f"Decision: {result.get('decision', 'ask_for_more_information')}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LangSmith + LangChain lab CLI.")
    parser.add_argument(
        "--prompt-version",
        default=PROMPT_VERSION,
        choices=["prompt-v1", "prompt-v2"],
        help="Prompt version for workflow/evaluation commands.",
    )
    parser.add_argument("--message", help="Legacy run mode: user request message.")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run one workflow request.")
    run_parser.add_argument("--message", required=True, help="User request message.")
    run_parser.add_argument(
        "--prompt-version",
        default=PROMPT_VERSION,
        choices=["prompt-v1", "prompt-v2"],
    )

    dataset_parser = subparsers.add_parser("dataset", help="Create/reuse the evaluation dataset.")
    dataset_parser.add_argument("--reset", action="store_true", help="Delete and recreate dataset.")

    eval_parser = subparsers.add_parser("eval", help="Run an evaluation experiment.")
    eval_parser.add_argument(
        "--prompt-version",
        default=PROMPT_VERSION,
        choices=["prompt-v1", "prompt-v2"],
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "run":
        run_workflow(message=args.message, prompt_version=args.prompt_version)
        return
    if args.command == "dataset":
        create_dataset(reset=args.reset)
        return
    if args.command == "eval":
        run_experiment(prompt_version=args.prompt_version)
        return

    # Backward-compatible path: `python app.py --message "..."`
    if args.message:
        run_workflow(message=args.message, prompt_version=args.prompt_version)
        return
    parser.error("Provide a subcommand (`run`, `dataset`, `eval`) or pass --message.")


if __name__ == "__main__":
    main()
