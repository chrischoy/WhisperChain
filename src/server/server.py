import asyncio
import json

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


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
            # Build a final message (for debugging we simply echo accumulated data)
            final_message = {
                "type": "transcription",
                "text": f"Final transcription: Received {len(received_data)} bytes",
                "is_final": True,
            }
            # Log and send the final message
            print("Server: Sending final message:", final_message)
            await websocket.send_json(final_message)
            # Give time for the message to be sent
            await asyncio.sleep(0.1)
            break
        else:
            # Accumulate the incoming bytes and send an intermediate echo message.
            received_data += data
            echo_message = {
                "type": "transcription",
                "text": f"Received chunk: {data.decode('utf-8', errors='ignore')}",
                "is_final": False,
            }
            print("Server: Echoing message:", echo_message)
            await websocket.send_json(echo_message)
    try:
        await websocket.close()
    except RuntimeError as e:
        # Ignore errors if the connection is already closed/completed
        print(f"Server: Warning while closing websocket: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
