"""
Sync example of receiving Crownstone SSE events.

Created by Ricardo Steijn.
Last update on 03-11-2021.
"""
import logging
from crownstone_sse import CrownstoneSSE
from crownstone_sse.events import (
    SwitchStateUpdateEvent,
    SystemEvent,
    PresenceEvent,
    AbilityChangeEvent,
    DataChangeEvent
)
from crownstone_sse.const import (
    OPERATION_CREATE,
    OPERATION_DELETE,
    OPERATION_UPDATE
)
from crownstone_sse import (
    EVENT_SYSTEM_STREAM_START,
    EVENT_CROWNSTONE_SWITCH_STATE_UPDATE,
    EVENT_PRESENCE_ENTER_LOCATION,
    EVENT_ABILITY_CHANGE_DIMMING,
    EVENT_DATA_CHANGE_CROWNSTONE
)


# enable logging.
logging.basicConfig(format='%(levelname)s :%(message)s', level=logging.DEBUG)


def switch_update(event: SwitchStateUpdateEvent):
    print("Crownstone {} switch state changed to {}".format(event.cloud_id, event.switch_state))


def notify_stream_start(event: SystemEvent):
    print(event.message)


def notify_presence_changed(event: PresenceEvent):
    print("User {} has entered location {}".format(event.user_id, event.location_id))


def notify_ability_changed(event: AbilityChangeEvent):
    print("Ability {} changed to {}".format(event.ability_type, event.ability_enabled))


def notify_data_changed(event: DataChangeEvent):
    if event.operation == OPERATION_CREATE:
        print("New data is available: {}".format(event.changed_item_name))
    if event.operation == OPERATION_UPDATE:
        print("Name of id {} has been updated to {}".format(event.changed_item_id, event.changed_item_name))
    if event.operation == OPERATION_DELETE:
        print("Data {} has been deleted".format(event.changed_item_name))


# Create a new instance of Crownstone SSE client.
# email (string): your Crownstone account email.
# password (string): your Crownstone account password.
# access_token (string) [optional]: Access token from a previous login to skip the login step.
# reconnection_time (int): time to wait before reconnection on connection loss.
sse_client = CrownstoneSSE(
    email="example@example.com",
    password="CrownstoneRocks"
)

# Add listeners for event types of your liking, and the desired callback to be executed. see above.
sse_client.add_event_listener(EVENT_SYSTEM_STREAM_START, notify_stream_start)
sse_client.add_event_listener(EVENT_CROWNSTONE_SWITCH_STATE_UPDATE, switch_update)
sse_client.add_event_listener(EVENT_PRESENCE_ENTER_LOCATION, notify_presence_changed)
sse_client.add_event_listener(EVENT_ABILITY_CHANGE_DIMMING, notify_ability_changed)
sse_client.add_event_listener(EVENT_DATA_CHANGE_CROWNSTONE, notify_data_changed)

# Wait until the thread finishes.
# You can terminate the thread by using SIGINT (ctrl + c or stop button in IDE).
try:
    sse_client.join()
except KeyboardInterrupt:
    sse_client.stop()
