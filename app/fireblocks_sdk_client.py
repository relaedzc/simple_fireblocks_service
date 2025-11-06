"""Fireblocks SDK (fireblocks-sdk-py) client initialization and dependency injection"""
from typing import Optional
from fireblocks_sdk import FireblocksSDK

from app.config import config


class FireblocksSDKClientManager:
    """Manager for Fireblocks SDK client singleton"""

    _client: Optional[FireblocksSDK] = None

    @classmethod
    def get_client(cls) -> FireblocksSDK:
        """Get or create Fireblocks SDK client instance"""
        if cls._client is None:
            cls._client = cls._create_client()
        return cls._client

    @classmethod
    def _create_client(cls) -> FireblocksSDK:
        """Create a new Fireblocks SDK client"""
        # Read the private key from file
        private_key = config.get_secret_key()

        # Initialize FireblocksSDK with private key and API key
        return FireblocksSDK(
            private_key=private_key,
            api_key=config.FIREBLOCKS_API_KEY
        )

    @classmethod
    def close_client(cls) -> None:
        """Close the Fireblocks SDK client"""
        if cls._client is not None:
            cls._client = None


def get_fireblocks_sdk_client() -> FireblocksSDK:
    """Dependency injection function for FastAPI routes"""
    return FireblocksSDKClientManager.get_client()
