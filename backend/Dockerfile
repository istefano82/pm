# Multi-stage build: Frontend build and Backend

# Stage 1: Frontend
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend
FROM python:3.12-slim
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy pyproject.toml and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy source
COPY src/ ./src/

# Copy static files from frontend stage
COPY --from=frontend /app/frontend/out ./static/

# Expose port
EXPOSE 8000

# Run the app
CMD ["uv", "run", "python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]