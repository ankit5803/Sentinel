# Sentinel — Project Context

> Read this file first, every session. It is the single source of truth for scope, decisions, and progress. Update it as you go — don't let it go stale.

## What this is

**Sentinel** — Real-Time AI Threat Detection & Self-Healing MLOps Platform.
Analyzes text for violent-threat risk (probability, severity, immediacy), explains its
decision, and continuously monitors itself in production — auto-retraining and
redeploying when data drift is detected, gated by evaluation before any model goes live.

Paired companion project (POSTPONED, not this month): a **from-scratch Redis clone**
(TCP server, RESP protocol, event loop, persistence) — planned for a later date, not
part of the current 19-day plan. Sentinel will still use real Redis (the library) as its
caching layer for now.

## Who's building this

Ankit Barik — AIML engineering fresher (2025 grad), Kolkata. Has an ongoing freelance
CV+RAG gig (separate project). Building this in **August 2026, ~19 days**, to
strengthen his CV before applying for AI/ML engineer roles. Already built "Athena"
(RAG chatbot) as a prior project — Sentinel + Redis-clone are meant to close SWE
fundamentals, systems depth, MLOps, and security-thinking gaps that Athena doesn't cover.

## Hardware

User has NVIDIA GeForce RTX 3050 Laptop GPU, 4GB VRAM, driver 610.62, CUDA UMD 13.3.
PyTorch 2.5.1+cu121 installed and CONFIRMED WORKING — torch.cuda.is_available() = True,
device correctly detected. 4GB VRAM is limited for transformer fine-tuning — DistilBERT
training will need a small batch size (likely 8-16) and possibly fp16/mixed precision
or gradient accumulation to fit comfortably. Not a blocker, just plan for it.

## Hard constraints

- 19 days total, **all on Sentinel**. Redis clone is POSTPONED to a later date — not part
  of this month's scope. Do not plan or build it now.
- Solo build. Must be finished and _working end-to-end_, not 80% done with more features.
- If behind schedule, cut in this order: Prometheus/Grafana first → fancy frontend polish
  second → TF-IDF baseline depth third. NEVER cut: working classifier, FastAPI backend,
  MLflow tracking, the drift→retrain→eval-gate→deploy loop (this is the whole point of
  the project), Docker, basic tests.
- Kubernetes, clustering/sharding/replication (Redis), multi-model ensembles, complex
  agentic LLM features — explicitly OUT OF SCOPE this month.

## Tech stack (locked in)

- **ML/NLP:** PyTorch, Hugging Face Transformers (DistilBERT), scikit-learn (TF-IDF+LogReg baseline)
- **Backend:** FastAPI, Pydantic, SQLAlchemy
- **Data:** PostgreSQL, Redis
- **MLOps:** MLflow (tracking + model registry), Evidently (drift detection), Prefect (retraining orchestration)
- **Frontend:** Next.js + TypeScript (minimal — 4-5 key metrics, not a full app)
- **Infra:** Docker, Docker Compose, GitHub Actions (CI/CD), Prometheus + Grafana (nice-to-have, cut first if behind)
- **Redis clone:** Python, asyncio, raw sockets, custom RESP parser

## Architecture (target end state)

```
User message → API Gateway (FastAPI) → Pre-processing → Language Detection
  → [English] → English Threat Detection Model (DistilBERT, fine-tuned on THREAT corpus)
  → [Hinglish] → Hinglish Threat Detection Model (DistilBERT, fine-tuned on weak-labeled Hinglish data)
  → (rules layer + context/semantic layer applied per-language before final model)
  → Risk Engine (probability × severity × immediacy × target specificity → risk level)
  → Decision (SAFE / REVIEW / HIGH RISK)
  → Logging + Postgres
  → Drift Detection (Evidently, watching incoming data + prediction distributions, per language)
  → [if drift threshold crossed] Retraining Pipeline (Prefect, per-language retrain)
  → Model Evaluation Gate (must beat current production model, per language)
  → MLflow Model Registry → Deploy (or reject if it doesn't beat prod)
```

Risk Engine output shape (not just `{"threat": true}`):

```json
{
  "threat_probability": 0.94,
  "risk_level": "HIGH",
  "immediacy": "HIGH",
  "target_identified": true,
  "confidence": 0.91,
  "reason": "Explicit intent + targeted threat language"
}
```

Classification categories: SAFE / NON-VIOLENT ABUSE / POTENTIAL THREAT / VIOLENT THREAT

## Day-by-day plan (Sentinel, days 1-19 — full month, Redis clone postponed)

