# build from parent folder : build context = project directory because of shared
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tree \
    && rm -rf /var/lib/apt/lists/*

COPY api/pyproject.toml ./api/
COPY shared/pyproject.toml ./shared/

RUN pip install uv
RUN uv pip install --system ./api
RUN uv pip install --system ./shared

COPY api/ ./api/
COPY shared/ ./shared/

ENV PYTHONPATH="/app:/app/shared:/app/api"
ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn api.app.main:app --host 0.0.0.0 --port $PORT"]
