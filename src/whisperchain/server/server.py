import asyncio
import os
from typing import List

import numpy as np
import pyaudio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pywhispercpp.model import Model, Segment

from whisperchain.core.chain import TranscriptionCleaner
from whisperchain.utils.logger import get_logger
from whisperchain.utils.segment import (
    list_of_segments_to_text,
    list_of_segments_to_text_with_timestamps,
)

logger = get_logger(__name__)

whisper_model = None
transcription_cleaner = None
DEBUG = bool(os.getenv("DEBUG"))

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    global whisper_model, transcription_cleaner
    logger.info("Initializing Whisper model...")
    whisper_model = Model()
    logger.info("Initializing transcription cleaner...")
    transcription_cleaner = TranscriptionCleaner()
    if DEBUG:
        logger.info("Running in DEBUG mode - audio playback enabled. Printing all chain logs.")


async def play_audio(audio_data: bytes):
    """Play the received audio data using PyAudio."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()
    p.terminate()


async def transcribe_audio(audio_data: bytes) -> List[Segment]:
    global whisper_model
    # Convert bytes to a numpy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    # Convert to float32
    audio_array = audio_array.astype(np.float32) / np.iinfo(np.int16).max
    # Transcribe the audio
    result: List[Segment] = whisper_model.transcribe(audio_array)
    return result


@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    received_data = b""
    while True:
        try:
            data = await websocket.receive_bytes()
        except WebSocketDisconnect:
            logger.info("Server: WebSocket disconnected")
            break

        if data.endswith(b"END\n"):
            # Remove the END marker and accumulate any remaining data.
            data_without_end = data[:-4]
            received_data += data_without_end
            # Transcribe the received audio
            segments = await transcribe_audio(received_data)
            # Clean the transcription
            cleaned_transcription = transcription_cleaner.clean(list_of_segments_to_text(segments))
            # Build a final message
            final_message = {
                "type": "transcription",
                "processed_bytes": len(received_data),
                "is_final": True,
                "transcription": list_of_segments_to_text_with_timestamps(segments),
                "cleaned_transcription": cleaned_transcription,
            }
            logger.info("Server: Sending final message: %s", final_message)
            await websocket.send_json(final_message)
            # Play back the received audio only in debug mode
            if DEBUG:
                logger.info("Server: Playing back received audio (DEBUG mode)...")
                await play_audio(received_data)
            await asyncio.sleep(0.1)
            break
        else:
            # Accumulate the incoming bytes and send an intermediate echo message.
            received_data += data
            echo_message = {
                "type": "transcription",
                "processed_bytes": len(data),
                "is_final": False,
            }
            logger.info("Server: Echoing message: %s", echo_message)
            await websocket.send_json(echo_message)
    try:
        await websocket.close()
    except RuntimeError as e:
        # Ignore errors if the connection is already closed/completed
        logger.warning("Server: Warning while closing websocket: %s", e)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
