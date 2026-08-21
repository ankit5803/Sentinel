# Sentinel: Architecture Code Map & Interview Study Guide

## Part 1: Architecture Code Map (Chronological Flow)

### Stage 0: The Cold Start (Server Boot & MLflow Handshake)

_Where it happens: `backend/app/main.py` and `backend/app/core/config.py`_

- **Database Check:** SQLAlchemy uses `backend/app/db/database.py` to ping the PostgreSQL container and ensure the `PredictionLog` table (`backend/app/models/models.py`) exists.
- **MLflow Handshake:** The backend reaches out to the MLflow Tracking Server using environment settings from `backend/app/core/config.py`.
- **Dynamic Version Resolution:** Bypasses direct alias-fetching network bugs by using `MlflowClient.get_model_version_by_alias()` to programmatically resolve `@production` aliases to hard version numbers.
- **Resilient Artifact Streaming & Fallback:** `mlflow.transformers.load_model()` streams heavy model weights over HTTP (with extended Gunicorn timeouts in Docker). If network retrieval fails, it executes a seamless fail-safe fallback to local container artifacts. Models are hot-loaded into the global `models` dictionary in memory.

### Stage 1: Request Validation

_Where it happens: `backend/app/schemas.py`_

- **Pydantic Intercept:** The `/api/v1/analyze` endpoint expects an `AnalyzeRequest` payload. Pydantic validates input types, non-empty constraints, and length limits, automatically returning `422 Unprocessable Entity` on invalid requests before compute resources are spent.

### Stage 2: Language Routing

_Where it happens: `backend/app/main.py` (`analyze_text` function)_

- **Heuristic Override:** Fast set-intersection checks against common Romanized Hindi/Hinglish structural tokens.
- **Statistical Detection:** `langdetect.detect()` evaluates ambiguous strings.
- **Router Decision:** Dispatches request to either the English or Hinglish pipeline in `models`.

### Stage 3: Neural Inference

_Where it happens: `backend/app/main.py` (Inference block)_

- **Pipeline Execution:** Runs `selected_pipeline(request.text, truncation=True, max_length=128)`.
- **Probability Normalization:** Normalizes positive class probabilities (`VIOLENT_THREAT` / `NON_VIOLENT_ABUSE`) into a unified float score (0.0 to 1.0).

### Stage 4: Contextual Guardrails (Risk Engine)

_Where it happens: `backend/app/ml/risk_engine.py`_

- **Context Extraction:** Regex scanners evaluate target specificity and temporal immediacy.
- **Dynamic Escalation:** Mathematical multipliers boost the threat probability based on context cues.
- **Safety Floor Override:** Suppresses false positives by overriding context multipliers when the raw base probability is below the critical threshold (< 0.45).
- **Decision Categorization:** Formats risk into categorical tiers (`SAFE`, `REVIEW`, `HIGH RISK`).

### Stage 5: Data Persistence (The Vault)

_Where it happens: `backend/app/main.py` and `backend/app/models/models.py`_

- **Audit Logging:** Maps inputs, raw probabilities, decisions, and explanation metadata into a SQLAlchemy `PredictionLog` record.
- **Transaction Commit:** Flushes the record to PostgreSQL to maintain the baseline comparison dataset for downstream drift analysis.

### Stage 6: Response Serialization

_Where it happens: `backend/app/main.py` and `backend/app/schemas.py`_

- **Response Contract:** Formats the computed output into a strictly validated `RiskDecision` schema and returns HTTP 200 OK.

### Stage 7: Production Monitoring (Data Drift Detection)

_Where it happens: `ml/training/drift_detector.py` and `simulate_traffic.py`_

- **Direct Data Extraction:** Bypasses the API layer entirely, using a SQLAlchemy + `psycopg2` engine to stream production text logs directly from PostgreSQL into a Pandas DataFrame.
- **Distribution Comparison:** Evidently AI computes statistical distance between the baseline training vocabulary (2019 data) and live traffic (modern evasive slang).
- **Trigger:** If dataset drift thresholds are breached, it flags the system for automated retraining.

### Stage 8: Automated Orchestration (The Self-Healing Loop)

_Where it happens: `ml/training/retrain_pipeline.py`_

- **Prefect DAGs:** Defines a Directed Acyclic Graph (`@flow`) breaking the recovery process into isolated, retryable `@task` blocks.
- **Pipeline Execution:** 1) Extracts newly drifted data. 2) Triggers a GPU fine-tuning job to build a new Challenger model. 3) Hands the Challenger over to the Evaluation Gate.

