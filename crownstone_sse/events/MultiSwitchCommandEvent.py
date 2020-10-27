class MultiSwitchCommandEvent:
    """Command SSE event requesting to switch a list of crownstones"""

    def __init__(self, data) -> None:
        """Init event"""
        self.data = data

    @property
    def sphere_id(self) -> str:
        return self.data['sphere']['id']

    @property
    def crownstone_list(self) -> list:
        """ Returns a list of SwitchCommand """
        switch_list = []
        for cmd in self.data['switchData']:
            switch_list.append(SwitchCommand(cmd))
        return switch_list


class SwitchCommand:
    def __init__(self, data):
        self.data = data

    @property
    def cloud_id(self) -> str:
        return self.data['id']

    @property
    def unique_id(self) -> str:
        return self.data['uid']

    @property
    def switch_val(self) -> int:
        switch_val = 0

        if self.data['type'] == 'TURN_ON':
            # switch_val = SwitchValSpecial.SMART_ON
            switch_val = 255

        elif self.data['type'] == 'TURN_OFF':
            switch_val = 0

        elif self.data['type'] == 'PERCENTAGE':
            switch_val = int(self.data['percentage'])
            if self.switch_val < 0:
                switch_val = 0
            if self.switch_val > 100:
                switch_val = 100

        return switch_val

