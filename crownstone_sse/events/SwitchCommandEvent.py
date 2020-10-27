from crownstone_sse.SwitchCommandValue import SwitchCommandValue, SwitchCommandType


class SwitchCommandEvent:
    """
    Command SSE event requesting to switch a crownstone

    Deprecated.
    """

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
    def switch_val(self) -> SwitchCommandValue:
        # Map float 0..1.
        float_val = float(self.data['crownstone']['switchState'])
        percentage = round(float_val * 100.0)
        if percentage < 1:
            return SwitchCommandValue(SwitchCommandType.TURN_OFF)
        elif percentage > 99:
            return SwitchCommandValue(SwitchCommandType.TURN_ON)
        else:
            return SwitchCommandValue(SwitchCommandType.PERCENTAGE, percentage)
