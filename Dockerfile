# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything including local models directly into the image


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]