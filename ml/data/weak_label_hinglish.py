"""
Build a weakly-labeled Hinglish dataset:
    1. Reservoir-sample N sentences from the (huge, 52M-line) HingCorpus train file
       without loading the whole file into memory.
    2. Weak-label each sampled sentence using:
       - The Mathur et al. profanity lexicon (term, meaning, severity 1-5)
         -> presence of a profane term => candidate NON_VIOLENT_ABUSE
       - A small hand-curated list of Hinglish/Hindi violence-indicator phrases
         (e.g. "maar dunga", "jaan se maar", "khatam kar dunga")
         -> presence of a violence phrase => candidate POTENTIAL_THREAT
       - Both present in the same sentence => candidate VIOLENT_THREAT
       - Neither present => SAFE
    3. Output a CSV for manual spot-check review before it's trusted for training.

IMPORTANT: these are WEAK labels from lexicon matching, not ground truth. A subset
must be manually reviewed (see review_sample.py, written after this) before this
data is used to train anything. Document the % reviewed in ml/data/README.md.

Output: ml/data/processed/hinglish_weak_labeled.csv
    Columns: sentence, weak_label, matched_profanity_terms, matched_violence_phrases, source
"""

import csv
import random
import re
from pathlib import Path

HINGCORPUS_PATH = Path(__file__).parent / "raw" / "hingcorpus" / "concatenated_train_final_shuffled.txt"
PROFANITY_PATH = Path(__file__).parent / "raw" / "profanity_lexicon" / "Hinglish_Profanity_List.csv"
OUT_PATH = Path(__file__).parent / "processed" / "hinglish_weak_labeled.csv"

SAMPLE_SIZE = 50_000  # target number of sentences to sample from the 52M-line corpus
RANDOM_SEED = 42

# Hand-curated violence-indicator phrases (Hinglish/Hindi, Roman script).
# This list is intentionally small and will need expansion after manual review —
# it exists to catch violent-threat language that a pure profanity lexicon misses
# (e.g. "maar dunga" = "I will kill/beat you" is a threat, not a slur).
VIOLENCE_INDICATOR_PHRASES = [
    "maar dunga", "maar doonga", "jaan se maar", "khatam kar dunga",
    "goli maar", "chaku maar", "zinda nahi chodunga", "dekh lunga tujhe",
    "kill you", "i will kill", "marunga tujhe", "mar jayega",
]


def load_profanity_lexicon(path: Path) -> list[tuple[str, str, int]]:
    terms = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 3:
                print(f"[WARN] Skipping malformed lexicon line: {line!r}")
                continue
            term, meaning, severity = parts[0], parts[1], parts[2]
            try:
                severity = int(severity)
            except ValueError:
                severity = 1
            terms.append((term.strip().lower(), meaning.strip(), severity))
    return terms


def build_term_pattern(terms: list[str]) -> re.Pattern:
    """Word-boundary regex matching any term in the list, case-insensitive."""
    escaped = [re.escape(t) for t in terms]
    pattern = r"\b(" + "|".join(escaped) + r")\b"
    return re.compile(pattern, re.IGNORECASE)


def reservoir_sample_lines(path: Path, k: int, seed: int) -> list[str]:
    """
    Uniformly sample k lines from a file without loading the whole file into
    memory — needed since HingCorpus train file is ~4.9GB / 52M lines.
    """
    rng = random.Random(seed)
    reservoir: list[str] = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            if len(reservoir) < k:
                reservoir.append(line)
            else:
                j = rng.randint(0, i)
                if j < k:
                    reservoir[j] = line
    return reservoir


def weak_label_sentence(
    sentence: str,
    profanity_pattern: re.Pattern,
    violence_pattern: re.Pattern,
) -> tuple[str, str, str]:
    profanity_matches = profanity_pattern.findall(sentence)
    violence_matches = violence_pattern.findall(sentence)

    has_profanity = len(profanity_matches) > 0
    has_violence = len(violence_matches) > 0

    if has_profanity and has_violence:
        label = "VIOLENT_THREAT"
    elif has_violence:
        label = "POTENTIAL_THREAT"
    elif has_profanity:
        label = "NON_VIOLENT_ABUSE"
    else:
        label = "SAFE"

    return (
        label,
        ";".join(set(m.lower() for m in profanity_matches)),
        ";".join(set(m.lower() for m in violence_matches)),
    )


def main():
    if not HINGCORPUS_PATH.exists():
        raise FileNotFoundError(f"HingCorpus file not found at {HINGCORPUS_PATH}")
    if not PROFANITY_PATH.exists():
        raise FileNotFoundError(f"Profanity lexicon not found at {PROFANITY_PATH}")

    print(f"Loading profanity lexicon from {PROFANITY_PATH} ...")
    lexicon = load_profanity_lexicon(PROFANITY_PATH)
    profanity_terms = [t for t, _, _ in lexicon]
    print(f"Loaded {len(profanity_terms)} profanity terms")

    profanity_pattern = build_term_pattern(profanity_terms)
    violence_pattern = build_term_pattern(VIOLENCE_INDICATOR_PHRASES)

    print(f"Reservoir-sampling up to {SAMPLE_SIZE} sentences from {HINGCORPUS_PATH} ...")
    sampled = reservoir_sample_lines(HINGCORPUS_PATH, SAMPLE_SIZE, RANDOM_SEED)
    print(f"Sampled {len(sampled)} sentences")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    label_counts = {"SAFE": 0, "NON_VIOLENT_ABUSE": 0, "POTENTIAL_THREAT": 0, "VIOLENT_THREAT": 0}

    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["sentence", "weak_label", "matched_profanity_terms", "matched_violence_phrases", "source"],
        )
        writer.writeheader()
        for sentence in sampled:
            label, prof_matches, viol_matches = weak_label_sentence(
                sentence, profanity_pattern, violence_pattern
            )
            label_counts[label] += 1
            writer.writerow({
                "sentence": sentence,
                "weak_label": label,
                "matched_profanity_terms": prof_matches,
                "matched_violence_phrases": viol_matches,
                "source": "hingcorpus_weak_labeled",
            })

    total = len(sampled)
    print("\nWeak label distribution:")
    for label, count in label_counts.items():
        print(f"  {label:20s} {count:6d} ({count / total * 100:.2f}%)")
    print(f"\nWritten to: {OUT_PATH}")
    print("\n⚠ These are WEAK labels from lexicon matching, NOT ground truth.")
    print("⚠ Manually review a sample before trusting this for training.")


if __name__ == "__main__":
    main()