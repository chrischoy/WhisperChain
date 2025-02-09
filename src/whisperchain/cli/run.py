import multiprocessing as mp
import sys
from pathlib import Path
from typing import Optional

import click
import streamlit.web.cli as stcli
import uvicorn

from whisperchain.client.key_listener import HotKeyRecordingListener
from whisperchain.core.config import ClientConfig, ServerConfig, config
from whisperchain.server.server import WhisperServer


def run_server(server_config: ServerConfig):
    """Run the WhisperServer with given config"""
    server = WhisperServer(config=server_config)
    uvicorn.run(server.app, host=server_config.host, port=server_config.port)


def run_ui():
    """Run the Streamlit UI"""
    # Ensure config is up to date
    config.generate_streamlit_config()

    # Get the UI script path
    ui_path = Path(__file__).parent.parent / "ui" / "streamlit_app.py"

    # Just run the script, config.toml will be used automatically
    sys.argv = ["streamlit", "run", str(ui_path)]
    stcli.main()


def run_client(client_config: ClientConfig):
    """Run the recording client"""
    listener = HotKeyRecordingListener(config=client_config)
    listener.start()


@click.command()
@click.option("--server-only", is_flag=True, help="Run only the server")
@click.option("--ui-only", is_flag=True, help="Run only the UI")
@click.option("--client-only", is_flag=True, help="Run only the client")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def main(server_only: bool, ui_only: bool, client_only: bool, debug: bool):
    """Run WhisperChain components"""
    server_process = None
    ui_process = None
    client_process = None

    try:
        # Load configs
        server_config = ServerConfig(debug=debug)
        client_config = ClientConfig()

        # Start components based on flags
        if server_only:
            run_server(server_config)
        elif ui_only:
            run_ui()
        elif client_only:
            run_client(client_config)
        else:
            # Start server in separate process
            server_process = mp.Process(target=run_server, args=(server_config,))
            server_process.start()

            # Start UI in separate process
            ui_process = mp.Process(target=run_ui)
            ui_process.start()

            # Run client in main process
            run_client(client_config)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup processes
        if server_process and server_process.is_alive():
            server_process.terminate()
            server_process.join()
        if ui_process and ui_process.is_alive():
            ui_process.terminate()
            ui_process.join()


if __name__ == "__main__":
    main()
