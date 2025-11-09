"""Token issuance endpoints"""
from fastapi import APIRouter, HTTPException, Depends, status
from fireblocks_sdk import FireblocksSDK
from fireblocks_sdk.tokenization_api_types import (
    CreateTokenRequest as SDKCreateTokenRequest,
    EVMTokenCreateParams as SDKEVMTokenCreateParams,
    StellarRippleCreateParams as SDKStellarRippleCreateParams,
    ParameterWithValue as SDKParameterWithValue
)

from app.models import CreateTokenRequest, TokenResponse
from app.fireblocks_sdk_client import get_fireblocks_sdk_client

router = APIRouter(prefix="/tokens", tags=["Tokens"])


@router.post(
    "",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Issue a new token",
    description="Creates a new token on EVM-based blockchains, Stellar, or Ripple"
)
async def issue_new_token(
    request: CreateTokenRequest,
    fireblocks: FireblocksSDK = Depends(get_fireblocks_sdk_client)
) -> TokenResponse:
    """
    Issue a new token.

    For EVM-based networks (Ethereum, Polygon, etc.):
    - Deploys a contract template to the blockchain
    - Links the token to your workspace
    - Provide evm_params with contract_id and optional deploy_function_params

    For Stellar and Ripple:
    - Links a newly created token directly to the workspace
    - No contract deployment needed
    - Provide stellar_ripple_params with issuer_address, symbol, and name

    **Request body:**
    - **vault_account_id**: The vault account ID (required)
    - **asset_id**: The asset ID (optional)
    - **blockchain_id**: The blockchain ID (e.g., 'ETHEREUM', 'POLYGON') (optional)
    - **display_name**: Display name for the token (optional)
    - **evm_params**: Parameters for EVM token creation (required for EVM)
    - **stellar_ripple_params**: Parameters for Stellar/Ripple token creation (required for Stellar/Ripple)
    """
    try:
        # Validate that at least one set of params is provided
        if not request.evm_params and not request.stellar_ripple_params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either evm_params or stellar_ripple_params must be provided"
            )

        if request.evm_params and request.stellar_ripple_params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only one of evm_params or stellar_ripple_params should be provided"
            )

        # Build the create_params based on which type is provided
        if request.evm_params:
            # Convert Pydantic models to SDK types for EVM
            deploy_params = None
            if request.evm_params.deploy_function_params:
                deploy_params = [
                    SDKParameterWithValue(
                        name=param.name,
                        type=param.type,
                        internal_type=param.internal_type,
                        value=param.value,
                        function_value=None,  # Not used in basic scenarios
                        description=param.description
                    )
                    for param in request.evm_params.deploy_function_params
                ]

            create_params = SDKEVMTokenCreateParams(
                contract_id=request.evm_params.contract_id,
                deploy_function_params=deploy_params
            )
        else:
            # Convert Pydantic models to SDK types for Stellar/Ripple
            create_params = SDKStellarRippleCreateParams(
                issuer_address=request.stellar_ripple_params.issuer_address,
                symbol=request.stellar_ripple_params.symbol,
                name=request.stellar_ripple_params.name
            )

        # Create the SDK request object
        sdk_request = SDKCreateTokenRequest(
            vault_account_id=request.vault_account_id,
            create_params=create_params,
            asset_id=request.asset_id,
            blockchain_id=request.blockchain_id,
            display_name=request.display_name
        )

        # Call Fireblocks SDK to issue the token
        token_data = fireblocks.issue_new_token(sdk_request)

        # Convert to response model
        return TokenResponse(
            id=token_data.get('id'),
            status=token_data.get('status'),
            asset_id=token_data.get('assetId'),
            blockchain_id=token_data.get('blockchainId'),
            vault_account_id=token_data.get('vaultAccountId'),
            additional_data=token_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to issue token: {str(e)}"
        )
