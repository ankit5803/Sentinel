<div align="center">

# 🛡️ Sentinel

### Real-Time AI Threat Detection & Self-Healing MLOps Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-005571?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MLflow](https://img.shields.io/badge/MLflow-Registry-0194E2?style=flat-square&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Prefect](https://img.shields.io/badge/Prefect-Orchestration-000000?style=flat-square&logo=prefect&logoColor=white)](https://www.prefect.io/)

_An enterprise-grade, containerized MLOps system featuring automated data drift monitoring, evaluation-gated retraining loops, and context-aware natural language threat analysis._

[Key Features](#-core-architecture--components) • [Tech Stack](#️-technology-stack) • [Quick Start](#-quick-start) • [API Usage](#-api-usage) • [System Design](#-end-to-end-mlops-loop)

---

</div>

## 🎯 Overview

**Sentinel** moves beyond standard academic ML notebooks by implementing a complete, closed-loop production lifecycle. It ingests text streams, routes them across specialized neural classifiers based on language detection, applies deterministic risk guardrails, logs audit telemetry to a persistent vault, and **autonomously detects data drift to retrain and promote models without human intervention**.

---

## 🏛️ Core Architecture & Components

```text
Incoming Text
  ├── 1. FastAPI Gateway (Pydantic Schema Validation)
  ├── 2. Heuristic Language Router [English vs. Romanized Hinglish]
  ├── 3. DistilBERT Classifier (Hot-loaded via MLflow @production Registry)
  ├── 4. Contextual Risk Engine (Probability × Target × Immediacy)
  └── 5. PostgreSQL Audit Vault ("The Vault")
1. Defense-in-Design InferenceDual-Language Specialization: Decouples English and Romanized Hindi (Hinglish) into independent pipelines (distilbert-base-uncased and distilbert-base-multilingual-cased) trained with class-weighted cross-entropy loss to handle severe real-world data imbalance (~4% positive rates).Contextual Risk Engine: Intercepts raw neural probabilities, applying regular-expression and keyword-based heuristics to evaluate target specificity and temporal immediacy, returning structured decisions (SAFE, REVIEW, HIGH RISK).2. Autonomous MLOps LoopObservability & Drift: Evidently AI streams production audit logs directly from PostgreSQL, performing statistical distribution comparisons against historical training baselines.Orchestration & Retraining: Prefect manages Directed Acyclic Graphs (DAGs) that orchestrate background retraining jobs upon drift triggers.The Evaluation Gate ("The Arena"): Prevents silent production regressions by executing strict holdout test-set benchmarking. A candidate model is prohibited from receiving the @production registry tag unless it programmatically outperforms the active champion.🛠️ Technology StackLayerTechnologiesML & NLPPyTorch, Hugging Face Transformers (DistilBERT), scikit-learnBackend & APIFastAPI, Pydantic, SQLAlchemy ORM, UvicornData & StoragePostgreSQL ("The Vault")MLOps & GovernanceMLflow (Tracking & Model Registry), Evidently AI (Drift), Prefect (DAGs)InfrastructureDocker, Docker Compose, GitHub Actions (CI/CD)🚀 Quick StartEnsure you have Docker Desktop and Python 3.11+ installed locally.1. Clone the RepositoryBashgit clone [https://github.com/your-username/Sentinel.git](https://github.com/your-username/Sentinel.git)
cd Sentinel
2. Spin Up Infrastructure (Docker Compose)Boots PostgreSQL, MLflow, and the FastAPI backend simultaneously with mapped volumes and timeout configurations:Bashdocker compose up -d --build
3. Seed the MLflow Model RegistryPacks and registers the pre-trained production artifact weights into the Dockerized registry:Bashpython ml/training/register_to_docker_mlflow.py
4. Run Drift Simulation & Self-Healing PipelineBash# Simulate adversarial text drift and write logs to PostgreSQL
python ml/training/simulate_traffic.py

# Detect distribution shift via Evidently AI
python ml/training/drift_detector.py

# Trigger the Prefect automated retrain and evaluation loop
python ml/training/retrain_pipeline.py
🔌 API UsageAccess the live interactive Swagger documentation at http://localhost:8000/docs.Analyze Endpoint (POST /api/v1/analyze)Bashcurl -X 'POST' \
  'http://localhost:8000/api/v1/analyze' \
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
📂 Repository StructurePlaintext├── .github/workflows/    # Automated CI/CD pipeline definitions
├── backend/              # FastAPI server, SQLAlchemy schemas, business logic
├── ml/
│   ├── data/             # Sourcing scripts, weak-label pipelines, test splits
│   └── training/         # DistilBERT training, Evidently configs, Prefect DAGs
├── docker-compose.yml    # Multi-container infrastructure orchestration
└── PROJECT_CONTEXT.md    # Comprehensive architectural design & decision log
```
