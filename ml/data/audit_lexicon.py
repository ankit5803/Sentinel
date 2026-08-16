"""
Sanity-check the profanity lexicon for likely bad entries before trusting it
for weak-labeling. Flags:
  - severity values outside the documented 1-5 range (the source claims 1-5;
    anything outside that is a red flag, like the "banda" -> 7 entry found manually)
  - very common, everyday Hindi/Hinglish words that are almost certainly NOT
    profanity (a manually curated stoplist of common false-positive-prone words)
  - duplicate terms with conflicting severities

This doesn't replace manual review — it just surfaces likely problems fast so
you're not scanning 200+ lines by eye.
"""

import csv
from pathlib import Path

LEXICON_PATH = Path(__file__).parent / "raw" / "profanity_lexicon" / "Hinglish_Profanity_List.csv"

# Common, everyday Hindi/Hinglish words that should almost never be profanity.
# If any of these show up in the lexicon, flag for manual removal/review.
SUSPECT_COMMON_WORDS = {
    "banda", "bandi", "aadmi", "ladka", "ladki", "yaar", "bhai", "didi",
    "accha", "theek", "kya", "hai", "nahi", "haan", "kaun", "kaise",
    "log", "insaan", "dost", "family", "ghar", "kaam",
}


def audit(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Lexicon not found at {path}")

    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 3:
                print(f"[MALFORMED] line {line_num}: {line!r}")
                continue
            term, meaning, severity_str = parts[0].strip().lower(), parts[1].strip(), parts[2].strip()
            try:
                severity = int(severity_str)
            except ValueError:
                severity = None
            rows.append((line_num, term, meaning, severity))

    print(f"Total entries: {len(rows)}\n")

    print("=== Out-of-range severity (expected 1-5) ===")
    out_of_range = [r for r in rows if r[3] is None or not (1 <= r[3] <= 5)]
    for line_num, term, meaning, severity in out_of_range:
        print(f"  line {line_num}: {term} -> severity={severity} (meaning: {meaning})")
    if not out_of_range:
        print("  none found")

    print("\n=== Suspect common/neutral words present in lexicon ===")
    suspects = [r for r in rows if r[1] in SUSPECT_COMMON_WORDS]
    for line_num, term, meaning, severity in suspects:
        print(f"  line {line_num}: {term} -> severity={severity} (meaning: {meaning})")
    if not suspects:
        print("  none found")

    print("\n=== Duplicate terms with different severities ===")
    from collections import defaultdict
    by_term = defaultdict(list)
    for line_num, term, meaning, severity in rows:
        by_term[term].append((line_num, severity))
    dupes = {t: v for t, v in by_term.items() if len(v) > 1}
    for term, entries in dupes.items():
        print(f"  {term}: {entries}")
    if not dupes:
        print("  none found")

    print(f"\nTotal flagged for review: {len(out_of_range) + len(suspects) + len(dupes)}")


if __name__ == "__main__":
    audit(LEXICON_PATH)