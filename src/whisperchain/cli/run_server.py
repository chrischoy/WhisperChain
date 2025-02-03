import click
import uvicorn

from whisperchain.server.server import app


@click.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8000, help="Server port")
def main(host: str, port: int):
    """Run the FastAPI server."""
    uvicorn.run(app, host=host, port=port)
