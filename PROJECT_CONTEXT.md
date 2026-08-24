# Sentinel — Project Context

> Read this file first, every session. It is the single source of truth for scope, decisions, and progress. Update it as you go — don't let it go stale.

---

## 🎯 What this is

**Sentinel** — Real-Time AI Threat Detection & Self-Healing MLOps Platform.
Analyzes multi-language text (English & Hinglish) for violent-threat risk and toxic abuse (probability, severity, immediacy, target specificity), explains its decision via a deterministic Risk Engine, and continuously monitors itself in production — detecting covariate data drift, auto-labeling incoming logs via a Teacher LLM (Groq Llama 3.3-70B), retraining challenger models, benchmarking them in an MLflow Evaluation Arena, and dynamically promoting/syncing winning weights straight to the Hugging Face Hub without downtime.

Paired companion project (POSTPONED, not this month): a **from-scratch Redis clone** (TCP server, RESP protocol, event loop, persistence) — planned for a later date, not part of the current 19-day plan.

---

## 👤 Who's building this

**Ankit Barik** — AIML engineering fresher (2025 grad), Kolkata. Has an ongoing freelance CV+RAG gig (separate project). Building this in **August 2026, ~19 days**, to strengthen his portfolio and CV before applying for AI/ML and MLOps engineer roles. Built "Athena" (RAG chatbot) as a prior project — Sentinel is engineered to demonstrate production systems depth, real-time defensive NLP, closed-loop MLOps, automated CI/CD, and distributed cloud deployment.

---

## 💻 Hardware & Local Environment

- **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU (4GB VRAM), CUDA Driver 610.62, CUDA UMD 13.3.
- **Compute Framework:** PyTorch with CUDA acceleration confirmed working (`torch.cuda.is_available() = True`).
- **Memory Optimization:** Mixed precision (`fp16`), small batch sizes (8-16), and gradient accumulation utilized to fit DistilBERT fine-tuning comfortably within 4GB VRAM.

---

## ☁️ Distributed Cloud Deployment Architecture (Live & Active)

All services are fully deployed across free-tier cloud infrastructure:

- **Frontend Dashboard:** Hosted on **Vercel** (Next.js + TypeScript) providing real-time inference testing, threat distribution analytics, and live risk categorization.
- **Backend API:** Hosted on **Hugging Face Spaces** (`https://ankit03-sentinel-api.hf.space`), running high-performance **FastAPI** mounted on Gradio with dynamic model loading and fallback mechanisms.
- **Database Vault:** Managed persistent **PostgreSQL** instance hosted on **Render**, storing live production logs, raw classification scores, and audit metadata.
- **Model Registry & Weight Storage:** Hosted on **Hugging Face Hub** (`Ankit03/sentinel-model-weights`), storing language-partitioned transformer weights (`/english_distilbert` and `/hinglish_distilbert`).
- **LLM Teacher Layer:** Ultra-low latency inference via **Groq Cloud API** (`llama-3.3-70b-versatile`) for zero-shot weak supervision and automated dataset labeling.

---

## 🔒 Hard Constraints

- 19 days total, **all on Sentinel**. Redis clone is POSTPONED to a later date.
- Solo build. Finished and **fully working end-to-end**.
- Never cut: working classifier, FastAPI backend, live PostgreSQL vault, MLflow tracking, the drift $\rightarrow$ weak-label $\rightarrow$ retrain $\rightarrow$ eval-gate $\rightarrow$ deploy loop, Docker setups, and cloud deployments.
- Out of Scope: Kubernetes, multi-node clustering, complex multi-agent frameworks.

---

## 🛠️ Tech Stack (Locked In)

- **ML / NLP:** PyTorch, Hugging Face Transformers (`DistilBERT`), Scikit-Learn, LangDetect
- **Backend:** FastAPI, Pydantic V2, SQLAlchemy ORM, Uvicorn, Gradio (HF Spaces mounting)
- **Data & Ingestion:** PostgreSQL (Render), `psycopg2-binary`, Pandas, NumPy
- **MLOps & Governance:** MLflow (Experiment Tracking + Model Registry with `@production` aliases), Evidently AI (Data Drift Detection), Prefect (v3.x DAG Orchestration)
- **Teacher LLM:** Groq SDK (`llama-3.3-70b-versatile`)
- **Frontend & Cloud:** Next.js, Vercel, Hugging Face Spaces, Render, Hugging Face Hub API (`HfApi`)

---

## 🏗️ Architecture (End-to-End State)

