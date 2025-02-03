# Whisper Chain

<p align="center">
  <img src="https://github.com/chrischoy/WhisperChain/raw/main/assets/logo.jpg" width="30%" alt="Whisper Chain Logo" />
</p>

## Overview

Typing is boring, let's use voice to control your computer. This project combines:
- Real-time speech recognition using Whisper.cpp
- Transcription cleanup using LangChain
- Global hotkey support for voice control
- Automatic clipboard integration for the cleaned transcription

## Requirements

- Python 3.8+
- OpenAI API Key
- For MacOS:
  - ffmpeg (for audio processing)
  - portaudio (for audio capture)

## Installation

1. Install system dependencies (MacOS):
```bash
# Install ffmpeg and portaudio using Homebrew
brew install ffmpeg portaudio
```

2. Install the project:

```bash
pip install build
python -m build
pip install .
```

## Usage

1. Start the application:
```bash
# Run with default settings
whisperchain

# Run with custom configuration
whisperchain --config config.json

# Override specific settings
whisperchain --port 8080 --hotkey "<ctrl>+<alt>+t"
```

2. Use the global hotkey (`<ctrl>+<alt>+r` by default. `<ctrl>+<option>+r` on MacOS):
   - Press and hold to start recording
   - Speak your text
   - Release to stop recording
   - The cleaned transcription will be copied to your clipboard automatically

The application will start both the server and client processes. Press Ctrl+C to stop both processes.

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
TEST_WITH_MIC=1 pytest tests/test_stream_client.py -v -k test_stream_client_with_real_mic

# Run all tests including microphone test
TEST_WITH_MIC=1 pytest tests/
```

### Building the project

```bash
pip install build
python -m build
pip install .
```

## License

[LICENSE](LICENSE)

## Acknowledgments

- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- [pywhispercpp](https://github.com/absadiki/pywhispercpp.git)
- [LangChain](https://github.com/langchain-ai/langchain)
