# syntax=docker/dockerfile:1.6
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8002

WORKDIR /app

COPY src/mcp_servers/marketing/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY src/common /app/src/common
COPY src/mcp_servers/__init__.py /app/src/mcp_servers/__init__.py
COPY src/mcp_servers/marketing /app/src/mcp_servers/marketing
COPY src/__init__.py /app/src/__init__.py

EXPOSE 8002

CMD ["python", "-m", "uvicorn", "src.mcp_servers.marketing.server:app", "--host", "0.0.0.0", "--port", "8002"]
