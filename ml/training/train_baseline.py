"""
TF-IDF + Logistic Regression baseline classifier.

Run once per language:
    python train_baseline.py english
    python train_baseline.py hinglish

Trains on {language}_train.csv, evaluates on {language}_val.csv, and prints a
full classification report (precision/recall/F1 per class) plus a confusion
matrix. This baseline exists to (a) give us a sanity-check number before the
DistilBERT model, and (b) something concrete to compare the transformer
against later ("DistilBERT improved F1 on VIOLENT_THREAT from X to Y").

Handles class imbalance via class_weight='balanced' in LogisticRegression —
without this, a model could get high accuracy just by always predicting SAFE.

Output: ml/training/artifacts/{language}_baseline_model.joblib (vectorizer + model)
"""

import sys
import csv
import time
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


def load_split(language: str, split: str) -> tuple[list[str], list[str]]:
    path = DATA_DIR / f"{language}_{split}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found — run build_training_set.py first")

    sentences, labels = [], []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            sentences.append(row["sentence"])
            labels.append(row["label"])
    return sentences, labels


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("english", "hinglish"):
        print("Usage: python train_baseline.py <english|hinglish>")
        sys.exit(1)

    language = sys.argv[1]
    print(f"=== Training baseline for: {language} ===\n")

    X_train, y_train = load_split(language, "train")
    X_val, y_val = load_split(language, "val")

    print(f"Train examples: {len(X_train)}")
    print(f"Val examples:   {len(X_val)}")
    print(f"Classes present in train: {sorted(set(y_train))}\n")

    # TF-IDF: word-level, unigrams+bigrams (bigrams help catch phrases like
    # "maar dunga" that a single word wouldn't capture), cap vocab size to
    # keep it fast and avoid overfitting on rare tokens.
    vectorizer = TfidfVectorizer(
        max_features=20_000,
        ngram_range=(1, 2),
        min_df=2,
    )

    t0 = time.time()
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    print(f"Vectorized in {time.time() - t0:.2f}s (vocab size: {len(vectorizer.vocabulary_)})")

    # class_weight='balanced' auto-adjusts for the heavy class imbalance
    # (e.g. 95%+ SAFE) so the model doesn't just learn to always predict SAFE.
    clf = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )

    t0 = time.time()
    clf.fit(X_train_vec, y_train)
    print(f"Trained in {time.time() - t0:.2f}s\n")

    y_pred = clf.predict(X_val_vec)

    print("=== Classification Report (validation set) ===")
    print(classification_report(y_val, y_pred, zero_division=0))

    print("=== Confusion Matrix ===")
    labels_sorted = sorted(set(y_val) | set(y_pred))
    cm = confusion_matrix(y_val, y_pred, labels=labels_sorted)
    print(f"Labels order: {labels_sorted}")
    for row in cm:
        print(row)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ARTIFACTS_DIR / f"{language}_baseline_model.joblib"
    joblib.dump({"vectorizer": vectorizer, "model": clf}, out_path)
    print(f"\nSaved model + vectorizer to: {out_path}")


if __name__ == "__main__":
    main()