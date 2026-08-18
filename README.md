# Sentinel — Real-Time AI Threat Detection & Self-Healing MLOps Platform

A production-grade system that analyzes text in real time to detect violent
threats, scores severity/immediacy, explains its reasoning, and continuously
monitors itself in production — auto-retraining and redeploying when data
drift is detected, gated by evaluation before any model goes live.

Built as a solo, 19-day project (August 2026) to demonstrate end-to-end ML
engineering: from raw data sourcing through a self-healing MLOps loop, not
just a notebook that trains a model once.

Companion project (built separately, credited on this author's CV): **Athena**,
a multimodal RAG chatbot.

---

## Status: Phase 2 complete (Data + Baseline + DistilBERT)

This README documents everything done so far. The system currently has two
trained, evaluated text classifiers. The FastAPI backend, Risk Engine,
MLOps loop (MLflow/Evidently/Prefect), and dashboard are the next phases —
see `PROJECT_CONTEXT.md` for the full day-by-day plan and current progress log.

---

## Why two separate models

Sentinel trains **two independently specialized classifiers** — one for
English, one for Hinglish (code-mixed Hindi-English) — rather than one merged
multilingual model. A language-specific model can specialize on that
language's patterns instead of being diluted across two very different text
distributions. The backend will route incoming text to the correct model
based on detected language.

---

## Data

### English — THREAT corpus (Hammer et al. 2019)

- Source: [erikve/YouTube-Threat-Corpus](https://github.com/erikve/YouTube-Threat-Corpus)
- 28,643 sentences from 9,845 YouTube comments, manually annotated for violent
  threats.
- Class balance: **95.16% SAFE / 4.84% VIOLENT_THREAT** — this severe,
  realistic imbalance is intentional and is why the project tracks
  precision/recall/F1 rather than accuracy throughout.

### Hinglish — self-built weakly-labeled dataset

Every pre-packaged Hinglish hate-speech dataset with real text turned out to
be gated or unusable:

- **Bohra et al. 2018** — releases only tweet IDs, not text (Twitter ToS)
- **Mathur et al. 2018 (HOT dataset)** — same issue, only a profanity word
  list is public
- **HASOC** — gated behind emailing organizers for a password
- **L3Cube** — has real Hinglish text (HingCorpus) but no matching
  hate-speech labels for Hindi-English (their labeled set, MeHate, is
  Marathi-English)
- A Kaggle "Hinglish abusive" dataset — inspected directly and found to read
  more like a constructed slur wordlist than genuine natural sentences

**Solution: built a weakly-labeled dataset from two real, public sources:**

1. **L3Cube-HingCorpus** — real Hinglish sentences scraped from Twitter (52.93M
   sentences total; sampled 50,000 for this project) — genuinely code-mixed,
   natural social-media text.
2. **A profanity lexicon** (originally from Mathur et al.'s repo) used for
   lexicon-based weak labeling: sentences containing a profane/abusive term
   are flagged as candidate abuse; sentences containing a small hand-curated
   list of Hindi/Hinglish violence-indicator phrases (e.g. "maar dunga") are
   flagged as candidate threats.

**Data quality iteration (this is real, not glossed over):**
The profanity lexicon (209 terms) had real quality problems, found through
manual spot-checking:

- A common neutral word ("banda" = "person/guy") was incorrectly listed as
  profanity at severity 7/10.
- Several other everyday words (dum, doob, kutta, ched, jaat, jamai, etc.)
  were either false positives or too context-dependent for a plain
  word-match to resolve safely.
- 3 duplicate terms had conflicting severity scores.

After cleaning (209 → 136 terms, keeping a small terrorism-relevant
allowlist despite lower severity scores), manual review agreement improved
from **74.5% → 87.5% → 100%** across three review passes. Tooling built for
this: `audit_lexicon.py` (flags suspect entries automatically),
`clean_lexicon.py` (applies documented cleanup rules), `review_sample.py`
(interactive manual spot-check tool).

**Final Hinglish label distribution** (50,000 sampled sentences):
97.83% SAFE / 2.15% NON_VIOLENT_ABUSE / 0.02% POTENTIAL_THREAT / 0% VIOLENT_THREAT.

**Known, honest limitation:** POTENTIAL_THREAT and VIOLENT_THREAT are
near-empty in the Hinglish data (9 and 0 examples respectively, out of
50,000). This is expected — casual social-media chatter rarely contains overt
violent threats — but it means the Hinglish model currently **cannot
reliably detect violent threats**; its real strength is SAFE vs.
NON_VIOLENT_ABUSE. This is stated plainly rather than implied away.

---

## Models

Both languages were trained with two approaches to give an honest
before/after comparison, not just a single black-box number.

### Baseline: TF-IDF + Logistic Regression

`class_weight='balanced'` used to handle the severe class imbalance.

| Language | Class             | Precision | Recall | F1   |
| -------- | ----------------- | --------- | ------ | ---- |
| English  | VIOLENT_THREAT    | 0.53      | 0.77   | 0.63 |
| English  | SAFE              | 0.99      | 0.97   | 0.98 |
| Hinglish | NON_VIOLENT_ABUSE | 0.99      | 0.87   | 0.93 |
| Hinglish | POTENTIAL_THREAT  | 0.00      | 0.00   | 0.00 |
| Hinglish | SAFE              | 1.00      | 1.00   | 1.00 |

### Fine-tuned: DistilBERT

- English: `distilbert-base-uncased`
- Hinglish: `distilbert-base-multilingual-cased` (better suited to
  code-mixed/Romanized text than an English-only model)

Trained with a custom weighted cross-entropy loss (same imbalance-handling
principle as the baseline), fp16 mixed precision, batch size 8 with gradient
accumulation (effective batch 16) — tuned to fit a 4GB VRAM GPU
(RTX 3050 Laptop) with no out-of-memory issues.

| Language | Class             | Precision | Recall   | F1       |
| -------- | ----------------- | --------- | -------- | -------- |
| English  | VIOLENT_THREAT    | **0.77**  | **0.79** | **0.78** |
| English  | SAFE              | 0.99      | 0.99     | 0.99     |
| Hinglish | NON_VIOLENT_ABUSE | 0.97      | 0.89     | 0.93     |
| Hinglish | POTENTIAL_THREAT  | 0.00      | 0.00     | 0.00     |
| Hinglish | SAFE              | 1.00      | 1.00     | 1.00     |

**Results, read honestly:**

- **English: a clear, meaningful win.** DistilBERT improved VIOLENT_THREAT F1
  from 0.63 to 0.78 — precision nearly doubled (fewer false alarms) while
  recall held steady (still catching ~79% of real threats).
- **Hinglish: roughly matched the baseline, not a clear win.** This is an
  expected, explainable result: transformers need real data volume to show
  their advantage, and with only ~1,000 abuse examples and 9 threat examples,
  there wasn't enough signal for DistilBERT to meaningfully outperform a
  simpler model. Reported honestly rather than cherry-picked.
- **POTENTIAL_THREAT is unlearnable by either model** given the data
  available — a data problem, not a model problem. Documented as a known
  limitation, not hidden.

---

## Repository structure (Phase 1)

```
ml/data/
├── raw/                          # source data (large files gitignored)
├── processed/                    # cleaned + split datasets
├── parse_threat.py               # parses raw THREAT corpus -> clean CSV
├── weak_label_hinglish.py        # samples HingCorpus + weak-labels via lexicon
├── review_sample.py              # interactive manual label review tool
├── audit_lexicon.py              # flags suspect lexicon entries
├── clean_lexicon.py              # applies lexicon cleanup rules
└── build_training_set.py         # builds per-language train/val/test splits

ml/training/
├── train_baseline.py             # TF-IDF + Logistic Regression, per language
├── train_distilbert.py           # DistilBERT fine-tuning, per language
└── artifacts/                    # trained models (gitignored — large files)
```

## Reproducing this phase

```bash
cd ml/data
python parse_threat.py
python weak_label_hinglish.py
python audit_lexicon.py      # optional — review flagged entries manually
python clean_lexicon.py      # optional — only if you've customized the removal rules
python review_sample.py      # optional — manual spot-check
python build_training_set.py

cd ../training
python train_baseline.py english
python train_baseline.py hinglish
python train_distilbert.py english
python train_distilbert.py hinglish
```

Raw source data (THREAT corpus, HingCorpus, profanity lexicon) is not
included in this repo due to file size and licensing — see `PROJECT_CONTEXT.md`
for exact download sources.

---

## What's next

Days 4-6 of the build plan: FastAPI backend, PostgreSQL schema, Redis
integration, and the Risk Engine (turning a raw model prediction into a
structured `{threat_probability, risk_level, immediacy, target_identified,
confidence, reason}` response instead of a bare classification). Full
day-by-day plan and live progress log in `PROJECT_CONTEXT.md`.
