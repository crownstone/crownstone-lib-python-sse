class AbilityChangeEvent:
    """Event that indicates an ability change"""

    def __init__(self, data, type) -> None:
        """Init event"""
        self.data = data
        self.type = type

    @property
    def sphere_id(self) -> str:
        return self.data['sphere']['id']

    @property
    def cloud_id(self) -> str:
        return self.data['stone']['id']

    @property
    def unique_id(self) -> str:
        return self.data['stone']['uid']

    @property
    def ability_type(self) -> str:
        return self.data['ability']['type']

    @property
    def ability_enabled(self) -> bool:
        return self.data['ability']['enabled']

    @property
    def ability_synced_to_crownstone(self) -> bool:
        return self.data['ability']['syncedToCrownstone']
