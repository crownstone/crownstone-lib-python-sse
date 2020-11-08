from crownstone_sse.helpers.switch_command_value import (
    SwitchCommandValue, 
    SwitchCommandType
)


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
    def switch_val(self) -> SwitchCommandValue:
        if self.data['type'] == 'TURN_ON':
            return SwitchCommandValue(SwitchCommandType.TURN_ON)

        elif self.data['type'] == 'TURN_OFF':
            return SwitchCommandValue(SwitchCommandType.TURN_OFF)

        elif self.data['type'] == 'PERCENTAGE':
            percentage = int(self.data['percentage'])
            if percentage < 0:
                percentage = 0
            if percentage > 100:
                percentage = 100
            return SwitchCommandValue(SwitchCommandType.PERCENTAGE, percentage)

        else:
            return SwitchCommandValue(SwitchCommandType.UNKNOWN)

