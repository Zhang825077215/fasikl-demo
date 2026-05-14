# Fasikl Patient Assistant Demo

Patient-facing support assistant backend built with FastAPI, LangGraph, uv, Python 3.12.13,
and optional OpenAI model classification.

The demo accepts a patient speech transcript or text question and returns:

- topic/category
- patient-facing response
- next-step action
- portal navigation suggestion
- optional support ticket

The app works without an OpenAI key by using deterministic rules and response templates, which keeps
the interview demo stable. If `OPENAI_API_KEY` is set, the classifier and response node can use
`langchain-openai`; if a model call fails, the agent falls back to local rules/templates.

## Setup

```bash
uv sync
```

Optional LLM configuration:

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4.1-mini"
```

## Run the API

```bash
uv run uvicorn --app-dir src fasikl_assistant.api:app --reload
```

Open:

- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Example request:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"id":"C002","transcript":"The stimulation feels stronger than usual and uncomfortable.","session_id":"demo"}'
```

Run all sample messages:

```bash
curl -X POST http://127.0.0.1:8000/samples/run
```

## CLI

```bash
uv run fasikl-demo --samples
uv run fasikl-demo "I cannot log into the portal."
```

## Tests and Lint

```bash
uv run pytest -q
uv run ruff check .
```

## What I Built

This is a backend agent for patient support triage. It handles the sample patient messages from
`goal.txt`, classifies each request, generates a safe response, chooses a next action, and suggests
where the patient should go in the portal.

Implemented categories:

- `device_issue`
- `clinical_concern`
- `billing`
- `logistics`
- `account_access`

Implemented actions:

- `auto_reply`
- `route_to_device_support`
- `route_to_clinical_team`
- `route_to_billing_team`
- `route_to_logistics_team`
- `escalate_urgent`

## Key Design Decisions

The agent is built as a LangGraph workflow:

1. `classify`: detect category and safety flags.
2. `route`: choose the next action and create a mock support ticket when needed.
3. `respond`: produce the patient-facing response.

MCP-style integrations are represented as normal Python functions in `mock_mcp.py`. These functions
suggest portal links, create mock tickets, and return mock prescription or shipping status text.

The useful extra feature is lightweight conversation context. The agent remembers the previous
category per `session_id`, so a follow-up such as "What should I upload next?" can inherit the
prescription/logistics topic from the previous turn.

## Automatic vs Human Routed Requests

Requests can be handled automatically when the answer is low risk and operational, such as login
help, charging instructions, travel guidance, and insurance update instructions.

Requests should route to a human when they require account-specific lookup, device support follow-up,
billing verification, prescription status confirmation, shipment status confirmation, or clinical
judgment.

Requests should escalate urgently when the transcript contains high-risk symptoms such as trouble
breathing, severe pain, chest pain, fainting, bleeding, burns, infection, or swelling.

The demo distinguishes these with safety keyword checks first, then category/action rules, and
optionally an OpenAI classifier.

## Support Workflow Integration

In a production workflow, the `Ticket` returned by `/analyze` would be sent to the existing CRM,
support queue, or EHR-adjacent case management system. The `category`, `action`, `priority`,
`session_id`, transcript, and portal link would become structured fields for routing and reporting.

The portal could display the response immediately while also showing the ticket status when a human
team is involved.

## Main Failure Mode Concern

The biggest concern is under-escalating a clinical or urgent issue. The system should bias toward
human review when confidence is low, symptoms are ambiguous, or the patient describes discomfort,
skin reaction, pain, therapy restart, or device use uncertainty.

## What I Would Build Next

With one more week, I would add:

- stronger clinical safety policies reviewed by domain experts
- retrieval over approved FAQ and device instructions
- structured confidence thresholds and audit logs
- authenticated integration with support ticketing and shipment/prescription APIs
- evaluation tests over a larger set of red-team patient transcripts

## AI Tools and External Resources Used

This implementation was built with Codex assistance. The runtime libraries are FastAPI, LangGraph,
LangChain OpenAI, Pydantic, uvicorn, pytest, and Ruff.
