"""Exceptions for Crownstone SSE client."""
from __future__ import annotations

from enum import Enum


class ConnectError(Enum):
    """Connection errors for Crownstone SSE."""

    CONNECTION_FAILED_NO_INTERNET = "CONNECTION_FAILED_NO_INTERNET"
    CONNECTION_NO_RESPONSE = "CONNECTION_NO_RESPONSE"
    CONNECTION_TO_CLOUD_LOST = "CONNECTION_TO_CLOUD_LOST"


class AuthError(Enum):
    """Authentication errors for Crownstone SSE."""

    AUTHENTICATION_ERROR = "WRONG_EMAIL_PASSWORD"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "INVALID_ACCESS_TOKEN"


class ClientError(Enum):
    """Client errors for Crownstone SSE."""

    CLOSE_RECEIVED = "CLOSE_RECEIVED"


class CrownstoneClientException(Exception):
    """Client exception for Crownstone SSE."""

    def __init__(self, exc_type: ClientError, message: str | None = None):
        """Initialize exception."""
        super().__init__(exc_type, message)
        self.type = exc_type
        self.message = message


class CrownstoneAuthException(Exception):
    """Authentication exception for Crownstone SSE."""

    def __init__(self, exc_type: AuthError, message: str | None = None):
        """Initialize exception."""
        super().__init__(exc_type, message)
        self.type = exc_type
        self.message = message


class CrownstoneConnectionException(Exception):
    """Connection exception for Crownstone SSE."""

    def __init__(self, exc_type: ConnectError, message: str | None = None):
        """Initialize exception."""
        super().__init__(exc_type, message)
        self.type = exc_type
        self.message = message
