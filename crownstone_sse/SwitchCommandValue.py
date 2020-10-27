from enum import Enum, auto

class SwitchCommandType(Enum):
	UNKNOWN = auto()
	TURN_ON = auto()
	TURN_OFF = auto()
	PERCENTAGE = auto()

class SwitchCommandValue:
	def __init__(self, cmdType: SwitchCommandType, percentage: int = None):
		self.type = cmdType
		self.percentage = 0
		if percentage is not None:
			self.percentage = percentage