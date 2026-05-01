import re
import logging

logger = logging.getLogger(__name__)

# Weighted intent signals — higher weight = stronger buying/need signal
INTENT_SIGNALS = {
    # Strong buying intent (weight: 3)
    "looking to buy": 3,
    "ready to purchase": 3,
    "want to invest in": 3,
    "need a solution": 3,
    "can anyone recommend": 3,
    "what tool do you use": 3,
    "best software for": 3,
    "where can i find": 3,
    # Medium intent (weight: 2)
    "looking for": 2,
    "need help with": 2,
    "struggling with": 2,
    "any recommendations": 2,
    "alternative to": 2,
    "how do you handle": 2,
    "switch from": 2,
    "migrate from": 2,
    "tool for": 2,
    "service for": 2,
    "platform for": 2,
    "frustrated with": 2,
    # Low intent / general interest (weight: 1)
    "anyone tried": 1,
    "thoughts on": 1,
    "experience with": 1,
    "how to": 1,
    "help": 1,
    "need": 1,
    "looking": 1,
    "advice": 1,
    "suggestion": 1,
    "recommend": 1,
}

MAX_POSSIBLE_SCORE = sum(INTENT_SIGNALS.values())


def score(text: str) -> float:
    """Score text for purchase/need intent. Returns 0.0-1.0."""
    if not text:
        return 0.0

    text_lower = text.lower()
    total_weight = 0

    for phrase, weight in INTENT_SIGNALS.items():
        if phrase in text_lower:
            total_weight += weight

    # Normalize to 0-1 range, cap at 1.0
    raw_score = min(total_weight / 10, 1.0)  # 10 = practical max for a single post

    return round(raw_score, 3)


def score_batch(texts: list[str]) -> list[float]:
    """Score multiple texts efficiently."""
    return [score(t) for t in texts]
