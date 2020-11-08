import aiohttp
import asynctest


class MockResponse:
    """Mock context manager aiohttp client session"""

    def __init__(self, status, json):
        self._json = json
        self.status = status

    async def json(self):
        return self._json

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


class MockStreamResponse:
    """Mock stream response"""

    def __init__(self, status):
        self.status = status
        self.content = aiohttp.StreamReader(
            protocol=asynctest.Mock(),
            limit=2**16
        )
