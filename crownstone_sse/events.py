"""
Crownstone SSE event data containers to access the received event data.

See https://github.com/crownstone/crownstone-lib-nodejs-sse/blob/master/README.md
for full details on the events.
"""
import json
from typing import TypeVar

from crownstone_sse.const import (
    EVENT_ABILITY_CHANGE,
    EVENT_COMMAND,
    EVENT_DATA_CHANGE,
    EVENT_PING,
    EVENT_PRESENCE,
    EVENT_SWITCH_STATE_UPDATE,
    EVENT_SYSTEM,
)
from crownstone_sse.helpers.switch_command import SwitchCommand


class AbilityChangeEvent:
    """Event that indicates an ability change."""

    def __init__(self, data: dict) -> None:
        """Initialize event."""
        self.data = data

    def __str__(self) -> str:
        """Return event data as string"""
        return json.dumps(self.data)

    @property
    def type(self) -> str:
        """Return the event type."""
        return self.data["type"]

    @property
    def sub_type(self) -> str:
        """Return the event sub-type."""
        return self.data["subType"]

    @property
    def sphere_id(self) -> str:
        """Return the sphere id."""
        return self.data["sphere"]["id"]

    @property
    def cloud_id(self) -> str:
        """Return the cloud id."""
        return self.data["stone"]["id"]

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return self.data["stone"]["uid"]

    @property
    def ability_type(self) -> str:
        """Return the ability type."""
        return self.data["ability"]["type"]

    @property
    def ability_enabled(self) -> bool:
        """Return if the ability is enabled."""
        return self.data["ability"]["enabled"]

    @property
    def ability_synced_to_crownstone(self) -> bool:
        """Return if the ability is synced to the Crownstone."""
        return self.data["ability"]["syncedToCrownstone"]


class DataChangeEvent:
    """Data Change SSE event."""

    def __init__(self, data: dict) -> None:
        """Initialize event."""
        self.data = data

    def __str__(self) -> str:
        """Return event data as string"""
        return json.dumps(self.data)

    @property
    def type(self) -> str:
        """Return the event type."""
        return self.data["type"]

    @property
    def sub_type(self) -> str:
        """Return the event sub-type."""
        return self.data["subType"]

    @property
    def operation(self) -> str:
        """Return the operation done on the data."""
        return self.data["operation"]

    @property
    def sphere_id(self) -> str:
        """Return the sphere id."""
        return self.data["sphere"]["id"]

    @property
    def changed_item_id(self) -> str:
        """Return the id of the changed item."""
        return self.data["changedItem"]["id"]

    @property
    def changed_item_name(self) -> str:
        """Return the name of the changed item."""
        return self.data["changedItem"]["name"]


class MultiSwitchCommandEvent:
    """Command SSE event requesting to switch a list of crownstones."""

    def __init__(self, data: dict) -> None:
        """Initialize event."""
        self.data = data

    def __str__(self) -> str:
        """Return event data as string"""
        return json.dumps(self.data)

    @property
    def type(self) -> str:
        """Return the event type."""
        return self.data["type"]

    @property
    def sub_type(self) -> str:
        """Return the event sub-type."""
        return self.data["subType"]

    @property
    def sphere_id(self) -> str:
        """Return the sphere id."""
        return self.data["sphere"]["id"]

    @property
    def crownstone_list(self) -> list:
        """ Return a list of SwitchCommand."""
        switch_list = []
        for cmd in self.data["switchData"]:
            switch_list.append(SwitchCommand(cmd))
        return switch_list


class PresenceEvent:
    """Presence SSE event."""

    def __init__(self, data: dict) -> None:
        """Initialize event."""
        self.data = data

    def __str__(self) -> str:
        """Return event data as string"""
        return json.dumps(self.data)

    @property
    def type(self) -> str:
        """Return the event type."""
        return self.data["type"]

    @property
    def sub_type(self) -> str:
        """Return the event sub-type."""
        return self.data["subType"]

    @property
    def sphere_id(self) -> str:
        """Return the sphere id."""
        return self.data["sphere"]["id"]

    @property
    def location_id(self) -> str:
        """Return the location id."""
        return self.data["location"]["id"]

    @property
    def user_id(self) -> str:
        """Return the user id."""
        return self.data["user"]["id"]


class SwitchStateUpdateEvent:
    """A Crownstone was switched."""

    def __init__(self, data: dict) -> None:
        """Initialize event."""
        self.data = data

    def __str__(self) -> str:
        """Return event data as string"""
        return json.dumps(self.data)

    @property
    def type(self) -> str:
        """Return the event type."""
        return self.data["type"]

    @property
    def sub_type(self) -> str:
        """Return the event sub-type."""
        return self.data["subType"]

    @property
    def sphere_id(self) -> str:
        """Return the sphere id."""
        return self.data["sphere"]["id"]

    @property
    def cloud_id(self) -> str:
        """Return the cloud id."""
        return self.data["crownstone"]["id"]

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return self.data["crownstone"]["uid"]

    @property
    def switch_state(self) -> int:
        """Return the switch state."""
        return int(self.data["crownstone"]["percentage"])


class SystemEvent:
    """System SSE event."""

    def __init__(self, data: dict) -> None:
        """Initialize event."""
        self.data = data

    def __str__(self) -> str:
        """Return event data as string"""
        return json.dumps(self.data)

    @property
    def type(self) -> str:
        """Return the event type."""
        return self.data["type"]

    @property
    def sub_type(self) -> str:
        """Return the event sub-type."""
        return self.data["subType"]

    @property
    def code(self) -> int:
        """Return the code."""
        return self.data["code"]

    @property
    def message(self) -> str:
        """Return the message."""
        return self.data["message"]


class PingEvent:
    """Ping event that indicates the connection is alive."""

    def __init__(self, data: dict) -> None:
        """Initialize event."""
        self.data = data

    def __str__(self) -> str:
        """Return event data as string"""
        return json.dumps(self.data)

    @property
    def type(self) -> str:
        """Return the event type."""
        return self.data["type"]

    @property
    def counter(self) -> int:
        """Return the count of this ping event."""
        return self.data["counter"]

    @property
    def elapsed_time(self) -> int:
        """Return the elapsed time since the connection was made."""
        return int(self.data["counter"]) * 30


Event = TypeVar(
    "Event",
    AbilityChangeEvent,
    DataChangeEvent,
    MultiSwitchCommandEvent,
    SystemEvent,
    SwitchStateUpdateEvent,
    PresenceEvent,
    PingEvent,
)


def parse_event(data: dict) -> Event or None:
    """Return the correct Crownstone Event based on data."""
    if data["type"] == EVENT_PING:
        return PingEvent(data)

    if data["type"] == EVENT_SYSTEM:
        return SystemEvent(data)

    if data["type"] == EVENT_COMMAND:
        return MultiSwitchCommandEvent(data)

    if data["type"] == EVENT_SWITCH_STATE_UPDATE:
        return SwitchStateUpdateEvent(data)

    if data["type"] == EVENT_DATA_CHANGE:
        return DataChangeEvent(data)

    if data["type"] == EVENT_PRESENCE:
        return PresenceEvent(data)

    if data["type"] == EVENT_ABILITY_CHANGE:
        return AbilityChangeEvent(data)

    return None
