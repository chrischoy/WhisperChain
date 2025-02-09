import json
from pathlib import Path

import toml
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


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    model_name: str = "base.en"
    debug: bool = False

    def validate_model_name(cls, v):
        from pywhispercpp.constants import AVAILABLE_MODELS

        if v not in AVAILABLE_MODELS:
            raise ValueError(f"Model {v} not found in {AVAILABLE_MODELS}")
        return v


class UIConfig(BaseModel):
    """Streamlit UI configuration"""

    title: str = "WhisperChain Dashboard"
    page_icon: str = "🎙️"
    layout: str = "wide"

    # Server connection
    server_url: str = "http://localhost:8000"
    refresh_interval: float = 5.0  # seconds
    quick_refresh: float = 0.1  # seconds

    # Display settings
    history_limit: int = 100
    default_expanded: bool = False

    # Theme
    theme_base: str = "light"
    theme_primary_color: str = "#F63366"


class ConfigManager:
    """Central configuration manager"""

    _instance = None

    def __init__(self):
        self.config_dir = Path.home() / ".whisperchain"
        self.config_dir.mkdir(exist_ok=True)

        # Load configs
        self.ui_config = self._load_ui_config()

    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance

    def _load_ui_config(self) -> UIConfig:
        """Load UI config from file or create default"""
        config_file = self.config_dir / "ui_config.json"

        if config_file.exists():
            return UIConfig.parse_file(config_file)

        # Create default config
        config = UIConfig()
        self.save_ui_config(config)
        return config

    def save_ui_config(self, config: UIConfig):
        """Save UI config to file"""
        config_file = self.config_dir / "ui_config.json"
        with open(config_file, "w") as f:
            json.dump(config.dict(), f, indent=2)

    def generate_streamlit_config(self):
        """Generate Streamlit config.toml content"""
        streamlit_config = {
            "browser": {
                "gatherUsageStats": False,
            },
            "server": {
                "headless": True,
                "runOnSave": True,
                "address": "localhost",
                "port": 8501,
                "enableCORS": True,
            },
            "theme": {
                "base": self.ui_config.theme_base,
                "primaryColor": self.ui_config.theme_primary_color,
            },
        }

        # Write to .streamlit/config.toml
        config_path = Path.home() / ".streamlit" / "config.toml"
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, "w") as f:
            toml.dump(streamlit_config, f)


# Global config instance
config = ConfigManager.get_instance()
