"""
text_cleaning.py
-----------------
Shared text preprocessing utilities used by both the training pipeline
(notebooks/train.py) and the live API service. Keeping this logic in one
place guarantees that tickets are cleaned identically at train time and
at inference time.
"""

import re
import string

import spacy

# Load once at import time - reused across the whole process.
try:
    _NLP = spacy.load("en_core_web_sm", disable=["ner", "parser"])
except OSError:  # pragma: no cover
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' not found. Run:\n"
        "  python -m spacy download en_core_web_sm"
    )

_URL_RE = re.compile(r"http\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\S+@\S+")
_MULTISPACE_RE = re.compile(r"\s+")


def clean_text(raw_text: str) -> str:
    """Lowercase, strip noise, and normalize a raw ticket string."""
    text = raw_text.lower().strip()
    text = _URL_RE.sub(" ", text)
    text = _EMAIL_RE.sub(" ", text)
    text = text.translate(str.maketrans("", "", string.digits))
    text = text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))
    text = _MULTISPACE_RE.sub(" ", text).strip()
    return text


def tokenize_and_lemmatize(clean: str) -> str:
    """Tokenize with spaCy, drop stopwords/short tokens, return lemmas joined by space."""
    doc = _NLP(clean)
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct and len(token.lemma_) > 2
    ]
    return " ".join(tokens)


def preprocess(raw_text: str) -> str:
    """Full pipeline: clean -> tokenize -> lemmatize. Used everywhere a ticket enters the system."""
    return tokenize_and_lemmatize(clean_text(raw_text))


# Keyword banks used by the rule-based priority booster (services/priority.py)
URGENCY_KEYWORDS = {
    "urgent", "asap", "immediately", "critical", "emergency", "blocking",
    "down", "outage", "broken", "crash", "losing", "angry", "cancel",
    "refund", "legal", "lawsuit", "escalate", "fraud",
}