### Stage 9: The Automated Evaluation Gate (The Arena)

_Where it happens: `ml/training/eval_gate.py` (Triggered by Stage 8)_

- **Champion Loading:** Downloads the active `@production` artifact from MLflow.
- **Challenger Ingestion:** Loads candidate retraining artifacts.
- **Holdout Benchmarking:** Executes batched inference across the holdout test set on GPU.
- **Gated Promotion Logic:** Computes target-class F1 scores. Automatically blocks deployment unless the candidate strictly exceeds the champion's score (`F1_challenger > F1_champion`).

---

## Part 2: Interview Mastery Checklist

### 1. Backend, Systems & Concurrency

- [x] **FastAPI Lifespan Context Manager (`@asynccontextmanager`):** Why `lifespan` replaces deprecated startup/shutdown event handlers to manage state (loading heavy ML models into memory once, cleaning up VRAM on teardown).
- [ ] **Asynchronous vs. Synchronous Execution:** The difference between `async def` and regular `def` in FastAPI. Why ML model inference (CPU/GPU-bound) and synchronous database drivers run inside standard `def` threadpools to avoid blocking the ASGI event loop.
- [x] **Pydantic V2 & Data Serialization:** Request parsing, type coercion, field constraints, schema validation, and how Pydantic protects endpoints from malformed payloads.
- [x] **Database Connection Pooling & ORM:** How SQLAlchemy engine pools connections (`pool_size`, `max_overflow`), how sessions manage transactions (`db.add()`, `db.commit()`), and why `get_db` uses a generator with `yield`.
- [x] **Environment Configuration Management:** Decoupling code from deployment environments using `pydantic-settings` (`BaseSettings`) and 12-Factor App design principles.
- [x] **Direct vs. Indirect Data Ingestion:** Why analytics and drift scripts use `psycopg2`/`pd.read_sql` for binary streams directly from PostgreSQL instead of making slow, memory-heavy HTTP GET requests to the FastAPI layer.

### 2. Machine Learning, NLP & Hardware

- [x] **DistilBERT Architecture & Transformer Trade-offs:** Knowledge distillation (60% smaller, 40% faster than BERT-base while retaining 97% language understanding). Attention mechanisms, tokenization subwords, truncation, and padding.
- [x] **Handling Severe Class Imbalance:** Why standard Cross-Entropy Loss fails on rare positive distributions (4-5% threat rates) and how class-weighted loss functions prevent majority-class collapse.
- [x] **Evaluation Metrics Selection:** Precision (minimizing false alarms) vs. Recall (catching every real threat) vs. F1-score (harmonic mean) on skewed distributions. Macro vs. Micro vs. Weighted F1.
- [x] **Memory-Constrained GPU Optimization:** How Mixed Precision Training (`fp16`), gradient accumulation, and small batch sizes allow transformer fine-tuning on limited VRAM (4GB).
- [x] **Weak Supervision & Lexicon Bootstrapping:** Programmatic dataset labeling using heuristic rules/lexicons and human-in-the-loop manual spot-checking to validate label quality.

### 3. MLOps, Model Governance & Lifecycle

- [x] **MLflow Tracking vs. MLflow Model Registry:** Tracking runs (hyperparameters, metrics, run artifacts) vs. Centralized Model Storage (versioning, lifecycle stages, metadata, dependencies).
- [x] **MLflow Model Aliases (`@production` vs `@challenger`):** Decoupling backend code from hardcoded storage paths. Dynamic loading via `models:/<name>@<alias>`.
- [x] **Silent AI Failures & Data Drift (Evidently AI):** How models fail silently when the real world changes (e.g., 2026 adversarial slang vs 2019 training data). Detecting covariate shift (input distribution changes) and target shift over time.
- [x] **Workflow Orchestration (Prefect):** Moving from monolithic Python scripts to Directed Acyclic Graphs (DAGs). The architectural difference between `@task` and `@flow`, managing state, automatic retries on failure, and decoupled execution.
- [x] **Evaluation Gating (The Arena Pattern):** Preventing regressions by enforcing automated programmatic thresholds before candidate artifacts can receive production routing tags.

### 4. Systems Architecture & Security Design

