# AI Triage Workflow

A small GitHub issue triage workflow built for the AI Engineering homework.

The workflow follows the required shape:

```text
preprocess -> classify -> route
cat > README.md <<'EOF'
# AI Triage Workflow

A small GitHub issue triage workflow built for the AI Engineering homework.

The workflow follows the required shape:

```text
preprocess -> classify -> route
```

It combines deterministic code with an agent-based classification step:

- `preprocess_issue`: plain function executor
- `classify_issue_agent`: Gemini-backed agent executor with structured output
- `route_issue`: deterministic router executor
- streamed events are printed while the workflow runs

If no Gemini API key is configured, or if the model call fails, the workflow falls back to a deterministic mock classifier so the demo remains runnable.

## Domain

GitHub issue triage.

Input items are raw GitHub-like issues with:

- title
- body

The workflow classifies each issue and routes it to one of:

- `security_review`
- `human_review`
- `ask_more_info`
- `backlog`

## Classification schema

The agent returns structured JSON matching this schema:

```json
{
  "category": "bug | feature | question | security | unclear",
  "urgency": "low | medium | high",
  "sentiment": "neutral | frustrated | angry",
  "missing_info": ["..."],
  "needs_human": true,
  "recommended_route": "security_review | human_review | ask_more_info | backlog"
}
```

The final route is selected by deterministic code, not directly by the model.

## Routing rules

The router applies explicit rules:

1. Security issues go to `security_review`
2. Issues requiring human judgment go to `human_review`
3. Issues with missing required information go to `ask_more_info`
4. Clear non-urgent issues go to `backlog`

This keeps the model useful for judgment while keeping business routing auditable and testable.

## Project structure

```text
ai-triage-workflow/
  README.md
  requirements.txt
  .env.example
  src/
    main.py
    models.py
    preprocess.py
    classifier.py
    router.py
    workflow.py
  examples/
    sample_issues.json
    sample_run.txt
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional: configure Gemini.

```bash
cp .env.example .env
```

Then edit `.env`:

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Without a key, the workflow still runs with the mock classifier.

## Run

Run all sample issues:

```bash
python -m src.main
```

Run only the first sample issue:

```bash
MAX_SAMPLE_ISSUES=1 python -m src.main
```

A sample output is included in:

```text
examples/sample_run.txt
```

## Example event stream

The workflow prints each executor step as it completes:

```text
executor_completed: preprocess_issue
executor_completed: classify_issue_agent
executor_completed: route_issue
output
```

This satisfies the streamed-events requirement and makes the workflow observable instead of a silent black box.

## Notes

This is intentionally small. The goal is not to build a production GitHub bot, but to demonstrate a clear triage workflow with:

- at least 3 executors
- one plain-function node
- one agent classification node
- structured output
- conditional routing
- human escalation path
- streamed events
