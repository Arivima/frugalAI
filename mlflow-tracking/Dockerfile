FROM python:3.12.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tree \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install uv

COPY mlflow-tracking/pyproject.toml ./
RUN uv pip install --system --no-cache-dir ./

RUN useradd -m mlflowuser
USER mlflowuser

COPY --chown=mlflowuser:mlflowuser mlflow-tracking/ ./

EXPOSE 5000

# Required env variables
ENV BACKEND_STORE_URI=""
ENV ARTIFACT_ROOT=""

CMD mlflow server \
    --backend-store-uri $BACKEND_STORE_URI \
    --default-artifact-root $ARTIFACT_ROOT \
    --host 0.0.0.0 \
    --port 5000



