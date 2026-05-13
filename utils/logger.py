
from config import config


def get_logger():
    import structlog

    log_level = config.log_level
    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer(ensure_ascii=False)
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )

    return  structlog.get_logger()
