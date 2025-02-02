import multiprocessing as mp
import os
import time

import pytest

from src.client.stream_client import AudioCapture


# Run if TEST_WITH_MIC is set
@pytest.mark.skipif(not os.getenv("TEST_WITH_MIC"), reason="Requires microphone input")
def test_audio_capture():
    q = mp.Queue()
    is_recording = mp.Event()
    is_recording.set()
    capture_instance = AudioCapture(q, is_recording)
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
