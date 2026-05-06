"""Run LangSmith experiments for prompt version comparison."""

from __future__ import annotations

import argparse

from app import run_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LangSmith evaluation experiment.")
    parser.add_argument("--prompt-version", default="prompt-v1", choices=["prompt-v1", "prompt-v2"])
    args = parser.parse_args()
    run_experiment(prompt_version=args.prompt_version)


if __name__ == "__main__":
    main()
