Markdown

<div align="center">

# 🛡️ Sentinel

**Production Real-Time AI Threat Detection & Self-Healing MLOps Platform**

[![Vercel](https://img.shields.io/badge/Frontend-Vercel-black?logo=vercel&logoColor=white)](https://vercel.com)
[![Hugging Face Spaces](https://img.shields.io/badge/Backend-HF%20Spaces-FFD21E?logo=huggingface&logoColor=black)](https://ankit03-sentinel-api.hf.space)
[![Render](https://img.shields.io/badge/Database-Render%20Postgres-46E3B7?logo=render&logoColor=black)](https://render.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Prefect](https://img.shields.io/badge/Prefect-024DFD?logo=prefect&logoColor=white)](https://www.prefect.io/)
[![Groq](https://img.shields.io/badge/LLM%20Teacher-Groq%20Llama%203.3-F55036)](https://groq.com)

[🌐 Live Dashboard (Vercel)](#) • [⚡ Live API Endpoint (HF Space)](https://ankit03-sentinel-api.hf.space) • [📦 Model Hub Weights](https://huggingface.co/Ankit03/sentinel-model-weights)

</div>

---

## 📖 Overview

**Sentinel** is an enterprise-grade AI moderation and threat defense system built to detect targeted violent threats, abusive language, and severe toxicity across both **English** and **Hinglish** (code-switched Hindi-English) text streams in real time.

Unlike static classification endpoints, Sentinel is engineered as an **autonomous, self-healing MLOps system**. It continuously monitors live inference traffic for covariate data drift, programmatically generates weak supervision labels using an **LLM Teacher (Groq Llama 3.3-70B)**, fine-tunes candidate models, validates them against production in an automated **Evaluation Arena (MLflow)**, and syncs winning model weights directly to the cloud without manual intervention.

---

## ☁️ Distributed Cloud Deployment Architecture

Sentinel is architected as a distributed, decoupled cloud-native ecosystem across specialized infrastructure providers:

| Component                | Platform                | Role & Architecture Details                                                                                                                                     |
| :----------------------- | :---------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend Dashboard**   | **Vercel**              | Next.js + TypeScript analytics UI displaying live threat distributions, classification latencies, and risk monitoring.                                          |
| **Backend API**          | **Hugging Face Spaces** | High-performance **FastAPI** service mounted seamlessly onto **Gradio** (`https://ankit03-sentinel-api.hf.space`) with automatic cloud fallback weight loaders. |
| **Database Vault**       | **Render**              | Managed persistent **PostgreSQL** instance capturing real-time prediction logs, inference scores, and input metadata for drift tracking.                        |
| **Model Registry & Hub** | **Hugging Face Hub**    | Remote artifact repository hosting fine-tuned transformer checkpoints (`Ankit03/sentinel-model-weights`) synced automatically by the MLOps pipeline.            |
| **LLM Teacher Layer**    | **Groq Cloud**          | High-throughput **Llama-3.3-70B-Versatile** inference engine executing zero-shot weak supervision and programmatic data labeling during retraining cycles.      |

---

## 🏗️ System Workflow & Data Flow

```mermaid
flowchart TD
    subgraph Online_Inference ["⚡ Online Inference Plane"]
        Client["🖥️ Client / Vercel Dashboard"] -->|POST /api/v1/analyze| API["🚀 FastAPI (HF Spaces + Gradio)"]
        API --> Router{"🔀 Language Router"}
        Router -->|English| DistilBERT_EN["🧠 English DistilBERT"]
        Router -->|Hinglish| DistilBERT_HI["🧠 Hinglish DistilBERT"]
        DistilBERT_EN --> RiskEngine["🛡️ Contextual Risk Engine\n(Probability × Immediacy × Target)"]
        DistilBERT_HI --> RiskEngine
        RiskEngine --> DB[("🗄️ PostgreSQL (Render)\nPrediction Logs")]
        RiskEngine -->|JSON Decision| Client
    end

    subgraph Offline_MLOps ["🔄 Autonomous Self-Healing Plane (Prefect + MLflow)"]
        DB -.->|Stream Logs via psycopg2| Drift["📈 Evidently AI\nDrift Detection"]
        Drift -->|Covariate Shift Detected| Prefect["⚙️ Prefect Orchestrator"]

        Prefect --> Task1["1️⃣ Ingest Unlabelled Mixed Logs"]
        Task1 --> Task2["2️⃣ Groq Llama-3.3 Weak Supervision\n(Auto-Labeling Teacher)"]
        Task2 --> Task3["3️⃣ Train Challenger Transformer"]
        Task3 --> Task4{"4️⃣ MLflow Evaluation Arena\nF1_Challenger >= F1_Champion?"}

        Task4 -->|Passed| Promote["🏆 Promote to @production\n& Sync to Hugging Face Hub"]
        Task4 -->|Failed| Reject["🛡️ Reject Challenger\n(Production Unchanged)"]
        Promote -->|Auto-Push Weights| HFHub[("📦 Ankit03/sentinel-model-weights")]
        HFHub -.->|Zero-Downtime Reload| API
    end
✨ Key Features & Technical Highlights
Multi-Language Transformer Pipeline: Fine-tuned DistilBERT architectures trained with class-weighted loss functions to resolve severe threat class imbalance (top ~4% positive distribution).

Defense-in-Depth Risk Engine: Combines probabilistic neural predictions with deterministic heuristic guardrails, evaluating temporal immediacy and entity targeting before categorizing inputs into SAFE, REVIEW, or HIGH RISK.

Gradio-Mounted FastAPI Core: Backend operates as a standard production ASGI FastAPI service mounted cleanly on Gradio for native Hugging Face Spaces compatibility.

Automated LLM Weak Supervision: Live user logs with detected vocabulary drift are auto-labeled via Groq's ultra-low-latency Llama-3.3-70B API, eliminating human labeling bottlenecks.

The Arena Evaluation Gate: Challenger models must strictly surpass the active MLflow @production Champion on a holdout benchmark F1-score to earn deployment.

Dynamic Cloud Versioning: Gated retrain victories automatically push binary artifacts into language-specific folders (/english_distilbert and /hinglish_distilbert) on the Hugging Face Model Hub.

🔌 API Reference
Analyze Text Risk
POST /api/v1/analyze

Request Payload:

JSON
{
  "text": "I will find where you live and destroy everything you own."
}
Response Payload:

JSON
{
  "text": "I will find where you live and destroy everything you own.",
  "language_detected": "english",
  "threat_probability": 0.9821,
  "risk_level": "HIGH_RISK",
  "immediacy": "HIGH",
  "target_identified": true,
  "reason": "High probability model classification escalated by explicit target and immediacy cues."
}
🛠️ Tech Stack Matrix
Machine Learning / NLP: PyTorch, Hugging Face Transformers (DistilBERT), Scikit-Learn, LangDetect

Backend & Serving: FastAPI, Pydantic V2, Uvicorn, Gradio

Databases & Storage: PostgreSQL (Render), SQLAlchemy ORM, psycopg2

MLOps & Orchestration: MLflow (Tracking & Registry), Prefect (v3.x DAGs), Evidently AI, Hugging Face Hub API (HfApi)

Teacher LLM: Groq SDK (llama-3.3-70b-versatile)

Frontend & Cloud Platforms: Next.js (Vercel), Hugging Face Spaces, Render

💻 Local Development & Setup
1. Clone & Setup Environment
Bash
git clone [https://github.com/Ankit03/sentinel.git](https://github.com/Ankit03/sentinel.git)
cd sentinel
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
2. Configure Environment Variables
Create a .env file in the root directory:

Code snippet
DATABASE_URL=postgresql://user:password@hostname:5432/sentinel
MLFLOW_TRACKING_URI=[http://127.0.0.1:5000](http://127.0.0.1:5000)
GROQ_API_KEY=gsk_your_groq_api_key
HF_TOKEN=hf_your_huggingface_access_token
3. Launch Local Backend & MLflow
Bash
# Terminal 1: Start MLflow Tracking Server
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow-artifacts --host 127.0.0.1 --port 5000

# Terminal 2: Start FastAPI Backend
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
4. Execute Self-Healing MLOps Retraining Loop
To manually extract multi-language production logs, run Groq weak supervision, and challenge the production model:

Bash
python ml/training/retrain_pipeline.py
👨‍💻 Author
Ankit Barik
```
