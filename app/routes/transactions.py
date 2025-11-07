"""Transaction management endpoints"""
from fastapi import APIRouter, HTTPException, Depends, status
from fireblocks_sdk import FireblocksSDK, TransferPeerPath, DestinationTransferPeerPath

from app.models import CreateTransactionRequest, TransactionResponse
from app.fireblocks_sdk_client import get_fireblocks_sdk_client

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a transaction",
    description="Creates a new transfer transaction between vault accounts"
)
async def create_transaction(
    request: CreateTransactionRequest,
    fireblocks: FireblocksSDK = Depends(get_fireblocks_sdk_client)
) -> TransactionResponse:
    """
    Create a new transfer transaction between vault accounts.

    - **asset_id**: The asset ID to transfer (e.g., BTC, ETH, SOL) (required)
    - **source_vault_account_id**: Source vault account ID (required)
    - **destination_vault_account_id**: Destination vault account ID (required)
    - **amount**: Amount to transfer (required)
    - **note**: Optional transaction note
    - **fee_level**: Optional fee level (HIGH, MEDIUM, LOW)
    """
    try:
        # Build source and destination objects for Fireblocks SDK
        source = TransferPeerPath("VAULT_ACCOUNT", request.source_vault_account_id)
        destination = DestinationTransferPeerPath("VAULT_ACCOUNT", request.destination_vault_account_id)

        # Call Fireblocks SDK to create transaction
        tx_data = fireblocks.create_transaction(
            asset_id=request.asset_id,
            amount=request.amount,
            source=source,
            destination=destination,
            tx_type="TRANSFER",
            note=request.note,
            fee_level=request.fee_level
        )

        # Convert to response model
        return TransactionResponse(
            id=tx_data.get('id'),
            status=tx_data.get('status'),
            asset_id=tx_data.get('assetId'),
            amount=tx_data.get('amount'),
            source=tx_data.get('source'),
            destination=tx_data.get('destination'),
            fee=tx_data.get('fee'),
            network_fee=tx_data.get('networkFee'),
            created_at=tx_data.get('createdAt'),
            last_updated=tx_data.get('lastUpdated'),
            tx_hash=tx_data.get('txHash'),
            sub_status=tx_data.get('subStatus'),
            # Capture any additional fields
            additional_data={k: v for k, v in tx_data.items()
                           if k not in ['id', 'status', 'assetId', 'amount', 'source',
                                       'destination', 'fee', 'networkFee', 'createdAt',
                                       'lastUpdated', 'txHash', 'subStatus']}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transaction: {str(e)}"
        )
