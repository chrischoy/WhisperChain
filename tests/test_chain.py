import pytest

from src.server.chain import TranscriptionCleaner


def test_transcription_cleaner():
    cleaner = TranscriptionCleaner()
    assert cleaner.clean("Hello, world!") == "Hello, world!"
