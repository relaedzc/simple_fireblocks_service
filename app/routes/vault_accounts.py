"""Vault account management endpoints"""
from fastapi import APIRouter, HTTPException, Depends, status
from fireblocks.client import Fireblocks
from fireblocks.models.create_vault_account_request import CreateVaultAccountRequest as FBCreateVaultAccountRequest

from app.models import CreateVaultAccountRequest, VaultAccountResponse
from app.fireblocks_client import get_fireblocks_client

router = APIRouter(prefix="/vault-accounts", tags=["Vault Accounts"])


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

        # Convert to response model
        return VaultAccountResponse(
            id=vault_account.id,
            name=vault_account.name,
            hidden_on_ui=vault_account.hidden_on_ui,
            auto_fuel=vault_account.auto_fuel
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vault account: {str(e)}"
        )
