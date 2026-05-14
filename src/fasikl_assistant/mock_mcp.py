import random
from hashlib import sha1

from fasikl_assistant.models import PortalLink, Ticket

PRESCRIPTION_STATUSES = [
    "Prescription not found; support should verify with the clinic.",
    "Prescription received and pending clinical review.",
    "Prescription approved and ready for the next onboarding step.",
]

SUPPLY_SHIPPING_STATUSES = [
    "Supply order is being prepared for shipment.",
    "Supply order shipped and is in transit.",
    "Supply order is delayed and needs review.",
]


def suggest_portal_link(category: str, transcript: str) -> PortalLink:
    text = transcript.casefold()
    if "charge" in text or "turning on" in text or "stopped" in text:
        return PortalLink(label="Device troubleshooting", path="/support/device-troubleshooting")
    if category == "clinical_concern":
        return PortalLink(label="Clinical support", path="/support/clinical")
    if "prescription" in text or "doctor" in text or "upload" in text:
        return PortalLink(label="Prescription documents", path="/documents/prescriptions")
    if "supplies" in text or "arrive" in text:
        return PortalLink(label="Supply orders", path="/orders/supplies")
    if "travel" in text:
        return PortalLink(label="Travel guidance", path="/support/travel")
    if category == "account_access":
        return PortalLink(label="Login help", path="/login/help")
    if category == "billing":
        return PortalLink(label="Insurance and billing", path="/billing/insurance")
    return PortalLink(label="Support center", path="/support")


def create_support_ticket(team: str, priority: str, transcript: str) -> Ticket:
    digest = sha1(f"{team}:{priority}:{transcript}".encode(), usedforsecurity=False).hexdigest()[:8]
    return Ticket(id=f"T-{digest}", team=team, priority=priority, summary=transcript[:140])


def prescription_status() -> str:
    return random.choice(PRESCRIPTION_STATUSES)


def supply_shipping_status() -> str:
    return random.choice(SUPPLY_SHIPPING_STATUSES)
