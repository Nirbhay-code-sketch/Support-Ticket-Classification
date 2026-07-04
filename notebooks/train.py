"""
train.py
--------
Trains two scikit-learn pipelines:
  1. Category classifier   (Billing / Technical / Account / Product / General)
  2. Priority classifier   (High / Medium / Low)

Both are TF-IDF + LinearSVC pipelines, chosen for strong performance on
short, sparse text like support tickets. Also prints an evaluation report
(precision/recall/F1/confusion matrix) for each model.

This script is the .py mirror of notebooks/train_model.ipynb - run either.

Usage:
    python train.py
"""

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.utils.text_cleaning import preprocess  # noqa: E402

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "tickets.csv"
MODEL_DIR = Path(__file__).resolve().parents[1] / "saved_models"
MODEL_DIR.mkdir(exist_ok=True)


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run `python data/generate_dataset.py` first, "
            "or drop in your own tickets.csv with columns: text, category, priority."
        )
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} tickets")
    print("Cleaning & tokenizing text (spaCy)...")
    df["clean_text"] = df["text"].apply(preprocess)
    return df


def build_pipeline() -> Pipeline:
    """TF-IDF vectorizer + calibrated LinearSVC (gives predict_proba for confidence scores)."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.9)),
        ("clf", CalibratedClassifierCV(LinearSVC(class_weight="balanced"), cv=3)),
    ])


def train_and_eval(df: pd.DataFrame, target_col: str, model_name: str) -> Pipeline:
    print(f"\n{'=' * 60}\nTraining {model_name} classifier (target = {target_col})\n{'=' * 60}")

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"], df[target_col], test_size=0.2, random_state=42, stratify=df[target_col]
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))
    print("Confusion matrix (rows=true, cols=pred):")
    labels = sorted(df[target_col].unique())
    print(pd.DataFrame(confusion_matrix(y_test, y_pred, labels=labels), index=labels, columns=labels))

    out_path = MODEL_DIR / f"{model_name}_model.joblib"
    joblib.dump(pipeline, out_path)
    print(f"Saved -> {out_path}")
    return pipeline


def main():
    df = load_data()
    train_and_eval(df, "category", "category")
    train_and_eval(df, "priority", "priority")
    print("\nAll models trained and saved to backend/saved_models/")


if __name__ == "__main__":
    main()
