import asyncio
import json
import os
import tempfile
import urllib.request

import pytest
import websockets
from fastapi.websockets import WebSocketDisconnect

from src.utils.logger import get_logger

logger = get_logger()


@pytest.fixture
def test_audio_path():
    """Fixture to download and provide a test audio file"""
    # Using a small public domain audio file from Wikimedia
    audio_url = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Example.ogg"

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp_file:
        # Download the file
        urllib.request.urlretrieve(audio_url, tmp_file.name)
        audio_path = tmp_file.name

    yield audio_path

    # Cleanup after test
    if os.path.exists(audio_path):
        os.unlink(audio_path)


@pytest.mark.asyncio
async def test_websocket_streaming(test_audio_path):
    """Test WebSocket streaming with audio file"""
    logger.info("Starting WebSocket test")

    async with websockets.connect("ws://localhost:8000/stream") as websocket:
        logger.info("WebSocket connected")

        # Send audio in chunks
        with open(test_audio_path, "rb") as f:
            while chunk := f.read(4096):  # 4KB chunks
                logger.debug(f"Sending chunk of size {len(chunk)}")
                await websocket.send(chunk)
                # Add small delay to allow processing
                await asyncio.sleep(0.1)

            # Send end marker
            logger.info("Sending END marker")
            await websocket.send(b"END\n")

        # Should receive multiple messages during transcription
        messages = []
        timeout = 0
        max_timeout = 50  # 5 seconds total timeout

        # Keep receiving messages until we get a final one or timeout
        while timeout < max_timeout:
            try:
                # Set a short timeout for each receive
                message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                data = json.loads(message)
                logger.debug(f"Received message: {data}")

                if data["type"] == "heartbeat":
                    continue

                messages.append(data)

                # Break if we get a final message
                if data.get("is_final", False):
                    logger.info("Received final message")
                    break

            except asyncio.TimeoutError:
                timeout += 1
                continue
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break

        # Verify message format and content
        assert len(messages) > 0, "Should receive at least one transcription"
        for msg in messages:
            assert msg["type"] == "transcription"
            assert "text" in msg
            assert "start" in msg
            assert "end" in msg
            assert "is_final" in msg
            assert isinstance(msg["text"], str)
            assert isinstance(msg["start"], (int, float))
            assert isinstance(msg["end"], (int, float))
            assert isinstance(msg["is_final"], bool)

        # Verify we got a final message
        assert any(
            msg.get("is_final", False) for msg in messages
        ), "Should receive a final message"
