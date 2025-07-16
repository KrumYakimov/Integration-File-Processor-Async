import logging
from logging import Logger

from config.settings import LOG_DIR, LOG_TO_CONSOLE

LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)


def setup_logger(name: str, level: int, filename: str) -> Logger:
    """
    Create and configure a logger with file and optional console output.

    :param name: Name of the logger.
    :param level: Logging level (e.g., logging.INFO, logging.ERROR).
    :param filename: Name of the log file where logs will be saved.
    :return: Configured Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent double logging if root logger is configured

    file_handler = logging.FileHandler(LOG_DIR / filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if LOG_TO_CONSOLE:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


info_logger: Logger = setup_logger("info_logger", logging.INFO, "info.log")
error_logger: Logger = setup_logger("error_logger", logging.ERROR, "error.log")
