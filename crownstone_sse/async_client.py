"""
Asynchronous iterator class that connects to the Crownstone Cloud,
and returns received events in data containers.

This class must be used in the event loop.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from enum import Enum, auto
from typing import Any

import aiohttp

from crownstone_sse.const import (
    CONNECTION_TIMEOUT,
    CONTENT_TYPE,
    EVENT_BASE_URL,
    EVENT_SYSTEM_NO_CONNECTION,
    EVENT_SYSTEM_TOKEN_EXPIRED,
    LOGIN_FAILED,
    LOGIN_FAILED_EMAIL_NOT_VERIFIED,
    LOGIN_URL,
    NO_CACHE,
    RECONNECTION_TIME,
)
from crownstone_sse.events import Event, SystemEvent, parse_event
from crownstone_sse.exceptions import (
    AuthError,
    ClientError,
    ConnectError,
    CrownstoneAuthException,
    CrownstoneClientException,
    CrownstoneConnectionException,
)
from crownstone_sse.helpers.aiohttp_client import create_client_session

_LOGGER = logging.getLogger(__name__)


class AsyncClientState(Enum):
    """Represent the current state of async Crownstone SSE client."""

    CONNECTING = auto()
    RUNNING = auto()
    CLOSED = auto()


class CrownstoneSSEAsync:
    """Crownstone event client async iterator."""

    _client_response: aiohttp.ClientResponse

    def __init__(
        self,
        email: str,
        password: str,
        access_token: str | None = None,
        websession: aiohttp.ClientSession | None = None,
        reconnection_time: int = RECONNECTION_TIME,
    ) -> None:
        """Initialize event client.

        :param email: Crownstone account email address.
            Used for login and automatic access token renewal.
        :param password: Crownstone account password.
            Used for login and automatic access token renewal.
        :param access_token: Access token obtained from logging in successfully
            to the Crownstone cloud. Can be provided to skip an extra login, for faster setup.
        :param websession: An aiohttp ClientSession instance.
            Creates a default session when none provided.
        :param reconnection_time: Time between reconnection in case of connection failure.
        """
        self._email = email
        self._password = password
        self._access_token = access_token
        self._available = False

        if websession is None:
            self.websession = create_client_session()
            self._close_session = True
        else:
            self.websession = websession
            self._close_session = False

        self._state = AsyncClientState.CLOSED
        self._reconnection_time = reconnection_time
        self._sleep_task: asyncio.Task[Any] | None = None

    @property
    def is_available(self) -> bool:
        """Returns whether the client is currently running."""
        return bool(self._state == AsyncClientState.RUNNING)

    async def __aenter__(self) -> CrownstoneSSEAsync:
        """Login & establish a new connection to the Crownstone SSE server."""
        if self._access_token is None:
            await self._async_login()
        await self._async_connect()

        return self

    async def __aexit__(self, *exc_info: tuple[Any]) -> None:
        """Close the connection to the Crownstone SSE server."""
        if self._client_response is not None:
            self._client_response.close()

        if self._close_session:
            await self.websession.close()

        self._state = AsyncClientState.CLOSED
        _LOGGER.debug("Crownstone SSE client closed.")

    async def __anext__(self) -> Event:
        """Return the next event"""
        # safeguard
        if not hasattr(self, "_client_response"):
            raise CrownstoneConnectionException(ConnectError.CONNECTION_NO_RESPONSE)

        # aiohttp StreamReader supports asynchronous iteration by line
        # the default separator is \n
        # this method already ensures we get complete data
        while self._client_response.status != 204:
            try:
                async for line in self._client_response.content:
                    # convert to string and remove returns/delimiters
                    line_str: str = line.decode("utf-8")
                    line_str = line_str.rstrip("\n").rstrip("\r")

                    # only look at the data lines, ignore everything else
                    if line_str.startswith("data:"):
                        line_str = line_str.lstrip("data:")
                        data: dict[str, Any] = json.loads(line_str)

                        event = parse_event(data)
                        # handle important system events
                        if isinstance(event, SystemEvent):
                            if event.sub_type == EVENT_SYSTEM_TOKEN_EXPIRED:
                                raise CrownstoneAuthException(AuthError.TOKEN_EXPIRED)
                            if event.sub_type == EVENT_SYSTEM_NO_CONNECTION:
                                _LOGGER.warning(event.message)

                        return event

            except aiohttp.ClientPayloadError:
                # a payload error due to packet loss
                # reconnection should retrieve server side cached events
                await self._async_connect()

            except aiohttp.ServerTimeoutError:
                # Read timeout. A ping event is send every 30 seconds
                # After 35 seconds no data, connection must be lost
                await self._async_reconnect()

            except CrownstoneAuthException as auth_err:
                # handle re-auth and reconnection
                if auth_err.type == AuthError.TOKEN_EXPIRED:
                    await self._async_login()
                    await self._async_connect()

            except CrownstoneClientException as client_err:
                # client is manually closed
                if client_err.type == ClientError.CLOSE_RECEIVED:
                    break

        raise StopAsyncIteration

    def __aiter__(self) -> CrownstoneSSEAsync:
        """Return instance."""
        return self

    async def _async_login(self) -> None:
        """Login to Crownstone Cloud using email and password."""
        sha_hash = hashlib.sha1(self._password.encode("utf-8"))
        hashed_password = sha_hash.hexdigest()

        # Create JSON object with login credentials
        login_data = {"email": self._email, "password": hashed_password}

        try:
            # login
            response = await self.websession.post(LOGIN_URL, json=login_data)
            data: dict[str, Any] = await response.json()
            # success
            if response.status == 200:
                self._access_token = data["id"]
                _LOGGER.debug("Login successful")
            # auth error
            elif response.status == 401:
                if "error" in data:
                    error = data["error"]
                    if error["code"] == LOGIN_FAILED:
                        raise CrownstoneAuthException(
                            AuthError.AUTHENTICATION_ERROR, "Wrong email/password"
                        )
                    if error["code"] == LOGIN_FAILED_EMAIL_NOT_VERIFIED:
                        raise CrownstoneAuthException(
                            AuthError.EMAIL_NOT_VERIFIED, "Email not verified"
                        )
            # unknown error
            else:
                raise CrownstoneAuthException(
                    AuthError.UNKNOWN_ERROR, "Unknown error occurred"
                )

        except aiohttp.ClientConnectionError as err:
            raise CrownstoneConnectionException(
                ConnectError.CONNECTION_FAILED_NO_INTERNET, "No internet connection"
            ) from err

    async def _async_connect(self) -> None:
        """Open a connection to the HTTP server."""
        # Headers for this request
        # According to SSE specification
        headers = {
            aiohttp.hdrs.CONTENT_TYPE: CONTENT_TYPE,
            aiohttp.hdrs.ACCEPT: CONTENT_TYPE,
            aiohttp.hdrs.CACHE_CONTROL: NO_CACHE,
        }

        # Override the default total timeout of 5 minutes for this stream
        # Stream should be alive forever unless explicitly stopped
        # a ping event is send every 30 second, if nothing is read, reconnect
        sse_timeout = aiohttp.ClientTimeout(total=None, sock_read=CONNECTION_TIMEOUT)

        try:
            response = await self.websession.get(
                url=f"{EVENT_BASE_URL}{self._access_token}",
                headers=headers,
                timeout=sse_timeout,
            )
            # Raises ClientResponseError
            response.raise_for_status()

            # aiohttp.ClientResponse instance
            self._client_response = response
            self._state = AsyncClientState.RUNNING
            _LOGGER.info("Crownstone SSE client is running.")

        except (aiohttp.ClientConnectionError, aiohttp.ClientResponseError):
            # keep trying to connect
            await self._async_reconnect()

    async def _async_reconnect(self) -> None:
        """Reconnect to the server after a connection loss / data error."""
        # lost connection to the SSE server, try to reconnect
        # log once
        if self._state != AsyncClientState.CONNECTING:
            _LOGGER.warning(
                "Lost connection to the Crownstone SSE server. "
                "Reconnecting in 30 seconds."
            )

        self._state = AsyncClientState.CONNECTING
        self._sleep_task = asyncio.create_task(asyncio.sleep(self._reconnection_time))
        try:
            await self._sleep_task
        except asyncio.CancelledError as err:
            raise StopAsyncIteration from err
        finally:
            self._sleep_task = None

        await self._async_connect()

    def close_client(self) -> None:
        """Manually close the Crownstone SSE client."""
        if self._state == AsyncClientState.CLOSED:
            return

        # If we're currently waiting on reconnecting
        # stop the task to exit immediately
        if self._sleep_task is not None:
            self._sleep_task.cancel()

        # Set an exception in StreamReader to stop the iteration
        if self._client_response is not None:
            self._client_response.content.set_exception(
                CrownstoneClientException(
                    ClientError.CLOSE_RECEIVED, "Connection close received"
                )
            )
