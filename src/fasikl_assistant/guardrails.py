from fasikl_assistant.text import has_any

URGENT_KEYWORDS = [
    "trouble breathing",
    "cannot breathe",
    "chest pain",
    "severe pain",
    "faint",
    "passed out",
    "bleeding",
    "burn",
    "infection",
    "swelling",
]


def safety_flags_for(transcript: str) -> list[str]:
    flags: list[str] = []
    if has_any(transcript, URGENT_KEYWORDS):
        flags.append("urgent_symptom")
    return flags
