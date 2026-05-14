from fasikl_assistant.models import Action, Category
from fasikl_assistant.text import has_any


def choose_action(category: Category, transcript: str, safety_flags: list[str]) -> Action:
    if safety_flags:
        return "escalate_urgent"
    if category == "clinical_concern":
        return "route_to_clinical_team"
    if category == "billing":
        return "route_to_billing_team"
    if category == "device_issue" and has_any(transcript, ["stopped", "turning on", "power"]):
        return "route_to_device_support"
    if category == "logistics" and has_any(
        transcript,
        ["prescription", "supplies", "arrive", "shipping"],
    ):
        return "route_to_logistics_team"
    return "auto_reply"
