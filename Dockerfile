# Use Python 3.12 slim image
FROM python:3.12-slim-bookworm

# Configure environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
# Copy streamlit requirements
COPY streamlit/requirements.txt ./streamlit/requirements.txt

# Create venv and install dependencies
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install project dependencies
RUN uv pip install .
# Install streamlit dependencies explicitly
RUN uv pip install -r streamlit/requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY main.py .
COPY streamlit/ ./streamlit/

# Create reports directory
RUN mkdir -p reports

# Expose Streamlit port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "streamlit/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
