"""
Sync example of receiving Crownstone SSE events.

Created by Ricardo Steijn.
Last update on 06-05-2021.
"""
import logging
from crownstone_sse import CrownstoneSSE
from crownstone_sse.events import (
    SwitchStateUpdateEvent,
    SystemEvent,
    PresenceEvent,
    AbilityChangeEvent,
    DataChangeEvent,
)
from crownstone_sse import (
    EVENT_ABILITY_CHANGE,
    EVENT_DATA_CHANGE,
    EVENT_PRESENCE,
    EVENT_PRESENCE_ENTER_LOCATION,
    EVENT_SWITCH_STATE_UPDATE,
    EVENT_SWITCH_STATE_UPDATE_CROWNSTONE,
    EVENT_SYSTEM,
    OPERATION_CREATE,
    OPERATION_DELETE,
    OPERATION_UPDATE,
)

# enable logging.
logging.basicConfig(format='%(levelname)s :%(message)s', level=logging.DEBUG)


def switch_update(event: SwitchStateUpdateEvent):
    if event.sub_type == EVENT_SWITCH_STATE_UPDATE_CROWNSTONE:
        print("Crownstone {} switch state changed to {}".format(event.cloud_id, event.switch_state))


def notify_stream_start(event: SystemEvent):
    print(event.message)


def notify_presence_changed(event: PresenceEvent):
    if event.sub_type == EVENT_PRESENCE_ENTER_LOCATION:
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
sse_client.add_event_listener(EVENT_SYSTEM, notify_stream_start)
sse_client.add_event_listener(EVENT_SWITCH_STATE_UPDATE, switch_update)
sse_client.add_event_listener(EVENT_PRESENCE, notify_presence_changed)
sse_client.add_event_listener(EVENT_ABILITY_CHANGE, notify_ability_changed)
sse_client.add_event_listener(EVENT_DATA_CHANGE, notify_data_changed)

# Wait until the thread finishes.
# You can terminate the thread by using SIGINT (ctrl + c or stop button in IDE).
try:
    sse_client.join()
except KeyboardInterrupt:
    sse_client.stop()
