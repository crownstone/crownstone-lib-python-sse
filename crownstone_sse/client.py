"""
Thread wrapper for CrownstoneSSEAsync.
Events are fired in an event bus.

This can be used in synchronous context.
"""
from __future__ import annotations

import asyncio
import threading
from typing import Any, Awaitable, Callable

from crownstone_sse.async_client import CrownstoneSSEAsync
from crownstone_sse.const import RECONNECTION_TIME
from crownstone_sse.util.eventbus import EventBus


class CrownstoneSSE(threading.Thread):
    """Crownstone threaded event client."""

    _client: CrownstoneSSEAsync

    def __init__(
        self,
        email: str,
        password: str,
        access_token: str | None = None,
        reconnection_time: int = RECONNECTION_TIME,
        project_name: str | None = None,
    ) -> None:
        """
        Initialize event client.

        :param email: Crownstone account email address.
            Used for login and automatic access token renewal.
        :param password: Crownstone account password.
            Used for login and automatic access token renewal.
        :param access_token: Access token obtained from logging in successfully
            to the Crownstone cloud. Can be provided to skip an extra login, for faster setup.
        :param reconnection_time: Time between reconnection in case of connection failure.
        """
        self._email = email
        self._password = password
        self._access_token = access_token
        self._reconnection_time = reconnection_time
        self._project_name = project_name
        self._bus = EventBus()

        super().__init__(target=self._start_client)
        self.start()

    def _start_client(self) -> None:
        """Start the SSE client."""
        asyncio.run(self._process_events())

    async def _process_events(self) -> None:
        """Get events from the server, and fire them in the event bus."""
        self._client = CrownstoneSSEAsync(
            email=self._email,
            password=self._password,
            access_token=self._access_token,
            reconnection_time=self._reconnection_time,
            project_name=self._project_name,
        )

        async with self._client as sse_client:
            async for event in sse_client:
                if event is not None:
                    self._bus.fire(event.type, event)

    def add_event_listener(
        self, event_type: str, callback: Callable[..., Any] | Awaitable[Any]
    ) -> Callable[..., Any]:
        """Add a new listener, return function to remove the listener."""
        return self._bus.add_event_listener(event_type, callback)

    def stop(self) -> None:
        """Stop the client & terminate the thread."""
        self._client.close_client()
