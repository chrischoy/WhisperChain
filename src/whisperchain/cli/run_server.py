import click
import uvicorn

from whisperchain.core.config import ServerConfig
from whisperchain.server.server import WhisperServer
from whisperchain.utils.secrets import load_secrets


@click.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8000, help="Server port")
@click.option("--model", default="base.en", help="Whisper model name")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def main(host: str, port: int, model: str, debug: bool):
    """Run the FastAPI server."""
    # Initialize secrets
    load_secrets()

    config = ServerConfig(host=host, port=port, model_name=model, debug=debug)
    server = WhisperServer(config)
    uvicorn.run(server.app, host=config.host, port=config.port)
