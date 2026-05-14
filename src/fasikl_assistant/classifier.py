from pydantic import BaseModel, Field

from fasikl_assistant.models import Category, Classification
from fasikl_assistant.text import keyword_score, normalize

CATEGORY_KEYWORDS: dict[Category, list[str]] = {
    "device_issue": [
        "device",
        "turning on",
        "stopped",
        "charge",
        "charging",
        "battery",
        "power",
    ],
    "clinical_concern": [
        "stimulation",
        "uncomfortable",
        "skin",
        "red",
        "therapy",
        "restart",
        "pain",
        "breathing",
    ],
    "billing": ["insurance", "billing", "bill", "invoice", "coverage", "copay"],
    "logistics": ["prescription", "doctor", "supplies", "arrive", "shipment", "shipping", "travel"],
    "account_access": ["log in", "login", "portal", "password", "account", "access"],
}

FOLLOW_UP_TERMS = ["what should i", "upload", "next", "that", "it", "this"]


class LlmClassification(BaseModel):
    category: Category
    confidence: float = Field(ge=0, le=1)
    rationale: str


def classify_with_rules(
    transcript: str,
    previous_category: Category | None = None,
) -> Classification:
    text = normalize(transcript)
    scores = {
        category: keyword_score(text, keywords) for category, keywords in CATEGORY_KEYWORDS.items()
    }

    if (
        previous_category
        and max(scores.values()) <= 1
        and any(term in text for term in FOLLOW_UP_TERMS)
    ):
        return Classification(
            category=previous_category,
            confidence=0.68,
            context_used=True,
            signals=["conversation_context"],
        )

    category = max(scores, key=lambda item: scores[item])
    score = scores[category]

    if score == 0:
        return Classification(
            category="logistics",
            confidence=0.35,
            signals=["fallback"],
        )

    confidence = min(0.95, 0.55 + (score * 0.1))
    signals = [keyword for keyword in CATEGORY_KEYWORDS[category] if keyword in text]
    return Classification(category=category, confidence=confidence, signals=signals)


def classify_with_openai(transcript: str, model_name: str) -> Classification:
    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model=model_name, temperature=0)
    structured = model.with_structured_output(LlmClassification)
    result = structured.invoke(
        "Classify this patient support request into exactly one category: "
        "device_issue, clinical_concern, billing, logistics, account_access. "
        f"Return a confidence score. Request: {transcript}"
    )
    return Classification(
        category=result.category,
        confidence=result.confidence,
        signals=[f"llm:{result.rationale}"],
    )
