import os
import platform
import tempfile
import urllib.request

import pytest
from pywhispercpp.model import Model


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


def test_whisper_model_loading():
    """Test that we can load the basic whisper model"""
    try:
        # Initialize model with base.en model
        model = Model("base.en", print_realtime=False, print_progress=False)
        assert model is not None, "Model should be loaded successfully"
    except Exception as e:
        pytest.fail(f"Failed to load whisper model: {str(e)}")


def test_basic_transcription(test_audio_path):
    """Test basic transcription functionality"""
    model = Model("base.en", print_realtime=False, print_progress=False)

    # Test transcription
    result = model.transcribe(test_audio_path)
    print(result)
    assert isinstance(result, list), "Transcription result should be a list of segments"
    assert len(result) > 0, "Transcription result should not be empty"
    assert hasattr(result[0], "text"), "Segments should have text attribute"


@pytest.mark.skipif(
    platform.system() != "Darwin" or not os.environ.get("WHISPER_COREML"),
    reason="CoreML tests only run on MacOS with WHISPER_COREML=1",
)
def test_coreml_support():
    """Test CoreML support on MacOS"""
    model = Model("base.en", print_realtime=False, print_progress=False)

    # Get system info to verify CoreML
    system_info = Model.system_info()
    # CoreML support is shown in system info
    assert "CoreML" in str(system_info), "CoreML support should be enabled on MacOS"
