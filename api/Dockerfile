# build from parent folder : build context = project directory because of shared
FROM python:3.11-slim

WORKDIR /app

COPY api/pyproject.toml ./api/
COPY shared/pyproject.toml ./shared/

RUN pip install --no-cache-dir uv
RUN uv pip install --system ./api ./shared

COPY api/ ./api/
COPY shared/ ./shared/

ENV PYTHONPATH="/app:/app/shared:/app/api"
ENV PYTHONUNBUFFERED=1

# Required env variables 
ENV GCP_PROJECT_ID=""
ENV GCS_BUCKET_NAME=""
ENV ADAPTER_NAME=""
ENV LOCAL_DIRECTORY=""
ENV MODEL_NAME=""
ENV BQ_DATASET_ID=""
ENV BQ_TABLE_ID=""
        
CMD ["sh", "-c", "uvicorn api.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
