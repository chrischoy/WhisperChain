import os
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .server import WhisperServer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app"""
    # Initialize Whisper server as singleton on startup
    whisper_server = WhisperServer()
    yield
    # Add cleanup here if needed in the future


app = FastAPI(
    title="Whisper Transcription Server",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Whisper server as singleton
whisper_server = WhisperServer()


@app.post("/transcribe")
async def transcribe_file(file: UploadFile = File(...)):
    """
    Endpoint to transcribe audio files
    Accepts audio file uploads and returns transcription
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Create temporary file to handle upload
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            # Write uploaded file to temp file
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()

            # Transcribe the audio
            result = await whisper_server.transcribe_file(temp_file.name)

            return {"filename": file.filename, "transcription": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Cleanup temp file
            os.unlink(temp_file.name)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio streaming
    Accepts audio chunks and returns transcriptions
    """
    async for transcription in whisper_server.transcribe_websocket(websocket):
        await websocket.send_json(transcription)  # Send each yielded message
