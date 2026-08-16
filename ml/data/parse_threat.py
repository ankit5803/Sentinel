"""
Parse the THREAT corpus (Hammer et al. 2019) raw .txt file into a clean CSV.

Input format (VideoCommentsThreatCorpus.txt):
    Metadata lines look like: "Video #1, Comment #1, Commenter #1, 1 week ago"
      -> these mark the start of a new YouTube comment (a group of sentences).
    Data lines are tab-separated: "<label>\t<sentence>"
      -> label is 0 (not a threat) or 1 (violent threat).

Output: ml/data/processed/threat_clean.csv
    Columns: comment_id, sentence_idx_in_comment, sentence, label, source

`comment_id` lets us reconstruct sentence context later (neighboring sentences
in the same comment) for the context-aware detection feature.
"""

import csv
import re
from pathlib import Path

RAW_PATH = Path(__file__).parent / "raw" / "threat" / "VideoCommentsThreatCorpus.txt"
OUT_PATH = Path(__file__).parent / "processed" / "threat_clean.csv"

# Metadata lines look like: "Video #1, Comment #1, Commenter #1, 1 week ago"
METADATA_PATTERN = re.compile(r"^Video #\d+, Comment #\d+, Commenter #\d+,")


def parse_threat_corpus(raw_path: Path) -> list[dict]:
    rows = []
    comment_id = -1
    sentence_idx = 0

    with open(raw_path, "r", encoding="utf-8", errors="replace") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue

            if METADATA_PATTERN.match(line):
                # New comment starts here
                comment_id += 1
                sentence_idx = 0
                continue

            # Expect "<label>\t<sentence>"
            parts = line.split("\t", 1)
            if len(parts) != 2:
                print(f"[WARN] Skipping malformed line {line_num}: {line[:80]!r}")
                continue

            label_str, sentence = parts
            label_str = label_str.strip()
            if label_str not in ("0", "1"):
                print(f"[WARN] Unexpected label {label_str!r} at line {line_num}, skipping")
                continue

            rows.append({
                "comment_id": comment_id,
                "sentence_idx_in_comment": sentence_idx,
                "sentence": sentence.strip(),
                "label": int(label_str),
                "source": "threat_corpus",
            })
            sentence_idx += 1

    return rows


def main():
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw THREAT corpus not found at {RAW_PATH}. "
            f"Place VideoCommentsThreatCorpus.txt in ml/data/raw/threat/"
        )

    rows = parse_threat_corpus(RAW_PATH)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["comment_id", "sentence_idx_in_comment", "sentence", "label", "source"],
        )
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    positives = sum(r["label"] for r in rows)
    print(f"Parsed {total} sentences from {rows[-1]['comment_id'] + 1 if rows else 0} comments")
    print(f"Violent threat (label=1): {positives} ({positives / total * 100:.2f}%)")
    print(f"Not threat   (label=0): {total - positives} ({(total - positives) / total * 100:.2f}%)")
    print(f"Written to: {OUT_PATH}")


if __name__ == "__main__":
    main()