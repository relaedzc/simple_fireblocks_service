"""FastAPI application for Fireblocks service"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import config
from app.fireblocks_client import FireblocksClientManager
from app.fireblocks_sdk_client import FireblocksSDKClientManager
from app.routes import vault_accounts, vault_wallets, vault_assets, transactions, tokens, vault_asset_addresses


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    try:
        config.validate()
        print("Configuration validated successfully")
        print("Fireblocks service started")
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        raise

    yield

    # Shutdown
    FireblocksClientManager.close_client()
    FireblocksSDKClientManager.close_client()
    print("Fireblocks service stopped")


app = FastAPI(
    title="Fireblocks Service",
    description="Internal service for managing Fireblocks operations",
    version="1.0.0",
    lifespan=lifespan
)


# Include routers
app.include_router(vault_accounts.router)
app.include_router(vault_wallets.router)
app.include_router(vault_assets.router)
app.include_router(vault_asset_addresses.router)
app.include_router(transactions.router)
app.include_router(tokens.router)


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "fireblocks-service",
            "version": "1.0.0"
        }
    )
