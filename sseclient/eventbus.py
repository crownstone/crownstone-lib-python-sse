import logging
import asyncio
from typing import Optional, Dict, List, Callable

_LOGGER = logging.getLogger(__name__)


class Event:
    """Event in the event bus"""

    def __init__(self, event_type: str, data: Optional[Dict] = None):
        """Init an event"""
        self.event_type = event_type
        self.data = data or {}

    def to_dict(self) -> Dict:
        """Return a dictionary representation of the event"""
        return {
            "event_type": self.event_type,
            "data": dict(self.data),
        }


class EventBus:
    """Event bus that listens and fires system or SSE events"""

    def __init__(self, loop=None) -> None:
        """Init the event bus"""
        self.loop: Optional[asyncio.AbstractEventLoop] = loop
        self.event_listeners: Dict[str, List[Callable]] = {}

    def get_event_listeners(self) -> Dict[str, int]:
        """Return all current event listeners and amount of events"""

        return {key: len(self.event_listeners[key]) for key in self.event_listeners}

    def add_event_listener(self, event_type: str, event_listener: Callable) -> Callable:
        """Listen to events of a specific type"""
        if event_type in self.event_listeners:
            self.event_listeners[event_type].append(event_listener)
        else:
            self.event_listeners[event_type] = [event_listener]

        # Return listener so it can be removed again, if necessary
        return event_listener

    def fire(self, event_type: str, event_data: Optional[Dict] = None) -> None:
        """Fire an event. Can be listened for."""
        event = Event(event_type, event_data)
        for listener in self.event_listeners.get(event_type, []):
            if self.loop:
                # Check what type of function is it & create task
                if asyncio.iscoroutine(listener):
                    self.loop.create_task(listener)
                elif asyncio.iscoroutinefunction(listener):
                    self.loop.create_task(listener(event))
                else:
                    self.loop.run_in_executor(None, listener, event)
            else:
                listener(event)

    def remove_event_listener(self, event_type: str, listener: Callable) -> None:
        """Remove a listener for an event type"""
        try:
            self.event_listeners[event_type].remove(listener)
        except ValueError:
            _LOGGER.warning("Error removing listener, it does not exist.")
