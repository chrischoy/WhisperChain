import multiprocessing as mp
import os
import time

import pyaudio
import pytest

from whisperchain.core.audio import AudioCapture
from whisperchain.core.config import AudioConfig


@pytest.mark.skipif(not os.getenv("TEST_WITH_MIC"), reason="Requires microphone input")
def test_audio_capture():
    q = mp.Queue()
    is_recording = mp.Event()
    is_recording.set()
    # Create an AudioCapture instance with default config
    capture_instance = AudioCapture(q, is_recording, config=AudioConfig())
    process = mp.Process(target=capture_instance.start)
    process.start()

    record_duration = 5  # seconds
    print("Test: Recording for 5 seconds...", flush=True)
    time.sleep(record_duration)
    # Stop recording gracefully and wait for the process to finish.
    is_recording.clear()

    # Get the total number of bytes captured.
    total_bytes = 0
    while not q.empty():
        try:
            data = q.get_nowait()
            total_bytes += len(data)
        except Exception:
            break
    assert total_bytes > 0, "No audio was captured"

    process.join(timeout=2.0)
    if process.is_alive():
        process.terminate()
        process.join()


@pytest.mark.skipif(not os.getenv("TEST_WITH_MIC"), reason="Requires microphone input")
def test_audio_playback():
    # Capture audio for 5 seconds and play it back.
    q = mp.Queue()
    is_recording = mp.Event()
    is_recording.set()
    config = AudioConfig()  # Use default config for playback
    # Create an AudioCapture instance with default config
    capture_instance = AudioCapture(q, is_recording, config=config)
    process = mp.Process(target=capture_instance.start)
    process.start()

    record_duration = 5  # seconds
    print("Test: Recording for 5 seconds...", flush=True)
    time.sleep(record_duration)
    # Stop recording gracefully and wait for the process to finish.
    is_recording.clear()

    # Get the total number of bytes captured.
    audio_data = bytearray()
    total_bytes = 0
    while not q.empty():
        try:
            data = q.get_nowait()
            audio_data.extend(data)
            total_bytes += len(data)
        except Exception:
            break
    assert total_bytes > 0, "No audio was captured"

    # Play the audio back using the same format as configured
    pyaudio.PyAudio().open(
        format=getattr(pyaudio, f"pa{config.format.capitalize()}"),
        channels=config.channels,
        rate=config.sample_rate,
        output=True,
    ).write(bytes(audio_data))
