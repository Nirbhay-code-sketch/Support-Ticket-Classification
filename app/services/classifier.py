"""
classifier.py
-------------
Loads the trained scikit-learn pipelines once at startup and exposes a
single `classify_ticket()` function used by the API layer.
"""

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

from app.services.priority import determine_priority
from app.utils.text_cleaning import preprocess

MODEL_DIR = Path(__file__).resolve().parents[2] / "saved_models"


class ModelNotTrainedError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _load_models():
    category_path = MODEL_DIR / "category_model.joblib"
    priority_path = MODEL_DIR / "priority_model.joblib"

    if not category_path.exists() or not priority_path.exists():
        raise ModelNotTrainedError(
            "Models not found. Run:\n"
            "  python data/generate_dataset.py\n"
            "  python notebooks/train.py\n"
            "from the backend/ directory first."
        )

    return joblib.load(category_path), joblib.load(priority_path)


def _predict_with_confidence(pipeline, clean_text: str):
    label = pipeline.predict([clean_text])[0]
    proba = pipeline.predict_proba([clean_text])[0]
    confidence = float(np.max(proba))
    return label, confidence


def classify_ticket(raw_text: str) -> dict:
    """
    End-to-end inference: raw ticket text -> category + priority + confidence.
    This is the single function the API route calls.
    """
    category_model, priority_model = _load_models()

    clean = preprocess(raw_text)
    if not clean:
        clean = raw_text.lower()  # fallback so an empty vector doesn't error out

    category, category_confidence = _predict_with_confidence(category_model, clean)
    ml_priority, priority_confidence = _predict_with_confidence(priority_model, clean)

    priority_result = determine_priority(
        raw_text=raw_text,
        ml_priority=ml_priority,
        ml_confidence=priority_confidence,
        category=category,
    )

    return {
        "category": category,
        "category_confidence": round(category_confidence, 3),
        **priority_result,
    }
