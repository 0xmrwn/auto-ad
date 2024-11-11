import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logger(
    log_file: Optional[Path] = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> None:
    """
    Setup application logging with both console and file handlers.

    Args:
        log_file: Path to log file. Defaults to logs/app.log
        console_level: Logging level for console output
        file_level: Logging level for file output
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatters
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler
    if log_file is None:
        log_file = Path("logs") / "app.log"

    # Ensure log directory exists
    log_file.parent.mkdir(exist_ok=True)

    # Setup rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"  # 1MB
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Log startup message
    logger.debug("Logging system initialized")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name for the logger, typically __name__

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""

    @property
    def logger(self) -> logging.Logger:
        """Get a logger instance for the class"""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
