# Whisper LangChain

## Overview

Typing is boring, let's use voice to control your computer.

## Requirements

- Python 3.8+
- OpenAI API Key
- For MacOS:
  - Xcode Command Line Tools (for pywhispercpp)
  - ffmpeg (for audio processing)

## Installation

1. Install system dependencies (MacOS):
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install ffmpeg using Homebrew
brew install ffmpeg
brew install portaudio
```

2. Install the project:

For MacOS (includes CoreML support):
```bash
# Install with CoreML support
WHISPER_COREML=1 pip install -e .
```

For other platforms:
```bash
pip install -e .
```

## Development

### Running Tests

Install test dependencies:
```bash
pip install -e ".[test]"
```

Run tests:
```bash
pytest tests/
```

Run tests with microphone input:
```bash
# Run specific microphone test
TEST_WITH_MIC=1 pytest tests/test_client.py -v -k test_stream_client_with_real_mic

# Run all tests including microphone test
TEST_WITH_MIC=1 pytest tests/
```

For MacOS CoreML tests:
```bash
WHISPER_COREML=1 pytest tests/
```
