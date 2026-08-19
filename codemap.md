Stage 0: The Cold Start (Server Boot)
Where it happens: backend/app/main.py and backend/app/core/config.py

Before a user even sends a message, your FastAPI server wakes up. When you run uvicorn app.main:app, the @asynccontextmanager async def lifespan() function in main.py is triggered:

Database Check: SQLAlchemy uses backend/app/db/database.py to ping your Docker PostgreSQL container, making sure the PredictionLog table (defined in backend/app/models/models.py) exists and is ready to accept data.

MLflow Handshake: The backend reaches out to your local MLflow Tracking Server using the environment variables defined in backend/app/core/config.py (e.g., MLFLOW_TRACKING_URI).

Dynamic Model Loading: Instead of looking for local files, mlflow.transformers.load_model() fetches the models tagged as @production directly from the Registry and hot-loads them into the global models dictionary in main.py.

Stage 1: The Request Arrives (Validation)
Where it happens: backend/app/schemas.py

A user sends a POST request to the /api/v1/analyze endpoint.

Pydantic Intercept: The endpoint expects an AnalyzeRequest object. Before the Python logic inside the endpoint runs, Pydantic checks schemas.py. If the user sent an empty string, an integer instead of text, or a payload that breaks the schema rules, Pydantic instantly rejects it with a 422 Unprocessable Entity error.

Stage 2: The Traffic Cop (Language Routing)
Where it happens: backend/app/main.py (inside def analyze_text())

Now that the text is validated, Sentinel needs to figure out which model should read it.

The Heuristic Override: In main.py, the system splits the sentence into words and checks it against a hardcoded Python set of hinglish_hints (tu, aaj, bahar, etc.).

langdetect: The script also calls langdetect.detect(request.text).

The Decision: An if/else block checks both results. If the heuristic catches Hinglish keywords, OR if langdetect guesses it's a related language, it assigns selected_pipeline = models["hinglish"]. Otherwise, it defaults to models["english"].

Stage 3: The Brain (ML Inference)
Where it happens: backend/app/main.py (inside the ML Inference try/except block)

The text is handed to the chosen Hugging Face Pipeline.

Execution: main.py runs prediction = selected_pipeline(request.text).

Probability Extraction: The neural network calculates the math. Since the models were trained to return either SAFE, VIOLENT_THREAT, or NON_VIOLENT_ABUSE, the code extracts the raw float (e.g., Threat Probability: 0.12).

Stage 4: The Guardrails (The Risk Engine)
Where it happens: backend/app/ml/risk_engine.py

The raw probability is passed to the SentinelRiskEngine.calculate_risk() method.

Context Scanning: In risk_engine.py, regex methods like \_check_target() and \_check_immediacy() scan the text against keyword lists.

The Escalator: If a target or timeframe is found, the engine mathematically penalizes the score (e.g., multiplying the threat probability by 1.2 or 1.5).

The Safety Valve: However, an if base_probability < 0.45 check realizes when a low-probability sentence (like "Come to my house today") triggered the keywords by accident. It safely overrides the keywords, returning SAFE.

Final Decision: The engine maps the final calculated math to a human-readable bucket (SAFE, REVIEW, or HIGH RISK).

Stage 5: The Vault (Database Logging)
Where it happens: backend/app/main.py (Database Logging section)

Before responding to the user, Sentinel must maintain an audit trail.

SQLAlchemy Commit: Inside main.py, the code creates a new PredictionLog object (using the schema from models.py). It populates it with the original text, language, raw probability, final risk level, and explanation reason.

Saving: db.add(log_entry) and db.commit() write it permanently to your Dockerized PostgreSQL database. Next week, our Drift Detector (Evidently) will query this exact table.

Stage 6: The Output
Where it happens: backend/app/main.py and backend/app/schemas.py

Finally, the backend returns the risk_decision object. Because the FastAPI endpoint was defined with response_model=RiskDecision (imported from schemas.py), it automatically formats the Python object into a strictly typed JSON response and sends it back to the user with a 200 OK status.
