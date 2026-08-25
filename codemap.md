# Sentinel: Architecture Code Map & Interview Study Guide

## Part 1: Architecture Code Map (Chronological Flow)

### Stage 0: The Cold Start (Server Boot & MLflow Handshake)

- **Database Check:** SQLAlchemy uses `backend/app/db/database.py` to ping the PostgreSQL container and ensure the `PredictionLog` table exists.
- **MLflow Handshake:** The backend reaches out to the MLflow Tracking Server using environment settings.
- **Dynamic Version Resolution:** Uses `result.version` on registration and `set_registered_model_alias()` to manage `@production` aliases.
- **Resilient Artifact Streaming & Fallback:** `mlflow.transformers.load_model()` streams heavy model weights. If network retrieval fails, it executes a seamless fail-safe fallback to local container artifacts.

### Stage 1: Request Validation

- **Pydantic Intercept:** The `/api/v1/analyze` endpoint expects an `AnalyzeRequest` payload and validates constraints, returning `422 Unprocessable Entity` on invalid requests.

### Stage 2: Language Routing

- **Heuristic Override:** Fast set-intersection checks against common Romanized Hindi/Hinglish structural tokens.
- **Statistical Detection:** `langdetect.detect()` evaluates ambiguous strings.
- **Router Decision:** Dispatches request to either the English or Hinglish pipeline in `models`.

### Stage 3: Neural Inference

- **Pipeline Execution:** Runs `selected_pipeline(request.text, truncation=True, max_length=128)`.
- **Probability Normalization:** Normalizes positive class probabilities (`VIOLENT_THREAT` / `NON_VIOLENT_ABUSE`) into a unified float score (0.0 to 1.0).

### Stage 4: Contextual Guardrails (Risk Engine)

- **Context Extraction:** Regex scanners evaluate target specificity and temporal immediacy.
- **Dynamic Escalation:** Mathematical multipliers boost the threat probability based on context cues.
- **Safety Floor Override:** Suppresses false positives when raw base probability is below critical threshold (< 0.45).
- **Decision Categorization:** Formats risk into categorical tiers (`SAFE`, `REVIEW`, `HIGH RISK`).

### Stage 5: Data Persistence (The Vault)

- **Audit Logging:** Maps inputs, raw probabilities, decisions, and explanation metadata into a SQLAlchemy `PredictionLog` record.
- **Transaction Commit:** Flushes the record to PostgreSQL to maintain the baseline comparison dataset.

### Stage 6: Response Serialization

- **Response Contract:** Formats the computed output into a strictly validated `RiskDecision` schema and returns HTTP 200 OK.

### Stage 7: Production Monitoring (Data Drift Detection)

- **Direct Data Extraction:** Streams production text logs directly from PostgreSQL into a Pandas DataFrame.
- **Distribution Comparison:** Evidently AI computes statistical distance between baseline and live traffic.
- **Trigger:** If dataset drift thresholds are breached, it flags the system for automated retraining.

### Stage 8: Automated Orchestration & Multi-Language Weak Supervision

- **Prefect DAGs:** Defines a Directed Acyclic Graph (`@flow`) breaking recovery into isolated `@task` blocks.
- **Live Ingestion & Dynamic Grouping:** Pulls unlabelled multi-language rows from PostgreSQL and segments them by `language_detected`.
- **Teacher LLM Auto-Labeling:** Routes raw traffic through **Groq (Llama 3.3-70b-versatile)** using tailored prompt contexts to assign weak labels.

### Stage 9: The Automated Evaluation Gate & Hugging Face Sync

- **Champion Loading:** Downloads active `@production` artifact from MLflow (or defaults to `0.0` for bootstrapping).
- **Holdout Benchmarking:** Executes batched inference across language-specific test splits on GPU.
- **Gated Promotion Logic:** Computes F1 scores. Automatically blocks deployment unless candidate exceeds champion (`F1_challenger >= F1_champion`).
- **Cloud Weight Synchronization:** Upon victory, registers version, sets `@production` alias, and uses `huggingface_hub` (`HfApi.upload_folder`) to stream winning artifacts into language-specific repositories (`Ankit03/sentinel-model-weights/english_distilbert` and `hinglish_distilbert`).

