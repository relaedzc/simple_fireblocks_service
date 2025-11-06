"""Configuration management for Fireblocks service"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""

    # Fireblocks API configuration
    FIREBLOCKS_API_KEY: str = os.getenv("FIREBLOCKS_API_KEY", "")
    FIREBLOCKS_SECRET_KEY_PATH: str = os.getenv("FIREBLOCKS_SECRET_KEY_PATH", "")

    @classmethod
    def get_secret_key(cls) -> str:
        """Read and return the Fireblocks secret key from file"""
        if not cls.FIREBLOCKS_SECRET_KEY_PATH:
            raise ValueError("FIREBLOCKS_SECRET_KEY_PATH environment variable is not set")

        secret_key_path = Path(cls.FIREBLOCKS_SECRET_KEY_PATH)

        if not secret_key_path.exists():
            raise FileNotFoundError(f"Secret key file not found at: {cls.FIREBLOCKS_SECRET_KEY_PATH}")

        with open(secret_key_path, 'r') as f:
            return f.read().strip()

    @classmethod
    def validate(cls) -> None:
        """Validate that all required configuration is present"""
        if not cls.FIREBLOCKS_API_KEY:
            raise ValueError("FIREBLOCKS_API_KEY environment variable is not set")

        if not cls.FIREBLOCKS_SECRET_KEY_PATH:
            raise ValueError("FIREBLOCKS_SECRET_KEY_PATH environment variable is not set")

        # Verify the secret key file exists and is readable
        cls.get_secret_key()


config = Config()
