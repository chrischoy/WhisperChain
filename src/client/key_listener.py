from pynput import keyboard

from src.client.stream_client import StreamClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HotKeyListener:
    def __init__(self, combination_str="<ctrl>+<alt>+r"):
        self.pressed = False
        # Parse the string into a combination set.
        self.combination = keyboard.HotKey.parse(combination_str)
        # Initialize a HotKey object with on_activate callback.
        self.hotkey = keyboard.HotKey(self.combination, self.on_activate)

    def on_activate(self):
        if not self.pressed:
            logger.info(f"Global hotkey: {self.combination} activated!")
            self.pressed = True

    def on_deactivate(self, key):
        # Release the key in the HotKey object.
        self.hotkey.release(key)
        if self.pressed:
            logger.info(f"Global hotkey: {self.combination} deactivated!")
            self.pressed = False

    def start(self):
        # Helper function to transform key press events.
        def for_canonical(f):
            return lambda k: f(listener.canonical(k))

        # Create a Listener using the canonical transformation.
        with keyboard.Listener(
            on_press=for_canonical(self.hotkey.press),
            on_release=for_canonical(self.on_deactivate),
        ) as listener:
            listener.join()


class HotKeyRecordingListener(HotKeyListener):
    def __init__(self, combination_str="<ctrl>+<alt>+r"):
        super().__init__(combination_str)
        # Create an instance of StreamClient.
        self.client = StreamClient()
        self.recording = False

    def on_activate(self):
        super().on_activate()
        if not self.recording:
            self.client.start_recording()
            self.recording = True

    def on_deactivate(self, key):
        super().on_deactivate(key)
        if self.recording:
            self.client.stop_recording()
            self.recording = False


if __name__ == "__main__":
    listener = HotKeyListener("<ctrl>+<alt>+r")
    listener.start()
