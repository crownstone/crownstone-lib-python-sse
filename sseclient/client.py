import asyncio
import logging
import signal
import sys
import json
from datetime import timedelta
from aiohttp import ClientSession, ClientConnectionError
from sseclient.eventbus import EventBus
from sseclient.const import (
    EVENT_CLIENT_STOP,
    EVENT_BASE_URL,
    MAX_CONNECT_RETRY,
    RECONNECTION_TIME,
    system_events,
)
from sseclient.exceptions import (
    CrownstoneSseException,
    ConnectError,
)
from typing import Coroutine, Optional

_LOGGER = logging.getLogger(__name__)


class CrownstoneSSE:
    """Client that manages IO with cloud and event server"""

    def __init__(self, event_bus: EventBus, access_token: str) -> None:
        """Init the SSE client"""
        self.loop = asyncio.new_event_loop()
        self.websession: Optional[ClientSession] = None
        self.event_bus = event_bus
        self.access_token = access_token
        self._tasks = []
        self.state = "not_running"
        self.retries = MAX_CONNECT_RETRY
        self.reconnect_time: timedelta = RECONNECTION_TIME
        self.stop_event: Optional[asyncio.Event] = None

    def start(self):
        """
        Start the SSE client in a different OS thread
        Thread safe.
        """
        try:
            asyncio.set_event_loop(self.loop)
            return self.loop.run_until_complete(self.async_start())
        finally:
            self.loop.close()

    async def async_start(self) -> None:
        """start the SSE client in current OS thread."""
        if self.state != "not_running":
            _LOGGER.warning("Crownstone SSE client is already running")

        # create an event that can be set to stop the loop
        self.stop_event = asyncio.Event()

        # create loop specific websession
        self.websession = ClientSession(loop=self.loop)

        # add handler to loop for sigterm and sigint (linux)
        if sys.platform != "win32":
            self.loop.add_signal_handler(signal.SIGTERM, self.signal_handler, 0)
            self.loop.add_signal_handler(signal.SIGINT, self.signal_handler, 0)

        self.state = 'running'

        # run this code until stop event received
        while not self.stop_event.is_set():
            await self.request()

    async def request(self):
        """
        Request events from URL https://events.crownstone.rocks/.
        """
        try:
            async with self.websession.get(f'{EVENT_BASE_URL}{self.access_token}') as response:
                # raise exception for any status code higher than 400
                response.raise_for_status()

                # parse data and fire events
                event = self.create_task(self.parse_event(response))
                await event

                # restore parameters
                self.reconnect_time = RECONNECTION_TIME
                self.retries = MAX_CONNECT_RETRY
        except ClientConnectionError:
            if self.retries <= 0 or self.state == 'not_running':
                self.create_task(self.async_stop())
                raise CrownstoneSseException(ConnectError.CONNECTION_FAILED_AFTER_5_RETRIES)
            else:
                self.reconnect_time *= 2
                _LOGGER.warning('Reconnection in {} seconds'.format(self.reconnect_time.total_seconds()))
                await asyncio.sleep(self.reconnect_time.total_seconds())
                self.retries -= 1
            return

    async def parse_event(self, response):
        """Process a response from websession."""
        async for line_bytes in response.content:
            line = line_bytes.decode('utf8')  # string
            line = line.rstrip('\n').rstrip('\r')  # remove spaces and returns

            if line.startswith(':'):
                # ignore :ping
                continue

            if line.startswith('data:'):
                line = line.lstrip('data:')
                data = json.loads(line)  # type dict
                await self.fire_event(data)

    async def fire_event(self, data):
        """Fire event based on data."""
        if data['type'] == 'system':
            for event in system_events:
                if data['subType'] == event:
                    self.event_bus.fire(event, data)

        if data['type'] == 'command':
            """To do"""

        if data['type'] == 'presence':
            """To do"""

    def signal_handler(self) -> None:
        """
        Signal handler for main event loop.
        Linux only;
        SIGTERM: Terminate the process. Sent by an other process.
        SIGINT: Interrupt the process. (Ctrl + C pressed).
        """
        self.loop.remove_signal_handler(signal.SIGTERM)
        self.loop.remove_signal_handler(signal.SIGINT)
        self.create_task(self.async_stop())

    def create_task(self, target: Coroutine) -> asyncio.tasks.Task:
        """
        Create a task to run in the event loop.
        For task tracking purposes.
        """
        task = self.loop.create_task(target)
        self._tasks.append(task)
        _LOGGER.info("Task created.")

        return task

    async def finish_tasks(self) -> None:
        """
        Wait for all scheduled tasks to complete
        This is called when the client gets suddenly stopped.
        """
        while self._tasks:
            not_completed_tasks = []
            for task in self._tasks:
                if not task.done():
                    not_completed_tasks.append(task)
            # Refresh the task list, because all tasks are currently awaited
            self._tasks.clear()
            if not_completed_tasks:
                print(not_completed_tasks)
                await asyncio.wait(not_completed_tasks)

    def stop(self) -> None:
        """
        Stop the Crownstone SSE client from an other loop.
        Thread safe.
        """
        # TO DO

    async def async_stop(self) -> None:
        """Stop Crownstone SSE client from within the loop."""
        # ignore if not running or already stopping
        if self.state == "not_running":
            return
        if self.state == "stopping":
            _LOGGER.warning("stop already called")
            return

        # stop the client, finish remaining tasks
        self.state = "stopping"
        self.event_bus.fire(EVENT_CLIENT_STOP)
        await self.finish_tasks()

        # Close the ClientSession
        self.websession.detach()

        self.state = "not_running"
        # set the stop event, which will raise the block
        _LOGGER.warning("Crownstone SSE client stopped.")
        self.stop_event.set()