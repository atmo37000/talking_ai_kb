from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge

# Создаем отдельный registry для изоляции метрик
registry = CollectorRegistry()

# RAG metrics
RAG_REQUESTS_TOTAL = Counter(
    "rag_requests_total",
    "Total number of API requests",
    ["status", "endpoint", "method"],
    registry=registry,
)
RAG_REQUEST_DURATION_SECONDS = Histogram(
    "rag_request_duration_seconds",
    "Duration of API requests",
    ["endpoint", "method"],
    registry=registry,
)
RAG_DISK_FREE_BYTES = Gauge(
    "rag_disk_free_bytes",
    "Free disk space in bytes on upload storage volume",
    registry=registry,
)
