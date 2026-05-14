from typing import Literal

from pydantic import BaseModel, Field

Category = Literal[
    "device_issue",
    "clinical_concern",
    "billing",
    "logistics",
    "account_access",
]

Action = Literal[
    "auto_reply",
    "route_to_device_support",
    "route_to_clinical_team",
    "route_to_billing_team",
    "route_to_logistics_team",
    "escalate_urgent",
]


class AnalyzeRequest(BaseModel):
    id: str | None = None
    transcript: str = Field(min_length=1)
    session_id: str = "default"


class PortalLink(BaseModel):
    label: str
    path: str


class Ticket(BaseModel):
    id: str
    team: str
    priority: Literal["normal", "urgent"]
    summary: str


class AnalyzeResponse(BaseModel):
    id: str | None = None
    transcript: str
    category: Category
    confidence: float = Field(ge=0, le=1)
    action: Action
    response: str
    portal_link: PortalLink
    ticket: Ticket | None = None
    context_used: bool = False
    safety_flags: list[str] = Field(default_factory=list)


class Classification(BaseModel):
    category: Category
    confidence: float = Field(ge=0, le=1)
    context_used: bool = False
    signals: list[str] = Field(default_factory=list)
