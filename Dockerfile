# Use Python 3.12 slim image
FROM python:3.12-slim-bookworm

# Configure environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies (curl for healthcheck/debugging if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv reference: https://github.com/astral-sh/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY pyproject.toml .

# Create virtual environment and install dependencies
# We use --system to install directly into the container's python environment
# or we can use the venv. Let's use the venv for cleaner separation
# but for simple docker containers, system install is often fine.
# Using uv verify to install into .venv
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN uv pip install .

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY api.py .
COPY main.py .

# Create empty file for report if needed or output directory
RUN touch incident_report.txt && chmod 666 incident_report.txt

# Expose port
EXPOSE 8000

# Run API by default
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
