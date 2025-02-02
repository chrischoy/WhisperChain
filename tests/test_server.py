import os
import platform
import tempfile
import urllib.request

import pytest
from fastapi.testclient import TestClient

from src.server.app import app

client = TestClient(app)


@pytest.fixture
def test_audio_path():
    """Fixture to download and provide a test audio file"""
    # Using a small public domain audio file from Wikimedia
    audio_url = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Example.ogg"

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp_file:
        # Download the file
        urllib.request.urlretrieve(audio_url, tmp_file.name)
        audio_path = tmp_file.name

    yield audio_path

    # Cleanup after test
    if os.path.exists(audio_path):
        os.unlink(audio_path)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_transcribe_no_file():
    """Test transcription endpoint with no file"""
    response = client.post("/transcribe")
    assert response.status_code == 422  # FastAPI validation error


def test_transcribe_with_audio(test_audio_path):
    """Test transcription with actual audio file"""
    with open(test_audio_path, "rb") as f:
        response = client.post("/transcribe", files={"file": ("test_audio.ogg", f, "audio/ogg")})

    assert response.status_code == 200
    result = response.json()
    assert "filename" in result
    assert "transcription" in result
    assert isinstance(result["transcription"], list)


@pytest.mark.skipif(
    platform.system() != "Darwin" or not os.environ.get("WHISPER_COREML"),
    reason="CoreML tests only run on MacOS with WHISPER_COREML=1",
)
def test_coreml_support():
    """Test CoreML support on MacOS"""
    response = client.get("/health")  # Just checking if server starts with CoreML
    assert response.status_code == 200
