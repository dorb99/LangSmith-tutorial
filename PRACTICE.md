# Practice Guide (LangChain + LangSmith)

This file is your **hands-on lab script**. Follow the missions in order. The app logic is intentionally simple so you can focus on **LangSmith tracing, metadata/tags, datasets, evaluations, and prompt version experiments**.

## Before you start (5 minutes)

1. Create `.env`:
   - Copy `.env.example` → `.env`
2. Fill these values in `.env`:
   - `OPENAI_API_KEY=...`
   - `LANGSMITH_API_KEY=...`
   - `LANGSMITH_TRACING=true`
   - `LANGSMITH_PROJECT=langsmith-langchain-lab`
3. Install:

```bash
pip install -r requirements.txt
```

If keys are missing, the code will raise a clear `ValueError` telling you what to set.

## Mission 1: Run the workflow and confirm trace structure

Run:

```bash
python app.py --message "I paid $184 for a team dinner yesterday at North Grill with 5 people, but I forgot the receipt."
```

In terminal, confirm you see:

- `Category: ...`
- `Risk level: ...`
- `Decision: ...`
- `Final answer: ...`

In LangSmith, open your project and find the latest run.

### What to check in LangSmith (trace)

- **Parent run name**: `full_company_request_workflow`
- **Child run names** (these should appear nested under the parent):
  - `classify_request`
  - `extract_details`
  - `add_policy_context`
  - `analyze_risk`
  - `generate_final_answer`
- **Inspect each child run**:
  - Inputs: Are the right fields passed?
  - Outputs: Is it valid JSON where expected?
  - Errors: Any parsing issues or tool errors?

## Mission 2: Learn tags + metadata inheritance (RunnableConfig)

Open `app.py` and find the `config = {...}` passed to:

- `workflow.invoke(..., config=config)`

Add:

- One new tag (example: `"practice-mission-2"`)
- One new metadata field (example: `"student": "dor"`)

Re-run the same command from Mission 1.

### What to check in LangSmith

- The **parent run** should show the new tag and metadata.
- Child runs should also show those values (tags/metadata are **inherited** through the runnable tree).

## Mission 3: Prompt versioning (prompt-v1 vs prompt-v2)

Run the same request with both prompt versions:

```bash
python app.py --prompt-version prompt-v1 --message "I paid $184 for a team dinner at North Grill with 5 people, but I forgot the receipt."
python app.py --prompt-version prompt-v2 --message "I paid $184 for a team dinner at North Grill with 5 people, but I forgot the receipt."
```

### What to compare in LangSmith

In `analyze_risk`:

- Does the output JSON follow the schema reliably?
- Are `risk_level` and `decision` consistent with policy?
- Is the `reason` clear and policy-based?

In `generate_final_answer`:

- Does it clearly explain the decision?
- Is it short and user-friendly?

## Mission 4: Create a LangSmith dataset from local examples

Run:

```bash
python app.py dataset
```

This creates/reuses:

- Dataset name: `company-request-assistant-dataset`
- Examples: 10 (from `data/examples.py`)

Optional reset:

```bash
python app.py dataset --reset
```

### What to check in LangSmith

- The dataset exists and has 10 examples.
- Each example includes:
  - inputs: `user_input`
  - reference outputs: `expected_category`, `expected_risk`, `expected_decision`
  - metadata: `case_type`, `difficulty`

## Mission 5: Run LangSmith experiments (evaluators + experiments)

Run prompt-v1 experiment:

```bash
python app.py eval --prompt-version prompt-v1
```

Run prompt-v2 experiment:

```bash
python app.py eval --prompt-version prompt-v2
```

### What to check in LangSmith (experiments)

Compare `prompt-v1` vs `prompt-v2` on:

- Evaluator results:
  - `category_match`
  - `risk_match`
  - `decision_match`
  - `no_unsafe_approval`
  - `has_reason`
- Operational signals:
  - latency
  - token usage
  - error rate / failed runs
- Failure analysis:
  - which examples fail consistently?
  - do failures correlate with a certain `case_type` or `difficulty`?

## Mission 6: Debug one failure using a trace (the real LangSmith skill)

1. Pick one failed example from an experiment.
2. Open that example’s **run trace**.
3. Decide where the failure happened:
   - classification
   - extraction
   - policy context
   - risk analysis
   - final response
4. Fix the smallest thing that could improve it:
   - Improve `risk_prompt_v2.py` rules wording
   - Improve `extraction_prompt.py` instructions
   - Tighten JSON-only instructions
5. Re-run the experiment and confirm the evaluator score improved.

### Debugging Report Template (copy/paste)

Failed input:
...

Expected behavior:
...

Actual behavior:
...

Where the failure happened:
classification / extraction / policy context / risk analysis / final response

Evidence from LangSmith:
...

Fix:
...

Result after rerun:
...

## Bonus Missions (optional)

### Bonus A: Add one more dataset example

Add an 11th example to `data/examples.py`, then run:

```bash
python app.py dataset --reset
```

Re-run both experiments and observe the new case’s behavior.

### Bonus B: Measure prompt improvements without changing code

Only change prompt text in `prompts/risk_prompt_v2.py` and re-run:

```bash
python app.py eval --prompt-version prompt-v2
```

Compare experiment results to your previous `prompt-v2` run.
