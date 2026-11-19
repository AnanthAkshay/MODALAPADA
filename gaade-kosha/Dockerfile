# Multi-stage Dockerfile for Gaade Kosha (Problem 2, Modalapada 2.0)
# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.11-slim

# Install system dependencies (ffmpeg for audio conversion/verification)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend, precomputed data index, sqlite database, audio, and scripts
COPY backend/ ./backend/
COPY data/ ./data/
COPY audio/wav/ ./audio/wav/
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# Copy built frontend assets from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    EMBEDDING_BACKEND=tfidf \
    PORT=8000 \
    HOST=0.0.0.0

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI application serving both REST API and static frontend UI
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

