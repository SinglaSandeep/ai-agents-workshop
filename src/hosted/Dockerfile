# syntax=docker/dockerfile:1.6
# Zava Inventory **hosted** agent — runs the Agent Framework agent behind
# `agent_framework_foundry_hosting.ResponsesHostServer` (Responses API).
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# Install dependencies first to leverage Docker layer caching. `--pre` is
# required because agent-framework-foundry-hosting ships only pre-releases.
COPY src/hosted/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --pre -r /app/requirements.txt

# Copy only what the hosted Inventory agent needs.
COPY src/__init__.py /app/src/__init__.py
COPY src/common /app/src/common
COPY src/prompts /app/src/prompts
COPY src/hosted /app/src/hosted

EXPOSE 8080

# Foundry/azd inject PORT; ResponsesHostServer binds to it automatically.
CMD ["python", "-m", "src.hosted.inventory_hosted"]
