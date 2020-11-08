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