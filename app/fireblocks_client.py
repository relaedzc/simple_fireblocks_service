"""Fireblocks client initialization and dependency injection"""
from typing import Optional
from fireblocks.client import Fireblocks
from fireblocks.client_configuration import ClientConfiguration
from fireblocks.base_path import BasePath

from app.config import config


class FireblocksClientManager:
    """Manager for Fireblocks client singleton"""

    _client: Optional[Fireblocks] = None

    @classmethod
    def get_client(cls) -> Fireblocks:
        """Get or create Fireblocks client instance"""
        if cls._client is None:
            cls._client = cls._create_client()
        return cls._client

    @classmethod
    def _create_client(cls) -> Fireblocks:
        """Create a new Fireblocks client with production configuration"""
        secret_key = config.get_secret_key()

        configuration = ClientConfiguration(
            api_key=config.FIREBLOCKS_API_KEY,
            secret_key=secret_key,
            base_path=BasePath.US  # Production environment
        )

        return Fireblocks(configuration)

    @classmethod
    def close_client(cls) -> None:
        """Close the Fireblocks client"""
        if cls._client is not None:
            cls._client.close()
            cls._client = None


def get_fireblocks_client() -> Fireblocks:
    """Dependency injection function for FastAPI routes"""
    return FireblocksClientManager.get_client()
