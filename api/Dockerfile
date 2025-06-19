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

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8080"]








# Python won’t try to write .pyc files on the import of source modules.
# ENV PYTHONDONTWRITEBYTECODE=1
# Force the stdout and stderr streams to be unbuffered
# ENV PYTHONUNBUFFERED=1

# RUN useradd -m -u 1000 appuser
# RUN chown -R appuser:appuser /app
# USER appuser

# COPY ../shared/pyproject.toml ../shared/uv.lock ./shared/
# RUN pip install uv && \
#     cd shared && uv pip install -r uv.lock && cd ..

# COPY pyproject.toml uv.lock ./

# -r uv.lock 
#--no-dev --system


# ENV PYTHONPATH="/app:/app/shared"

# HEALTHCHECK CMD curl --fail http://localhost:8080/health || exit 1