- **Days 1-3:** Data collection/prep, TF-IDF+LogReg baseline, DistilBERT fine-tune. Lock real metrics (precision/recall/F1/latency) before touching infra.
- **Days 4-6:** FastAPI backend, Postgres schema, Redis integration, Risk Engine logic. Fully working locally before adding MLOps layers.
- **Days 7-9:** MLflow tracking + model registry + eval gate (new model must beat production to deploy).
- **Days 10-13:** Evidently drift detection + Prefect retraining trigger. Protect this time — it's the core "wow" loop. Extra day vs original plan since full month is available.
- **Day 14:** End-to-end test: simulate drift live, confirm auto-retrain-and-promote loop actually works. Do this early enough to fix bugs.
- **Day 15:** Docker Compose + GitHub Actions CI/CD.
- **Days 16-17:** Dashboard (Next.js) + Prometheus/Grafana (back in scope now — more time available; still first thing cut if behind).
- **Days 18-19:** Buffer, demo video, README polish, final QA pass.

## Redis clone — POSTPONED

Not part of this month. Full 16-19 days now go to Sentinel alone. Revisit the Redis
clone plan (TCP server, RESP parser, core commands, persistence, benchmarking) as a
separate future project once Sentinel ships.

## Data sourcing note (sensitive topic — be deliberate)

Use existing public, licensed hate-speech/threat-language datasets (not scraped real
threats). Frame publicly (README, demo video, LinkedIn post) as AI-safety engineering,
not "look what dangerous prompts I can trigger." Keep tone professional and clearly
safety-oriented throughout.

## Progress log

> Append a dated 2-3 line entry every session. New sessions: read this section first to know exactly where things left off.

- **[not started yet]** — scaffold created (folders, git init, this file).
- **[decision]** — Redis clone postponed to a later date. Full 19 days now dedicated to Sentinel only. Plan revised accordingly (more buffer + Prometheus/Grafana back in scope).
- **[decision]** — Datasets finalized: THREAT corpus (Hammer et al. 2019, English, violent-threat-specific) + a self-built weakly-labeled Hinglish dataset (L3Cube-HingCorpus real text + Mathur et al. profanity lexicon for weak labels + manual spot-check QA). Every pre-packaged Hinglish hate-speech dataset with real text (Bohra, Mathur/HOT, HASOC, Kaggle studiousmonk) was rejected as gated, ID-only, or unverified — pivoted to building our own from confirmed-real sources.
- **[progress]** — Manual spot-check found a bad lexicon entry ("banda" = "guy/person", a common neutral word, was incorrectly listed as profanity severity 7) plus 3 duplicate terms with conflicting severities (chinaal, gaandu, gandu). Wrote audit_lexicon.py to catch this systematically going forward. Cleaned lexicon from 209 → 205 terms. Re-ran weak_label_hinglish.py: 50,000 sampled, 96.63% SAFE / 3.35% NON_VIOLENT_ABUSE / 0.02% POTENTIAL_THREAT / 0% VIOLENT_THREAT. Manual review agreement improved from 74.5% (before cleanup) to 87.5% (after cleanup, 48 rows reviewed).
- **[progress]** — Further manual review found more bad entries (dum, doob = false positives; kutta, ched = context-dependent, unsuitable for plain word-match) — removed. Then applied a broader rule via clean_lexicon.py: removed all entries with severity < 5 (mostly mild/ambiguous terms that were the main noise source) EXCEPT a small terrorism-relevant allowlist (jihadi, atankvadi, atankwadi, aatanki) kept despite severity 4. Removed 65 entries total, 136 kept (was 205). Re-ran weak_label_hinglish.py: 97.83% SAFE / 2.15% NON_VIOLENT_ABUSE / 0.02% POTENTIAL_THREAT / 0% VIOLENT_THREAT. Final manual review: 52/52 (100%) agreement — dataset quality confirmed, labeling iteration DONE.
- **[decision]** — Final training set will substitute reviewer_label from hinglish_reviewed.csv for all manually reviewed rows (treated as gold, ~100+ rows across review passes), leave remainder as weak labels (now high-confidence given 100% final agreement rate) — standard weak-supervision practice, documented in ml/data/README.md.
- **[note]** — Both datasets' English/Hinglish data is finalized and clean. Next: CUDA setup for RTX 3050 (4GB VRAM), then TF-IDF+LogReg baseline, then DistilBERT fine-tune (Days 1-3 of the plan).
- **[decision]** — Architecture change: train SEPARATE specialized models for English and Hinglish, not one merged multilingual model. Sentinel's backend will do language detection and route to the matching model. build*training_set.py now outputs english*{train,val,test}.csv and hinglish\_{train,val,test}.csv independently, each stratified-split. Rationale: language-specific models can specialize rather than being diluted across two very different text distributions — also a good interview talking point.
- **[progress]** — CUDA setup done: torch 2.5.1+cu121 installed, confirmed working (torch.cuda.is_available()=True, RTX 3050 Laptop GPU detected). ML deps installed (numpy, pandas, scikit-learn, transformers, accelerate). Next: write TF-IDF+LogReg baseline scripts for both languages, then DistilBERT fine-tune scripts (two models, one per language).
- **[note]** — User has a CUDA-capable GPU, not yet enabled/configured. Use for DistilBERT training and later retraining runs.

