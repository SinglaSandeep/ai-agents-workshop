# syntax=docker/dockerfile:1.6
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8001

WORKDIR /app

# Install dependencies first to leverage Docker layer caching
COPY src/mcp_servers/products/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy only what the Products server needs
COPY src/common /app/src/common
COPY src/mcp_servers/__init__.py /app/src/mcp_servers/__init__.py
COPY src/mcp_servers/products /app/src/mcp_servers/products
COPY src/__init__.py /app/src/__init__.py

EXPOSE 8001

# Container Apps will set PORT; uvicorn picks it up via the module entry point.
CMD ["python", "-m", "uvicorn", "src.mcp_servers.products.server:app", "--host", "0.0.0.0", "--port", "8001"]
