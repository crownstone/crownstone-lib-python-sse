class DataChangeEvent:
    """Data Change SSE event"""

    def __init__(self, data, type, operation) -> None:
        """Init event"""
        self.data = data
        self.type = type
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