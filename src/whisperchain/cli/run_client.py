import json
from typing import Optional

import click

from whisperchain.client.key_listener import HotKeyRecordingListener
from whisperchain.core.config import ClientConfig


@click.command()
@click.option("--hotkey", default="<ctrl>+<alt>+r", help="Hotkey to start/stop recording")
@click.option("--config", type=click.Path(exists=True), help="Path to config JSON file")
@click.option("--sample-rate", type=int, help="Audio sample rate in Hz")
@click.option("--channels", type=int, help="Number of audio channels")
@click.option("--chunk-size", type=int, help="Audio chunk size")
@click.option("--server-url", help="WebSocket server URL")
def main(
    hotkey: str,
    config: Optional[str],
    sample_rate: Optional[int],
    channels: Optional[int],
    chunk_size: Optional[int],
    server_url: Optional[str],
):
    """Start the voice control client."""
    # Load base configuration
    if config:
        with open(config) as f:
            config_dict = json.load(f)
        client_config = ClientConfig.parse_obj(config_dict)
    else:
        client_config = ClientConfig()

    # Override with command line arguments if provided
    if hotkey:
        client_config.hotkey = hotkey
    if sample_rate:
        client_config.audio.sample_rate = sample_rate
    if channels:
        client_config.audio.channels = channels
    if chunk_size:
        client_config.audio.chunk_size = chunk_size
    if server_url:
        client_config.server_url = server_url

    listener = HotKeyRecordingListener(hotkey=client_config.hotkey, config=client_config)
    listener.start()


if __name__ == "__main__":
    main()
