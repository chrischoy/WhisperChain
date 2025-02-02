# Project Plan

## Final Product

- Press to talk
- Transcribe speech to text using pywhispercpp
    - Use [pywhispercpp](https://github.com/absadiki/pywhispercpp) for Whisper.cpp integration
    - Support Apple silicon chips (M1, M2, ...)
    - Support CUDA for GPU acceleration
- Use LangChain to parse the text and clean up the text
    - E.g. "Ehh what is the emm wheather like in SF? no, Salt Lake City" -> "What is the weather like in Salt Lake City?"

## Milestones

- [ ] Speech to text setup
    - [ ] Install pywhispercpp with CoreML support for Apple Silicon
    - [ ] Basic transcription test
- [ ] Basic git commit hook to check if the code is formatted
    - [ ] Format the code
- [ ] Voice control integration
    - [ ] Set up pywhispercpp assistant mode
    - [ ] Configure audio input/output
    - [ ] Handle transcription events
- [ ] LangChain
    - [ ] Test OpenAI API Key loading
    - [ ] Parse the text and clean up the text
    - [ ] Support other LLMs (DeepSeek, Gemini, ...)
- [ ] Press to talk
    - [ ] Add a button to toggle voice control
        - [ ] Capture a hot key regardless of the current application
    - [ ] Show an icon when voice control is active
- [ ] Capture the context
    - [ ] System prompt
    - [ ] Chat history
