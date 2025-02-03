import asyncio
import os
from time import sleep

import pytest

from whisperchain.client.stream_client import StreamClient
from whisperchain.utils.logger import get_logger

logger = get_logger(__name__)


async def stop_after(client, seconds):
    await asyncio.sleep(seconds)
    # Clear the recording flag to trigger the stop logic in stream_microphone()
    client.stop()
    logger.info(f"Test: Cleared audio capturing flag after {seconds} seconds.")


@pytest.mark.skipif(
    not os.getenv("TEST_WITH_MIC"),
    reason="Requires microphone input. Run with TEST_WITH_MIC=1 to enable.",
)
@pytest.mark.asyncio
async def test_stream_client_with_real_mic():
    """
    Test StreamClient with actual microphone input.
    This test will record for 5 seconds and then force-stop the streamer.
    """
    print("\n=== Real Microphone Test ===")
    print("Please speak into your microphone when recording starts")
    print("Recording will last for 5 seconds")
    print("3...")
    sleep(1)
    print("2...")
    sleep(1)
    print("1...")
    sleep(1)
    print("Recording NOW!")

    messages = []
    total_bytes_sent = 0

    async with StreamClient() as client:
        # Schedule clearing the recording flag after 5 seconds.
        asyncio.create_task(stop_after(client, 5))
        async for message in client.stream_microphone():
            messages.append(message)
            # Extract byte count from message text if available
            if not message.get("is_final"):
                try:
                    byte_count = int(message["processed_bytes"])
                    total_bytes_sent += byte_count
                except (IndexError, ValueError):
                    pass
            if message.get("is_final"):
                final_byte_count = int(message["processed_bytes"])
                break

    print("\nTest Results:")
    print(f"Total bytes sent in chunks: {total_bytes_sent}")
    print(f"Final bytes received by server: {final_byte_count}")
    print("\nServer should now play back the received audio.")
    print("Please verify that the playback matches what you spoke.")

    # Basic assertions
    assert len(messages) > 0, "Should receive at least one message"
    assert any(msg.get("is_final") for msg in messages), "Should receive final message"
    assert final_byte_count > 0, "Server should receive nonzero bytes"
    assert (
        abs(total_bytes_sent - final_byte_count) < 8192
    ), "Bytes sent should approximately match bytes received"
