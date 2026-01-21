import logging
import sys
import os


def setup_logging():
    """
    Configura o logging centralizado da aplicação.

    Lê LOG_LEVEL do ambiente e configura formato estruturado.
    Reduz verbosidade de bibliotecas externas.

    Returns:
        logging.Logger: Logger principal da aplicação (impar-api).
    """
    log_level = os.getenv("LOG_LEVEL").upper()

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    app_logger = logging.getLogger("impar-api")
    app_logger.setLevel(getattr(logging, log_level, logging.INFO))

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langchain_core").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    app_logger.info(f"Logging configurado com nível: {log_level}")

    return app_logger


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger com prefixo da aplicação.

    Args:
        name: Nome do módulo (ex: 'chat_service').

    Returns:
        logging.Logger: Logger configurado como 'impar-api.{name}'.
    """
    logger = logging.getLogger(f"impar-api.{name}")
    logger.setLevel(logging.NOTSET)
    return logger

