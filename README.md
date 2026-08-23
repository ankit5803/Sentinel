---
title: Sentinel API
emoji: 🛡️
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: "4.44.1"
app_file: app.py
pinned: false
---

<div align="center">

# 🛡️ Sentinel

### Real-Time AI Threat Detection & Self-Healing MLOps Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-005571?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MLflow](https://img.shields.io/badge/MLflow-Registry-0194E2?style=flat-square&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Prefect](https://img.shields.io/badge/Prefect-Orchestration-000000?style=flat-square&logo=prefect&logoColor=white)](https://www.prefect.io/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-FFD21E?style=flat-square)](https://huggingface.co/)

_An enterprise-grade, distributed MLOps system featuring automated data drift monitoring, evaluation-gated retraining loops, and context-aware natural language threat analysis._

[Live Cloud API](#-live-cloud-deployment) • [Key Features](#-core-architecture--components) • [Tech Stack](#️-technology-stack) • [Quick Start](#-quick-start)

---

</div>

## 🎯 Overview

**Sentinel** moves beyond standard academic Machine Learning notebooks by implementing a complete, closed-loop production lifecycle. It is designed to intercept and analyze text streams for high-risk threat language using dual-language neural classifiers (English and Romanized Hinglish).

It doesn't just predict; it **self-heals**. Sentinel routes predictions through deterministic risk guardrails, logs audit telemetry to a persistent remote vault, and autonomously detects data drift to retrain, benchmark, and promote models without human intervention.

### ✨ Recent Engineering Milestones

- **Multi-Cloud Distributed Architecture:** Successfully decoupled compute from storage, deploying the heavy inference FastAPI layer on **Hugging Face Spaces (16GB RAM)** while securely routing telemetry to a persistent **Render PostgreSQL Vault**.
- **Inference Optimization:** Shaved ~10GB of bloat from the production Docker container (11.3GB ➔ 1.45GB) by strategically overriding default PyTorch CUDA binaries with CPU-only wheels and eliminating pip cache layers, achieving a lightweight edge-ready image.
- **Continuous Integration:** Implemented GitHub Actions CI/CD pipelines to automatically build, test, and verify Docker containers and database connections on every push.

---

## 🏛️ Core Architecture & Components

```text
Incoming Text Stream
 ├── 1. FastAPI Gateway (Pydantic Schema Validation)
 ├── 2. Heuristic Language Router [English vs. Romanized Hinglish]
 ├── 3. DistilBERT Classifier (Hot-loaded via MLflow @production Registry)
 ├── 4. Contextual Risk Engine (Probability × Target × Immediacy)
 └── 5. PostgreSQL Audit Vault (Remote Cloud Logging)
1. Defense-in-Design InferenceDual-Language Specialization: Decouples English and Romanized Hindi (Hinglish) into independent pipelines (distilbert-base-uncased and distilbert-base-multilingual-cased) trained with class-weighted cross-entropy loss to handle severe real-world data imbalance (~4% positive rates).Contextual Risk Engine: Intercepts raw neural probabilities, applying regular-expression and keyword-based heuristics to evaluate target specificity and temporal immediacy, returning structured decisions (SAFE, REVIEW, HIGH RISK).2. Autonomous MLOps LoopObservability & Drift: Evidently AI streams production audit logs directly from PostgreSQL, performing statistical distribution comparisons against historical training baselines.Orchestration & Retraining: Prefect manages Directed Acyclic Graphs (DAGs) that orchestrate background retraining jobs using a local GPU when drift triggers occur.The Evaluation Gate ("The Arena"): Prevents silent production regressions by executing strict holdout test-set benchmarking. A candidate model is prohibited from receiving the @production registry tag unless it programmatically outperforms the active champion.🛠️ Technology StackLayerTechnologiesML & NLPPyTorch, Hugging Face Transformers (DistilBERT), scikit-learnBackend & APIFastAPI, Pydantic, SQLAlchemy ORM, Uvicorn, Gradio SDK (Mount)Data & StoragePostgreSQL (Render)MLOps & CI/CDMLflow, Evidently AI, Prefect, GitHub ActionsInfrastructureDocker, Docker Compose, Hugging Face Spaces☁️ Live Cloud DeploymentThe API is actively hosted in the cloud using a custom FastAPI mount injected into a Hugging Face Space.Live Swagger UI: View Documentation & Test LiveExample Cloud API RequestBashcurl -X 'POST' \
  '[https://ankit03-sentinel-api.hf.space/api/v1/analyze](https://ankit03-sentinel-api.hf.space/api/v1/analyze)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "I am going to find you tonight and make sure you disappear."
}'
Structured JSON Response:JSON{
  "threat_probability": 0.94,
  "risk_level": "HIGH",
  "immediacy": "HIGH",
  "target_identified": true,
  "confidence": 0.91,
  "reason": "Explicit intent + targeted threat language"
}
🚀 Local Quick StartEnsure you have Docker Desktop and Python 3.11+ installed locally.1. Clone the RepositoryBashgit clone [https://github.com/your-username/Sentinel.git](https://github.com/your-username/Sentinel.git)
cd Sentinel
2. Spin Up Infrastructure (Docker Compose)Boots a local PostgreSQL database, MLflow server, and the FastAPI backend simultaneously:Bashdocker compose up -d --build
3. Seed the MLflow Model RegistryPacks and registers the pre-trained production artifact weights into the Dockerized registry:Bashpython ml/training/register_to_docker_mlflow.py
4. Run Drift Simulation & Self-Healing PipelineBash# Simulate adversarial text drift and write logs to PostgreSQL
python ml/training/simulate_traffic.py

# Detect distribution shift via Evidently AI
python ml/training/drift_detector.py

# Trigger the Prefect automated retrain and evaluation loop
python ml/training/retrain_pipeline.py
📂 Repository StructurePlaintext├── .github/workflows/    # GitHub Actions CI/CD pipelines
├── backend/              # FastAPI server, SQLAlchemy schemas, business logic
├── ml/
│   ├── data/             # Sourcing scripts, weak-label pipelines, test splits
│   └── training/         # DistilBERT training, Evidently configs, Prefect DAGs
├── docker-compose.yml    # Multi-container local infrastructure
├── Dockerfile            # Optimized 1.45GB CPU-only container definition
├── app.py                # Cloud entrypoint (Trojan Horse FastAPI mount)
└── requirements.txt      # Production dependencies
```
