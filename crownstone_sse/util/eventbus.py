"""Eventbus that can be used in either sync or async context."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable

from crownstone_sse.events import Event

_LOGGER = logging.getLogger(__name__)


class EventBus:
    """Event bus that listens to - and fires SSE events."""

    def __init__(self) -> None:
        """Initialize the event bus."""
        self._event_listeners: dict[str, list[Any]] = {}

    def get_event_listeners(self) -> dict[str, int]:
        """Return all current event listeners and amount of events."""
        return {key: len(self._event_listeners[key]) for key in self._event_listeners}

    def add_event_listener(
        self, event_type: str, callback: Callable[..., Any] | Awaitable[Any]
    ) -> Callable[..., Any]:
        """Listen to events of a specific type."""
        if event_type in self._event_listeners:
            self._event_listeners[event_type].append(callback)
        else:
            self._event_listeners[event_type] = [callback]

        # Return remove function so listener can be removed, if necessary
        def remove_listener() -> None:
            """Remove the listener."""
            self._remove_event_listener(event_type, callback)

        return remove_listener

    def fire(self, event_type: str, event: Event) -> None:
        """Fire an event."""
        for listener in self._event_listeners.get(event_type, []):
            try:
                loop = asyncio.get_running_loop()
                # async context only, when an event loop is running
                if asyncio.iscoroutine(listener):
                    asyncio.create_task(listener)
                elif asyncio.iscoroutinefunction(listener):
                    asyncio.create_task(listener(event))
                else:
                    loop.run_in_executor(None, listener, event)

            except RuntimeError:
                # no running loop, just call the function normally
                listener(event)

    def _remove_event_listener(
        self, event_type: str, listener: Callable[..., Any] | Awaitable[Any]
    ) -> None:
        """Remove a listener for an event type."""
        try:
            self._event_listeners[event_type].remove(listener)

            # delete event type if list empty
            if not self._event_listeners[event_type]:
                self._event_listeners.pop(event_type)

        except (KeyError, ValueError):
            _LOGGER.warning("Error removing unknown listener.")
