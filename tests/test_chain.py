import pytest
from pywhispercpp.model import Segment

from whisperchain.core.chain import TranscriptionCleaner
from whisperchain.utils.segment import list_of_segments_to_text


@pytest.fixture
def cleaner():
    return TranscriptionCleaner()


def test_transcription_cleaner(cleaner):
    assert cleaner.clean("Hello, world!") == "Hello, world!"


def test_list_of_segments(cleaner):
    segments = [
        Segment(0, 100, "ummm"),
        Segment(100, 200, "Hello, world!"),
    ]
    final_text = list_of_segments_to_text(segments)
    assert final_text == "ummm Hello, world!"

    cleaned_text = cleaner.clean(final_text)
    assert cleaned_text == "Hello, world!"
