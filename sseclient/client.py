import asyncio
import logging
import signal
import sys
import json
import hashlib
from datetime import timedelta
from threading import Thread
from aiohttp import (
    ClientSession,
    ClientConnectionError,
    ClientPayloadError
)
from sseclient.eventbus import EventBus
from sseclient.const import (
    EVENT_CLIENT_STOP,
    EVENT_BASE_URL,
    LOGIN_URL,
    MAX_CONNECT_RETRY,
    RECONNECTION_TIME,
    EVENT_SYSTEM_TOKEN_EXPIRED,
    EVENT_SWITCH_STATE_UPDATE,
    system_events,
    presence_events,
    command_events,
    data_change_events,
    operations
)
from sseclient.events import (
    SystemEvent,
    CommandEvent,
    PresenceEvent,
    DataChangeEvent,
    SwitchStateUpdateEvent
)
from sseclient.exceptions import (
    sse_exception_handler,
    CrownstoneSseException,
    ConnectError,
)
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class CrownstoneSSE(Thread):
    """Client that manages IO with cloud and event server"""

    def __init__(self, access_token: str = None) -> None:
        """Init the SSE client"""
        self.loop = asyncio.new_event_loop()
        self.loop.set_exception_handler(sse_exception_handler)
        self.websession: ClientSession = ClientSession(loop=self.loop)
        self.event_bus: EventBus = EventBus()
        self.state = "not_running"
        self.retries = MAX_CONNECT_RETRY
        self.reconnect_time: timedelta = RECONNECTION_TIME
        self.stop_event: Optional[asyncio.Event] = None
        # Instance information
        self.access_token = access_token
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        # Initialize thread
        super().__init__(target=self.run)

    def run(self):
        """Start the SSE client"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.async_start())

    async def async_start(self) -> None:
        """start the SSE client in current OS thread."""
        if self.state != "not_running":
            _LOGGER.warning("Crownstone SSE client is already running")

        if self.access_token is None:
            if not self.email or not self.password:
                _LOGGER.error("No access token available and no email/password provided. Use .set_user_information()")
            else:
                await self.login()

        # create an event that can be set to stop the loop
        self.stop_event = asyncio.Event()

        # add handler to loop for sigterm and sigint (linux)
        if sys.platform != "win32":
            self.loop.add_signal_handler(signal.SIGTERM, self.signal_handler, 0)
            self.loop.add_signal_handler(signal.SIGINT, self.signal_handler, 0)

        # Connect to the event server & start streaming
        await self.connect()

        self.state = 'running'

    def set_user_information(self, email: str, password: str):
        self.email = email
        self.password = password

    async def login(self) -> None:
        """Login to Crownstone using email and password"""
        shasum = hashlib.sha1(self.password.encode('utf-8'))
        hashed_password = shasum.hexdigest()

        # Create JSON object with login credentials
        data = {
            "email": self.email,
            "password": hashed_password,
        }
        # login
        try:
            async with self.websession.post(LOGIN_URL, data=data) as result:
                result.raise_for_status()
                data = await result.json()
                self.access_token = data['id']
        except ClientConnectionError:
            _LOGGER.error("Could not connect to the crownstone cloud")

        _LOGGER.warning("Login successful")

    async def connect(self):
        """
        Open a stream on URL https://events.crownstone.rocks/.
        """
        try:
            async with self.websession.get(f'{EVENT_BASE_URL}{self.access_token}') as response:
                response.raise_for_status()
                await self.stream(response)
        except ClientConnectionError:
            if self.retries <= 0:
                await self.async_stop()
                raise CrownstoneSseException(ConnectError.CONNECTION_FAILED_AFTER_5_RETRIES)
            else:
                self.reconnect_time *= 2
                _LOGGER.warning('Reconnection in {} seconds'.format(self.reconnect_time.total_seconds()))
                await asyncio.sleep(self.reconnect_time.total_seconds())
                await self.connect()

    async def stream(self, stream_response):
        """Start streaming"""
        # aiohttp StreamReader instance
        stream_reader = stream_response.content

        while stream_response.status != 204:  # no data
            try:
                async for event in stream_reader:
                    if self.stop_event.is_set():
                        break
                    event = event.decode('utf8')  # string
                    event = event.rstrip('\n').rstrip('\r')  # remove returns

                    if event.startswith(':'):
                        # ignore :ping
                        continue

                    if event.startswith('data:'):
                        line = event.lstrip('data:')
                        data = json.loads(line)  # type dict
                        await self.fire_events(data)
            except asyncio.exceptions.TimeoutError:
                # pass on timeout error raised from none, only stop on event, and no data.
                print("hallo")
            except ClientPayloadError:
                # Connection was lost, payload uncompleted. try to reconnect
                await self.connect()

    async def fire_events(self, data) -> None:
        """Fire event based on the data"""
        if data['type'] == 'system':
            for system_event in system_events:
                if data['subType'] == system_event:
                    if system_event == EVENT_SYSTEM_TOKEN_EXPIRED:
                        await self.refresh_token()
                    event = SystemEvent(data)
                    self.event_bus.fire(system_event, event)

        if data['type'] == 'command':
            for command_event in command_events:
                if data['subType'] == command_event:
                    event = CommandEvent(data)
                    self.event_bus.fire(command_event, event)

        if data['type'] == EVENT_SWITCH_STATE_UPDATE:
            event = SwitchStateUpdateEvent(data)
            self.event_bus.fire(EVENT_SWITCH_STATE_UPDATE, event)

        if data['type'] == 'dataChange':
            for data_change_event in data_change_events:
                if data['subType'] == data_change_event:
                    for operation in operations:
                        if data['operation'] == operation:
                            event = DataChangeEvent(data, operation)
                            self.event_bus.fire(data_change_event, event)

        if data['type'] == 'presence':
            for presence_event in presence_events:
                if data['subType'] == presence_event:
                    event = PresenceEvent(data)
                    self.event_bus.fire(presence_event, event)

    async def signal_handler(self) -> None:
        """
        Signal handler for main event loop.
        Linux only;
        SIGTERM: Terminate the process. Sent by an other process.
        SIGINT: Interrupt the process. (Ctrl + C pressed).
        """
        self.loop.remove_signal_handler(signal.SIGTERM)
        self.loop.remove_signal_handler(signal.SIGINT)
        await self.async_stop()

    def add_event_listener(self, event_type, callback):
        self.event_bus.add_event_listener(event_type=event_type, event_listener=callback)

    async def refresh_token(self) -> None:
        """Refresh token when token expired event received"""
        await self.login()
        await self.connect()

    def stop(self) -> None:
        """
        Stop the Crownstone SSE client from an other thread.
        Thread safe.
        """

    async def async_stop(self) -> None:
        """Stop Crownstone SSE client from within the loop."""
        # ignore if not running or already stopping
        if self.state == "not_running":
            return
        if self.state == "stopping":
            _LOGGER.warning("stop already called")
            return

        # stop the client, finish remaining tasks
        self.stop_event.set()
        self.state = "stopping"
        self.event_bus.fire(EVENT_CLIENT_STOP)  # callback

        # Close the ClientSession
        await self.websession.close()

        self.state = "not_running"
        _LOGGER.warning("Crownstone SSE client stopped.")
