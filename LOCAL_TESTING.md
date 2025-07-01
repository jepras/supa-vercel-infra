# Local Testing Guide

This guide will help you test the application locally before deploying to Vercel.

## Prerequisites

- Node.js 18+
- Python 3.9+
- Supabase account
- OAuth provider accounts (Pipedrive, Microsoft Azure)

## Quick Setup

Run the setup script:

```bash
./setup-local.sh
```

## Step-by-Step Setup

### 1. Environment Variables

Create and configure your `.env.local` file:

```bash
cp env.example .env.local
```

**Required variables for local testing:**

```bash
# Supabase (get from your Supabase project)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OAuth Providers (for local testing)
PIPEDRIVE_CLIENT_ID=your_pipedrive_client_id
PIPEDRIVE_CLIENT_SECRET=your_pipedrive_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

# Security (generate these)
ENCRYPTION_KEY=your_32_byte_encryption_key
WEBHOOK_SECRET=your_webhook_secret

# Development
NODE_ENV=development
```

**Generate encryption key:**
```bash
# Generate a 32-byte key
openssl rand -base64 32
```

### 2. Database Setup

Start Supabase locally:

```bash
npx supabase start
```

Apply migrations:

```bash
npx supabase db reset
```

### 3. OAuth Provider Configuration

#### Pipedrive Setup

1. Go to [Pipedrive Developer Hub](https://developers.pipedrive.com/)
2. Create a new app
3. Set redirect URI: `http://localhost:3000/api/oauth/pipedrive/callback`
4. Copy Client ID and Client Secret to `.env.local`

#### Microsoft Azure Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new application
3. Set redirect URI: `http://localhost:3000/api/oauth/azure/callback`
4. Add required permissions:
   - `Mail.Read`
   - `Mail.ReadWrite`
   - `User.Read`
5. Copy Client ID and Client Secret to `.env.local`

### 4. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Testing the Application

### 1. Authentication Test

1. Navigate to `http://localhost:3000`
2. You should be redirected to `/login` if not authenticated
3. Create a test account or sign in
4. Verify you're redirected to `/dashboard`

### 2. OAuth Integration Test

1. Go to `/dashboard`
2. Click "Connect Pipedrive" or "Connect Outlook"
3. A popup window should open with the OAuth provider
4. Complete the authorization flow
5. Verify the integration appears as "Connected" in the dashboard
6. Check the activity logs tab for OAuth events

### 3. Database Verification

Check that data is being stored correctly:

```bash
# Connect to local Supabase
npx supabase db reset

# Check integrations table
npx supabase db query "SELECT * FROM integrations;"

# Check activity logs
npx supabase db query "SELECT * FROM activity_logs;"
```

### 4. API Endpoint Testing

Test the OAuth endpoints directly:

```bash
# Test OAuth initiation (requires authentication)
curl -X POST http://localhost:3000/api/oauth/pipedrive/connect \
  -H "Authorization: Bearer YOUR_SUPABASE_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

## Troubleshooting Local Issues

### Common Problems

1. **OAuth Redirect URI Mismatch**
   - Ensure redirect URIs in OAuth provider settings exactly match:
     - `http://localhost:3000/api/oauth/pipedrive/callback`
     - `http://localhost:3000/api/oauth/azure/callback`

2. **Environment Variables**
   - Verify all variables are set in `.env.local`
   - Check that `ENCRYPTION_KEY` is exactly 32 bytes
   - Restart the dev server after changing environment variables

3. **Database Connection**
   - Ensure Supabase is running: `npx supabase status`
   - Reset database if needed: `npx supabase db reset`

4. **Python Dependencies**
   - Install Python dependencies: `pip install -r api/requirements.txt`
   - For local testing, you can use `vercel dev` to test serverless functions

### Debug Mode

Enable debug logging:

```bash
# Set debug environment variable
export DEBUG=*

# Start with debug logging
npm run dev
```

### Testing Serverless Functions Locally

Install Vercel CLI and test Python functions:

```bash
# Install Vercel CLI
npm i -g vercel

# Test serverless functions locally
vercel dev

# This will start both frontend and serverless functions
# Frontend: http://localhost:3000
# Functions: http://localhost:3001
```

## Local vs Production Differences

| Aspect | Local | Production |
|--------|-------|------------|
| Redirect URIs | `http://localhost:3000` | `https://your-domain.vercel.app` |
| Database | Local Supabase | Remote Supabase |
| Functions | Vercel dev server | Vercel production |
| Environment | `.env.local` | Vercel dashboard |

## Next Steps After Local Testing

1. **Fix any issues** found during local testing
2. **Deploy to Vercel** with production environment variables
3. **Update OAuth redirect URIs** to production URLs
4. **Test production deployment**

## Security Notes for Local Testing

- Use test OAuth applications for local development
- Don't commit `.env.local` to version control
- Use different encryption keys for local vs production
- Test with dummy data when possible 