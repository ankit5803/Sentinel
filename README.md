# Sentinel — Real-Time AI Threat Detection & Self-Healing MLOps Platform

A production-grade system that analyzes text in real time to detect violent threats, scores severity/immediacy, explains its reasoning, and continuously monitors itself in production — auto-retraining and redeploying when data drift is detected, gated by evaluation before any model goes live.

Built as a solo, 19-day project (August 2026) to demonstrate end-to-end ML engineering: from raw data sourcing through a fully containerized, self-healing MLOps loop.

---

## Status: Day 14 Complete (End-to-End MLOps Loop + Docker Infrastructure Stable)

This project has completed its core MLOps architecture. The system features:

- **Two fine-tuned DistilBERT models** (English & Hinglish) dynamically hot-loaded from an internal MLflow Model Registry.
- **A FastAPI Backend** with Pydantic validation, heuristic language routing, and a Contextual Risk Engine.
- **Persistent Audit Logging** into a Dockerized PostgreSQL Vault ("The Vault").
- **Automated Data Drift Detection** via Evidently AI, tracking distribution shifts between 2019 training baselines and modern live traffic.
- **Self-Healing Orchestration** via Prefect DAGs that trigger automated model retraining and benchmark Challengers against Production in an Evaluation Gate ("The Arena").
- **Complete Dockerization** with absolute path volume mapping and Gunicorn artifact proxy streaming timeouts.

---

## Architecture & Core Loop

```text
User message → API Gateway (FastAPI) → Pre-processing → Language Detection
  → [English] / [Hinglish] Threat Detection Model (DistilBERT via MLflow @production)
  → Risk Engine (probability × severity × immediacy × target specificity → risk level)
  → Decision (SAFE / REVIEW / HIGH RISK)
  → Logging → PostgreSQL Vault
  → Drift Detection (Evidently AI watching production traffic distributions)
  → [Drift Detected] → Prefect Retraining Pipeline & Challenger Training
  → Model Evaluation Gate (Challenger must beat Champion F1 score on holdout test set)
  → MLflow Model Registry → Automated Promotion (@production hot-swap)
Architecture HighlightsAPI Gateway (FastAPI): Uses Pydantic for strict schema validation, returning 422 Unprocessable Entity on malformed requests to protect compute resources.Dynamic Language Routing: Combines langdetect with custom heuristic token sets to separate English from code-mixed Romanized Hindi (Hinglish) traffic.The Contextual Risk Engine: Intercepts raw model probabilities to evaluate target specificity, temporal immediacy, and safety-floor thresholds, producing a transparent explanation and structured decision (SAFE, REVIEW, HIGH RISK).The MLOps Vault (PostgreSQL & MLflow): Decouples model storage from code via absolute-path volume mounting (sqlite:////mlflow/mlflow.db) and robust artifact proxying (--serve-artifacts, --timeout 120).The Self-Healing Loop (Evidently + Prefect): Continuously monitors live query logs, flags covariate/target drift, orchestrates DAG-based retraining tasks, and enforces strict evaluation gating before promoting models.DataEnglish — THREAT corpus (Hammer et al. 2019)Source: erikve/YouTube-Threat-Corpus28,643 sentences from 9,845 YouTube comments, manually annotated for violent threats. Class balance: 95.16% SAFE / 4.84% VIOLENT_THREAT.Hinglish — Self-Built Weakly-Labeled DatasetBuilt using raw social-media text from L3Cube-HingCorpus (52.93M sentences, sampled 50,000) paired with a cleaned profanity lexicon (Mathur et al.) for weak labeling. Hand-reviewed subsets achieved 100% final agreement after systematic lexicon audits (audit_lexicon.py, clean_lexicon.py).Models & PerformanceBoth languages were trained on a local NVIDIA RTX 3050 (4GB VRAM) using mixed precision (fp16) and gradient accumulation.LanguageModelTarget ClassPrecisionRecallF1 ScoreEnglishDistilBERT (uncased)VIOLENT_THREAT0.770.790.78 (up from baseline 0.63)HinglishDistilBERT (multilingual-cased)NON_VIOLENT_ABUSE0.970.890.93Repository StructurePlaintextml/
├── data/                 # Raw/processed datasets & cleaning scripts
├── training/             # Baselines, DistilBERT, registration, Evidently, Prefect pipeline
backend/
├── app/                  # FastAPI app, schemas, DB models, risk engine, config
infra/                    # Docker configs
docker-compose.yml        # Orchestration for Backend, PostgreSQL, and MLflow
.github/workflows/ci.yml  # Automated CI/CD pipeline
Running the System Locally (Docker Compose)The entire application stack (API, PostgreSQL, MLflow) is containerized and managed via Docker Compose.1. Build and Boot the StackPowerShelldocker compose up -d --build
2. Seed MLflow with Production ModelsPowerShellpython ml/training/register_to_docker_mlflow.py
3. Test Live Traffic & Simulate DriftPowerShellpython ml/training/simulate_traffic.py
python ml/training/drift_detector.py
4. Trigger the Self-Healing Prefect PipelinePowerShellpython ml/training/retrain_pipeline.py
Access the interactive API documentation at http://localhost:8000/docs and the MLflow Tracking Dashboard at http://localhost:5000.
```
