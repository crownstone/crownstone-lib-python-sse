from sseclient.client import CrownstoneSSE
from sseclient.events import (
    SwitchStateUpdateEvent,
    PresenceEvent,
    SystemEvent
)
from sseclient.const import (
    EVENT_SYSTEM_STREAM_START,
    EVENT_SWITCH_STATE_UPDATE,
    EVENT_PRESENCE_ENTER_LOCATION,
)


def crownstone_update(event: SwitchStateUpdateEvent):
    print("Crownstone {} state changed to {}".format(event.cloud_id, event.switch_state))


def notify_stream_start(event: SystemEvent):
    print(event.message)


def notify_presence_changed(event: PresenceEvent):
    print("User {} has entered location {}".format(event.user_id, event.location_id))


sse_client = CrownstoneSSE()
sse_client.set_user_information('email', 'password')
sse_client.start()

sse_client.add_event_listener(EVENT_SYSTEM_STREAM_START, notify_stream_start)
sse_client.add_event_listener(EVENT_SWITCH_STATE_UPDATE, crownstone_update)
sse_client.add_event_listener(EVENT_PRESENCE_ENTER_LOCATION, notify_presence_changed)