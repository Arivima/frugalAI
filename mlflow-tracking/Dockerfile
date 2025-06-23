FROM python:3.12.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tree \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app && \
    useradd --create-home --shell /bin/bash mlflowuser && \
    chown -R mlflowuser:mlflowuser /app

WORKDIR /app

RUN pip install uv
COPY mlflow-tracking/pyproject.toml ./
RUN uv pip install --system --no-cache-dir ./

COPY --chown=mlflowuser:mlflowuser mlflow-tracking/ ./

USER mlflowuser

# Required env variables 
ENV BACKEND_STORE_URI=""
ENV ARTIFACT_ROOT=""

# need to use shell form for the exec to work
CMD ["sh", "-c", "mlflow server --backend-store-uri \"$BACKEND_STORE_URI\" --default-artifact-root \"$ARTIFACT_ROOT\" --host 0.0.0.0 --port \"$PORT\""]
