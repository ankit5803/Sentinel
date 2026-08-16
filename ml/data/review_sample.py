"""
Interactive manual spot-check tool for the weak-labeled Hinglish dataset.

Pulls a random sample (stratified toward the rarer/higher-risk classes, since
those matter most to get right) and lets you confirm or correct each label by
typing a single key. Saves your corrections to a separate reviewed CSV.

Run this, go through the prompts, press Ctrl+C anytime to stop early — your
progress up to that point is still saved.

Output: ml/data/processed/hinglish_reviewed.csv
    Columns: sentence, weak_label, reviewer_label, matched_profanity_terms,
             matched_violence_phrases, source
"""

import csv
import random
from pathlib import Path

IN_PATH = Path(__file__).parent / "processed" / "hinglish_weak_labeled.csv"
OUT_PATH = Path(__file__).parent / "processed" / "hinglish_reviewed.csv"

# How many of each class to review. Prioritize the rare/high-risk classes —
# reviewing all 9 POTENTIAL_THREAT rows costs nothing, reviewing all 48k SAFE
# rows would take forever and isn't where the risk of bad labels is anyway.
REVIEW_TARGETS = {
    "VIOLENT_THREAT": 9999,      # review all (likely very few)
    "POTENTIAL_THREAT": 9999,    # review all (likely very few)
    "NON_VIOLENT_ABUSE": 150,    # sample a chunk
    "SAFE": 100,                 # spot-check a smaller chunk (mainly checking for false negatives)
}

VALID_LABELS = ["SAFE", "NON_VIOLENT_ABUSE", "POTENTIAL_THREAT", "VIOLENT_THREAT"]
LABEL_KEYS = {"1": "SAFE", "2": "NON_VIOLENT_ABUSE", "3": "POTENTIAL_THREAT", "4": "VIOLENT_THREAT"}


def load_rows(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def build_review_batch(rows: list[dict], seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    by_label: dict[str, list[dict]] = {label: [] for label in VALID_LABELS}
    for row in rows:
        by_label.setdefault(row["weak_label"], []).append(row)

    batch = []
    for label, target_n in REVIEW_TARGETS.items():
        pool = by_label.get(label, [])
        rng.shuffle(pool)
        batch.extend(pool[:target_n])

    rng.shuffle(batch)
    return batch


def main():
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Run weak_label_hinglish.py first — {IN_PATH} not found")

    rows = load_rows(IN_PATH)
    batch = build_review_batch(rows)

    print(f"Loaded {len(rows)} weak-labeled rows. Reviewing {len(batch)} of them.\n")
    print("For each sentence, confirm or correct the label:")
    print("  [enter] = confirm weak label as-is")
    print("  1 = SAFE   2 = NON_VIOLENT_ABUSE   3 = POTENTIAL_THREAT   4 = VIOLENT_THREAT")
    print("  s = skip (won't be written to output)")
    print("  q = quit and save progress so far\n")

    reviewed = []
    try:
        for i, row in enumerate(batch, start=1):
            print(f"\n[{i}/{len(batch)}] weak_label={row['weak_label']}")
            print(f"  sentence: {row['sentence']}")
            if row.get("matched_profanity_terms"):
                print(f"  matched profanity: {row['matched_profanity_terms']}")
            if row.get("matched_violence_phrases"):
                print(f"  matched violence phrases: {row['matched_violence_phrases']}")

            choice = input("  your call > ").strip().lower()

            if choice == "q":
                break
            if choice == "s":
                continue
            if choice == "":
                final_label = row["weak_label"]
            elif choice in LABEL_KEYS:
                final_label = LABEL_KEYS[choice]
            else:
                print("  [invalid input, treating as skip]")
                continue

            row["reviewer_label"] = final_label
            reviewed.append(row)
    except KeyboardInterrupt:
        print("\n\nStopped early — saving progress so far.")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["sentence", "weak_label", "reviewer_label", "matched_profanity_terms", "matched_violence_phrases", "source"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviewed)

    agree = sum(1 for r in reviewed if r["reviewer_label"] == r["weak_label"])
    total = len(reviewed)
    print(f"\nReviewed {total} rows. Agreement with weak label: {agree}/{total} ({agree/total*100:.1f}%)" if total else "\nNo rows reviewed.")
    print(f"Saved to: {OUT_PATH}")


if __name__ == "__main__":
    main()