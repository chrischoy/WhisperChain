import getpass
import os
from pathlib import Path

from dotenv import load_dotenv


def get_config_dir() -> Path:
    """Get or create configuration directory."""
    config_dir = Path.home() / ".whisperchain"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def setup_openai_api_key() -> str:
    """Interactive setup for OpenAI API key with automatic .env creation."""
    print("\nOpenAI API key")
    print("You can find your OpenAI API keys at: https://platform.openai.com/api-keys")

    api_key = getpass.getpass("\nEnter your OpenAI API key: ").strip()

    if not api_key:
        raise ValueError("OpenAI API key is required")
    return api_key


def setup_secrets() -> dict:
    """Interactive setup for API keys with automatic .env creation."""
    print("\nWhisperChain Setup")
    print("------------------")
    print("API keys are required for this application.")

    openai_api_key = setup_openai_api_key()

    # Save to .env file in user's config directory
    env_path = get_config_dir() / ".env"

    # Create or update .env file
    with open(env_path, "a+") as f:
        f.seek(0)
        content = f.read()
        if "OPENAI_API_KEY" not in content:
            f.write(f"\nOPENAI_API_KEY={openai_api_key}")

    os.environ["OPENAI_API_KEY"] = openai_api_key
    print(f"\nAPI keys have been saved to {env_path}")
    return {"openai_api_key": openai_api_key}


def load_secrets() -> dict:
    """Get API keys from environment or prompt for setup."""
    # Load from all possible .env locations
    load_dotenv()  # Load from current directory
    load_dotenv(get_config_dir() / ".env")  # Load from ~/.whisperchain/.env

    # Try environment variable first
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key

    # If not found, run interactive setup
    return setup_secrets()
