from fasikl_assistant.agent import PatientAssistantAgent
from fasikl_assistant.models import AnalyzeRequest
from fasikl_assistant.sample_data import SAMPLE_MESSAGES


def test_all_goal_samples_receive_category_response_action_and_link():
    agent = PatientAssistantAgent(use_llm=False)

    for item in SAMPLE_MESSAGES:
        result = agent.analyze(
            AnalyzeRequest(id=item.id, transcript=item.transcript, session_id=f"sample-{item.id}")
        )

        assert result.id == item.id
        assert result.category in {
            "device_issue",
            "clinical_concern",
            "billing",
            "logistics",
            "account_access",
        }
        assert result.response
        assert result.action in {
            "auto_reply",
            "route_to_device_support",
            "route_to_clinical_team",
            "route_to_billing_team",
            "route_to_logistics_team",
            "escalate_urgent",
        }
        assert result.portal_link is not None
