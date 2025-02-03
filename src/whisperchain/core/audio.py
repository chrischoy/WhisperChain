import multiprocessing as mp

import pyaudio

from whisperchain.core.config import AudioConfig
from whisperchain.utils.logger import get_logger

logger = get_logger(__name__)


class AudioCapture:
    def __init__(self, queue: mp.Queue, is_recording: mp.Event, config: AudioConfig = None):
        self.queue = queue
        self.is_recording = is_recording
        self.config = config or AudioConfig()
        self.audio = None
        self.stream = None

    def start(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=getattr(pyaudio, f"pa{self.config.format.capitalize()}"),
            channels=self.config.channels,
            rate=self.config.sample_rate,
            input=True,
            frames_per_buffer=self.config.chunk_size,
        )
        logger.info("AudioCapture: Started capturing audio")
        while self.is_recording.is_set():
            try:
                data = self.stream.read(self.config.chunk_size, exception_on_overflow=False)
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
