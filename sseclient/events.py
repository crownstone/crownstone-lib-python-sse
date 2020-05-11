class SystemEvent:
    """System SSE event"""

    def __init__(self, data) -> None:
        """Init event"""
        self.data = data or {}

    @property
    def code(self) -> int:
        return self.data['code']

    @property
    def message(self) -> str:
        return self.data['message']


class CommandEvent:
    """Command SSE event to switch a crownstone"""

    def __init__(self, data) -> None:
        """Init event"""
        self.data = data

    @property
    def sphere_id(self) -> str:
        return self.data['sphere']['id']

    @property
    def cloud_id(self) -> str:
        return self.data['crownstone']['id']

    @property
    def unique_id(self) -> str:
        return self.data['crownstone']['uid']

    @property
    def switch_state(self) -> str:
        return self.data['crownstone']['switchState']


class PresenceEvent:
    """Presence SSE event"""

    def __init__(self, data) -> None:
        """Init event"""
        self.data = data

    @property
    def sphere_id(self) -> str:
        return self.data['sphere']['id']

    @property
    def location_id(self) -> str:
        return self.data['location']['id']

    @property
    def user_id(self) -> str:
        return self.data['user']['id']


class DataChangeEvent:
    """Data Change SSE event"""

    def __init__(self, data, operation) -> None:
        """Init event"""
        self.data = data
        self.operation = operation

    @property
    def sphere_id(self) -> str:
        return self.data['sphere']['id']

    @property
    def changed_item_id(self) -> str:
        return self.data['changedItem']['id']

    @property
    def changed_item_name(self) -> str:
        return self.data['changedItem']['id']


class SwitchStateUpdateEvent:
    """A Crownstone was switched"""

    def __init__(self, data) -> None:
        """Init event"""
        self.data = data

    @property
    def sphere_id(self) -> str:
        return self.data['sphere']['id']

    @property
    def cloud_id(self) -> str:
        return self.data['crownstone']['id']

    @property
    def unique_id(self) -> str:
        return self.data['crownstone']['uid']

    @property
    def switch_state(self) -> float:
        return self.data['crownstone']['switchState']