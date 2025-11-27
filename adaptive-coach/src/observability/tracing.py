# src/observability/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

def init_tracing(service_name: str = "adaptive_coach"):
    """Initialize a simple console exporter for local tracing."""
    provider = TracerProvider()
    exporter = ConsoleSpanExporter()
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(service_name)
    return tracer

# Use like:
# tracer = init_tracing()
# with tracer.start_as_current_span("my-span"):
#     ... do instrumented work ...
