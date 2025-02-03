# Project Plan

## Final Product

- Press to talk
- Transcribe speech to text using pywhispercpp
    - Use [pywhispercpp](https://github.com/absadiki/pywhispercpp) for Whisper.cpp integration
    - Support Apple silicon chips (M1, M2, ...)
    - Support CUDA for GPU acceleration
    - Support real-time transcription via WebSocket
- Use LangChain to parse the text and clean up the text
    - E.g. "Ehh what is the emm wheather like in SF? no, Salt Lake City" -> "What is the weather like in Salt Lake City?"
    - Support multiple LLM providers

## Milestones

- [x] Speech to text setup
    - [x] Install pywhispercpp with CoreML support for Apple Silicon
    - [x] Basic transcription test
- [x] Basic git commit hook to check if the code is formatted
    - [x] Format the code
- [x] Voice Processing Server
    - [x] FastAPI server setup
    - [x] Audio upload endpoint
    - [x] Streaming audio support
- [x] LangChain Integration
    - [x] Test OpenAI API Key loading
    - [x] Chain configuration
    - [x] Text processing pipeline
    - [x] Response formatting
    - [ ] Support other LLMs (DeepSeek, Gemini, ...)
- [ ] Press to talk
    - [x] Key listener
    - [x] Capture a hot key regardless of the current application
    - [x] Put the final result in the system clipboard
    - [ ] Show an icon when voice control is active
- [ ] Context Management
    - [ ] System prompt configuration
    - [ ] Chat history persistence
- [ ] Documentation
    - [ ] API Documentation (OpenAPI/Swagger)
    - [ ] Usage examples and guides
