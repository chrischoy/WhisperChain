import multiprocessing as mp

import pyaudio

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AudioCapture:
    SAMPLE_RATE = 16000
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    CHUNK_SIZE = 4096  # ~256ms at 16kHz

    def __init__(self, queue: mp.Queue, is_recording: mp.Event):
        self.queue = queue
        self.is_recording = is_recording
        self.audio = None
        self.stream = None

    def start(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE,
        )
        logger.info("AudioCapture: Started capturing audio")
        while self.is_recording.is_set():
            try:
                data = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                logger.info(f"AudioCapture: Captured {len(data)} bytes")
                self.queue.put(data)
            except Exception as e:
                logger.error(f"AudioCapture error: {e}")
                break
        self.cleanup()

    def cleanup(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        logger.info("AudioCapture: Stopped capturing audio")
