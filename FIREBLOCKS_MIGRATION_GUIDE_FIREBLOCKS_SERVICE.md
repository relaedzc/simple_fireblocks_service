# Fireblocks Service XRPL Endpoints Implementation Guide

**For:** Fireblocks Service (`fireblocks_service` - FastAPI microservice)
**Role:** Fireblocks SDK wrapper for vault operations and XRPL transactions
**Architecture:** Next.js → Django (auth) → Fireblocks Service (you) → Fireblocks API

---

## Context

You are working on the FastAPI microservice that wraps the Fireblocks SDK. Currently, you have endpoints for:
- Creating vault accounts
- Creating vault wallets
- Getting vault asset balances
- Creating transactions

**New Requirement:** Add endpoints to support XRPL DEX operations:
1. Get paginated vault accounts with filtering
2. Get vault account asset addresses (deposit addresses)
3. Execute XRPL-specific transactions

---

## Architecture Overview

```
┌──────────────┐      ┌─────────────────────┐      ┌────────────────────┐      ┌──────────────┐
│  Next.js     │─────▶│  Django             │─────▶│  Fireblocks        │─────▶│  Fireblocks  │
│  Frontend    │      │  - Verify API Key   │      │  Service           │      │  API         │
│              │      │  - Proxy requests   │      │  (You are here)    │      │              │
│              │      │                     │      │  - Vault SDK calls │      │              │
└──────────────┘      └─────────────────────┘      │  - XRPL operations │      └──────────────┘
                                                     └────────────────────┘
```

**Your Job:** Add new FastAPI endpoints that wrap Fireblocks SDK calls

---

## Current Structure Analysis

Based on your existing code:

```
fireblocks_service/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration management
│   ├── fireblocks_client.py       # py-sdk client (vault accounts)
│   ├── fireblocks_sdk_client.py   # fireblocks-sdk-py (wallets/assets/transactions)
│   ├── models.py                  # Pydantic models
│   └── routes/
│       ├── vault_accounts.py      # Vault account endpoints
│       ├── vault_wallets.py       # Vault wallet endpoints
│       ├── vault_assets.py        # Vault asset balance endpoints
│       └── transactions.py        # Transaction endpoints
```

---

## Implementation Tasks

### Task 1: Update Pydantic Models

Add new request/response models to `app/models.py`:

```python
"""
Add these new models to your existing models.py file
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

# ============= VAULT ACCOUNTS MODELS =============

class VaultAccountsQueryParams(BaseModel):
    """Query parameters for getting paginated vault accounts"""
    namePrefix: Optional[str] = Field(None, description="Filter by name prefix")
    nameSuffix: Optional[str] = Field(None, description="Filter by name suffix")
    minAmountThreshold: Optional[float] = Field(None, description="Minimum amount threshold")
    assetId: Optional[str] = Field(None, description="Filter by asset ID")
    orderBy: Optional[str] = Field(None, description="Order by field")
    before: Optional[str] = Field(None, description="Pagination cursor (before)")
    after: Optional[str] = Field(None, description="Pagination cursor (after)")
    limit: Optional[int] = Field(100, description="Results per page", ge=1, le=500)
    tagIds: Optional[str] = Field(None, description="Comma-separated tag IDs")


# ============= VAULT ASSET ADDRESSES MODELS =============

class VaultAssetAddressesQueryParams(BaseModel):
    """Query parameters for getting vault account asset addresses"""
    before: Optional[str] = Field(None, description="Pagination cursor (before)")
    after: Optional[str] = Field(None, description="Pagination cursor (after)")
    limit: Optional[int] = Field(100, description="Results per page", ge=1, le=500)


# ============= XRPL TRANSACTION MODELS =============

class XRPLTransactionRequest(BaseModel):
    """Request model for executing XRPL transactions"""
    assetId: str = Field(..., description="Asset ID (e.g., XRP, XRP_TEST)")
    transactionType: str = Field(..., description="Type of XRPL transaction")
    vaultAccountId: str = Field(..., description="Source vault account ID")
    params: Dict[str, Any] = Field(..., description="Transaction-specific parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "assetId": "XRP_TEST",
                "transactionType": "TRANSFER",
                "vaultAccountId": "123",
                "params": {
                    "destination": "rN7n7otQDd6FczFgLdlqtyMVrn3HMfGhKh",
                    "amount": "10"
                }
            }
        }
```

