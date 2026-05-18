# Dockerfile
# Reproducible research environment for the false-lv-chords project.
#
# Purpose:
#   - create a stable Python environment;
#   - install project dependencies with uv;
#   - run scripts, notebooks, tests, DVC stages, and MLflow commands inside a container;
#   - make the project easier to reproduce on another machine.
#
# Notes:
#   - Raw biomedical data are not copied into the image because .dockerignore excludes them.
#   - The image installs dependencies from pyproject.toml and uv.lock.
#   - The project itself is copied after dependency installation.
#   - Use docker-compose.yml for local research and MLflow UI.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH="/app/src"

WORKDIR /app

# System dependencies:
# - git: useful for DVC/MLflow metadata and repository inspection
# - curl/ca-certificates: basic network tooling
# - build-essential: fallback for packages that need compilation
# - bash: convenient interactive shell in the research container
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        build-essential \
        ca-certificates \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install uv from the official uv image.
COPY --from=ghcr.io/astral-sh/uv:0.11.12 /uv /uvx /usr/local/bin/

# Copy dependency files first to maximize Docker layer caching.
COPY pyproject.toml uv.lock .python-version README.md ./

# Install dependencies from uv.lock.
# --no-install-project is intentional for the early project stage:
# the src/false_chords package may still be under construction.
RUN uv sync --frozen --no-install-project --group dev

# Copy the rest of the repository.
# Sensitive and heavy files are excluded by .dockerignore.
COPY . .

# Create expected runtime directories if they do not exist.
RUN mkdir -p \
    data/raw \
    data/interim \
    data/processed \
    outputs/reports \
    outputs/tables \
    outputs/figures \
    outputs/diagnostics \
    models/baseline \
    models/elastic_net \
    models/sparse_pls \
    models/bayesian \
    mlruns

# Default command: open an interactive shell.
CMD ["bash"]
