import asyncio
import json
import multiprocessing as mp
import time

import websockets

from core.audio import AudioCapture
from src.utils.logger import get_logger

logger = get_logger(__name__)


# StreamClient manages the connection to the WebSocket server and sends audio captured by AudioCapture.
class StreamClient:
    MIN_BUFFER_SIZE = 32000  # When accumulated audio exceeds this, send it (in bytes)

    def __init__(self, server_url="ws://localhost:8000/stream", record_duration=5):
        self.server_url = server_url
        self.record_duration = record_duration
        self.audio_queue = mp.Queue()
        self.is_recording = mp.Event()
        self.audio_process = None

    def start_recording(self):
        self.is_recording.set()
        capture = AudioCapture(self.audio_queue, self.is_recording)
        self.audio_process = mp.Process(target=capture.start)
        self.audio_process.start()
        logger.info("StreamClient: Started recording process")

    def stop_recording(self):
        if self.is_recording.is_set():
            logger.info("StreamClient: Stopping recording")
            self.is_recording.clear()
        if self.audio_process:
            self.audio_process.join(timeout=2.0)
            if self.audio_process.is_alive():
                logger.warning("StreamClient: Terminating lingering audio process")
                self.audio_process.terminate()
            self.audio_process = None
            logger.info("StreamClient: Recording stopped")

    async def stream_microphone(self):
        audio_buffer = bytearray()
        end_sent = False
        start_time = time.time()
        # Open a WebSocket connection.
        async with websockets.connect(self.server_url) as websocket:
            logger.info("StreamClient: Connected to server")
            self.start_recording()
            # Loop until we receive a final message from the server
            while True:
                # Check if recording duration has elapsed & final data should be sent.
                if time.time() - start_time >= self.record_duration and not end_sent:
                    self.stop_recording()
                    if len(audio_buffer) > 0:
                        await websocket.send(bytes(audio_buffer))
                        logger.info("StreamClient: Sent remaining audio, cleared buffer")
                        audio_buffer.clear()
                    logger.info("StreamClient: Sending END marker")
                    await websocket.send(b"END\n")
                    end_sent = True

                if not end_sent:
                    try:
                        # Consume any available audio data from the queue.
                        data = self.audio_queue.get_nowait()
                        logger.info(f"StreamClient: Got {len(data)} bytes from queue")
                        audio_buffer.extend(data)
                        if len(audio_buffer) >= self.MIN_BUFFER_SIZE:
                            await websocket.send(bytes(audio_buffer))
                            logger.info("StreamClient: Sent audio chunk")
                            audio_buffer.clear()
                    except Exception:
                        # No data available; sleep briefly to yield control.
                        await asyncio.sleep(0.01)

                # Listen for messages from the server.
                try:
                    # Use a short timeout to periodically check the recording status.
                    message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                    msg = json.loads(message)
                    logger.info(f"StreamClient: Received message: {msg}")
                    yield msg
                    if msg.get("is_final"):
                        break
                except asyncio.TimeoutError:
                    continue
            await asyncio.sleep(0.1)
            logger.info("StreamClient: Stream ended")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.stop_recording()
