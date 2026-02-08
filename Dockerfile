# =============================================================================
# Dockerfile for Windrecorder - Streamlit Web UI
# =============================================================================
FROM python:3.11-slim

LABEL author="Windrecorder Team"
LABEL description="Windrecorder Streamlit Web UI for memory search engine"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PYTHONIOENCODING=utf-8

# Copy requirements file first and install dependencies
COPY requirements_docker.txt ./
RUN pip install --no-cache-dir -r requirements_docker.txt

# Copy application source
COPY . /app/

# Create necessary directories and set permissions
RUN mkdir -p /app/userdata /app/db /app/cache /app/logs && \
    chmod -R 755 /app

# Copy and install entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the Streamlit port
EXPOSE 8501

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
