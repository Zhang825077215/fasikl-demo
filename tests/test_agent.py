from types import SimpleNamespace

import fasikl_assistant.agent as agent_module
from fasikl_assistant.agent import PatientAssistantAgent
from fasikl_assistant.models import AnalyzeRequest, Classification


def analyze(text: str, session_id: str = "test-session"):
    agent = PatientAssistantAgent(use_llm=False)
    return agent.analyze(AnalyzeRequest(transcript=text, session_id=session_id))


def test_device_power_issue_returns_troubleshooting_and_device_route():
    result = analyze("My device stopped turning on yesterday and I use it every morning.")

    assert result.category == "device_issue"
    assert result.action == "route_to_device_support"
    assert result.portal_link.path == "/support/device-troubleshooting"
    assert "charge" in result.response.lower()


def test_uncomfortable_stimulation_routes_to_clinical_team():
    result = analyze("The stimulation feels stronger than usual and uncomfortable.")

    assert result.category == "clinical_concern"
    assert result.action == "route_to_clinical_team"
    assert result.portal_link.path == "/support/clinical"
    assert "pause" in result.response.lower()


def test_urgent_symptoms_escalate_urgently():
    result = analyze("I have severe pain and trouble breathing after using the device.")

    assert result.category == "clinical_concern"
    assert result.action == "escalate_urgent"
    assert result.ticket is not None
    assert result.ticket.priority == "urgent"
    assert "urgent" in result.response.lower()


def test_follow_up_context_reuses_previous_topic():
    agent = PatientAssistantAgent(use_llm=False)
    first = agent.analyze(
        AnalyzeRequest(
            transcript="My doctor sent the prescription last week. Did you receive it?",
            session_id="rx-1",
        )
    )
    second = agent.analyze(
        AnalyzeRequest(transcript="What should I upload next?", session_id="rx-1")
    )

    assert first.category == "logistics"
    assert second.category == "logistics"
    assert second.context_used is True
    assert second.portal_link.path == "/documents/prescriptions"


def test_response_node_uses_llm_when_enabled(monkeypatch):
    class FakeChatOpenAI:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def invoke(self, messages):
            assert "category: account_access" in messages
            assert "action: auto_reply" in messages
            return SimpleNamespace(content="LLM generated portal login response.")

    monkeypatch.setattr(agent_module, "ChatOpenAI", FakeChatOpenAI)
    monkeypatch.setattr(
        agent_module,
        "classify_with_openai",
        lambda transcript, model_name: Classification(
            category="account_access",
            confidence=0.91,
            signals=["test"],
        ),
    )

    agent = PatientAssistantAgent(use_llm=True, model_name="test-model")
    result = agent.analyze(
        AnalyzeRequest(transcript="I cannot log into the portal.", session_id="llm-response")
    )

    assert result.response == "LLM generated portal login response."
