class PresenceEvent:
    """Presence SSE event"""

    def __init__(self, data, type) -> None:
        """Init event"""
        self.data = data
        self.type = type

    @property
    def sphere_id(self) -> str:
        return self.data['sphere']['id']

    @property
    def location_id(self) -> str:
        return self.data['location']['id']

    @property
    def user_id(self) -> str:
        return self.data['user']['id']