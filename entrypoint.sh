#!/bin/bash
# =============================================================================
# Entrypoint for Windrecorder Docker Container
# =============================================================================
set -e

echo "=========================================="
echo "  Windrecorder Docker Container Starting"
echo "=========================================="

# Create necessary directories if they don't exist
mkdir -p /app/userdata /app/db /app/cache /app/logs

# Set working directory
cd /app

# Start Streamlit web UI
echo "Starting Streamlit Web UI..."
echo "Access the web UI at: http://localhost:8501"

exec streamlit run webui.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.enableCORS false \
    --server.enableXsrfProtection false