---

### Task 2: Create New Route for Paginated Vault Accounts

Create or update `app/routes/vault_accounts.py`:

```python
"""
Update or add to your existing vault_accounts.py file
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.fireblocks_client import get_fireblocks_client
from app.models import VaultAccountsQueryParams
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/vault-accounts")
async def get_paged_vault_accounts(
    namePrefix: Optional[str] = Query(None),
    nameSuffix: Optional[str] = Query(None),
    minAmountThreshold: Optional[float] = Query(None),
    assetId: Optional[str] = Query(None),
    orderBy: Optional[str] = Query(None),
    before: Optional[str] = Query(None),
    after: Optional[str] = Query(None),
    limit: Optional[int] = Query(100, ge=1, le=500),
    tagIds: Optional[str] = Query(None),
):
    """
    Get paginated vault accounts with filtering.

    This endpoint returns a limited amount of results with a quick response time.
    Supports filtering by name prefix/suffix, asset, amount threshold, and tags.
    """
    try:
        # Get Fireblocks client
        client = get_fireblocks_client()

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

        # Handle tagIds (convert comma-separated to list)
        if tagIds:
            params["tag_ids"] = tagIds.split(",")

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        logger.info(f"Fetching vault accounts with params: {params}")

        # Call Fireblocks SDK
        # NOTE: Method name may differ - check your Fireblocks SDK documentation
        # Common method names:
        # - client.get_vault_accounts_with_page_info(**params)
        # - client.vault_accounts.list_paged(**params)
        # - client.get_paged_vault_accounts(**params)

        response = client.get_vault_accounts_with_page_info(**params)

        # Return response in expected format
        return {
            "data": response,
            "statusCode": 200
        }

    except Exception as e:
        logger.error(f"Error fetching vault accounts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch vault accounts: {str(e)}"
        )
```

**IMPORTANT:** The Fireblocks SDK method name `get_vault_accounts_with_page_info` is a placeholder. You must check your Fireblocks Python SDK documentation for the correct method name. It might be:
- `client.get_vault_accounts_with_page_info()`
- `client.vault_accounts.list()`
- `client.get_paged_vault_accounts()`

---

### Task 3: Create Route for Vault Asset Addresses

Create `app/routes/vault_asset_addresses.py` (new file):

```python
"""
New route file for vault asset address operations
"""

from fastapi import APIRouter, HTTPException, Path, Query
from typing import Optional
from app.fireblocks_sdk_client import get_fireblocks_sdk_client
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/vault-assets/{vault_account_id}/{asset_id}/addresses")
async def get_vault_account_asset_addresses(
    vault_account_id: str = Path(..., description="Vault account ID"),
    asset_id: str = Path(..., description="Asset ID (e.g., XRP, XRP_TEST, BTC, ETH)"),
    before: Optional[str] = Query(None, description="Pagination cursor (before)"),
    after: Optional[str] = Query(None, description="Pagination cursor (after)"),
    limit: Optional[int] = Query(100, ge=1, le=500, description="Results per page"),
):
    """
    Get deposit addresses for a specific asset in a vault account.

    Returns paginated list of addresses with their metadata (address, tag, legacy_address, etc.)
    """
    try:
        # Get Fireblocks SDK client
        client = get_fireblocks_sdk_client()

        logger.info(f"Fetching addresses for vault {vault_account_id}, asset {asset_id}")

        # Call Fireblocks SDK
        # NOTE: Method name may differ - check your Fireblocks SDK documentation
        # Common method names:
        # - client.get_deposit_addresses(vault_account_id, asset_id)
        # - client.vault_accounts.get_asset_addresses(vault_account_id, asset_id)
        # - client.get_vault_account_asset_addresses(vault_account_id, asset_id)

        # Build params if pagination is supported
        params = {}
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        if limit:
            params["limit"] = limit

        # Call SDK (adjust based on your SDK version)
        if params:
            # If SDK supports pagination params
            response = client.get_deposit_addresses(
                vault_account_id,
                asset_id,
                **params
            )
        else:
            # If SDK doesn't support pagination
            response = client.get_deposit_addresses(vault_account_id, asset_id)

        # Return response in expected format
        return {
            "data": {
                "addresses": response if isinstance(response, list) else [response]
            },
            "statusCode": 200
        }

    except Exception as e:
        logger.error(f"Error fetching vault asset addresses: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch vault account asset addresses: {str(e)}"
        )
```

