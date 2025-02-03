import multiprocessing as mp
from typing import Optional

import click
import uvicorn

from whisperchain.client.key_listener import HotKeyRecordingListener
from whisperchain.core.config import ClientConfig
from whisperchain.server.server import app


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server."""
    uvicorn.run(app, host=host, port=port)


def run_client(config: Optional[ClientConfig] = None):
    """Run the key listener client."""
    listener = HotKeyRecordingListener(config=config)
    listener.start()


@click.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8000, help="Server port")
@click.option("--config", type=click.Path(exists=True), help="Path to config JSON file")
@click.option("--hotkey", help="Override hotkey combination")
def main(host: str, port: int, config: Optional[str], hotkey: Optional[str]):
    """Start both the server and client processes."""
    # Load config if provided
    client_config = None
    if config:
        import json

        with open(config) as f:
            config_dict = json.load(f)
            client_config = ClientConfig.parse_obj(config_dict)
    if hotkey:
        client_config = client_config or ClientConfig()
        client_config.hotkey = hotkey

    # Start server in a separate process
    server_process = mp.Process(target=run_server, args=(host, port), name="WhisperServer")
    server_process.start()

    try:
        # Start client in the main process
        run_client(client_config)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        if server_process.is_alive():
            server_process.terminate()
            server_process.join()


if __name__ == "__main__":
    main()
