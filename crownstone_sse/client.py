import asyncio
import logging
import json
import hashlib
import time
from threading import Thread
from aiohttp import (
    ClientSession,
    ClientConnectionError,
    ClientPayloadError
)
from crownstone_sse.util.eventbus import EventBus
from crownstone_sse.const import (
    EVENT_BASE_URL, LOGIN_URL,
    RECONNECTION_TIME,
    CONNECTION_TIMEOUT,
    EVENT_SYSTEM,
    EVENT_COMMAND,
    EVENT_PRESENCE,
    EVENT_DATA_CHANGE,
    OPERATION,
    EVENT_SWITCH_STATE_UPDATE,
    EVENT_ABILITY_CHANGE,
    EVENT_CLIENT_STOP,
    EVENT_SYSTEM_TOKEN_EXPIRED,
    EVENT_SYSTEM_NO_CONNECTION,
    system_events,
    presence_events,
    command_events,
    data_change_events,
    ability_change_events,
    operations,
    TYPE, SUBTYPE, ID, ERROR, CODE, DATA, UTF8, PING,
    RUNNING, NOT_RUNNING, STOPPING,
    LOGIN_FAILED, LOGIN_FAILED_EMAIL_NOT_VERIFIED
)
from crownstone_sse.events.SystemEvent import SystemEvent
from crownstone_sse.events.CommandEvent import CommandEvent
from crownstone_sse.events.DataChangeEvent import DataChangeEvent
from crownstone_sse.events.PresenceEvent import PresenceEvent
from crownstone_sse.events.SwitchStateUpdateEvent import SwitchStateUpdateEvent
from crownstone_sse.events.AbilityChangeEvent import AbilityChangeEvent
from crownstone_sse.exceptions import (
    sse_exception_handler,
    CrownstoneSseException,
    CrownstoneConnectionTimeout,
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
        self.state = NOT_RUNNING
        self.available = False
        self.stop_event: Optional[asyncio.Event] = None
        # Instance information
        self.access_token: Optional[str] = None
        self.email = email
        self.password = password
        # Initialize thread
        super().__init__(target=self.run)

    @property
    def is_available(self) -> bool:
        """Return if Crownstone SSE is available"""
        return self.available

    def run(self):
        """Start the SSE client"""
        try:
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.async_start())
        finally:
            self.loop.close()

    async def async_start(self) -> None:
        """start the SSE client in current OS thread."""
        if self.state != NOT_RUNNING:
            _LOGGER.debug("Crownstone SSE client is already running")

        if self.access_token is None:
            if not self.email or not self.password:
                _LOGGER.error("No access token available and no email/password provided. Use .set_access_token")
            else:
                await self.login()

        # create events for stop trigger
        self.stop_event = asyncio.Event()

        # Connect to the event server & start streaming
        self.state = RUNNING
        await self.connect()

    def set_access_token(self, access_token: str):
        self.access_token = access_token

    async def login(self) -> None:
        """Login to Crownstone using email and password"""
        shasum = hashlib.sha1(self.password.encode(UTF8))
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
                    self.access_token = data[ID]
                elif result.status == 401:
                    if ERROR in data:
                        error = data[ERROR]
                        if error[CODE] == LOGIN_FAILED:
                            raise CrownstoneSseException(AuthError.AUTHENTICATION_ERROR, "Wrong email/password")
                        elif error[CODE] == LOGIN_FAILED_EMAIL_NOT_VERIFIED:
                            raise CrownstoneSseException(AuthError.EMAIL_NOT_VERIFIED, "Email not verified")
                else:
                    raise CrownstoneSseException(AuthError.UNKNOWN_ERROR, "Unknown error occurred")
        except ClientConnectionError:
            raise CrownstoneSseException(ConnectError.CONNECTION_FAILED_NO_INTERNET, "No internet connection")

        _LOGGER.debug("Login successful")

    async def connect(self):
        """
        Open a stream on URL https://events.crownstone.rocks/.
        """
        try:
            async with self.websession.get(f'{EVENT_BASE_URL}{self.access_token}') as response:
                response.raise_for_status()
                await self.stream(response)
        except ClientConnectionError:
            _LOGGER.debug('Internet connection lost. Reconnection in {} seconds'.format(RECONNECTION_TIME))
            await asyncio.sleep(RECONNECTION_TIME)
            if self.state == NOT_RUNNING:
                return
            await self.connect()

    async def stream(self, stream_response):
        """Start streaming"""
        # aiohttp StreamReader instance
        stream_reader = stream_response.content
        # client is now available for receiving events
        self.available = True
        _LOGGER.info("Crownstone SSE Client has started.")

        try:
            # start params
            line_in_bytes = b''
            start_time = time.perf_counter()
            while stream_response.status != 204:  # no data
                # read the buffer of the stream
                chunk = stream_reader.read_nowait()
                for line in chunk.splitlines(True):
                    line_in_bytes += line
                    if line_in_bytes.endswith((b'\r\r', b'\n\n', b'\r\n\r\n')):
                        line = line_in_bytes.decode(UTF8)  # string
                        line = line.rstrip('\n').rstrip('\r')  # remove returns

                        if line.startswith(PING):
                            # connection alive received, update start time
                            start_time = time.perf_counter()

                        if line.startswith(DATA):
                            line = line.lstrip(DATA)
                            data = json.loads(line)  # type dict
                            # check for access token expiration and login + restart client
                            # no need to fire event for this first
                            if data[TYPE] == EVENT_SYSTEM and data[SUBTYPE] == EVENT_SYSTEM_TOKEN_EXPIRED:
                                await self.refresh_token()
                            # check for no connection between the sse server and the crownstone cloud
                            # log this issue
                            if data[TYPE] == EVENT_SYSTEM and data[SUBTYPE] == EVENT_SYSTEM_NO_CONNECTION:
                                _LOGGER.warning("No connection to Crownstone cloud, waiting for server to come back "
                                                "online")
                            # handle firing of events
                            self.fire_events(data)

                        line_in_bytes = b''

                # break if stop event is set after stop received
                # at the end of the loop for testing purposes
                if self.stop_event.is_set():
                    break

                # a ping is sent every 30 seconds to notify the connection is alive
                # if a ping event has not been sent after 40 seconds (10 second margin), raise connection error
                if time.perf_counter() - start_time > CONNECTION_TIMEOUT:
                    raise CrownstoneConnectionTimeout(ConnectError.CONNECTION_TIMEOUT, "Connection to server timed out")

                # let buffer fill itself with data
                await asyncio.sleep(0.05)

        except CrownstoneConnectionTimeout:
            # Internet connection was lost, try to reconnect
            _LOGGER.warning("Connection to server timed out, trying to reconnect...")
            self.available = False
            await self.connect()

        except ClientPayloadError:
            # Internet connection was lost, payload uncompleted. try to reconnect
            # This exception only occurred on Windows.
            self.available = False
            await self.connect()

        except KeyboardInterrupt:
            # Ctrl + C pressed or other command that causes interrupt
            await self.async_stop()

    def fire_events(self, data) -> None:
        """Fire event based on the data"""
        if data[TYPE] == EVENT_SYSTEM:
            for system_event in system_events:
                if data[SUBTYPE] == system_event:
                    event = SystemEvent(data)
                    self.event_bus.fire(system_event, event)

        if data[TYPE] == EVENT_COMMAND:
            for command_event in command_events:
                if data[SUBTYPE] == command_event:
                    event = CommandEvent(data)
                    self.event_bus.fire(command_event, event)

        if data[TYPE] == EVENT_SWITCH_STATE_UPDATE:
            event = SwitchStateUpdateEvent(data)
            self.event_bus.fire(EVENT_SWITCH_STATE_UPDATE, event)

        if data[TYPE] == EVENT_DATA_CHANGE:
            for data_change_event in data_change_events:
                if data[SUBTYPE] == data_change_event:
                    for operation in operations:
                        if data[OPERATION] == operation:
                            event = DataChangeEvent(data, data_change_event, operation)
                            self.event_bus.fire(data_change_event, event)

        if data[TYPE] == EVENT_PRESENCE:
            for presence_event in presence_events:
                if data[SUBTYPE] == presence_event:
                    event = PresenceEvent(data, presence_event)
                    self.event_bus.fire(presence_event, event)

        if data[TYPE] == EVENT_ABILITY_CHANGE:
            for ability_change_event in ability_change_events:
                if data[SUBTYPE] == ability_change_event:
                    event = AbilityChangeEvent(data, ability_change_event)
                    self.event_bus.fire(ability_change_event, event)

    def add_event_listener(self, event_type, callback):
        self.event_bus.add_event_listener(event_type=event_type, event_listener=callback)

    async def refresh_token(self) -> None:
        """Refresh token when token expired event received"""
        await self.login()
        await self.connect()

    def stop(self) -> None:
        """Stop the Crownstone SSE client from an other thread."""
        # ignore if not running
        if self.state == NOT_RUNNING:
            return
        asyncio.run_coroutine_threadsafe(self.async_stop(), self.loop)

    async def async_stop(self) -> None:
        """Stop Crownstone SSE client from within the loop."""
        # ignore if not running or already stopping
        if self.state == NOT_RUNNING:
            return
        if self.state == STOPPING:
            _LOGGER.debug("stop already called")
            return

        self.state = STOPPING
        self.available = False
        self.event_bus.fire(EVENT_CLIENT_STOP)  # for callback

        # Close the ClientSession
        await self.websession.close()

        self.state = NOT_RUNNING
        self.stop_event.set()
        _LOGGER.info("Crownstone SSE client stopped.")