## Open decisions / TBD

- ~~Exact dataset(s) for threat classification~~ — DECIDED (see Datasets section below).
- Whether Prometheus/Grafana makes the final cut — decide by Day 12 based on schedule.

## Datasets (decided)

Two datasets, run through **separate cleaning/labeling pipelines**, both mapping into
the same final schema (SAFE / NON-VIOLENT ABUSE / POTENTIAL THREAT / VIOLENT THREAT)
before hitting the shared training set. Not force-merged into one raw file — kept as
two independent pipelines with a shared output contract.

1. **THREAT corpus (Hammer et al. 2019)** — English, violent-threat-specific.
   ~30,000 sentences from ~10,000 YouTube comments, manually annotated violent-threat
   or not. Source: github.com/erikve/YouTube-Threat-Corpus. Severely imbalanced
   (~4-5% positive) — this is realistic and intentional, drives the precision/recall/F1
   focus (not accuracy) in the project. Must cite both Hammer et al. 2019 and the
   related Wester et al. 2016 paper per the dataset's usage terms.

2. **Weakly-labeled Hinglish dataset (built by us)** — since every pre-packaged Hinglish
   hate-speech dataset with real text turned out gated or questionable (see rejected
   list below), we build our own:
   - **Source text:** L3Cube-HingCorpus — real Hinglish sentences scraped from Twitter,
     52.93M sentences, publicly downloadable via Google Drive (no gate), from
     github.com/l3cube-pune/code-mixed-nlp. Take a manageable sample (not the full 52M).
   - **Weak labeling:** Hinglish_Profanity_List.csv from
     github.com/pmathur5k10/Hinglish-Offensive-Text-Classification (this specific file
     IS public in that repo, unlike the tweet text). Sentence contains a profane/abusive
     term from the list → weak-labeled as candidate ABUSIVE; flag severity-loaded terms
     (violence-related) as candidate POTENTIAL THREAT / VIOLENT THREAT for manual review.
   - **Manual spot-check:** hand-review and clean a meaningful subset (document exact %
     reviewed) to validate weak-label quality before training — this is the legitimate,
     defensible part of the technique (lexicon-based weak supervision), and the manual
     QA step is what makes it honest, not just automated noise.
   - Document this whole pipeline clearly in `ml/data/README.md` — it's a genuine data
     engineering story for interviews, stronger than "downloaded a labeled CSV."

   REJECTED (in order tried): Bohra et al. 2018 — only releases tweet IDs, not text,
   due to Twitter ToS (requires emailing author, unpredictable wait). Mathur et al.
   2018 (HOT dataset) — same problem, only the profanity word-list CSV is public, actual
   tweet text requires author contact (but see above — we're now using that public
   profanity list directly for weak labeling, which is a legitimate reuse). HASOC —
   gated behind emailing organizers for a password. L3Cube — has real Hinglish text
   (HingCorpus) but no Hindi-English hate-speech labels (their labeled hate-speech set,
   MeHate, is Marathi-English, wrong language pair) — this is why we use HingCorpus for
   raw text only, paired with the Mathur profanity list for labels. Kaggle
   "studiousmonk/code-mixed-hinglish-abusive-and-hate-speech" — description reads as a
   constructed profanity/slur wordlist rather than natural Hinglish sentences, quality
   unconfirmed and user's own inspection suggested it looked like plain English, not
   genuinely code-mixed — dropped in favor of building our own from verified real text.

   Lesson: any dataset sourced from Twitter/X and published post-~2018 is very likely
   ID-only due to ToS; prioritize datasets that explicitly ship raw text. Kaggle
   community datasets need direct inspection before trusting their label/language claims.

Rejected: HASOC (gated behind emailing organizers for a password — unpredictable
delay, not worth the risk on a 19-day clock). Jigsaw Toxic Comments (considered
initially, dropped in favor of THREAT which is purpose-built for violent threats
specifically rather than general toxicity).

**Label mapping logic (to be finalized Day 1, document actual rules in `ml/data/README.md` once built):**

- THREAT corpus: violent-threat=1 → VIOLENT THREAT; violent-threat=0 → SAFE (binary source, maps to 2 of the 4 classes directly)
- Bohra et al.: hate=1 → NON-VIOLENT ABUSE (unless language indicates targeted violence, in which case escalate to POTENTIAL THREAT — rule to be defined precisely during Day 1 data inspection); normal=0 → SAFE
