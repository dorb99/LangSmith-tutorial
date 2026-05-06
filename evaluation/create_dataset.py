"""Create or reuse a LangSmith dataset for this lab."""

from __future__ import annotations

import argparse

from app import create_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Create LangSmith evaluation dataset.")
    parser.add_argument("--reset", action="store_true", help="Delete and recreate dataset.")
    args = parser.parse_args()
    create_dataset(reset=args.reset)


if __name__ == "__main__":
    main()