**IMPORTANT:** The Fireblocks SDK method name `get_deposit_addresses` is a placeholder. Check your SDK documentation.

---

### Task 4: Create Route for XRPL Transactions

Create `app/routes/xrpl_transactions.py` (new file):

```python
"""
New route file for XRPL-specific transaction operations
"""

from fastapi import APIRouter, HTTPException
from app.fireblocks_sdk_client import get_fireblocks_sdk_client
from app.models import XRPLTransactionRequest
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/xrpl-transactions")
async def execute_xrpl_transaction(request: XRPLTransactionRequest):
    """
    Execute an XRPL-specific transaction via Fireblocks.

    Supports XRPL operations like transfers, trust line creation, offers, etc.
    """
    try:
        # Get Fireblocks SDK client
        client = get_fireblocks_sdk_client()

        logger.info(f"Executing XRPL transaction: {request.transactionType} for vault {request.vaultAccountId}")

        # Extract request data
        asset_id = request.assetId
        vault_account_id = request.vaultAccountId
        tx_type = request.transactionType
        params = request.params

        # Build Fireblocks transaction request
        # NOTE: This is a generic transaction structure - adjust based on your SDK
        transaction_data = {
            "assetId": asset_id,
            "source": {
                "type": "VAULT_ACCOUNT",
                "id": vault_account_id
            },
            "note": f"XRPL {tx_type} transaction",
        }

        # Add destination if present in params
        if "destination" in params:
            transaction_data["destination"] = {
                "type": "ONE_TIME_ADDRESS",
                "oneTimeAddress": {
                    "address": params["destination"]
                }
            }

        # Add amount if present in params
        if "amount" in params:
            transaction_data["amount"] = str(params["amount"])

        # Add fee level if specified
        if "feeLevel" in params:
            transaction_data["feeLevel"] = params["feeLevel"]
        else:
            transaction_data["feeLevel"] = "MEDIUM"  # Default

        # Add extra parameters (for XRPL-specific fields)
        if "extraParameters" in params:
            transaction_data["extraParameters"] = params["extraParameters"]

        # Call Fireblocks SDK to create transaction
        # NOTE: Method name may differ - check your Fireblocks SDK documentation
        # Common method names:
        # - client.create_transaction(**transaction_data)
        # - client.transactions.create(**transaction_data)
        # - client.submit_transaction(**transaction_data)

        response = client.create_transaction(**transaction_data)

        logger.info(f"XRPL transaction created: {response.get('id')}")

        # Return response
        return {
            "data": response,
            "statusCode": 201
        }

    except Exception as e:
        logger.error(f"Error executing XRPL transaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute XRPL transaction: {str(e)}"
        )
```

**IMPORTANT:** The transaction structure and method name are placeholders. Consult:
1. Fireblocks Python SDK documentation for `create_transaction()`
2. XRPL transaction requirements for your use case
3. Whether you need to use the `fireblocks-xrp-sdk` Python package (if it exists)

