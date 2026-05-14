# Design Note

## What was built

This repository contains a FastAPI backend agent for patient-facing support triage. It accepts text
or speech transcripts, classifies the request, returns a helpful response, selects a next-step
action, and suggests a portal link.

The agent uses LangGraph for orchestration and supports OpenAI classification through
`langchain-openai` when `OPENAI_API_KEY` is configured. Local deterministic rules remain the default
fallback so the demo can run reliably without external services.

## Key decisions

The workflow is split into three agent nodes: classify, route, and respond. This keeps safety checks,
support routing, and response generation independently testable.

Function-based mock tools replace MCP integrations for this demo. The functions create support
tickets, suggest portal navigation, and return mock prescription or shipping status messages.

Conversation context is included as the extra feature. The agent remembers the previous category by
`session_id`, allowing short follow-ups to stay on topic.

## Automatic handling vs human support

Automatic responses are suitable for low-risk, general questions such as charging instructions,
portal login help, travel guidance, and insurance update instructions.

Human routing is used when the request needs a support team, account-specific information, or
clinical judgment. Urgent escalation takes precedence over every other route when high-risk symptom
terms appear.

## Integration with support workflows

The returned `Ticket` object models the payload that would be sent to a CRM, support queue, or care
team workflow. In production, each routed action would include the transcript, patient identifier,
category, priority, confidence, and audit trail.

## Most concerning failure mode

The main risk is missing or downplaying a clinical problem. A production system should use approved
clinical policies, conservative thresholds, human review for low confidence, and continuous
evaluation against red-team transcripts.

## Next improvements

With another week, I would add retrieval over approved support content, real ticketing/API
integrations, persistent conversation storage, authentication, observability, and a larger automated
evaluation suite.
