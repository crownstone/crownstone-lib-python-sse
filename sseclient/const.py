"""Constants for the Crownstone Cloud lib"""
from datetime import timedelta

# URLs
EVENT_BASE_URL = "https://events.crownstone.rocks/sse?accessToken="

# SSE client
EVENT_CLIENT_STOP = "client_stop"
RECONNECTION_TIME = timedelta(seconds=5)
MAX_CONNECT_RETRY = 5

# SSE System events
EVENT_SSE_TOKEN_EXPIRED = 'TOKEN_EXPIRED'
EVENT_SSE_NO_ACCESS_TOKEN = "NO_ACCESS_TOKEN"
EVENT_SSE_NO_CONNECTION = "NO_CONNECTION"
EVENT_SSE_STREAM_START = "STREAM_START"
EVENT_SSE_STREAM_CLOSE = "STREAM_CLOSE"

# SSE command events
EVENT_SSE_SWITCH_CROWNSTONE = "switchCrownstone"

# SSE presence events
EVENT_SSE_ENTER_SPHERE = "enterSphere"
EVENT_SSE_EXIT_SPHERE = "exitSphere"
EVENT_SSE_ENTER_LOCATION = "enterLocation"
EVENT_SSE_EXIT_LOCATION = "exitLocation"

# lists for iteration
system_events = [
    EVENT_SSE_TOKEN_EXPIRED,
    EVENT_SSE_NO_ACCESS_TOKEN,
    EVENT_SSE_NO_CONNECTION,
    EVENT_SSE_STREAM_START,
    EVENT_SSE_STREAM_CLOSE
]

presence_events = [
    EVENT_SSE_ENTER_SPHERE,
    EVENT_SSE_EXIT_SPHERE,
    EVENT_SSE_ENTER_LOCATION,
    EVENT_SSE_EXIT_LOCATION
]