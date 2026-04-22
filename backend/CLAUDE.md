# Backend - Project Management MVP

This describes the backend for the Project Management MVP.

## Overview

The backend is a FastAPI application using Python, packaged with uv. It serves static files (frontend) at / and provides API endpoints under /api/.

## Structure

- **src/backend/main.py**: Main FastAPI app with routes for / (serves static/index.html) and /api/health.
- **static/**: Directory for static files, currently contains placeholder index.html.
- **pyproject.toml**: uv configuration with dependencies (FastAPI, uvicorn) and dev dependencies (pytest, httpx).

## Dependencies

- FastAPI: Web framework.
- uvicorn: ASGI server.
- pytest, httpx: For testing.

## Docker

- Dockerfile: Multi-stage build, installs uv, syncs dependencies, copies source and static files.
- Runs uvicorn on port 8000.

## API Endpoints

- GET /: Serves the main page (static/index.html).
- GET /api/health: Returns {"status": "ok", "message": "Backend is running"}.

## Testing

- Unit tests for routes in tests/ (to be added).
- Integration tests for API calls.
