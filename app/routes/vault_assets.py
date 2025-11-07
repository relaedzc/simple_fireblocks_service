"""Vault asset management endpoints"""
from fastapi import APIRouter, HTTPException, Depends, status
from fireblocks_sdk import FireblocksSDK

from app.models import VaultAssetResponse
from app.fireblocks_sdk_client import get_fireblocks_sdk_client

router = APIRouter(prefix="/vault-assets", tags=["Vault Assets"])


@router.get(
    "/{vault_account_id}/{asset_id}",
    response_model=VaultAssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get vault account asset balance",
    description="Retrieves balance information for a specific asset in a vault account"
)
async def get_vault_asset(
    vault_account_id: str,
    asset_id: str,
    fireblocks: FireblocksSDK = Depends(get_fireblocks_sdk_client)
) -> VaultAssetResponse:
    """
    Get balance information for a specific asset in a vault account.

    - **vault_account_id**: The ID of the vault account (required)
    - **asset_id**: The asset/blockchain identifier (e.g., BTC, ETH, SOL) (required)
    """
    try:
        # Call Fireblocks SDK to get vault asset
        asset_data = fireblocks.get_vault_account_asset(
            vault_account_id=vault_account_id,
            asset_id=asset_id
        )

        # Convert to response model
        return VaultAssetResponse(
            id=asset_data.get('id', asset_id),
            total=asset_data.get('total'),
            available=asset_data.get('available'),
            pending=asset_data.get('pending'),
            frozen=asset_data.get('frozen'),
            locked_amount=asset_data.get('lockedAmount'),
            staked=asset_data.get('staked'),
            block_height=asset_data.get('blockHeight'),
            block_hash=asset_data.get('blockHash'),
            # Capture any additional fields
            additional_data={k: v for k, v in asset_data.items()
                           if k not in ['id', 'total', 'available', 'pending', 'frozen',
                                       'lockedAmount', 'staked', 'blockHeight', 'blockHash']}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vault asset: {str(e)}"
        )
