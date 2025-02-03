import asyncio
import json
import multiprocessing as mp
import time

import websockets

from core.audio import AudioCapture
from src.utils.decorators import handle_exceptions
from src.utils.logger import get_logger

logger = get_logger(__name__)


# StreamClient manages the connection to the WebSocket server and sends audio captured by AudioCapture.
class StreamClient:
    MIN_BUFFER_SIZE = 32000  # When accumulated audio exceeds this, send it (in bytes)

    def __init__(self, server_url="ws://localhost:8000/stream"):
        self.server_url = server_url
        self.audio_queue = mp.Queue()
        self.is_audio_capturing = mp.Event()
        self.stop_event = mp.Event()
        self.audio_process = None

    def _start_audio_capture(self):
        self.stop_event.clear()
        self.is_audio_capturing.set()
        capture = AudioCapture(self.audio_queue, self.is_audio_capturing)
        self.audio_process = mp.Process(target=capture.start)
        self.audio_process.start()
        logger.info("StreamClient: Started recording process")

    def _stop_audio_capture(self):
        if self.is_audio_capturing.is_set():
            logger.info("StreamClient: Stopping audio capture")
            self.is_audio_capturing.clear()
        if self.audio_process:
            self.audio_process.join(timeout=2.0)
            if self.audio_process.is_alive():
                logger.warning("StreamClient: Terminating lingering audio process")
                self.audio_process.terminate()
            self.audio_process = None
            logger.info("StreamClient: Audio capture stopped")

    def stop(self):
        self.stop_event.set()

    @handle_exceptions
    async def stream_microphone(self):
        audio_buffer = bytearray()
        end_sent = False
        logger.info("StreamClient: Connecting to server")
        async with websockets.connect(self.server_url) as websocket:
            logger.info("StreamClient: Connected to server")
            self._start_audio_capture()
            while True:
                # Check if the is_audio_capturing event has been cleared (e.g., hotkey released)
                if self.stop_event.is_set() and not end_sent:
                    self._stop_audio_capture()
                    if audio_buffer:
                        await websocket.send(bytes(audio_buffer))
                        logger.info("StreamClient: Sent remaining audio, cleared buffer")
                        audio_buffer.clear()
                    logger.info("StreamClient: Sending END marker")
                    await websocket.send(b"END\n")
                    end_sent = True

                if not end_sent:
                    try:
                        data = self.audio_queue.get_nowait()
                        logger.info(f"StreamClient: Got {len(data)} bytes from queue")
                        audio_buffer.extend(data)
                        if len(audio_buffer) >= self.MIN_BUFFER_SIZE:
                            await websocket.send(bytes(audio_buffer))
                            logger.info("StreamClient: Sent audio chunk")
                            audio_buffer.clear()
                    except Exception:
                        await asyncio.sleep(0.01)

                try:
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
        self._stop_audio_capture()
