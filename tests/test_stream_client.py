import asyncio
import os
from time import sleep

import pytest

from src.client.stream_client import StreamClient
from src.utils.logger import get_logger

logger = get_logger()


@pytest.mark.skipif(
    not os.getenv("TEST_WITH_MIC"),
    reason="Requires microphone input. Run with TEST_WITH_MIC=1 to enable.",
)
@pytest.mark.asyncio
async def test_stream_client_with_real_mic():
    """
    Test StreamClient with actual microphone input.

    This test requires human interaction:
    1. Speak into the microphone when test starts
    2. Test will record for 5 seconds
    3. Server will play back the received audio
    4. Verify that the playback matches what was spoken

    Run with:
        TEST_WITH_MIC=1 pytest tests/test_stream_client.py -v -k test_stream_client_with_real_mic
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

    async with StreamClient(record_duration=5) as client:
        async for message in client.stream_microphone():
            messages.append(message)
            # Extract byte count from message text if available
            if not message.get("is_final"):
                try:
                    byte_count = int(message["text"].split(": ")[1].split(" ")[0])
                    total_bytes_sent += byte_count
                except (IndexError, ValueError):
                    pass
            if message.get("is_final"):
                final_byte_count = int(message["text"].split(": Received ")[1].split(" ")[0])
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
