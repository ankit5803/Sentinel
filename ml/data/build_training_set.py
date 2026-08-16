"""
Build SEPARATE training-ready datasets for English (THREAT corpus) and Hinglish
(weak-labeled) — two specialized models, not one merged multilingual model.
Each gets its own stratified train/val/test split (classes are heavily imbalanced).

Rationale: a language-specific model can specialize on that language's patterns
rather than being diluted across two very different text styles. Sentinel's
backend will do language detection and route to the matching model.

Label mapping:
  THREAT corpus:  label=1 -> VIOLENT_THREAT | label=0 -> SAFE
  Hinglish:       reviewer_label (manually confirmed, gold) takes priority
                  over weak_label where available; otherwise weak_label is used.

Output:
  ml/data/processed/english_{train,val,test}.csv
  ml/data/processed/hinglish_{train,val,test}.csv
    Columns: sentence, label, source
"""

import csv
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent / "processed"
THREAT_PATH = DATA_DIR / "threat_clean.csv"
HINGLISH_WEAK_PATH = DATA_DIR / "hinglish_weak_labeled.csv"
HINGLISH_REVIEWED_PATH = DATA_DIR / "hinglish_reviewed.csv"

LABELS = ["SAFE", "NON_VIOLENT_ABUSE", "POTENTIAL_THREAT", "VIOLENT_THREAT"]

TRAIN_FRAC, VAL_FRAC, TEST_FRAC = 0.70, 0.15, 0.15
RANDOM_SEED = 42


def load_threat(path: Path) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            label = "VIOLENT_THREAT" if row["label"] == "1" else "SAFE"
            rows.append({"sentence": row["sentence"], "label": label, "source": "threat_corpus"})
    return rows


def load_hinglish(weak_path: Path, reviewed_path: Path) -> list[dict]:
    # Reviewed (gold) labels take priority over weak labels for the same sentence.
    reviewed_by_sentence = {}
    if reviewed_path.exists():
        with open(reviewed_path, "r", encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f):
                reviewed_by_sentence[row["sentence"]] = row["reviewer_label"]

    rows = []
    with open(weak_path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            sentence = row["sentence"]
            if sentence in reviewed_by_sentence:
                label = reviewed_by_sentence[sentence]
                source = "hinglish_reviewed_gold"
            else:
                label = row["weak_label"]
                source = "hinglish_weak_labeled"
            rows.append({"sentence": sentence, "label": label, "source": source})
    return rows


def stratified_split(rows: list[dict], seed: int):
    import random
    rng = random.Random(seed)
    by_label: dict[str, list[dict]] = {label: [] for label in LABELS}
    for row in rows:
        by_label.setdefault(row["label"], []).append(row)

    train, val, test = [], [], []
    for label, group in by_label.items():
        rng.shuffle(group)
        n = len(group)
        n_train = int(n * TRAIN_FRAC)
        n_val = int(n * VAL_FRAC)
        train.extend(group[:n_train])
        val.extend(group[n_train:n_train + n_val])
        test.extend(group[n_train + n_val:])

    rng.shuffle(train)
    rng.shuffle(val)
    rng.shuffle(test)
    return train, val, test


def write_csv(rows: list[dict], path: Path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sentence", "label", "source"])
        writer.writeheader()
        writer.writerows(rows)


def process_language(name: str, rows: list[dict]):
    print(f"\n=== {name.upper()} ===")
    print(f"Total rows: {len(rows)}")

    counts = Counter(r["label"] for r in rows)
    for label in LABELS:
        c = counts.get(label, 0)
        pct = c / len(rows) * 100 if rows else 0
        print(f"  {label:20s} {c:6d} ({pct:.2f}%)")

    train, val, test = stratified_split(rows, RANDOM_SEED)

    write_csv(train, DATA_DIR / f"{name}_train.csv")
    write_csv(val, DATA_DIR / f"{name}_val.csv")
    write_csv(test, DATA_DIR / f"{name}_test.csv")

    print(f"Split sizes: train={len(train)}, val={len(val)}, test={len(test)}")
    print(f"Written to: {DATA_DIR}/{name}_train.csv, {name}_val.csv, {name}_test.csv")


def main():
    if not THREAT_PATH.exists():
        raise FileNotFoundError(f"Run parse_threat.py first — {THREAT_PATH} not found")
    if not HINGLISH_WEAK_PATH.exists():
        raise FileNotFoundError(f"Run weak_label_hinglish.py first — {HINGLISH_WEAK_PATH} not found")

    threat_rows = load_threat(THREAT_PATH)
    hinglish_rows = load_hinglish(HINGLISH_WEAK_PATH, HINGLISH_REVIEWED_PATH)

    process_language("english", threat_rows)
    process_language("hinglish", hinglish_rows)


if __name__ == "__main__":
    main()