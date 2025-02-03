import pytest

from whisperchain.client.key_listener import HotKeyRecordingListener


@pytest.fixture
def listener():
    # Create an instance of HotKeyRecordingListener with the default hotkey.
    listener = HotKeyRecordingListener("<ctrl>+<alt>+r")
    return listener


def test_on_activate(listener):
    # Initially, no recording and not pressed.
    assert listener.pressed is False
    print(f"Please press the hotkey: {listener.combination}")
    listener.start()
