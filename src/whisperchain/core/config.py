from pydantic import BaseModel, Field


class AudioConfig(BaseModel):
    """Audio capture configuration."""

    sample_rate: int = Field(default=16000, description="Sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    chunk_size: int = Field(
        default=4096, description="Chunk size for audio capture (~256ms at 16kHz)"
    )
    format: str = Field(default="int16", description="Audio format (int16, float32, etc.)")


class StreamConfig(BaseModel):
    """Stream client configuration."""

    min_buffer_size: int = Field(
        default=32000, description="Minimum buffer size in bytes before sending"
    )
    timeout: float = Field(default=0.1, description="Timeout for websocket operations in seconds")
    end_marker: str = Field(default="END\n", description="Marker to indicate end of stream")


class ClientConfig(BaseModel):
    """Client configuration including audio and stream settings."""

    server_url: str = Field(
        default="ws://localhost:8000/stream", description="WebSocket server URL"
    )
    hotkey: str = Field(default="<ctrl>+<alt>+r", description="Global hotkey combination")
    audio: AudioConfig = Field(default_factory=AudioConfig, description="Audio capture settings")
    stream: StreamConfig = Field(
        default_factory=StreamConfig, description="Stream client settings"
    )
