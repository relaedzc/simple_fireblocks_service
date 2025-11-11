"""Vault asset address management endpoints"""
from fastapi import APIRouter, HTTPException, Path, Query, Depends, status
from typing import Optional
from fireblocks.client import Fireblocks

from app.fireblocks_client import get_fireblocks_client
import logging

router = APIRouter(prefix="/vault-assets", tags=["Vault Asset Addresses"])
logger = logging.getLogger(__name__)


@router.get(
    "/{vault_account_id}/{asset_id}/addresses",
    status_code=status.HTTP_200_OK,
    summary="Get vault account asset addresses",
    description="Retrieves deposit addresses for a specific asset in a vault account"
)
async def get_vault_account_asset_addresses(
    vault_account_id: str = Path(..., description="Vault account ID"),
    asset_id: str = Path(..., description="Asset ID (e.g., XRP, XRP_TEST, BTC, ETH)"),
    before: Optional[str] = Query(None, description="Pagination cursor (before)"),
    after: Optional[str] = Query(None, description="Pagination cursor (after)"),
    limit: Optional[int] = Query(100, ge=1, le=500, description="Results per page"),
    fireblocks: Fireblocks = Depends(get_fireblocks_client)
):
    """
    Get deposit addresses for a specific asset in a vault account.

    Returns paginated list of addresses with their metadata (address, tag, legacy_address, etc.)
    """
    try:
        logger.info(f"Fetching addresses for vault {vault_account_id}, asset {asset_id}")

        # Build params for pagination
        params = {}
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        if limit:
            params["limit"] = limit

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        # Call Fireblocks SDK to get deposit addresses with pagination
        api_response = fireblocks.vaults.get_vault_account_asset_addresses_paginated(
            vault_account_id=vault_account_id,
            asset_id=asset_id,
            **params
        ).result()

        # Return response in expected format
        return {
            "data": api_response.data,
            "statusCode": 200
        }

    except Exception as e:
        logger.error(f"Error fetching vault asset addresses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vault account asset addresses: {str(e)}"
        )
