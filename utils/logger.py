"""Logging configuration for the forex agent system."""

import logging
import sys
from typing import Optional

# Global log level configuration
LOG_LEVEL = logging.INFO

# Format with timestamp, level, filename, line number, and message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the module)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set log level
    logger.setLevel(level or LOG_LEVEL)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level or LOG_LEVEL)

        # Formatter
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    return logger


def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Log a function call with parameters.

    Args:
        logger: Logger instance
        func_name: Name of the function
        **kwargs: Function parameters to log
    """
    params = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"→ {func_name}({params})")


def log_function_return(logger: logging.Logger, func_name: str, result: any = None):
    """
    Log a function return.

    Args:
        logger: Logger instance
        func_name: Name of the function
        result: Return value summary
    """
    if result is not None:
        logger.info(f"← {func_name} returned: {result}")
    else:
        logger.info(f"← {func_name} completed")


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Log an error with context.

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context about where the error occurred
    """
    if context:
        logger.error(f"❌ Error in {context}: {type(error).__name__}: {str(error)}", exc_info=True)
    else:
        logger.error(f"❌ Error: {type(error).__name__}: {str(error)}", exc_info=True)
