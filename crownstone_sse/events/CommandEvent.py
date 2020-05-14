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