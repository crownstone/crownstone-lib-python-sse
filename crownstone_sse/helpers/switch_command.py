"""Classes that represent a Crownstone switch command."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class SwitchCommandType(Enum):
    """Represent the switch type."""

    UNKNOWN = auto()
    TURN_ON = auto()
    TURN_OFF = auto()
    PERCENTAGE = auto()


@dataclass
class SwitchCommandValue:
    """Container for a switch command value."""

    type: SwitchCommandType
    percentage: int = 0


class SwitchCommand:
    """Command SSE event that requests to switch a single Crownstone."""

    def __init__(self, data: dict[str, Any]):
        """Initialize event."""
        self.data = data

    @property
    def cloud_id(self) -> str:
        """Return the cloud id."""
        return str(self.data["id"])

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return str(self.data["uid"])

    @property
    def switch_val(self) -> SwitchCommandValue:
        """Return the switch value based on the type."""
        if self.data["type"] == "TURN_ON":
            return SwitchCommandValue(SwitchCommandType.TURN_ON)

        if self.data["type"] == "TURN_OFF":
            return SwitchCommandValue(SwitchCommandType.TURN_OFF)

        if self.data["type"] == "PERCENTAGE":
            percentage = int(self.data["percentage"])
            if percentage < 0:
                percentage = 0
            if percentage > 100:
                percentage = 100
            return SwitchCommandValue(SwitchCommandType.PERCENTAGE, percentage)

        return SwitchCommandValue(SwitchCommandType.UNKNOWN)
