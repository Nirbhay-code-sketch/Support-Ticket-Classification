"""
priority.py
-----------
Priority isn't decided by the ML model alone. This module blends:
  1. The trained priority classifier's prediction + confidence
  2. A rule-based urgency booster (keyword signals, ALL-CAPS, punctuation)
  3. Category weighting (e.g. Technical outages skew more urgent than General queries)

This hybrid approach is standard practice in support-ops ML systems: pure
ML models miss obvious urgency cues in small/imbalanced datasets, while
pure rules miss nuance. Combining both is more robust in production.
"""

from app.utils.text_cleaning import URGENCY_KEYWORDS

PRIORITY_RANK = {"Low": 0, "Medium": 1, "High": 2}
RANK_TO_PRIORITY = {v: k for k, v in PRIORITY_RANK.items()}

CATEGORY_WEIGHT = {
    "Technical": 1,
    "Billing": 1,
    "Account": 0,
    "Product": -1,
    "General": -1,
}


def rule_based_score(raw_text: str) -> int:
    """Returns -1 / 0 / +1 / +2 nudge based on surface-level urgency signals."""
    text_lower = raw_text.lower()
    score = 0

    keyword_hits = sum(1 for kw in URGENCY_KEYWORDS if kw in text_lower)
    score += min(keyword_hits, 2)  # cap contribution

    # Shouting / exclamation marks correlate with urgency
    letters = [c for c in raw_text if c.isalpha()]
    if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.4:
        score += 1
    if raw_text.count("!") >= 2:
        score += 1

    return score


def determine_priority(
    raw_text: str,
    ml_priority: str,
    ml_confidence: float,
    category: str,
) -> dict:
    """
    Combine ML prediction with rule-based signals into a final priority.

    Returns dict with final priority, the ML's raw suggestion, and the
    reasons used, so the frontend / support agent can see *why*.
    """
    base_rank = PRIORITY_RANK.get(ml_priority, 1)
    nudge = rule_based_score(raw_text)
    nudge += CATEGORY_WEIGHT.get(category, 0) if ml_confidence < 0.6 else 0

    final_rank = max(0, min(2, base_rank + (1 if nudge >= 2 else 0)))
    final_priority = RANK_TO_PRIORITY[final_rank]

    reasons = []
    if final_priority != ml_priority:
        reasons.append("Escalated by urgency keywords/signals in the message")
    if ml_confidence < 0.6:
        reasons.append("Low model confidence - category weighting applied")
    if not reasons:
        reasons.append("Model prediction accepted as-is")

    return {
        "priority": final_priority,
        "model_suggested_priority": ml_priority,
        "model_confidence": round(ml_confidence, 3),
        "reasons": reasons,
    }
