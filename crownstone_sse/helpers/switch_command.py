"""Classes that represent a Crownstone switch command."""
from enum import Enum, auto


class SwitchCommandType(Enum):
    """Represent the switch type."""

    UNKNOWN = auto()
    TURN_ON = auto()
    TURN_OFF = auto()
    PERCENTAGE = auto()


class SwitchCommandValue:
    """Container for a switch command value."""

    def __init__(self, cmd_type: SwitchCommandType, percentage: int = None):
        """Initialize a switch command value."""
        self.type = cmd_type
        self.percentage = 0
        if percentage is not None:
            self.percentage = percentage


class SwitchCommand:
    """Command SSE event that requests to switch a single Crownstone."""

    def __init__(self, data):
        """Initialize event."""
        self.data = data

    @property
    def cloud_id(self) -> str:
        """Return the cloud id."""
        return self.data["id"]

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return self.data["uid"]

    @property
    def switch_val(self) -> SwitchCommandValue:
        """Return the switch value based on the type."""
        if self.data["type"] == "TURN_ON":
            return SwitchCommandValue(SwitchCommandType.TURN_ON)

        elif self.data["type"] == "TURN_OFF":
            return SwitchCommandValue(SwitchCommandType.TURN_OFF)

        elif self.data["type"] == "PERCENTAGE":
            percentage = int(self.data["percentage"])
            if percentage < 0:
                percentage = 0
            if percentage > 100:
                percentage = 100
            return SwitchCommandValue(SwitchCommandType.PERCENTAGE, percentage)

        else:
            return SwitchCommandValue(SwitchCommandType.UNKNOWN)
