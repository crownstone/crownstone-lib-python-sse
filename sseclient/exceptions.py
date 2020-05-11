"""Exceptions for Crownstone SSE client"""
import logging
from enum import Enum
from typing import Any, Dict

_LOGGER = logging.getLogger(__name__)


class ConnectError(Enum):
    CONNECTION_FAILED_NO_INTERNET = 'CONNECTION_FAILED_NO_INTERNET'


class CrownstoneSseException(Exception):
    type = None
    message = None

    def __init__(self, type, message=None):
        self.type = type
        self.message = message


def sse_exception_handler(_: Any, context: Dict) -> None:
    """Handle all exceptions inside the client."""
    kwargs = {}
    exception = context.get("exception")
    if exception:
        kwargs["exc_info"] = (type(exception), exception, exception.__traceback__)

    _LOGGER.error(
        "Error doing job: %s", context["message"], **kwargs
    )
