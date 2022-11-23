# crownstone-python-lib-sse
Asynchronous Python library that listens to Crownstone SSE events.

## Functionality
* Async: using asyncio and aiohttp, easy to integrate in existing projects.
* Multi-functional: Library provides an extra thread wrapper to run the client in sync context.
* Complete: Fully integrated event bus that can be used to listen to events, and run callbacks.

## Requirements
* Python 3.8 or higher
* Aiohttp 3.7

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

### Asynchronous example

```python
import asyncio
import logging
from crownstone_sse import CrownstoneSSEAsync

# enable logging
logging.basicConfig(format='%(levelname)s :%(message)s', level=logging.DEBUG)


async def main():
    # Create a new instance of Crownstone SSE client.
    # parameters:
    # email (string): your Crownstone account email.
    # password (string): your Crownstone account password.
    # access_token (string) [optional]: Access token from a previous login to skip the login step.
    # websession (aiohttp.ClientSession): provide the websession used in a project this is integrated in.
    # reconnection_time (int): time to wait before reconnection on connection loss.
    # project_name (string) [optional]: name of the project this is integrated in. This provides context to SSE logs in case of an error.
    client = CrownstoneSSEAsync(
        email="example@example.com",
        password="CrownstoneRocks",
        project_name="MyProject"
    )
    # wait for the client to finish (means: blocking, run forever).
    await process_events(client)
    # to use this concurrently in an asyncio project, run this instead:
    # asyncio.create_task(process_events(client))


async def process_events(sse_client: CrownstoneSSEAsync):
    async with sse_client as client:
        async for event in client:
            # prints string representation of the event.
            print(event)

            # optionally you can use the provided eventbus.
            # event_bus.fire(event.sub_type, event)

            # or access specific event details.
            # for example a switch state update:
            # print(event.switch_state)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
finally:
    print("Crownstone SSE client finished. Thanks for your time!")
```
The async client is meant to be used in an existing asyncio project. You can pass an existing `aiohttp.ClientSession` 
object to the client, and schedule the receiving of events in the running event loop by using:
```python
asyncio.create_task()
```
as shown in the example above.

### Using an event bus

Crownstone SSE library provides a very complete event bus that can be used to schedule coroutines as well as callbacks.
Make sure to initiate the event bus within the event loop.
The eventbus can be initiated like so:
```python
from crownstone_sse import EventBus

bus = EventBus()
```
Then you can create a coroutine to be executed upon receiving a specific event:
```python
async def async_update_local_switch_state(event: SwitchStateUpdateEvent):
    # example
    await crownstone.update_state(event.switch_state)

bus.add_event_listener(EVENT_CROWNSTONE_SWITCH_STATE_UPDATE, async_update_local_switch_state)
```
The usage of the eventbus is optional here. You can also use an existing eventbus in your project.

### Synchronous example

```python
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
# project_name (string) [optional]: name of the project this is integrated in. This provides context to SSE logs in case of an error.
sse_client = CrownstoneSSE(
    email="example@example.com",
    password="CrownstoneRocks",
    project_name="MyProject"
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
```
This library can be used in synchronous context, and the example above will likely be the go-to option for most users.
You can use the Thread next to other synchronous Python code. <br>
If you want to let the client run forever, you can use:
```python
sse_client.join()
```
As shown above. This will make the main thread wait till the sse_client thread is finished.
You should however always build in  a way to stop the client, you can do so by stopping on `KeyboardInterrupt` 
as shown above.

### Creating callbacks

Callbacks are functions that will be executed everytime an event comes in of an specific event type.<br>
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
You can add the listener like so:
```python
unsub = sse_client.add_event_listener(event_type, callback)
```
This returns an unsubscribe function in case you want to remove the listener again. To do that, simply call:
```python
unsub()
```

## Event types

Currently, there are 7 different event types:
* System event
* Command event
* Data change event
* Presence event
* Switch state update event
* Ability change event
* Ping event

### System event

A system event is represented as:
#### Type
* type
* sub_type
#### System  
* code
* message

### Switch command event

A switch command event is represented as:
#### Type
* type
* sub_type
#### Sphere
* sphere_id
#### Crownstone
* cloud_id
* unique_id
* switch_val (as SwitchCommandValue)

### Multi Switch command event

A multi switch command event is represented as:
#### Type
* type
* sub_type
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
#### Type
* type
* sub_type
#### Sphere
* sphere_id
#### Item
* changed_item_id
* changed_item_name

### Presence event

A presence event is represented as:
#### Type
* type
* sub_type
#### Sphere
* sphere_id
#### Location
* location_id
#### User
* user_id

### Switch state update event

A switch state update event is represented as:
#### Type
* type
* sub_type
#### Sphere
* sphere_id
#### Crownstone
* cloud_id
* unique_id
* switch_state (percentage)

### Ability change event

An ability change event is represented as:
#### Type
* type
* sub_type
#### Sphere
* sphere_id
#### Crownstone
* cloud_id
* unique_id
#### Ability
* ability_type
* ability_enabled
* ability_synced_to_crownstone

### Ping event

A ping event is represented as:
#### Type
* type
#### Counter
* counter
* elapsed_time (in seconds)

The ping event exists to notify the client that the connection is still alive, internally. <br> 
You can however use it to check how long the connection has been alive as well.

## Testing

Tests are not available yet for this version. The client has however been live tested on the following:
1. Logging in with Crownstone credentials.
2. Establishing a connection to the Crownstone SSE server.
3. Tested the connection staying alive for longer than 10 minutes (no total timeout).
4. Tested client reconnection by manually disabling internet, waiting over 35 seconds, and turning it back on.
5. Tested access token renewal by providing a short TTL on the access token when logging in.
6. Safely closing the connection and exiting the loop after a manual stop is called, both and running and reconnecting state.

# License

## Open-source license

This software is provided under a noncontagious open-source license towards the open-source community. It's available under three open-source licenses:
 
* License: LGPL v3+, Apache, MIT

<p align="center">
  <a href="http://www.gnu.org/licenses/lgpl-3.0">
    <img src="https://img.shields.io/badge/License-LGPL%20v3-blue.svg" alt="License: LGPL v3" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
  <a href="https://opensource.org/licenses/Apache-2.0">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0" />
  </a>
</p>

## Commercial license

This software can also be provided under a commercial license. If you are not an open-source developer or are not planning to release adaptations to the code under one or multiple of the mentioned licenses, contact us to obtain a commercial license.

* License: Crownstone commercial license

# Contact

For any question contact us at <https://crownstone.rocks/contact/> or on our discord server through <https://crownstone.rocks/forum/>.