---

## Part 2: Interview Mastery Checklist

### 1. Backend, Systems & Concurrency

- [x] **FastAPI Lifespan Context Manager (`@asynccontextmanager`):** Replaces deprecated startup/shutdown event handlers.
- [x] **Asynchronous vs. Synchronous Execution:** Why CPU/GPU-bound ML inference runs inside threadpools to avoid blocking ASGI.
- [x] **Pydantic V2 & Data Serialization:** Request parsing, type coercion, and schema validation.
- [x] **Database Connection Pooling & ORM:** SQLAlchemy engine pools, transaction sessions, and generator dependency injection.
- [x] **Environment Configuration Management:** Decoupling code using `pydantic-settings` and 12-Factor principles.
- [x] **Direct vs. Indirect Data Ingestion:** Using `psycopg2`/`pd.read_sql` for high-speed dataframe streaming directly from PostgreSQL.

### 2. Machine Learning, NLP & Hardware

- [x] **DistilBERT Architecture & Transformer Trade-offs:** Knowledge distillation (60% smaller, 40% faster while retaining 97% accuracy).
- [x] **Handling Severe Class Imbalance:** Weighted loss functions preventing majority-class collapse on rare threats.
- [x] **Evaluation Metrics Selection:** Precision vs. Recall vs. F1-score on skewed distributions.
- [x] **Memory-Constrained GPU Optimization:** Mixed precision (`fp16`) and small batch sizes for 4GB VRAM (RTX 3050).
- [x] **Weak Supervision & LLM Teacher Bootstrapping:** Programmatic labeling using live API-based LLMs (Groq Llama 3.3).

### 3. MLOps, Model Governance & Lifecycle

- [x] **MLflow Tracking vs. Model Registry:** Tracking runs vs. centralized model versioning and lifecycle stages.
- [x] **Model Aliases (`@production`) & Dynamic Versioning:** Decoupling code from storage paths via alias resolution.
- [x] **Silent AI Failures & Data Drift (Evidently AI):** Detecting covariate and target shift over time.
- [x] **Workflow Orchestration (Prefect):** DAGs, task state tracking, and automatic retries.
- [x] **Evaluation Gating (The Arena Pattern):** Enforcing programmatic F1 thresholds before promotion.

### 4. Systems Architecture & Security Design

- [x] **Defense-in-Depth AI Architecture:** Combining probabilistic neural nets with deterministic heuristics (Risk Engine).
- [x] **Fail-Safe Defaults:** Graceful fallbacks for network drops, timeouts, and cold-start baselines.
- [x] **Cloud-Native Deployment:** Public FastAPI hosting on Hugging Face Spaces paired with Render PostgreSQL.

---

## Part 3: Progress Log

- [progress] — Days 1-13 complete: Data pipelines, baselines, fine-tuning, FastAPI backend, Postgres vault, MLflow Model Registry, Evidently drift detection, Prefect orchestration.
- [progress] — Day 14 complete: Executed end-to-end local test, absolute-path SQLite mapping, and automated retraining loop.
- [progress] — Day 15 complete: Deployed FastAPI backend live on Hugging Face Spaces (`https://ankit03-sentinel-api.hf.space`) with Render PostgreSQL.
- [progress] — Days 16-17 (COMPLETED): Fully executed multi-language self-healing pipeline testing locally with Groq Llama 3.3 auto-labeling, MLflow evaluation arena validation, dynamic aliasing (`@production`), and automated Hugging Face weight synchronization (`Ankit03/sentinel-model-weights`).
  dsavhsavd hjsda bjdnsmnsdaj
