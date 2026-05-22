from __future__ import annotations

import os
from contextlib import contextmanager, nullcontext
from typing import Any


def configure_observability(app: Any | None = None) -> bool:
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        return False

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
    except ImportError:
        return False

    configure_azure_monitor(connection_string=connection_string)

    if app is not None:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
        except ImportError:
            pass

    return True


@contextmanager
def trace_span(name: str, **attributes: str):
    try:
        from opentelemetry import trace
    except ImportError:
        with nullcontext():
            yield None
        return

    tracer = trace.get_tracer("ai-agents-workshop")
    with tracer.start_as_current_span(name) as span:
        for key, value in attributes.items():
            span.set_attribute(key, value)
        yield span
