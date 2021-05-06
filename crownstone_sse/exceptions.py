"""Exceptions for Crownstone SSE client."""
from enum import Enum


class ConnectError(Enum):
    CONNECTION_FAILED_NO_INTERNET = "CONNECTION_FAILED_NO_INTERNET"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    CONNECTION_NO_RESPONSE = "CONNECTION_NO_RESPONSE"


class AuthError(Enum):
    AUTHENTICATION_ERROR = "WRONG_EMAIL_PASSWORD"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"


class ClientError(Enum):
    CLOSE_RECEIVED = "CLOSE_RECEIVED"


class CrownstoneClientException(Exception):
    type = None
    message = None

    def __init__(self, type, message=None):
        self.type = type
        self.message = message


class CrownstoneAuthException(Exception):
    type = None
    message = None

    def __init__(self, type, message=None):
        self.type = type
        self.message = message


class CrownstoneConnectionException(Exception):
    type = None
    message = None

    def __init__(self, type, message=None):
        self.type = type
        self.message = message
