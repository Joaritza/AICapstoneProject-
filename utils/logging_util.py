"""Logging utilities for Plant Based Assistant."""

import logging
from contextvars import ContextVar
from typing import Optional, Dict, Any

# Context variable for tracking request ID across async calls
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class ContextFilter(logging.Filter):
    """Logging filter to add context information to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add context variables to log record.

        Args:
            record: Log record

        Returns:
            True to allow the record to be logged
        """
        record.request_id = request_id_var.get() or "N/A"
        return True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with context filter applied.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    # Add context filter to all handlers
    for handler in logger.handlers:
        handler.addFilter(ContextFilter())
    return logger


def log_api_call(
    logger: logging.Logger,
    api_name: str,
    endpoint: str,
    method: str = "GET",
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    error: Optional[str] = None,
) -> None:
    """
    Log API call with structured information.

    Args:
        logger: Logger instance
        api_name: Name of API (e.g., 'USDA', 'Spoonacular')
        endpoint: API endpoint
        method: HTTP method
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        error: Error message if request failed
    """
    log_message = f"{api_name} {method} {endpoint}"

    if status_code:
        log_message += f" [{status_code}]"

    if duration_ms:
        log_message += f" ({duration_ms:.0f}ms)"

    if error:
        log_message += f" - Error: {error}"
        logger.warning(log_message)
    else:
        logger.debug(log_message)


def log_tool_execution(
    logger: logging.Logger,
    tool_name: str,
    inputs: Dict[str, Any],
    output: Any = None,
    error: Optional[str] = None,
) -> None:
    """
    Log tool execution with inputs and outputs.

    Args:
        logger: Logger instance
        tool_name: Name of the tool
        inputs: Tool input parameters
        output: Tool output (if successful)
        error: Error message if tool failed
    """
    if error:
        logger.warning(f"Tool '{tool_name}' failed: {error}")
    else:
        logger.debug(f"Tool '{tool_name}' executed with inputs: {inputs}")
