class SwitchCommandEvent:
    """Command SSE event requesting to switch a crownstone"""

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
    def switch_val(self) -> int:
        # Map float 0..1 to percentage 0..100 or special value.
        float_val = float(self.data['crownstone']['switchState'])
        switch_val = round(float_val * 100.0)
        if switch_val < 0:
            switch_val = 0
        if switch_val > 99:
            # switch_val = SwitchValSpecial.SMART_ON
            switch_val = 255

        return switch_val
