"""
Example receiving Crownstone SSE events and creating callbacks for the received data.

Created by Ricardo Steijn.
Last update on 9-11-2020
"""
from crownstone_sse.client import CrownstoneSSE
from crownstone_sse.events.switch_state_update_event import SwitchStateUpdateEvent
from crownstone_sse.events.system_event import SystemEvent
from crownstone_sse.events.presence_event import PresenceEvent
from crownstone_sse.events.ability_change_event import AbilityChangeEvent
from crownstone_sse.events.data_change_event import DataChangeEvent
from crownstone_sse.const import (
    EVENT_SYSTEM_STREAM_START,
    EVENT_SWITCH_STATE_UPDATE,
    EVENT_PRESENCE_ENTER_LOCATION,
    EVENT_ABILITY_CHANGE_DIMMING,
    EVENT_DATA_CHANGE_CROWNSTONE,
    OPERATION_CREATE,
    OPERATION_DELETE,
    OPERATION_UPDATE
)
import logging
import time

# enable logging
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


# Create a sse client instance. Pass your crownstone account information.
# email and password are required for logging in again when an access token has expired.
sse_client = CrownstoneSSE('email', 'password')
# for usage with existing access token you can use this function:
# sse_client.set_access_token('myAccessToken')

# Start running the client
sse_client.start()

# Add listeners for event types of your liking, and the desired callback to be executed. see above.
sse_client.add_event_listener(EVENT_SYSTEM_STREAM_START, notify_stream_start)
sse_client.add_event_listener(EVENT_SWITCH_STATE_UPDATE, switch_update)
sse_client.add_event_listener(EVENT_PRESENCE_ENTER_LOCATION, notify_presence_changed)
sse_client.add_event_listener(EVENT_ABILITY_CHANGE_DIMMING, notify_ability_changed)
sse_client.add_event_listener(EVENT_DATA_CHANGE_CROWNSTONE, notify_data_changed)

# block for 120 seconds (let the client run for 120 second before stopping)
time.sleep(120)
# stop the client
sse_client.stop()
