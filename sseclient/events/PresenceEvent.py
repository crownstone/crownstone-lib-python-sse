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