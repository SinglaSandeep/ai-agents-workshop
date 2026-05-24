"""Optional OpenTelemetry / Application Insights wiring.

Safe to import without the `observability` extra installed — every helper
falls back to a no-op when dependencies or the connection string are missing.
"""

from __future__ import annotations

from contextlib import contextmanager, nullcontext
from typing import Any

from .settings import get_settings


def configure_observability(app: Any | None = None) -> bool:
    """Configure Azure Monitor exporter and (optionally) instrument FastAPI."""
    settings = get_settings()
    if not settings.applicationinsights_connection_string:
        return False

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
    except ImportError:
        return False

    configure_azure_monitor(
        connection_string=settings.applicationinsights_connection_string,
        resource_attributes={"service.name": settings.otel_service_name},
    )

    if app is not None:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
        except ImportError:
            pass

    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        HTTPXClientInstrumentor().instrument()
    except ImportError:
        pass

    return True


@contextmanager
def trace_span(name: str, **attributes: Any):
    try:
        from opentelemetry import trace
    except ImportError:
        with nullcontext():
            yield None
        return

    tracer = trace.get_tracer("zava-ai-agents-workshop")
    with tracer.start_as_current_span(name) as span:
        for key, value in attributes.items():
            if value is not None:
                span.set_attribute(key, str(value))
        yield span
