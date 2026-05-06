# langsmith_langchain_lab

A beginner-to-mid-level educational project for learning **LangChain LCEL** with **LangSmith observability**.

## What this project teaches

- How to build a small multi-step LangChain workflow (without LangGraph).
- How to trace each workflow step in LangSmith.
- How to attach tags and metadata using `RunnableConfig` and `with_config`.
- How to run prompt version experiments (`prompt-v1` vs `prompt-v2`).
- How to create a LangSmith dataset and run evaluator-based experiments.

## Why the app is intentionally simple

The business logic is intentionally lightweight so students can focus on the real learning target: **LangSmith tracing, debugging, and evaluation workflows**.  
There is no frontend, no real database, and no real RAG.

## Project structure

```text
langsmith_langchain_lab/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── chains/
├── prompts/
├── data/
├── evaluation/
└── utils/
```

## Setup

1. Create virtual environment:
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy environment file:
   - `copy .env.example .env`
4. Add your keys in `.env`:
   - `OPENAI_API_KEY=...`
   - `LANGSMITH_API_KEY=...`

If required keys are missing, the app raises a clear `ValueError` with setup instructions.

## Run the app

```bash
python app.py --message "I paid $184 for a team dinner yesterday at North Grill with 5 people, but I forgot the receipt."
```

or with explicit subcommand:

```bash
python app.py run --message "I paid $184 for a team dinner yesterday at North Grill with 5 people, but I forgot the receipt."
```

Expected style of output:

- `Category: expense`
- `Risk level: medium`
- `Decision: needs_human_review`
- Final answer explains why.

The CLI also prints:

- LangSmith project name
- Prompt version

## View traces in LangSmith

Every run includes:

- Parent workflow run: `full_company_request_workflow`
- Child runs:
  - `classify_request`
  - `extract_details`
  - `add_policy_context`
  - `analyze_risk`
  - `generate_final_answer`

Open your LangSmith project (`LANGSMITH_PROJECT`) and inspect nested traces, tags, metadata, latency, and token usage.

## Create evaluation dataset

```bash
python app.py dataset
```

Creates/reuses dataset:

- `company-request-assistant-dataset`
- 10 examples from `data/examples.py`

Optional reset:

```bash
python app.py dataset --reset
```

## Run experiment: prompt-v1

```bash
python app.py eval --prompt-version prompt-v1
```

## Run experiment: prompt-v2

```bash
python app.py eval --prompt-version prompt-v2
```

Both runs are stored in LangSmith experiments with prompt version in:

- experiment prefix
- tags
- metadata

## Learning path

Use `PRACTICE.md` as the single lab script for missions, comparisons, and debugging report format.

## Final deliverables

- Working app
- LangSmith traces
- Dataset in LangSmith
- Two experiments (`prompt-v1` and `prompt-v2`)
- Evaluator results
- Debugging report
