import re


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def has_any(text: str, keywords: list[str]) -> bool:
    lowered = normalize(text)
    return any(keyword in lowered for keyword in keywords)


def keyword_score(text: str, keywords: list[str]) -> int:
    lowered = normalize(text)
    return sum(1 for keyword in keywords if keyword in lowered)
