# build from parent folder : build context = project directory because of shared
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tree \
    && rm -rf /var/lib/apt/lists/*

COPY front/pyproject.toml ./front/
COPY shared/pyproject.toml ./shared/

RUN pip install uv
RUN uv pip install --system ./front
RUN uv pip install --system ./shared

COPY front/ ./front/
COPY shared/ ./shared/

ENV PYTHONPATH="/app:/app/shared:/app/front"

EXPOSE 8502

CMD ["uv", "run", "python", "-m", "streamlit", "run", "front/app/home.py", "--server.port=8502"]








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
