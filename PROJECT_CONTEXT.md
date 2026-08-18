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

## Deployment (added as an explicit goal, not an afterthought)

User needs a REAL PUBLIC DEPLOYED LINK to put on their CV/resume — not just a
local Docker setup. Must be FREE (no paid tiers). Plan:

- **Render** or **Railway** free tier for the FastAPI backend + Postgres + Redis
  (both platforms offer free Postgres/Redis add-ons or easy container deploys).
- Decide between the two once we reach deployment — check current free-tier
  limits at that time (they change), pick whichever has better free Postgres/
  Redis support and simpler FastAPI deploy at that moment.
- Frontend (Next.js dashboard) can go on Vercel free tier separately if easier
  than co-hosting with backend.
- IMPORTANT: build with deployment in mind from the start, not bolted on at
  the end — use environment variables for all config (DB URLs, secrets) from
  Day 4 onward, not hardcoded values, so deployment isn't a last-minute rewrite.
- Deployment is no longer just "Day 14-15" — treat it as a standing constraint
  across all backend/infra work. Confirm the app actually runs via Docker
  Compose locally BEFORE attempting cloud deployment, to isolate issues.
- Given free-tier constraints, may need to simplify (e.g. skip Prometheus/
  Grafana entirely if the free tier can't support it, or use lighter-weight
  logging/monitoring shown via the dashboard instead) — flag this tradeoff
  when we get there rather than assuming full local stack ports 1:1 to a free host.

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
