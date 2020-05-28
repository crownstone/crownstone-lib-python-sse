import asynctest
from crownstone_sse.util.eventbus import EventBus
from crownstone_sse.const import EVENT_SYSTEM_STREAM_START, EVENT_SYSTEM_STREAM_CLOSE


class TestEventBus(asynctest.TestCase):
    """Test the event bus"""

    def setUp(self) -> None:
        self.eventbus = EventBus()

    def test_event_bus(self):
        test_callback_runs = []
        test_callback2_runs = []

        def test_callback(event):
            test_callback_runs.append(event)

        def test_callback2(event):
            test_callback2_runs.append(event)

        # add test listeners
        test_listener = self.eventbus.add_event_listener(EVENT_SYSTEM_STREAM_START, test_callback)
        self.eventbus.add_event_listener(EVENT_SYSTEM_STREAM_START, test_callback2)
        self.eventbus.add_event_listener(EVENT_SYSTEM_STREAM_CLOSE, test_callback2)
        # test if event type added to dict
        assert EVENT_SYSTEM_STREAM_START in self.eventbus.event_listeners
        assert EVENT_SYSTEM_STREAM_CLOSE in self.eventbus.event_listeners
        # test the list of callables
        assert len(self.eventbus.event_listeners[EVENT_SYSTEM_STREAM_START]) == 2
        assert len(self.eventbus.event_listeners[EVENT_SYSTEM_STREAM_CLOSE]) == 1

        listeners = self.eventbus.get_event_listeners()

        assert isinstance(listeners, dict)
        assert listeners[EVENT_SYSTEM_STREAM_START] == 2
        assert listeners[EVENT_SYSTEM_STREAM_CLOSE] == 1

        self.eventbus.fire(EVENT_SYSTEM_STREAM_START, 'test_event')
        self.eventbus.fire(EVENT_SYSTEM_STREAM_CLOSE, 'test_event')

        assert len(test_callback_runs) == 1
        assert len(test_callback2_runs) == 2

        # test removal of event listener
        self.eventbus.remove_event_listener(EVENT_SYSTEM_STREAM_START, test_listener)
        assert test_callback not in self.eventbus.event_listeners[EVENT_SYSTEM_STREAM_START]