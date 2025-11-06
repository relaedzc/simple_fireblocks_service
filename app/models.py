"""Pydantic models for request and response validation"""
from typing import Optional
from pydantic import BaseModel, Field


class CreateVaultAccountRequest(BaseModel):
    """Request model for creating a vault account"""

    name: str = Field(..., description="The name of the vault account", min_length=1)
    hidden_on_ui: bool = Field(False, description="Whether to hide the vault account in the UI")
    auto_fuel: bool = Field(False, description="Whether to enable automatic fueling for the vault account")


class VaultAccountResponse(BaseModel):
    """Response model for vault account operations"""

    id: str = Field(..., description="The ID of the vault account")
    name: str = Field(..., description="The name of the vault account")
    hidden_on_ui: Optional[bool] = Field(None, description="Whether the vault account is hidden in the UI")
    auto_fuel: Optional[bool] = Field(None, description="Whether automatic fueling is enabled")

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


class ErrorResponse(BaseModel):
    """Error response model"""

    detail: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Type of error")
