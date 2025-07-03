# Sales AI - AI-Powered Sales Opportunity Detection

A Next.js + Python serverless SaaS application that automatically detects sales opportunities from Outlook emails and creates deals in Pipedrive CRM using AI analysis.

## Features

- 🔐 **Secure Authentication** with Supabase
- 🔗 **Custom OAuth Integrations** with Pipedrive and Microsoft Outlook
- 🤖 **AI-Powered Analysis** for sales opportunity detection
- ⚡ **Real-time Updates** via Supabase subscriptions
- 📊 **Live Dashboard** for monitoring automation activity
- 🛡️ **GDPR Compliant** data handling with encrypted token storage

## Tech Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS v4, Shadcn/ui
- **Backend**: Python serverless functions (Vercel)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **AI**: OpenAI GPT-4
- **Deployment**: Vercel

## Project Structure

```
supa-vercel-infra/
├── src/                          # Next.js frontend
│   ├── app/                     # App Router pages
│   │   ├── dashboard/           # Dashboard with integrations
│   │   ├── login/              # Authentication page
│   │   └── page.tsx            # Landing page
│   ├── components/             # React components
│   │   └── ui/                # Shadcn/ui components
│   └── lib/                   # Utilities
│       └── supabase.ts        # Supabase client
├── api/                        # Python serverless functions
│   ├── lib/                   # Shared utilities
│   │   ├── oauth_manager.py   # OAuth token management
│   │   └── supabase_client.py # Database client
│   ├── oauth/                 # OAuth flow handlers
│   │   ├── pipedrive/         # Pipedrive OAuth
│   │   └── azure/            # Azure OAuth
│   └── requirements.txt       # Python dependencies
├── supabase/                  # Database migrations
│   └── migrations/           # SQL migration files
└── vercel.json              # Vercel configuration
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd supa-vercel-infra
npm install
```

### 2. Environment Variables

Copy the example environment file and configure your variables:

```bash
cp env.example .env.local
```

Required environment variables:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OAuth Providers
PIPEDRIVE_CLIENT_ID=your_pipedrive_client_id
PIPEDRIVE_CLIENT_SECRET=your_pipedrive_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

# AI
OPENAI_API_KEY=your_openai_api_key

# Security
ENCRYPTION_KEY=your_32_byte_encryption_key
WEBHOOK_SECRET=your_webhook_validation_secret
```

### 3. Database Setup

```bash
# Start Supabase locally
npx supabase start

# Apply migrations
npx supabase db reset

# Or push to remote Supabase
npx supabase db push
```

### 4. OAuth Provider Setup

#### Pipedrive Setup

1. Go to [Pipedrive Developer Hub](https://developers.pipedrive.com/)
2. Create a new app
3. Set redirect URI: `https://your-domain.vercel.app/api/oauth/pipedrive/callback`
4. Copy Client ID and Client Secret to environment variables

#### Microsoft Azure Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new application
3. Set redirect URI: `https://your-domain.vercel.app/api/oauth/azure/callback`
4. Add required permissions:
   - `Mail.Read`
   - `Mail.ReadWrite`
   - `User.Read`
5. Copy Client ID and Client Secret to environment variables

### 5. Development

```bash
# Start development server
npm run dev

# The app will be available at http://localhost:3000
```

### 6. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add SUPABASE_SERVICE_ROLE_KEY
# ... add all other environment variables
```

## Vercel Deployment Settings

When importing your GitHub repo to Vercel:

**Root Directory:** `./` (default)

**Build Settings:**
- **Framework Preset:** Next.js
- **Build Command:** `npm run build` (auto-detected)
- **Output Directory:** `.next` (auto-detected)
- **Install Command:** `npm install` (auto-detected)

**Environment Variables:** Add all variables from `.env.local` to Vercel dashboard.

## Custom OAuth Flow

This application uses custom OAuth flows for business logic, not authentication:

### Flow Overview

1. **User Authentication**: Users authenticate via Supabase (email/password)
2. **Integration Connection**: Users connect Pipedrive and Outlook via custom OAuth
3. **Token Storage**: OAuth tokens are encrypted and stored in Supabase
4. **Business Logic**: Tokens are used for API calls to Pipedrive and Outlook
5. **AI Processing**: Email content is analyzed for sales opportunities
6. **Automation**: Deals are automatically created in Pipedrive

### Security Features

- **Token Encryption**: All OAuth tokens are encrypted using Fernet (AES-128)
- **Row Level Security**: Database tables use RLS policies for user isolation
- **JWT Validation**: API routes validate Supabase JWT tokens
- **State Parameter**: OAuth flows include state parameter for CSRF protection

## API Endpoints

### OAuth Endpoints

- `POST /api/oauth/pipedrive/connect` - Initiate Pipedrive OAuth
- `GET /api/oauth/pipedrive/callback` - Pipedrive OAuth callback
- `POST /api/oauth/azure/connect` - Initiate Azure OAuth
- `GET /api/oauth/azure/callback` - Azure OAuth callback

### Authentication

All API endpoints require a valid Supabase JWT token in the Authorization header:

```
Authorization: Bearer <supabase_jwt_token>
```

## Database Schema

### Core Tables

- **integrations**: OAuth integration data (encrypted tokens)
- **opportunity_logs**: Sales opportunity processing logs (GDPR compliant)
- **activity_logs**: Real-time activity monitoring

### Row Level Security

All tables have RLS policies ensuring users can only access their own data:

```sql
CREATE POLICY "Users can only access their own data" ON integrations
  FOR ALL USING (user_id = auth.uid());
```

## Development Workflow

### Local Development

```bash
# Start frontend
npm run dev

# Start Supabase locally
npx supabase start

# Test OAuth flows locally
# Update redirect URIs to http://localhost:3000/api/oauth/*/callback
```

### Testing OAuth

1. Start the development server
2. Navigate to `/dashboard`
3. Click "Connect Pipedrive" or "Connect Outlook"
4. Complete OAuth flow in popup window
5. Verify integration appears in dashboard

### Database Migrations

```bash
# Create new migration
npx supabase migration new migration_name

# Apply migrations
npx supabase migration up

# Reset database
npx supabase db reset
```

## Troubleshooting

### Common Issues

1. **OAuth Redirect URI Mismatch**
   - Ensure redirect URIs match exactly in OAuth provider settings
   - Use `http://localhost:3000` for local development
   - Use your Vercel domain for production

2. **Environment Variables**
   - Verify all environment variables are set in Vercel dashboard
   - Check that `ENCRYPTION_KEY` is exactly 32 bytes

3. **Database Connection**
   - Ensure Supabase is running locally: `npx supabase start`
   - Verify migrations are applied: `npx supabase db reset`

4. **Python Dependencies**
   - Ensure `api/requirements.txt` is up to date
   - Vercel will automatically install dependencies



## Security Considerations

- **Token Encryption**: OAuth tokens are encrypted at rest
- **HTTPS Only**: All production traffic uses HTTPS
- **CORS**: Proper CORS headers for API endpoints
- **Rate Limiting**: Implement rate limiting for production use
- **Input Validation**: All user inputs are validated
- **Error Handling**: Sensitive information is not exposed in error messages

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Supabase and Vercel documentation
3. Open an issue in the repository 