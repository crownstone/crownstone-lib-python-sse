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
$ python setup.py install
```

## Install in a virtual environment
To install the library execute the following command:
```console
$ python -m venv venv
```
Activate your venv using:
```console
$ source venv/bin/activate
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
from crownstone_sse.events.switch_state_update_event import SwitchStateUpdateEvent
from crownstone_sse.events.system_event import SystemEvent
from crownstone_sse.events.presence_event import PresenceEvent
from crownstone_sse.events.ability_change_event import AbilityChangeEvent
from crownstone_sse.const import (
    EVENT_SYSTEM_STREAM_START,
    EVENT_SWITCH_STATE_UPDATE,
    EVENT_PRESENCE_ENTER_LOCATION,
    EVENT_ABILITY_CHANGE_DIMMING,
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
    print("Ability {} has been {}".format(event.ability_type, event.ability_enabled))


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

# block for 120 seconds (let the client run for 120 second before stopping)
time.sleep(120)
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
Currently, there are 6 different event types:
* System event
* Command event
* Data change event
* Presence event
* Switch state update event
* Ability change event

### System event
A system event is represented as:
* code
* message

### Switch command event
A switch command event is represented as:
#### Sphere
* sphere_id
#### Crownstone
* cloud_id
* unique_id
* switch_val (as SwitchCommandValue)

### Multi Switch command event
A multi switch command event is represented as:
#### Sphere
* sphere_id
#### Crownstone list
* crownstone_list
#### Each crownstone in the list:
* cloud_id
* unique_id
* switch_val (as SwitchCommandValue)

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
* switch_state (percentage)

### Ability change event
An ability change event is represented as:
#### Sphere
* sphere_id
#### Crownstone
* cloud_id
* unique_id
#### Ability
* ability_type
* ability_enabled
* ability_synced_to_crownstone

## Testing
To run the tests using tox install tox first by running:
```console
$ pip install tox
```
To execute the tests cd to the project folder and run:
```console
$ tox
```
To see which parts of the code are covered by the tests, a coverage report is generated after the tests have been successfull.<br>
To see the coverage report run:
```console
$ coverage report
```
If you like to get a better overview of the test you can generate a HTML file like so:
```console
$ coverage html
```
To view your html file directly on Linux:
```console
$ ./htmlcov/index.html
```
On Windows simply navigate to the htmlcov folder inside the project folder, and double-click index.html. It will be executed in your selected browser.
