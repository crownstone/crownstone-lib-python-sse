import asyncio
import logging
import json
import hashlib
from threading import Thread
from aiohttp import (
    ClientSession,
    ClientConnectionError,
    ClientPayloadError
)
from crownstone_sse.util.eventbus import EventBus
from crownstone_sse.const import (
    EVENT_CLIENT_STOP,
    EVENT_BASE_URL,
    LOGIN_URL,
    RECONNECTION_TIME,
    EVENT_SYSTEM_TOKEN_EXPIRED,
    EVENT_SYSTEM_NO_CONNECTION,
    EVENT_SWITCH_STATE_UPDATE,
    system_events,
    presence_events,
    command_events,
    data_change_events,
    operations
)
from crownstone_sse.events.SystemEvent import SystemEvent
from crownstone_sse.events.CommandEvent import CommandEvent
from crownstone_sse.events.DataChangeEvent import DataChangeEvent
from crownstone_sse.events.PresenceEvent import PresenceEvent
from crownstone_sse.events.SwitchStateUpdateEvent import SwitchStateUpdateEvent
from crownstone_sse.exceptions import (
    sse_exception_handler,
    CrownstoneSseException,
    ConnectError,
    AuthError,
)
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class CrownstoneSSE(Thread):
    """Client that manages IO with cloud and event server"""

    def __init__(self, email: str, password: str) -> None:
        """Init the SSE client"""
        self.loop = asyncio.new_event_loop()
        self.loop.set_exception_handler(sse_exception_handler)
        self.websession: ClientSession = ClientSession(loop=self.loop, read_timeout=None)
        self.event_bus: EventBus = EventBus()
        self.state = "not_running"
        self.stop_event: Optional[asyncio.Event] = None
        # Instance information
        self.access_token: Optional[str] = None
        self.email = email
        self.password = password
        # Initialize thread
        super().__init__(target=self.run)

    def run(self):
        """Start the SSE client"""
        try:
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.async_start())
        finally:
            self.loop.close()

    async def async_start(self) -> None:
        """start the SSE client in current OS thread."""
        if self.state != "not_running":
            _LOGGER.warning("Crownstone SSE client is already running")

        if self.access_token is None:
            if not self.email or not self.password:
                _LOGGER.error("No access token available and no email/password provided. Use .set_access_token")
            else:
                await self.login()

        # create events for stop trigger
        self.stop_event = asyncio.Event()

        # Connect to the event server & start streaming
        await self.connect()

    def set_access_token(self, access_token: str):
        self.access_token = access_token

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
                data = await result.json()
                if result.status == 200:
                    self.access_token = data['id']
                elif result.status == 401:
                    if 'error' in data:
                        error = data['error']
                        if error['code'] == 'LOGIN_FAILED':
                            raise CrownstoneSseException(AuthError.AUTHENTICATION_ERROR, "Wrong email/password")
                        elif error['code'] == 'LOGIN_FAILED_EMAIL_NOT_VERIFIED':
                            raise CrownstoneSseException(AuthError.EMAIL_NOT_VERIFIED, "Email not verified")
                else:
                    raise CrownstoneSseException(AuthError.UNKNOWN_ERROR, "Unknown error occurred")
        except ClientConnectionError:
            raise CrownstoneSseException(ConnectError.CONNECTION_FAILED_NO_INTERNET, "No internet connection")

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
            _LOGGER.warning('Internet connection lost. Reconnection in {} seconds'.format(RECONNECTION_TIME))
            await asyncio.sleep(RECONNECTION_TIME)
            await self.connect()

    async def stream(self, stream_response):
        """Start streaming"""
        # aiohttp StreamReader instance
        stream_reader = stream_response.content
        # client is now running, and can be stopped
        self.state = "running"

        try:
            line_in_bytes = b''
            while stream_response.status != 204:  # no data
                # read the buffer of the stream
                chunk = stream_reader.read_nowait()
                for line in chunk.splitlines(True):
                    line_in_bytes += line
                    if line_in_bytes.endswith((b'\r\r', b'\n\n', b'\r\n\r\n')):
                        line = line_in_bytes.decode('utf8')  # string
                        line = line.rstrip('\n').rstrip('\r')  # remove returns

                        if line.startswith('data:'):
                            line = line.lstrip('data:')
                            data = json.loads(line)  # type dict
                            # check for access token expiration and login + restart client
                            # no need to fire event for this first
                            if data['type'] == 'system' and data['subType'] == EVENT_SYSTEM_TOKEN_EXPIRED:
                                await self.refresh_token()
                            # check for no connection between the sse server and the crownstone cloud
                            # simply try to reconnect
                            if data['type'] == 'system' and data['subType'] == EVENT_SYSTEM_NO_CONNECTION:
                                await self.connect()
                            # handle firing of events
                            self.fire_events(data)

                        line_in_bytes = b''

                # break if stop event is set after stop received
                # at the end of the loop for testing purposes
                if self.stop_event.is_set():
                    break

                # let buffer fill itself with data
                await asyncio.sleep(0.05)

        except ClientPayloadError:
            # Internet connection was lost, payload uncompleted. try to reconnect
            # .connect() will handle further reconnection
            await self.connect()
        except KeyboardInterrupt:
            # Ctrl + C pressed or other command that causes interrupt
            await self.async_stop()

    def fire_events(self, data) -> None:
        """Fire event based on the data"""
        if data['type'] == 'system':
            for system_event in system_events:
                if data['subType'] == system_event:
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
                            event = DataChangeEvent(data, data_change_event, operation)
                            self.event_bus.fire(data_change_event, event)

        if data['type'] == 'presence':
            for presence_event in presence_events:
                if data['subType'] == presence_event:
                    event = PresenceEvent(data, presence_event)
                    self.event_bus.fire(presence_event, event)

    def add_event_listener(self, event_type, callback):
        self.event_bus.add_event_listener(event_type=event_type, event_listener=callback)

    async def refresh_token(self) -> None:
        """Refresh token when token expired event received"""
        await self.login()
        await self.connect()

    def stop(self) -> None:
        """Stop the Crownstone SSE client from an other thread."""
        # ignore if not running
        if self.state == 'not_running':
            return
        self.loop.create_task(self.async_stop())

    async def async_stop(self) -> None:
        """Stop Crownstone SSE client from within the loop."""
        # ignore if not running or already stopping
        if self.state == "not_running":
            return
        if self.state == "stopping":
            _LOGGER.warning("stop already called")
            return

        self.state = "stopping"
        self.event_bus.fire(EVENT_CLIENT_STOP)  # for callback

        # Close the ClientSession
        await self.websession.close()

        self.state = "not_running"
        self.stop_event.set()
        _LOGGER.warning("Crownstone SSE client stopped.")