---

### Task 5: Register New Routes in Main App

Update `app/main.py` to include the new routes:

```python
"""
Update your existing main.py file
"""

from fastapi import FastAPI
from app.routes import vault_accounts, vault_wallets, vault_assets, transactions
from app.routes import vault_asset_addresses, xrpl_transactions  # NEW IMPORTS

app = FastAPI(
    title="Fireblocks Service",
    description="Internal FastAPI service for managing Fireblocks operations",
    version="1.0.0"
)

# Existing routes
app.include_router(vault_accounts.router, tags=["Vault Accounts"])
app.include_router(vault_wallets.router, tags=["Vault Wallets"])
app.include_router(vault_assets.router, tags=["Vault Assets"])
app.include_router(transactions.router, tags=["Transactions"])

# NEW ROUTES
app.include_router(vault_asset_addresses.router, tags=["Vault Asset Addresses"])
app.include_router(xrpl_transactions.router, tags=["XRPL Transactions"])

@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": "fireblocks-service",
        "version": "1.0.0"
    }
```

---

## Testing

### Prerequisites

1. Ensure Fireblocks service is running:
```bash
cd /home/relaed/Programs/zerocap/fireblocks_service
source .venv/bin/activate
fastapi dev app/main.py --port 8000
```

2. Access API docs at: `http://localhost:8000/docs`

### Test 1: Get Paginated Vault Accounts

```bash
# Test without filters
curl -X GET "http://localhost:8000/vault-accounts?limit=10"

# Test with name prefix filter
curl -X GET "http://localhost:8000/vault-accounts?namePrefix=acacia-customer&limit=10"

# Test with asset filter
curl -X GET "http://localhost:8000/vault-accounts?assetId=XRP_TEST&limit=10"

# Expected response format:
# {
#   "data": {
#     "accounts": [...],
#     "paging": { "before": "...", "after": "..." }
#   },
#   "statusCode": 200
# }
```

### Test 2: Get Vault Account Asset Addresses

```bash
# Replace with actual vault ID
VAULT_ID="123"
ASSET_ID="XRP_TEST"

curl -X GET "http://localhost:8000/vault-assets/$VAULT_ID/$ASSET_ID/addresses?limit=10"

# Expected response format:
# {
#   "data": {
#     "addresses": [
#       {
#         "address": "rN7n7otQDd6FczFgLdlqtyMVrn3HMfGhKh",
#         "tag": "12345",
#         "legacy_address": null
#       }
#     ]
#   },
#   "statusCode": 200
# }
```

### Test 3: Execute XRPL Transaction

```bash
curl -X POST "http://localhost:8000/xrpl-transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "assetId": "XRP_TEST",
    "transactionType": "TRANSFER",
    "vaultAccountId": "123",
    "params": {
      "destination": "rN7n7otQDd6FczFgLdlqtyMVrn3HMfGhKh",
      "amount": "10",
      "feeLevel": "MEDIUM"
    }
  }'

# Expected response format:
# {
#   "data": {
#     "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#     "status": "SUBMITTED",
#     "assetId": "XRP_TEST",
#     "amount": "10",
#     ...
#   },
#   "statusCode": 201
# }
```

### Test 4: Interactive API Documentation

Visit `http://localhost:8000/docs` to test all endpoints interactively with Swagger UI.

---

## Important Implementation Notes

### 1. Fireblocks SDK Method Names

The method names used in the code are **PLACEHOLDERS**. You MUST verify the actual method names from your Fireblocks Python SDK documentation:

**For py-sdk (fireblocks):**
- Check: https://pypi.org/project/fireblocks/
- Documentation: https://github.com/fireblocks/py-sdk

**For fireblocks-sdk-py:**
- Check: https://pypi.org/project/fireblocks-sdk/
- Documentation: https://github.com/fireblocks/fireblocks-sdk-py

