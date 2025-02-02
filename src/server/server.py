import asyncio
import json

import pyaudio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI()


async def play_audio(audio_data: bytes):
    """Play the received audio data using PyAudio."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()
    p.terminate()


@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    received_data = b""
    while True:
        try:
            data = await websocket.receive_bytes()
        except WebSocketDisconnect:
            break

        if data.endswith(b"END\n"):
            # Remove the END marker and accumulate any remaining data.
            data_without_end = data[:-4]
            received_data += data_without_end
            # Build a final message
            final_message = {
                "type": "transcription",
                "text": f"Final transcription: Received {len(received_data)} bytes",
                "is_final": True,
            }
            logger.info("Server: Sending final message: %s", final_message)
            await websocket.send_json(final_message)
            # Play back the received audio
            logger.info("Server: Playing back received audio...")
            await play_audio(received_data)
            await asyncio.sleep(0.1)
            break
        else:
            # Accumulate the incoming bytes and send an intermediate echo message.
            received_data += data
            echo_message = {
                "type": "transcription",
                "text": f"Received chunk: {len(data)} bytes",  # Changed to show byte count instead of decoding
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
