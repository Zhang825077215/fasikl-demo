from fasikl_assistant.mock_mcp import prescription_status, supply_shipping_status
from fasikl_assistant.models import Action, Category


def build_response(category: Category, action: Action, transcript: str) -> str:
    text = transcript.casefold()

    if action == "escalate_urgent":
        return (
            "This may need urgent clinical attention. Please stop using the device for now, "
            "contact your care team immediately, and call emergency services if symptoms "
            "feel severe."
        )
    if category == "clinical_concern":
        return (
            "Please pause therapy until a clinician reviews this. I will route this to the "
            "clinical team so they can advise on comfort, skin changes, or restarting therapy."
        )
    if "turning on" in text or "stopped" in text:
        return (
            "Try charging the device with the approved charger and checking the power connection. "
            "Because you use it daily, I will route this to device support for follow-up."
        )
    if "charge" in text:
        return (
            "Use the approved charger, confirm the charging indicator turns on, "
            "and leave it connected until full."
        )
    if "prescription" in text or "doctor" in text or "upload" in text:
        return (
            f"{prescription_status()} You can also upload or review prescription documents "
            "in the portal."
        )
    if "supplies" in text or "arrive" in text:
        return f"{supply_shipping_status()} I will send this to the logistics team."
    if "travel" in text:
        return (
            "Most travel questions can be answered from the travel guidance page. "
            "Bring your charger and follow your clinician's usage instructions."
        )
    if category == "account_access":
        return (
            "Use the login help page to reset your password or recover portal access. "
            "Support can help if recovery does not work."
        )
    if category == "billing":
        return (
            "Please update your insurance information in the billing area so the billing team "
            "can verify coverage."
        )
    return "I can help route this to the right team or point you to the most relevant portal page."
