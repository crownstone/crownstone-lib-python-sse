"""
Example receiving Crownstone SSE events and creating callbacks for the received data.

Created by Ricardo Steijn.
Last update on 14-5-2020
"""
from crownstone_sse.client import CrownstoneSSE
from crownstone_sse.events.SwitchStateUpdateEvent import SwitchStateUpdateEvent
from crownstone_sse.events.SystemEvent import SystemEvent
from crownstone_sse.events.PresenceEvent import PresenceEvent
from crownstone_sse.const import (
    EVENT_SYSTEM_STREAM_START,
    EVENT_SWITCH_STATE_UPDATE,
    EVENT_PRESENCE_ENTER_LOCATION,
)
import time


def crownstone_update(event: SwitchStateUpdateEvent):
    print("Crownstone {} state changed to {}".format(event.cloud_id, event.switch_state))
    # It is possible to stop the client after it has been fully started.
    # e.g. after an event was received.


def notify_stream_start(event: SystemEvent):
    print(event.message)


def notify_presence_changed(event: PresenceEvent):
    print("User {} has entered location {}".format(event.user_id, event.location_id))


# Create a sse client instance. Pass your crownstone account your information.
# email and password are required for logging in again when an access token has expired.
sse_client = CrownstoneSSE('email', 'password')
# for usage with existing access token you can use this function:
# sse_client.set_access_token('myAccessToken')

# Start running the client
sse_client.start()

# Add listeners for event types of your liking, and the desired callback to be executed. see above.
sse_client.add_event_listener(EVENT_SYSTEM_STREAM_START, notify_stream_start)
sse_client.add_event_listener(EVENT_SWITCH_STATE_UPDATE, crownstone_update)
sse_client.add_event_listener(EVENT_PRESENCE_ENTER_LOCATION, notify_presence_changed)

# block for 20 seconds (let the client run for 20 second before stopping)
time.sleep(20)
# stop the client
sse_client.stop()