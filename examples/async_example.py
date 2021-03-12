"""
Async example of receiving Crownstone SSE events.

Created by Ricardo Steijn.
Last update on 03-11-2021.
"""
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
    client = CrownstoneSSEAsync(
        email="example@example.com",
        password="CrownstoneRocks"
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
