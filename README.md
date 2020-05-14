# crownstone-python-lib-sse
Asynchronous Python library that listens to Crownstone SSE events.

## Functionality
* Async: using asyncio and aiohttp, optimized for speed.
* Easy to use: simply pass your crownstone email and password to the constructor, and start the client!
* Complete: Fully integrated event bus that can be used to listen to events, and run callbacks.
* Independent: Client runs in a separate thread, your main thread will not be blocked!

## Requirements
* Python 3.7 or higher
* Aiohttp 3.6.2

## Standard installation
cd to the project folder and run:
```console
$ python3.7 setup.py install
```

## Install in a virtual environment
To install the library excute the following command:
```console
$ python3.7 -m venv venv3.7
```
Activate your venv using:
```console
$ source venv3.7/bin/activate
```
Once activated, the venv is used to executed python files, and libraries will be installed in the venv.<br>
To install this library, cd to the project folder and run:
```console
$ python setup.py install
```

## Getting started
### Example
```python
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


def notify_stream_start(event: SystemEvent):
    print(event.message)


def notify_presence_changed(event: PresenceEvent):
    print("User {} has entered location {}".format(event.user_id, event.location_id))


# Create a sse client instance. Pass your crownstone account information.
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

# let the client run for 20 seconds (block)
time.sleep(20)

# stop the client
sse_client.stop()
```
### Creating callbacks
Callbacks are functions that will be executed everytime an event comes in of an specific event type.<br>
Callback functions are standard functions, NOT coroutines!<br>
The standard format for a callback is:
```python
def callback(event: EventTypeClass):
    # do something
```
Each event has it's own fields. It is recommended to provide the event type class hint to keep better track of which event it is, and what fields it has. <br>
For example:
```python
def callback(event: PresenceEvent):
    print(event.user_id)
    print(event.location_id)
```

## Event types
Currently, there are 5 different event types:
* System event
* Command event
* Data change event
* Presence event
* Switch state update event

### System event
A system event is represented as:
* code
* message

### Command event
A command event is represented as:
#### Sphere
* sphere_id
#### Crownstone
* cloud_id
* unique_id
* switch_state

### Data change event
A data change event is represented as:
* operation (update | delete | create)
#### Sphere
* sphere_id
#### Item
* changed_item_id
* changed_item_name

### Presence event
A presence event is represented as:
#### Sphere
* sphere_id
#### Location
* location_id
#### User
* user_id

### Switch state update event
A switch state update event is represented as:
#### Sphere
* sphere_id
#### Crownstone
* cloud_id
* unique_id
* switch_state

## Testing
Tests coming soon!
