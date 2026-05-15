from prometheus_client import CollectorRegistry, Counter, Histogram

# Создаем отдельный registry для изоляции метрик
registry = CollectorRegistry()

# Counter: монотонно растущее значение (кол-во запросов)
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'],  # Labels для группировки
    registry=registry
)

# Histogram: распределение значений (время выполнения)
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

# Счетчики API вызовов
api_calls_total = Counter(
    'api_calls_total',
    'Total number of API calls by type',
    ['api_type'],
    registry=registry
)

# Отдельные счетчики для ошибок
http_errors_4xx_total = Counter(
    'http_errors_4xx_total',
    'Total number of 4xx HTTP errors',
    ['endpoint', 'status_code'],
    registry=registry
)

http_errors_5xx_total = Counter(
    'http_errors_5xx_total',
    'Total number of 5xx HTTP errors',
    ['endpoint', 'status_code'],
    registry=registry
)