```text
User Message → Frontend (Vercel) → API Gateway (FastAPI on HF Spaces)
  → Language Detection (Heuristics + langdetect)
  → [English]  → English Threat Model (DistilBERT fine-tuned on THREAT corpus)
  → [Hinglish] → Hinglish Abuse Model (DistilBERT fine-tuned on code-switched corpus)
  → Risk Engine (Probability × Immediacy × Target Specificity)
  → Categorical Decision (SAFE / NON-VIOLENT ABUSE / POTENTIAL THREAT / VIOLENT THREAT)
  → Response Serialization (RiskDecision Schema)
  → Async Persistence → PostgreSQL Vault (Render)

  [OFFLINE SELF-HEALING LOOP]
  → Live Data Extraction (psycopg2 binary streaming from Render)
  → Drift Detection (Evidently AI tracking covariate vocabulary shift)
  → [Drift Detected] Trigger Prefect DAG Flow:
      1. Dynamic extraction of unlabelled multi-language logs
      2. Weak Supervision via Groq Llama 3.3-70B Teacher LLM
      3. Challenger Transformer Fine-Tuning
      4. MLflow Evaluation Arena Gate (Holdout test F1: Challenger >= Champion)
      5. Gated Promotion: Assign @production alias in MLflow Registry
      6. Automated Cloud Sync: HfApi uploads model weights to Hugging Face Hub
```

### Risk Engine Output Schema:

```json
{
  "text": "I will destroy everything you own.",
  "language_detected": "english",
  "threat_probability": 0.9821,
  "risk_level": "HIGH_RISK",
  "immediacy": "HIGH",
  "target_identified": true,
  "reason": "High probability model classification escalated by explicit target and immediacy cues."
}
```

---

## 📅 Day-by-Day Timeline & Milestones

- **Days 1–3:** Data collection/prep, TF-IDF + Logistic Regression baselines, DistilBERT fine-tuning for English and Hinglish splits.
- **Days 4–6:** FastAPI backend development, PostgreSQL schema design, Risk Engine deterministic logic, Docker containerization.
- **Days 7–9:** MLflow tracking, local model registry setup, and evaluation gate implementation (`eval_gate.py`).
- **Days 10–13:** Evidently AI data drift detection, Prefect DAG orchestration, self-healing pipeline bootstrapping.
- **Day 14 (COMPLETED):** End-to-end local testing. Resolved SQLite volume persistence, Gunicorn timeout handling (`--timeout 120`), and dynamic MLflow version-alias resolution.
- **Day 15 (COMPLETED / CLOUD DEPLOYED):** Public deployment of FastAPI backend to Hugging Face Spaces (`https://ankit03-sentinel-api.hf.space`) with live connection to Render PostgreSQL.
- **Days 16–17 (COMPLETED):** Full Next.js frontend deployment on Vercel. Implemented dynamic multi-language weak supervision using Groq Llama-3.3-70B, automated MLflow evaluation arena, and direct weight synchronization to Hugging Face Hub (`Ankit03/sentinel-model-weights`).
- **Days 18–19 (CURRENT / FINAL):** Final repository polish, comprehensive README and architecture guide documentation, demo video recording, portfolio integration, and final QA pass.

---

## 📝 Progress Log

- **[progress] — Days 1–13 complete:** Data pipelines, Baselines, DistilBERT fine-tuning, FastAPI backend, PostgreSQL vault, MLflow Model Registry, Evidently drift detection, Prefect self-healing orchestration.
- **[progress] — Day 14 complete:** Executed end-to-end local test. Resolved Docker network persistence issues by updating MLflow SQLite URIs to absolute paths and enabling server artifacts. Verified full traffic simulation $\rightarrow$ drift detection $\rightarrow$ automated retraining loop.
- **[progress] — Day 15 complete:** Hosted production-ready Sentinel FastAPI backend live on Hugging Face Spaces (`https://ankit03-sentinel-api.hf.space`), paired with a persistent PostgreSQL database hosted on Render. Configured root `run.py` routing, Gradio mounting, and enabled automatic cloud weight loading.
- **[progress] — Days 16–17 complete:** Fully executed multi-language self-healing pipeline testing. Integrated live Groq Llama 3.3 weak-supervision auto-labeling for mixed English and Hinglish incoming traffic, automated multi-language evaluation arena validation in MLflow, dynamic version aliasing (`@production`), and automated Hugging Face weight synchronization (`Ankit03/sentinel-model-weights/english_distilbert` and `/hinglish_distilbert`). Frontend live on Vercel.
- **[progress] — Days 18–19 (in progress):** Project codebase clean-up, Git tracking synchronization, documentation finalization, and demo presentation preparation.
