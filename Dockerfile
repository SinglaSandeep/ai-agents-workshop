# syntax=docker/dockerfile:1.6
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --pre -r /app/requirements.txt

# Copy the source the chat app needs at runtime.
COPY src /app/src

EXPOSE 8000

# Container Apps sets PORT; uvicorn picks it up via the shell form.
CMD ["sh", "-c", "python -m uvicorn src.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