### 2. Response Format Consistency

The Next.js frontend expects responses in this format:
```json
{
  "data": { ... },
  "statusCode": 200
}
```

Ensure all your endpoints return this structure.

### 3. XRPL-Specific SDK

Check if there's a Python version of `fireblocks-xrp-sdk`:
- If yes, use it for XRPL transactions (similar to the TypeScript version in Next.js)
- If no, use the generic Fireblocks transaction API with XRPL-specific parameters

### 4. Error Handling

Ensure consistent error responses:
```json
{
  "detail": "Error message here"
}
```

FastAPI automatically wraps errors in this format when using `HTTPException`.

### 5. Pagination

If the Fireblocks SDK doesn't support pagination parameters (`before`, `after`, `limit`), you may need to:
- Implement client-side pagination
- Return all results and let Django/Next.js handle pagination
- Document the limitation

---

## Troubleshooting

### Issue: "Method not found" errors from Fireblocks SDK

**Cause:** Using incorrect method names for the SDK

**Solution:**
1. Check your SDK version: `pip show fireblocks` and `pip show fireblocks-sdk`
2. Read the SDK source code or documentation
3. Try these alternative method names:
   - `client.vault_accounts.list()`
   - `client.get_vault_accounts()`
   - `client.list_vault_accounts()`

### Issue: Response format doesn't match Next.js expectations

**Cause:** Fireblocks SDK returns different structure than expected

**Solution:** Transform the response before returning:
```python
# Example transformation
fireblocks_response = client.get_vault_accounts()

# Transform to expected format
return {
    "data": {
        "accounts": fireblocks_response,
        "paging": {
            "before": None,
            "after": None
        }
    },
    "statusCode": 200
}
```

### Issue: XRPL transactions failing

**Cause:** Incorrect transaction structure for XRPL

**Solutions:**
1. Check Fireblocks XRPL documentation for required fields
2. Consult Fireblocks support for XRPL-specific requirements
3. Check if you need `extraParameters` for XRPL fields
4. Verify vault account has XRP asset configured

---

## Deployment Notes

### Production Considerations

1. **Environment Variables:** Ensure `.env` has production Fireblocks credentials
2. **Internal Networking:** Service should only be accessible from Django (not public internet)
3. **Logging:** Use structured logging for production monitoring
4. **Rate Limiting:** Consider adding rate limits to prevent API abuse
5. **Timeouts:** XRPL transactions may take longer - adjust timeout settings

### Running in Production

```bash
# Production deployment with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with gunicorn + uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Completion Checklist

- [ ] `app/models.py` updated with new Pydantic models
- [ ] `app/routes/vault_accounts.py` updated with paginated endpoint
- [ ] `app/routes/vault_asset_addresses.py` created
- [ ] `app/routes/xrpl_transactions.py` created
- [ ] `app/main.py` updated to register new routes
- [ ] Verified Fireblocks SDK method names (not using placeholders)
- [ ] Test 1: Get paginated vault accounts succeeds
- [ ] Test 2: Get vault asset addresses succeeds
- [ ] Test 3: Execute XRPL transaction succeeds
- [ ] API documentation auto-generated at `/docs`
- [ ] Error responses are consistent
- [ ] Response format matches Next.js expectations

---

## Questions to Ask Other Teams

**For Django Developer:**
- What exact response format does Django expect from these endpoints?
- Should I add any authentication to the Fireblocks service endpoints? (Currently they're unprotected)
- What error format should I return?

**For Next.js Frontend Developer:**
- What query parameters do you need for vault accounts filtering?
- What XRPL transaction types do you need to support?
- What response fields are required vs optional?
- Do you need pagination support?

---

## Additional Resources

- **Fireblocks API Docs:** https://developers.fireblocks.com/
- **Fireblocks Python SDK:** https://github.com/fireblocks/py-sdk
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **XRPL Docs:** https://xrpl.org/docs.html
