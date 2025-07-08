# Token Refresh Implementation

This document describes the automatic token refresh implementation for both Pipedrive and Microsoft Graph API integrations.

## Overview

Both Pipedrive and Microsoft OAuth tokens have expiration times. To ensure uninterrupted service, the system automatically refreshes tokens when they expire, so users don't need to re-authenticate frequently.

## Architecture

### 1. Token Storage
- **Encrypted Storage**: All tokens are encrypted before storing in Supabase
- **Refresh Tokens**: Both providers return refresh tokens that are stored securely
- **User Association**: Tokens are associated with specific users via `user_id`

### 2. Automatic Refresh Mechanism
- **Lazy Refresh**: Tokens are refreshed only when needed (on 401 errors)
- **Transparent**: API calls automatically handle token refresh without user intervention
- **Retry Logic**: Failed API calls due to expired tokens are retried with fresh tokens

## Implementation Details

### Pipedrive Token Refresh

**File**: `backend/app/agents/pipedrive_manager.py`

**Key Features**:
- Automatic token loading from Supabase
- Token decryption on load
- Automatic refresh on 401 errors
- Token re-encryption and storage after refresh

**Refresh Flow**:
1. API call fails with 401 (Unauthorized)
2. System detects expired token
3. Uses refresh token to get new access token
4. Updates tokens in Supabase (encrypted)
5. Retries original API call with new token

**Code Example**:
```python
async def _make_api_call(self, method: str, url: str, **kwargs):
    # Make initial API call
    response = await client.request(method, url, **kwargs)
    
    if response.status_code == 401:
        # Token expired, refresh and retry
        await self._refresh_access_token()
        # Retry with new token
        response = await client.request(method, url, **kwargs)
```

### Microsoft Token Refresh

**File**: `backend/app/agents/microsoft_manager.py`

**Key Features**:
- Similar architecture to Pipedrive
- Microsoft Graph API specific endpoints
- Handles Microsoft user ID mapping
- Webhook subscription management

**Refresh Flow**:
1. API call fails with 401 (Unauthorized)
2. System detects expired token
3. Uses refresh token to get new access token from Microsoft
4. Updates tokens in Supabase (encrypted)
5. Retries original API call with new token

## Error Handling

### Error Decorators
- `@handle_token_refresh_errors`: Handles token refresh specific errors
- `@handle_pipedrive_errors`: Handles Pipedrive API errors with retry logic
- `@handle_microsoft_errors`: Handles Microsoft Graph API errors with retry logic

### Custom Exceptions
- `TokenRefreshError`: Raised when token refresh fails
- `PipedriveError`: Raised when Pipedrive operations fail
- `MicrosoftError`: Raised when Microsoft operations fail

## Testing

### Test Endpoints

**Token Refresh Test**: `POST /api/ai/test-token-refresh/{user_id}`
- Tests both Pipedrive and Microsoft token refresh
- Returns detailed status for each provider
- Shows user information if tokens are valid

### Test Scripts

**Python Script**: `backend/test_token_refresh.py`
```bash
# Set environment variables
export TEST_USER_ID="your-user-id"
export BACKEND_URL="https://your-backend.railway.app"

# Run test
python backend/test_token_refresh.py
```

**Curl Script**: `backend/test_token_refresh_curl.sh`
```bash
# Set environment variables
export TEST_USER_ID="your-user-id"
export BACKEND_URL="https://your-backend.railway.app"

# Run test
./backend/test_token_refresh_curl.sh
```

## Environment Variables

### Required for Token Refresh
- `PIPEDRIVE_CLIENT_ID`: Pipedrive OAuth client ID
- `PIPEDRIVE_CLIENT_SECRET`: Pipedrive OAuth client secret
- `MICROSOFT_CLIENT_ID`: Microsoft OAuth client ID
- `MICROSOFT_CLIENT_SECRET`: Microsoft OAuth client secret
- `ENCRYPTION_KEY`: Key for encrypting/decrypting tokens

### Database Schema
The `integrations` table stores:
- `access_token`: Encrypted access token
- `refresh_token`: Encrypted refresh token
- `token_expires_at`: Token expiration timestamp
- `user_id`: Associated user ID
- `provider`: "pipedrive" or "microsoft"
- `microsoft_user_id`: Microsoft-specific user ID (for Microsoft integrations)

## Security Considerations

### Token Encryption
- All tokens are encrypted using AES-256-GCM
- Encryption key is stored as environment variable
- Decryption only happens in memory during API calls

### Token Rotation
- Refresh tokens are updated when new ones are provided
- Old tokens are immediately replaced
- No token reuse across sessions

### Access Control
- Tokens are user-specific
- Row Level Security (RLS) policies protect token access
- API calls require valid user authentication

## Monitoring and Logging

### Agent Logger
- Structured logging for all token operations
- Correlation IDs for tracking operations
- Success/failure metrics for token refresh

### Log Categories
- `log_token_refresh()`: Token refresh operations
- `log_pipedrive_operation()`: Pipedrive API operations
- `log_microsoft_operation()`: Microsoft API operations

## Production Deployment

### Railway Configuration
All required environment variables must be set in Railway:
- OAuth client IDs and secrets
- Encryption key
- Database connection strings

### Health Checks
- Token refresh endpoints are available for monitoring
- Automatic retry logic handles temporary failures
- Graceful degradation when tokens are invalid

## Troubleshooting

### Common Issues

1. **Token Refresh Fails**
   - Check OAuth client credentials
   - Verify encryption key is correct
   - Check network connectivity to OAuth providers

2. **401 Errors Persist**
   - Refresh tokens may be expired
   - User may need to re-authenticate
   - Check OAuth app permissions

3. **Database Errors**
   - Verify Supabase connection
   - Check RLS policies
   - Ensure user exists in database

### Debug Steps
1. Check application logs for token refresh errors
2. Test token refresh endpoint manually
3. Verify OAuth app configuration
4. Check environment variables in Railway

## Future Enhancements

### Planned Improvements
- Proactive token refresh (before expiration)
- Token refresh metrics and alerts
- Multi-tenant token management
- Token refresh webhook notifications

### Monitoring
- Token expiration tracking
- Refresh success rate monitoring
- User re-authentication frequency tracking 