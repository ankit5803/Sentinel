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
User message → API Gateway (FastAPI) → Pre-processing
  → Threat Detection Engine (rules layer + DistilBERT classifier + context/semantic layer)
  → Risk Engine (probability × severity × immediacy × target specificity → risk level)
  → Decision (SAFE / REVIEW / HIGH RISK)
  → Logging + Postgres
  → Drift Detection (Evidently, watching incoming data + prediction distributions)
  → [if drift threshold crossed] Retraining Pipeline (Prefect)
  → Model Evaluation Gate (must beat current production model)
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

## Open decisions / TBD

- Exact dataset(s) for threat classification — TBD Day 1.
- Whether Prometheus/Grafana makes the final cut — decide by Day 12 based on schedule.
