import os
from dataclasses import dataclass, field
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from fasikl_assistant.classifier import classify_with_openai, classify_with_rules
from fasikl_assistant.guardrails import safety_flags_for
from fasikl_assistant.mock_mcp import (
    create_support_ticket,
    prescription_status,
    suggest_portal_link,
    supply_shipping_status,
)
from fasikl_assistant.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    Category,
    Classification,
    Ticket,
)
from fasikl_assistant.responder import build_response
from fasikl_assistant.router import choose_action


@dataclass
class ConversationStore:
    previous_categories: dict[str, Category] = field(default_factory=dict)

    def get_previous_category(self, session_id: str) -> Category | None:
        return self.previous_categories.get(session_id)

    def remember(self, session_id: str, category: Category) -> None:
        self.previous_categories[session_id] = category


class AgentState(TypedDict, total=False):
    request: AnalyzeRequest
    classification: Classification
    safety_flags: list[str]
    action: str
    response: str
    ticket: Ticket | None


class PatientAssistantAgent:
    def __init__(
        self,
        *,
        store: ConversationStore | None = None,
        use_llm: bool | None = None,
        model_name: str | None = None,
    ) -> None:
        self.store = store or ConversationStore()
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.use_llm = bool(os.getenv("OPENAI_API_KEY")) if use_llm is None else use_llm
        self.graph = self._build_graph()

    def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        state = self.graph.invoke({"request": request})
        classification = state["classification"]
        action = state["action"]
        ticket = state["ticket"]
        self.store.remember(request.session_id, classification.category)

        return AnalyzeResponse(
            id=request.id,
            transcript=request.transcript,
            category=classification.category,
            confidence=classification.confidence,
            action=action,
            response=state["response"],
            portal_link=suggest_portal_link(classification.category, request.transcript),
            ticket=ticket,
            context_used=classification.context_used,
            safety_flags=state["safety_flags"],
        )

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("classify", self._classify)
        graph.add_node("route", self._route)
        graph.add_node("respond", self._respond)
        graph.add_edge(START, "classify")
        graph.add_edge("classify", "route")
        graph.add_edge("route", "respond")
        graph.add_edge("respond", END)
        return graph.compile()

    def _classify(self, state: AgentState) -> AgentState:
        request = state["request"]
        previous = self.store.get_previous_category(request.session_id)
        safety_flags = safety_flags_for(request.transcript)

        if self.use_llm:
            try:
                classification = classify_with_openai(request.transcript, self.model_name)
            except Exception:
                classification = classify_with_rules(request.transcript, previous)
        else:
            classification = classify_with_rules(request.transcript, previous)

        if safety_flags and classification.category != "clinical_concern":
            classification = Classification(
                category="clinical_concern",
                confidence=max(classification.confidence, 0.9),
                context_used=classification.context_used,
                signals=[*classification.signals, *safety_flags],
            )
        return {**state, "classification": classification, "safety_flags": safety_flags}

    def _route(self, state: AgentState) -> AgentState:
        request = state["request"]
        classification = state["classification"]
        action = choose_action(classification.category, request.transcript, state["safety_flags"])
        ticket = None
        if action != "auto_reply":
            team = action.removeprefix("route_to_").removesuffix("_team")
            priority = "urgent" if action == "escalate_urgent" else "normal"
            ticket = create_support_ticket(
                team=team,
                priority=priority,
                transcript=request.transcript,
            )
        return {**state, "action": action, "ticket": ticket}

    def _respond(self, state: AgentState) -> AgentState:
        request = state["request"]
        classification = state["classification"]
        fallback_response = build_response(
            classification.category,
            state["action"],
            request.transcript,
        )
        if self.use_llm:
            try:
                response = self._build_llm_response(state, fallback_response)
            except Exception:
                response = fallback_response
        else:
            response = fallback_response
        return {**state, "response": response}

    def _build_llm_response(self, state: AgentState, fallback_response: str) -> str:
        request = state["request"]
        classification = state["classification"]
        tool_context = self._response_tool_context(request.transcript)
        prompt = (
            "You are a patient-facing support assistant for a medical device portal. "
            "Write a concise, safe response for the patient. Do not diagnose. "
            "If urgent symptoms are present, tell the patient to stop using the device for now, "
            "contact the care team immediately, and call emergency services for severe "
            "symptoms.\n\n"
            f"transcript: {request.transcript}\n"
            f"category: {classification.category}\n"
            f"action: {state['action']}\n"
            f"safety_flags: {', '.join(state['safety_flags']) or 'none'}\n"
            f"mock_tool_context: {tool_context}\n"
            f"safe_fallback_response: {fallback_response}\n\n"
            "Return only the patient-facing response."
        )
        model = ChatOpenAI(model=self.model_name, temperature=0.2)
        result = model.invoke(prompt)
        content = getattr(result, "content", str(result)).strip()
        return content or fallback_response

    def _response_tool_context(self, transcript: str) -> str:
        text = transcript.casefold()
        if "prescription" in text or "doctor" in text or "upload" in text:
            return prescription_status()
        if "supplies" in text or "arrive" in text or "shipping" in text:
            return supply_shipping_status()
        return "No mock tool status needed."