- [x] **Defense-in-Depth AI Architecture:** Why raw transformer output should not drive critical business decisions alone; using deterministic guardrails (Risk Engine) alongside probabilistic neural networks.
- [x] **Fail-Safe Defaults:** Designing graceful fallbacks when components fail (e.g., graceful fallback to local container artifacts if MLflow artifact streaming encounters timeouts/network drops).
- [x] **Docker Containerization & Networking:** Container isolation, absolute path SQLite volume mapping (`sqlite:////mlflow/mlflow.db`), port mapping (`5432:5432`, `8000:8000`), network bridges, and volume persistence.

---

## Part 3: The MLOps Developer's Stack Guide

_(Libraries, frameworks, and tools used to build Sentinel)_

### 1. Languages & Core Runtime

- **Python 3.11 / 3.12:** Type hints, generator functions (`yield`), context managers, virtual environments (`venv`), and package dependency resolution.
- **CUDA & cuDNN (NVIDIA):** Managing GPU acceleration, device memory allocation (`.to("cuda")`), VRAM cache management, and OOM debugging.

### 2. Machine Learning, NLP & Data Engineering

- **`torch` (PyTorch):** Core tensor math, `CrossEntropyLoss` for class imbalance, and mixed-precision training (`fp16`).
- **`transformers` & `datasets` (Hugging Face):** `distilbert` architectures, `AutoTokenizer`, `pipeline`, subword tokenization (WordPiece), truncation, dynamic padding, and attention masks.
- **`scikit-learn`:** `TfidfVectorizer`, `LogisticRegression`, evaluation metrics (`f1_score`, `precision_score`, `recall_score`, `classification_report`), and class weight computation.
- **`pandas` & `numpy`:** Tabular ETL, dataframe filtering, transformations, and reservoir sampling.
- **`langdetect` & `re` (Regex):** Statistical n-gram language classification and heuristic guardrail rule matching.

### 3. Backend, API & Data Validation

- **`fastapi`:** Async REST APIs, `@asynccontextmanager` lifecycles, route definitions, and Dependency Injection (`Depends(get_db)`).
- **`uvicorn`:** ASGI web server, reload flags, and worker processes.
- **`pydantic` & `pydantic-settings`:** Strict data contracts (`BaseModel`), input validation, environment configuration (12-Factor App), and automatic JSON serialization.
- **`requests` / `httpx`:** Client-side HTTP simulation and integration testing.

### 4. Database & Persistence Layer

- **PostgreSQL:** Relational database design, schemas, and primary keys.
- **`SQLAlchemy`:** Python ORM, connection pools (`create_engine`), Base mapping (`DeclarativeBase`), and transaction sessions (`db.add`, `db.commit`).
- **`psycopg2-binary`:** Low-level C-based PostgreSQL DB-API driver for high-speed dataframe streaming.

### 5. MLOps, Governance & Automation

- **`mlflow`:** Experiment tracking, flavor logging (`mlflow.transformers`), Model Registry, artifact proxying (`--serve-artifacts`), and dynamic version resolution.
- **`evidently` (v0.6.x):** Statistical drift detection (`Report`, `DataDriftPreset`), computing divergence between reference and live data, and HTML dashboard generation.
- **`prefect` (v3.x):** Self-healing automation DAGs (`@task`, `@flow`), task state tracking, automatic retries, and local orchestration servers.

### 6. Infrastructure, DevOps & Deployment

- **Docker & Docker Compose:** `Dockerfile` creation (layer caching, non-root users), multi-service coordination, absolute-path volume mounting (`sentinel_mlflow_data`), network bridges, and Gunicorn timeout tuning (`--timeout 120`).
- **Git & GitHub Actions:** Version control, `.gitignore` for large files, and CI/CD yaml pipelines.
- **Cloud PaaS (Render / Railway):** Configuring environment secrets, provisioning hosted databases, and container deployment.

### 7. System Architecture Patterns

| Pattern                    | How it is used in Sentinel                                                                                     |
| :------------------------- | :------------------------------------------------------------------------------------------------------------- |
| **Defense-in-Depth AI**    | Probabilistic neural nets (DistilBERT) + deterministic heuristics (Risk Engine).                               |
| **The Arena / Eval Gate**  | A challenger model cannot replace the production champion unless it programmatically outperforms it.           |
| **Separation of Concerns** | Decoupling routing, validation, config, persistence, business logic, and orchestration.                        |
| **Fail-Safe Defaults**     | Graceful fallback to local container artifacts if MLflow network requests drop or crash.                       |
| **Dynamic Model Aliasing** | Decoupling code from physical file paths; resolving `@production` dynamically permits zero-downtime hot-swaps. |
