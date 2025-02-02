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
    1. Speak into the microphone when test starts.
    2. Recording will last for 5 seconds.
    3. Verify that a final transcription message is received from the server.

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
    # Create the stream client with record_duration set to 5 seconds
    async with StreamClient(record_duration=5) as client:
        async for message in client.stream_microphone():
            messages.append(message)
            if message.get("is_final"):
                break

    print("\nReceived messages:")
    for msg in messages:
        print(f"[{'FINAL' if msg.get('is_final') else 'partial'}] {msg.get('text')}")

    # Basic assertions to ensure proper behavior.
    assert len(messages) > 0, "Should receive at least one transcription"
    assert any(
        msg.get("is_final", False) for msg in messages
    ), "Should receive final transcription"
