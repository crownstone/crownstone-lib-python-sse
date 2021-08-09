"""Constants used by Crownstone SSE components."""
from typing import Final

# URLs
EVENT_BASE_URL: Final = "https://events.crownstone.rocks/sse?accessToken="
LOGIN_URL: Final = "https://cloud.crownstone.rocks/api/users/login"

# Headers
CONTENT_TYPE: Final = "text/event-stream"
NO_CACHE: Final = "no-cache"

# Connection parameters
RECONNECTION_TIME: Final = 30
CONNECTION_TIMEOUT: Final = 35

# SSE Ping event
EVENT_PING: Final = "ping"

# SSE System events
EVENT_SYSTEM: Final = "system"
EVENT_SYSTEM_TOKEN_EXPIRED: Final = "TOKEN_EXPIRED"
EVENT_SYSTEM_NO_ACCESS_TOKEN: Final = "NO_ACCESS_TOKEN"
EVENT_SYSTEM_NO_CONNECTION: Final = "NO_CONNECTION"
EVENT_SYSTEM_STREAM_START: Final = "STREAM_START"
EVENT_SYSTEM_STREAM_CLOSED: Final = "STREAM_CLOSED"

# SSE dataChange events
EVENT_DATA_CHANGE: Final = "dataChange"
EVENT_DATA_CHANGE_CROWNSTONE: Final = "stones"
EVENT_DATA_CHANGE_SPHERES: Final = "spheres"
EVENT_DATA_CHANGE_USERS: Final = "users"
EVENT_DATA_CHANGE_LOCATIONS: Final = "locations"

# dataChange operations
OPERATION: Final = "operation"
OPERATION_CREATE: Final = "create"
OPERATION_DELETE: Final = "delete"
OPERATION_UPDATE: Final = "update"

# SwitchState update events
EVENT_SWITCH_STATE_UPDATE: Final = "switchStateUpdate"
EVENT_SWITCH_STATE_UPDATE_CROWNSTONE: Final = "stone"

# SSE command events
EVENT_COMMAND: Final = "command"
EVENT_COMMAND_SWITCH_MULTIPLE_CROWNSTONES: Final = "multiSwitch"

# SSE presence events
EVENT_PRESENCE: Final = "presence"
EVENT_PRESENCE_ENTER_SPHERE: Final = "enterSphere"
EVENT_PRESENCE_EXIT_SPHERE: Final = "exitSphere"
EVENT_PRESENCE_ENTER_LOCATION: Final = "enterLocation"
EVENT_PRESENCE_EXIT_LOCATION: Final = "exitLocation"

# SSE abilityChange events
EVENT_ABILITY_CHANGE: Final = "abilityChange"
EVENT_ABILITY_CHANGE_DIMMING: Final = "dimming"
EVENT_ABILITY_CHANGE_SWITCHCRAFT: Final = "switchcraft"
EVENT_ABILITY_CHANGE_TAP_TO_TOGGLE : Final= "tapToToggle"

# errors
LOGIN_FAILED: Final = "LOGIN_FAILED"
LOGIN_FAILED_EMAIL_NOT_VERIFIED: Final = "LOGIN_FAILED_EMAIL_NOT_VERIFIED"

# lists for iteration
system_events: Final[list[str]] = [
    EVENT_SYSTEM_TOKEN_EXPIRED,
    EVENT_SYSTEM_NO_ACCESS_TOKEN,
    EVENT_SYSTEM_NO_CONNECTION,
    EVENT_SYSTEM_STREAM_START,
    EVENT_SYSTEM_STREAM_CLOSED,
]

presence_events: Final[list[str]] = [
    EVENT_PRESENCE_ENTER_SPHERE,
    EVENT_PRESENCE_EXIT_SPHERE,
    EVENT_PRESENCE_ENTER_LOCATION,
    EVENT_PRESENCE_EXIT_LOCATION,
]

data_change_events: Final[list[str]] = [
    EVENT_DATA_CHANGE_USERS,
    EVENT_DATA_CHANGE_SPHERES,
    EVENT_DATA_CHANGE_CROWNSTONE,
    EVENT_DATA_CHANGE_LOCATIONS,
]

ability_change_events: Final[list[str]] = [
    EVENT_ABILITY_CHANGE_DIMMING,
    EVENT_ABILITY_CHANGE_SWITCHCRAFT,
    EVENT_ABILITY_CHANGE_TAP_TO_TOGGLE,
]
