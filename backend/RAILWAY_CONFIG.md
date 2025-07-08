# Railway Configuration Guide

This document outlines the environment variables needed for the production deployment on Railway.

## Required Environment Variables

### AI Configuration
```bash
# OpenRouter API Key (required for AI functionality)
OPENROUTER_API_KEY=your_openrouter_api_key

# Default AI Model (optional, defaults to openai/gpt-4o-mini)
DEFAULT_AI_MODEL=openai/gpt-4o-mini
```

### Supabase Configuration
```bash
# Supabase URL and Keys (required for database access)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### OAuth Configuration
```bash
# Pipedrive OAuth
PIPEDRIVE_CLIENT_ID=your_pipedrive_client_id
PIPEDRIVE_CLIENT_SECRET=your_pipedrive_client_secret
PIPEDRIVE_REDIRECT_URI=https://supa-vercel-infra.vercel.app/oauth/pipedrive/callback

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_REDIRECT_URI=https://supa-vercel-infra.vercel.app/oauth/microsoft/callback
```

### Security Configuration
```bash
# Encryption key for token storage (32 bytes)
ENCRYPTION_KEY=your_32_byte_encryption_key_for_token_storage

# Webhook validation secret
WEBHOOK_SECRET=your_webhook_validation_secret
```

### Frontend URL
```bash
# Frontend URL for CORS and redirects
NEXT_PUBLIC_BACKEND_URL=https://supa-vercel-infra-production.up.railway.app
```

## How to Set Environment Variables in Railway

1. Go to your Railway project dashboard
2. Navigate to the "Variables" tab
3. Add each environment variable listed above
4. Make sure to use the production values (not localhost URLs)

## Testing the Configuration

After setting up the environment variables, you can test the endpoints:

### 1. Health Check
```bash
curl https://supa-vercel-infra-production.up.railway.app/api/health
```

### 2. AI Health Check
```bash
curl https://supa-vercel-infra-production.up.railway.app/api/ai/health
```

### 3. OAuth Infrastructure Test
```bash
curl https://supa-vercel-infra-production.up.railway.app/api/oauth/test
```

### 4. Test with User Tokens (requires user ID)
```bash
# Replace USER_ID with an actual user ID that has Pipedrive tokens stored
curl -X POST https://supa-vercel-infra-production.up.railway.app/api/ai/test-with-user-tokens/USER_ID
```

## Production vs Development Mode

The system automatically detects the environment:

- **Development Mode**: Uses environment variables for testing (if `PIPEDRIVE_ACCESS_TOKEN` is set)
- **Production Mode**: Loads tokens from Supabase database for authenticated users

## Token Storage

In production, tokens are:
1. **Encrypted** using the `ENCRYPTION_KEY`
2. **Stored** in the `integrations` table in Supabase
3. **Retrieved** and **decrypted** when needed for API calls
4. **Refreshed** automatically when they expire

## Troubleshooting

### Common Issues

1. **"No Pipedrive integration found for user"**
   - User needs to complete OAuth flow to store tokens
   - Check if user has connected Pipedrive account

2. **"Failed to decrypt tokens from Supabase"**
   - Check if `ENCRYPTION_KEY` is set correctly
   - Verify the encryption key hasn't changed since tokens were stored

3. **"OpenRouter API key not configured"**
   - Set `OPENROUTER_API_KEY` in Railway environment variables

4. **"Missing required environment variables"**
   - Ensure all required variables are set in Railway
   - Check for typos in variable names

### Testing Locally

To test locally with production-like behavior:

1. Remove `PIPEDRIVE_ACCESS_TOKEN` from your local `.env`
2. Set up all other environment variables
3. Use the test endpoints to verify functionality

## Next Steps

After configuring Railway:

1. **Test the endpoints** using the curl commands above
2. **Connect OAuth accounts** through the frontend
3. **Set up webhooks** for real email processing
4. **Monitor the system** using the monitoring endpoints 