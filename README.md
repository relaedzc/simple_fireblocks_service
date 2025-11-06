# Fireblocks Service

An internal FastAPI service for managing Fireblocks operations with secure credential management.

## Overview

This service provides a REST API interface to Fireblocks, allowing you to keep your Fireblocks API credentials secure on a single server. The service is designed for internal use within your infrastructure.

## Features

- Secure credential management (API key and secret key file separation)
- RESTful API for Fireblocks operations
- Vault account creation and management
- Automatic API documentation (Swagger UI and ReDoc)
- Production-ready Fireblocks configuration
- Health check endpoints
- Modular architecture

## Project Structure

```
fireblocks_service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── fireblocks_client.py    # Fireblocks client singleton
│   ├── models.py               # Pydantic request/response models
│   └── routes/
│       ├── __init__.py
│       └── vault_accounts.py   # Vault account endpoints
├── .env.example                # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the Repository

```bash
cd /path/to/fireblocks_service
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and set your credentials:

```env
FIREBLOCKS_API_KEY=your-api-key-here
FIREBLOCKS_SECRET_KEY_PATH=/path/to/your/fireblocks_secret.key
```

**Important:**
- The API key is stored in the `.env` file
- The secret key must be in a separate `.key` file (PEM format)
- Both `.env` and `.key` files are ignored by git for security

## Running the Service

### Development Mode

```bash
fastapi dev app/main.py
```

The service will start on `http://localhost:8000`

### Development Mode with Custom Port

```bash
fastapi dev app/main.py --port 8080
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production with Custom Port

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```

## API Documentation

Once the service is running, you can access the interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## API Endpoints

### Health Check

```
GET /
```

Returns the service health status.

**Example:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "healthy",
  "service": "fireblocks-service",
  "version": "1.0.0"
}
```

### Create Vault Account

```
POST /vault-accounts
```

Creates a new vault account in Fireblocks.

**Request Body:**
```json
{
  "name": "My Vault Account",
  "hidden_on_ui": false,
  "auto_fuel": false
}
```

**Parameters:**
- `name` (string, required): The name of the vault account
- `hidden_on_ui` (boolean, optional): Whether to hide the account in Fireblocks UI (default: false)
- `auto_fuel` (boolean, optional): Whether to enable automatic fueling (default: false)

**Example:**
```bash
curl -X POST "http://localhost:8000/vault-accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Vault Account",
    "hidden_on_ui": false,
    "auto_fuel": false
  }'
```

**Response (201 Created):**
```json
{
  "id": "0",
  "name": "My Vault Account",
  "hidden_on_ui": false,
  "auto_fuel": false
}
```

**Error Response (500):**
```json
{
  "detail": "Failed to create vault account: <error message>"
}
```

### Create Vault Wallet

```
POST /vault-wallets
```

Creates a new wallet/asset in a vault account.

**Request Body:**
```json
{
  "vault_account_id": "0",
  "asset_id": "ETH"
}
```

**Parameters:**
- `vault_account_id` (string, required): The ID of the vault account
- `asset_id` (string, required): The asset/blockchain identifier (e.g., BTC, ETH, SOL, MATIC)

**Example:**
```bash
curl -X POST "http://localhost:8000/vault-wallets" \
  -H "Content-Type: application/json" \
  -d '{
    "vault_account_id": "0",
    "asset_id": "ETH"
  }'
```

**Response (201 Created):**
```json
{
  "id": "0",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "legacy_address": null,
  "tag": null
}
```

**Error Response (500):**
```json
{
  "detail": "Failed to create vault wallet: <error message>"
}
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FIREBLOCKS_API_KEY` | Your Fireblocks API key | Yes |
| `FIREBLOCKS_SECRET_KEY_PATH` | Path to your Fireblocks secret key file (.key) | Yes |

### Fireblocks Environment

The service is configured to use the **Fireblocks Production (US)** environment by default. This is set in `app/fireblocks_client.py`:

```python
base_path=BasePath.US  # Production environment
```

## Security Notes

- Never commit `.env` or `.key` files to version control
- Keep your secret key file in a secure location with restricted permissions
- Run this service in a secure, internal network
- Consider adding authentication to the API endpoints if exposing beyond localhost
- Use HTTPS in production environments
- Regularly rotate your API credentials

## Error Handling

The service includes comprehensive error handling:

- Configuration validation on startup
- Fireblocks API error propagation
- HTTP status codes following REST conventions
- Detailed error messages in responses

## Development

### Adding New Endpoints

1. Create a new router in `app/routes/`
2. Define Pydantic models in `app/models.py`
3. Register the router in `app/main.py`

### Testing

You can test the endpoints using:
- The interactive Swagger UI at `/docs`
- curl commands
- Postman or similar API testing tools
- Python requests library

## License

Internal use only.

## Support

For issues or questions, contact your infrastructure team.
