"""Pydantic models for request and response validation"""
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class CreateVaultAccountRequest(BaseModel):
    """Request model for creating a vault account"""

    name: str = Field(..., description="The name of the vault account", min_length=1)
    hidden_on_ui: bool = Field(False, description="Whether to hide the vault account in the UI")
    auto_fuel: bool = Field(False, description="Whether to enable automatic fueling for the vault account")


class VaultAssetInAccount(BaseModel):
    """Asset information within a vault account"""

    id: str = Field(..., description="The asset ID")
    total: Optional[str] = Field(None, description="Total balance")
    balance: Optional[str] = Field(None, description="Balance")
    available: Optional[str] = Field(None, description="Available balance")
    pending: Optional[str] = Field(None, description="Pending balance")
    frozen: Optional[str] = Field(None, description="Frozen balance")
    locked_amount: Optional[str] = Field(None, description="Locked amount")
    staked: Optional[str] = Field(None, description="Staked balance")
    total_staked_cpu: Optional[str] = Field(None, description="Total staked CPU")
    total_staked_network: Optional[str] = Field(None, description="Total staked network")
    self_staked_cpu: Optional[str] = Field(None, description="Self staked CPU")
    self_staked_network: Optional[str] = Field(None, description="Self staked network")
    pending_refund_cpu: Optional[str] = Field(None, description="Pending refund CPU")
    pending_refund_network: Optional[str] = Field(None, description="Pending refund network")
    block_height: Optional[str] = Field(None, description="Block height")
    block_hash: Optional[str] = Field(None, description="Block hash")
    rewards_info: Optional[Dict[str, Any]] = Field(None, description="Rewards information")

    class Config:
        from_attributes = True


class VaultAccountResponse(BaseModel):
    """Response model for vault account operations"""

    id: str = Field(..., description="The ID of the vault account")
    name: str = Field(..., description="The name of the vault account")
    hidden_on_ui: Optional[bool] = Field(None, description="Whether the vault account is hidden in the UI")
    auto_fuel: Optional[bool] = Field(None, description="Whether automatic fueling is enabled")
    customer_ref_id: Optional[str] = Field(None, description="Customer reference ID")
    assets: Optional[list[VaultAssetInAccount]] = Field(None, description="Assets in the vault account")
    tags: Optional[Dict[str, Any]] = Field(None, description="Tags associated with the vault account")

    class Config:
        from_attributes = True


class CreateVaultWalletRequest(BaseModel):
    """Request model for creating a vault wallet"""

    vault_account_id: str = Field(..., description="The ID of the vault account", min_length=1)
    asset_id: str = Field(..., description="The asset ID (e.g., BTC, ETH, SOL)", min_length=1)


class VaultWalletResponse(BaseModel):
    """Response model for vault wallet operations"""

    id: str = Field(..., description="The vault account ID")
    address: Optional[str] = Field(None, description="The wallet address")
    legacy_address: Optional[str] = Field(None, description="Legacy format address (for applicable blockchains)")
    tag: Optional[str] = Field(None, description="Tag/memo field (for applicable assets)")

    class Config:
        from_attributes = True


class VaultAssetResponse(BaseModel):
    """Response model for vault asset balance information"""

    id: str = Field(..., description="The asset ID")
    total: Optional[str] = Field(None, description="Total balance")
    available: Optional[str] = Field(None, description="Available balance")
    pending: Optional[str] = Field(None, description="Pending balance")
    frozen: Optional[str] = Field(None, description="Frozen balance")
    locked_amount: Optional[str] = Field(None, description="Locked amount")
    staked: Optional[str] = Field(None, description="Staked balance")
    block_height: Optional[str] = Field(None, description="Block height")
    block_hash: Optional[str] = Field(None, description="Block hash")
    # Store any additional fields that might be returned
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional asset data")

    class Config:
        from_attributes = True


class CreateTransactionRequest(BaseModel):
    """Request model for creating a transaction"""

    asset_id: str = Field(..., description="The asset ID (e.g., BTC, ETH, SOL)", min_length=1)
    source_vault_account_id: str = Field(..., description="Source vault account ID", min_length=1)
    destination_vault_account_id: str = Field(..., description="Destination vault account ID", min_length=1)
    amount: str = Field(..., description="Transfer amount", min_length=1)
    note: Optional[str] = Field(None, description="Transaction note")
    fee_level: Optional[str] = Field(None, description="Fee level: HIGH, MEDIUM, or LOW")


class TransactionResponse(BaseModel):
    """Response model for transaction operations"""

    id: str = Field(..., description="Transaction ID")
    status: str = Field(..., description="Transaction status")
    asset_id: Optional[str] = Field(None, description="Asset ID")
    amount: Optional[str] = Field(None, description="Transaction amount")
    source: Optional[Dict[str, Any]] = Field(None, description="Source details")
    destination: Optional[Dict[str, Any]] = Field(None, description="Destination details")
    fee: Optional[str] = Field(None, description="Transaction fee")
    network_fee: Optional[str] = Field(None, description="Network fee")
    created_at: Optional[int] = Field(None, description="Creation timestamp")
    last_updated: Optional[int] = Field(None, description="Last update timestamp")
    tx_hash: Optional[str] = Field(None, description="Transaction hash")
    sub_status: Optional[str] = Field(None, description="Transaction sub-status")
    # Store any additional fields
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional transaction data")

    class Config:
        from_attributes = True


class ParameterWithValue(BaseModel):
    """Parameter with value for EVM token deployment"""

    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (e.g., 'string', 'uint256')")
    internal_type: str = Field(..., description="Internal Solidity type")
    value: Any = Field(..., description="Parameter value (string, int, float, or bool)")
    description: Optional[str] = Field(None, description="Parameter description")


class EVMTokenCreateParams(BaseModel):
    """Parameters for creating an EVM-based token"""

    contract_id: str = Field(..., description="The contract template ID to deploy", min_length=1)
    deploy_function_params: Optional[list[ParameterWithValue]] = Field(None, description="Parameters for the contract deployment function")


class StellarRippleCreateParams(BaseModel):
    """Parameters for creating a Stellar or Ripple token"""

    issuer_address: Optional[str] = Field(None, description="The issuer address for the token")
    symbol: Optional[str] = Field(None, description="The token symbol")
    name: Optional[str] = Field(None, description="The token name")


class CreateTokenRequest(BaseModel):
    """Request model for issuing a new token"""

    vault_account_id: str = Field(..., description="The vault account ID", min_length=1)
    asset_id: Optional[str] = Field(None, description="The asset ID")
    blockchain_id: Optional[str] = Field(None, description="The blockchain ID (e.g., 'ETHEREUM', 'POLYGON')")
    display_name: Optional[str] = Field(None, description="Display name for the token")
    # Use a discriminated union approach - one of these should be provided
    evm_params: Optional[EVMTokenCreateParams] = Field(None, description="Parameters for EVM-based token creation")
    stellar_ripple_params: Optional[StellarRippleCreateParams] = Field(None, description="Parameters for Stellar/Ripple token creation")


class TokenResponse(BaseModel):
    """Response model for token issuance"""

    id: Optional[str] = Field(None, description="Token ID")
    status: Optional[str] = Field(None, description="Token status (PENDING or SUCCESS)")
    asset_id: Optional[str] = Field(None, description="Asset ID")
    blockchain_id: Optional[str] = Field(None, description="Blockchain ID")
    vault_account_id: Optional[str] = Field(None, description="Vault account ID")
    # Store any additional fields that might be returned
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional token data")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response model"""

    detail: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Type of error")
