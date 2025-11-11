"""Vault account management endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional
from fireblocks.client import Fireblocks
from fireblocks.models.create_vault_account_request import CreateVaultAccountRequest as FBCreateVaultAccountRequest

from app.models import CreateVaultAccountRequest, VaultAccountResponse, VaultAssetInAccount
from app.fireblocks_client import get_fireblocks_client
import logging

router = APIRouter(prefix="/vault-accounts", tags=["Vault Accounts"])
logger = logging.getLogger(__name__)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get paginated vault accounts",
    description="Retrieves vault accounts with filtering and pagination support"
)
async def get_paged_vault_accounts(
    namePrefix: Optional[str] = Query(None, description="Filter by name prefix"),
    nameSuffix: Optional[str] = Query(None, description="Filter by name suffix"),
    minAmountThreshold: Optional[float] = Query(None, description="Minimum amount threshold"),
    assetId: Optional[str] = Query(None, description="Filter by asset ID"),
    orderBy: Optional[str] = Query(None, description="Order by field"),
    before: Optional[str] = Query(None, description="Pagination cursor (before)"),
    after: Optional[str] = Query(None, description="Pagination cursor (after)"),
    limit: Optional[int] = Query(100, ge=1, le=500, description="Results per page"),
    fireblocks: Fireblocks = Depends(get_fireblocks_client)
):
    """
    Get paginated vault accounts with filtering.

    This endpoint returns a limited amount of results with a quick response time.
    Supports filtering by name prefix/suffix, asset, amount threshold.
    """
    try:
        # Build params dict (remove None values)
        params = {
            "name_prefix": namePrefix,
            "name_suffix": nameSuffix,
            "min_amount_threshold": minAmountThreshold,
            "asset_id": assetId,
            "order_by": orderBy,
            "before": before,
            "after": after,
            "limit": limit,
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        logger.info(f"Fetching vault accounts with params: {params}")

        # Call Fireblocks SDK
        # Note: Using get_paged_vault_accounts for pagination support
        api_response = fireblocks.vaults.get_paged_vault_accounts(**params).result()

        # Return response in expected format
        return {
            "data": api_response.data,
            "statusCode": 200
        }

    except Exception as e:
        logger.error(f"Error fetching vault accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vault accounts: {str(e)}"
        )


@router.get(
    "/{vault_account_id}",
    response_model=VaultAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a vault account by ID",
    description="Retrieves a vault account by its unique identifier"
)
async def get_vault_account(
    vault_account_id: str,
    fireblocks: Fireblocks = Depends(get_fireblocks_client)
) -> VaultAccountResponse:
    """
    Get a vault account by its unique ID.

    - **vault_account_id**: The unique identifier of the vault account (required)
    """
    try:
        # Call Fireblocks API
        api_response = fireblocks.vaults.get_vault_account(vault_account_id).result()

        # Extract vault account data from the API response
        vault_account = api_response.data

        # Convert assets to response model
        assets = None
        if vault_account.assets:
            assets = [
                VaultAssetInAccount(
                    id=asset.id,
                    total=asset.total,
                    balance=asset.balance,
                    available=asset.available,
                    pending=asset.pending,
                    frozen=asset.frozen,
                    locked_amount=asset.locked_amount,
                    staked=asset.staked,
                    total_staked_cpu=asset.total_staked_cpu,
                    total_staked_network=asset.total_staked_network,
                    self_staked_cpu=asset.self_staked_cpu,
                    self_staked_network=asset.self_staked_network,
                    pending_refund_cpu=asset.pending_refund_cpu,
                    pending_refund_network=asset.pending_refund_network,
                    block_height=asset.block_height,
                    block_hash=asset.block_hash,
                    rewards_info=asset.rewards_info.to_dict() if hasattr(asset, 'rewards_info') and asset.rewards_info else None
                )
                for asset in vault_account.assets
            ]

        # Convert to response model
        return VaultAccountResponse(
            id=vault_account.id,
            name=vault_account.name,
            hidden_on_ui=vault_account.hidden_on_ui,
            auto_fuel=vault_account.auto_fuel,
            customer_ref_id=vault_account.customer_ref_id,
            assets=assets,
            tags=vault_account.tags
        )

    except Exception as e:
        # Check if it's a 404 error (vault account not found)
        error_message = str(e)
        if "404" in error_message or "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vault account with ID '{vault_account_id}' not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve vault account: {error_message}"
        )


@router.post(
    "",
    response_model=VaultAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vault account",
    description="Creates a new vault account in Fireblocks"
)
async def create_vault_account(
    request: CreateVaultAccountRequest,
    fireblocks: Fireblocks = Depends(get_fireblocks_client)
) -> VaultAccountResponse:
    """
    Create a new vault account with the specified parameters.

    - **name**: The name of the vault account (required)
    - **hidden_on_ui**: Whether to hide the vault account in the UI (default: False)
    - **auto_fuel**: Whether to enable automatic fueling (default: False)
    """
    try:
        # Create Fireblocks request object
        fb_request = FBCreateVaultAccountRequest(
            name=request.name,
            hidden_on_ui=request.hidden_on_ui,
            auto_fuel=request.auto_fuel
        )

        # Call Fireblocks API
        api_response = fireblocks.vaults.create_vault_account(fb_request).result()

        # Extract vault account data from the API response
        vault_account = api_response.data

        # Convert assets to response model
        assets = None
        if vault_account.assets:
            assets = [
                VaultAssetInAccount(
                    id=asset.id,
                    total=asset.total,
                    balance=asset.balance,
                    available=asset.available,
                    pending=asset.pending,
                    frozen=asset.frozen,
                    locked_amount=asset.locked_amount,
                    staked=asset.staked,
                    total_staked_cpu=asset.total_staked_cpu,
                    total_staked_network=asset.total_staked_network,
                    self_staked_cpu=asset.self_staked_cpu,
                    self_staked_network=asset.self_staked_network,
                    pending_refund_cpu=asset.pending_refund_cpu,
                    pending_refund_network=asset.pending_refund_network,
                    block_height=asset.block_height,
                    block_hash=asset.block_hash,
                    rewards_info=asset.rewards_info.to_dict() if hasattr(asset, 'rewards_info') and asset.rewards_info else None
                )
                for asset in vault_account.assets
            ]

        # Convert to response model
        return VaultAccountResponse(
            id=vault_account.id,
            name=vault_account.name,
            hidden_on_ui=vault_account.hidden_on_ui,
            auto_fuel=vault_account.auto_fuel,
            customer_ref_id=vault_account.customer_ref_id,
            assets=assets,
            tags=vault_account.tags
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vault account: {str(e)}"
        )
