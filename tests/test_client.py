import asynctest
import asyncio
import aiohttp
import threading
from crownstone_sse.client import CrownstoneSSE
from crownstone_sse.util.eventbus import EventBus
from crownstone_sse.exceptions import CrownstoneSseException, AuthError
from tests.mocked_replies.login_data import login_data
from tests.mock_classes.response import MockResponse, MockStreamResponse
from tests.mocked_replies.stream_response import stream_data, token_expired_data, no_connection_data
from tests.mocked_replies.login_errors import auth_error, not_verified
from tests.mocked_events.system_events import stream_start
from crownstone_sse.events.SystemEvent import SystemEvent


class TestCrownstoneSSE(asynctest.TestCase):
    """Test the main class"""

    def setUp(self):
        self.sse_client = CrownstoneSSE('email', 'password')

    def test_init(self):
        assert isinstance(self.sse_client, threading.Thread)
        assert isinstance(self.sse_client.loop, asyncio.AbstractEventLoop)
        assert isinstance(self.sse_client.websession, aiohttp.ClientSession)
        assert isinstance(self.sse_client.event_bus, EventBus)

    def test_run(self):
        with asynctest.patch.object(CrownstoneSSE, 'async_start') as start_mock:
            self.sse_client.start()

        start_mock.assert_called()
        assert self.sse_client.is_alive()

    @asynctest.patch.object(CrownstoneSSE, 'connect')
    async def test_start(self, mock_connect):
        # test access token check
        with asynctest.patch.object(CrownstoneSSE, 'login') as login_mock_no_token:
            await self.sse_client.async_start()

        # login should be called, because access token is None
        login_mock_no_token.assert_called()
        login_mock_no_token.assert_awaited()

        # set an access token
        self.sse_client.set_access_token('access_token')

        with asynctest.patch.object(CrownstoneSSE, 'login') as login_mock_token:
            await self.sse_client.async_start()

        # login should not be called
        login_mock_token.assert_not_called()

    @asynctest.patch('aiohttp.ClientSession.post')
    async def test_login(self, request_mock):
        # mock regular login
        request_mock.return_value = MockResponse(200, login_data)
        await self.sse_client.login()
        assert self.sse_client.access_token == login_data['id']

        # mock login with wrong email/password
        request_mock.return_value = MockResponse(401, auth_error)
        with self.assertRaises(CrownstoneSseException) as auth_err:
            await self.sse_client.login()
        assert auth_err.exception.type == AuthError.AUTHENTICATION_ERROR

        # mock login with email not verified
        request_mock.return_value = MockResponse(401, not_verified)
        with self.assertRaises(CrownstoneSseException) as not_verified_err:
            await self.sse_client.login()
        assert not_verified_err.exception.type == AuthError.EMAIL_NOT_VERIFIED

        # mock login with unknown error
        request_mock.return_value = MockResponse(501, {})
        with self.assertRaises(CrownstoneSseException) as unknown_err:
            await self.sse_client.login()
        assert unknown_err.exception.type == AuthError.UNKNOWN_ERROR

    @asynctest.patch('aiohttp.ClientSession.get')
    async def test_connect(self, mocked_exception):
        # mock raising exception
        mocked_exception.side_effect = aiohttp.ClientConnectionError('test')
        # stop the function for recalling itself forever
        with asynctest.patch.object(CrownstoneSSE, 'connect') as connect_mock:
            await self.sse_client.connect()

        # test if function called correctly
        connect_mock.assert_called()

    @asynctest.patch('aiohttp.StreamReader.read_nowait')
    async def test_stream(self, mock_stream):
        mock_stream.return_value = stream_data
        mock_stream_response = MockStreamResponse(200)
        # fake stop event
        self.sse_client.stop_event = asyncio.Event()
        self.sse_client.stop_event.set()
        # mock the fire events function
        with asynctest.patch.object(CrownstoneSSE, 'fire_events') as fire_event_mock:
            await self.sse_client.stream(mock_stream_response)

        # test if data correctly received and parsed
        fire_event_mock.assert_called_once_with({'type': 'testType', 'subType': 'testSubType'})

        # test no data available
        mock_stream_response = MockStreamResponse(204)
        with asynctest.patch.object(CrownstoneSSE, 'fire_events') as fire_event_mock:
            await self.sse_client.stream(mock_stream_response)

        # test if fire events is not called this time
        fire_event_mock.assert_not_called()

        # mock token expired
        mock_stream.return_value = token_expired_data
        mock_stream_response = MockStreamResponse(200)
        with asynctest.patch.object(CrownstoneSSE, 'refresh_token') as refresh_mock:
            await self.sse_client.stream(mock_stream_response)

        # test refresh call
        refresh_mock.assert_called_once()

        # mock no connection to cloud
        mock_stream.return_value = no_connection_data
        with asynctest.patch.object(CrownstoneSSE, 'connect') as connect_mock:
            await self.sse_client.stream(mock_stream_response)

        # test reconnection
        connect_mock.assert_called_once()

        # mock connect function
        mock_stream.side_effect = aiohttp.ClientPayloadError('test')
        with asynctest.patch.object(CrownstoneSSE, 'connect') as connect_mock:
            await self.sse_client.stream(mock_stream_response)

        # test if reconnect called
        connect_mock.assert_called_once()

    @asynctest.patch.object(EventBus, 'fire')
    def test_fire_events(self, mock_fire):
        # test events
        with asynctest.patch.object(SystemEvent, '__init__') as system_event_mock:
            system_event_mock.return_value = None
            self.sse_client.fire_events(stream_start)
        # test event creation
        system_event_mock.assert_called_once_with(stream_start)
        assert len(mock_fire.mock_calls) == 1

    @asynctest.patch.object(CrownstoneSSE, 'login')
    @asynctest.patch.object(CrownstoneSSE, 'connect')
    async def test_refresh(self, mock_login, mock_connect):
        await self.sse_client.refresh_token()
        mock_connect.assert_called_once()
        mock_login.assert_called_once()
        mock_connect.assert_awaited()
        mock_login.assert_awaited()

    async def test_stop(self):
        self.sse_client.stop_event = asyncio.Event()
        # set state to running for test
        self.sse_client.state = 'running'
        await self.sse_client.async_stop()

        assert self.sse_client.stop_event.is_set()
        assert self.sse_client.state == 'not_running'
        assert self.sse_client.websession.closed
