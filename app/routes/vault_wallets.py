"""Vault wallet management endpoints"""
from fastapi import APIRouter, HTTPException, Depends, status
from fireblocks_sdk import FireblocksSDK

from app.models import CreateVaultWalletRequest, VaultWalletResponse
from app.fireblocks_sdk_client import get_fireblocks_sdk_client

router = APIRouter(prefix="/vault-wallets", tags=["Vault Wallets"])


@router.post(
    "",
    response_model=VaultWalletResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vault wallet",
    description="Creates a new wallet/asset in a vault account"
)
async def create_vault_wallet(
    request: CreateVaultWalletRequest,
    fireblocks: FireblocksSDK = Depends(get_fireblocks_sdk_client)
) -> VaultWalletResponse:
    """
    Create a new wallet for a specific asset in a vault account.

    - **vault_account_id**: The ID of the vault account (required)
    - **asset_id**: The asset/blockchain identifier (e.g., BTC, ETH, SOL) (required)
    """
    try:
        # Call Fireblocks SDK to create vault asset
        wallet_data = fireblocks.create_vault_asset(
            vault_account_id=request.vault_account_id,
            asset_id=request.asset_id
        )

        # Convert to response model
        return VaultWalletResponse(
            id=wallet_data.get('id', request.vault_account_id),
            address=wallet_data.get('address'),
            legacy_address=wallet_data.get('legacyAddress'),
            tag=wallet_data.get('tag')
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vault wallet: {str(e)}"
        )
