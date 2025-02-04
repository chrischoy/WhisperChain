import multiprocessing as mp
from typing import Optional

import click
import uvicorn

from whisperchain.client.key_listener import HotKeyRecordingListener
from whisperchain.core.config import ClientConfig, ServerConfig
from whisperchain.server.server import WhisperServer
from whisperchain.utils.secrets import load_secrets


def run_server(config: ServerConfig):
    """Run the FastAPI server."""
    server = WhisperServer(config)
    uvicorn.run(server.app, host=config.host, port=config.port)


def run_client(config: Optional[ClientConfig] = None):
    """Run the key listener client."""
    listener = HotKeyRecordingListener(config=config)
    listener.start()


@click.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8000, help="Server port")
@click.option("--model", default="base.en", help="Whisper model name")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(exists=True), help="Path to config JSON file")
@click.option("--hotkey", help="Override hotkey combination")
def main(
    host: str, port: int, model: str, debug: bool, config: Optional[str], hotkey: Optional[str]
):
    """Start both the server and client processes."""
    # Initialize secrets
    load_secrets()

    # Load config if provided
    client_config = None
    server_config = None

    if config:
        import json

        with open(config) as f:
            config_dict = json.load(f)
            client_config = ClientConfig.model_validate(config_dict.get("client", {}))
            server_config = ServerConfig.model_validate(config_dict.get("server", {}))

    # Override with CLI options
    server_config = server_config or ServerConfig()
    if host:
        server_config.host = host
    if port:
        server_config.port = port
    if model:
        server_config.model_name = model
    server_config.debug = debug

    if hotkey:
        client_config = client_config or ClientConfig()
        client_config.hotkey = hotkey

    # Start server in a separate process
    server_process = mp.Process(target=run_server, args=(server_config,), name="WhisperServer")
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
