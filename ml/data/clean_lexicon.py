"""
One-time cleanup pass on the profanity lexicon based on manual review findings.

Rules applied:
  1. Remove an explicit list of confirmed-bad entries (neutral/common words that
     were incorrectly listed as profanity, found via manual spot-check).
  2. Remove all remaining entries with severity < 5, EXCEPT a small allowlist of
     terrorism/threat-relevant terms that are kept despite lower severity scores
     because they're meaningful signal for a threat-detection system specifically.

Run once. Overwrites the lexicon file in place (prints a backup path first).
"""

import csv
import shutil
from pathlib import Path

LEXICON_PATH = Path(__file__).parent / "raw" / "profanity_lexicon" / "Hinglish_Profanity_List.csv"
BACKUP_PATH = LEXICON_PATH.with_suffix(".csv.bak")

# Confirmed-bad entries found via manual review — neutral/common words wrongly
# listed as profanity (banda, dum, doob, kutta, ched already removed manually;
# these are the newest batch found).
EXPLICIT_REMOVE = {"jaat", "jamai", "chatani", "chipkali", "bhoot", "gandnatije"}

# Kept despite severity < 5 — relevant to threat detection specifically, not
# generic profanity, so worth keeping as a signal even at lower severity.
SEVERITY_ALLOWLIST = {"jihadi", "atankvadi", "atankwadi", "aatanki"}

SEVERITY_THRESHOLD = 5


def clean():
    if not LEXICON_PATH.exists():
        raise FileNotFoundError(f"Lexicon not found at {LEXICON_PATH}")

    shutil.copy(LEXICON_PATH, BACKUP_PATH)
    print(f"Backed up original to: {BACKUP_PATH}")

    kept, removed = [], []
    with open(LEXICON_PATH, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            term = parts[0].strip().lower()
            try:
                severity = int(parts[2].strip())
            except ValueError:
                severity = 0

            if term in EXPLICIT_REMOVE:
                removed.append((term, "explicit_remove"))
                continue
            if severity < SEVERITY_THRESHOLD and term not in SEVERITY_ALLOWLIST:
                removed.append((term, f"severity={severity}<{SEVERITY_THRESHOLD}"))
                continue

            kept.append(line)

    with open(LEXICON_PATH, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(kept) + "\n")

    print(f"\nRemoved {len(removed)} entries:")
    for term, reason in removed:
        print(f"  {term} ({reason})")
    print(f"\nKept {len(kept)} entries")
    print(f"Written to: {LEXICON_PATH}")


if __name__ == "__main__":
    clean()