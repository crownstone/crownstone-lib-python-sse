"""Exceptions for Crownstone SSE client"""
from enum import Enum


class ConnectError(Enum):
    CONNECTION_FAILED_AFTER_5_RETRIES = 'CONNECTION_FAILED_AFTER_5_RETRIES'


class CrownstoneSseException(Exception):
    type = None
    message = None

    def __init__(self, type, message=None):
        self.type = type
        self.message = message
