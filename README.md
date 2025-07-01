# SaaS App - Sales Opportunity Detection

A single-user SaaS application using Next.js frontend with Python serverless functions, deployed entirely on Vercel. Features Supabase auth/database and AI-driven sales opportunity detection between sent emails and Pipedrive CRM.

## Architecture Stack

- **Frontend**: Next.js, TypeScript, Tailwind CSS, Shadcn/ui components
- **Backend**: Python serverless functions (Vercel)
- **Database & Auth**: Supabase
- **Integrations**: Pipedrive CRM, Microsoft Outlook
- **AI**: LLM API for sales opportunity detection
- **Deployment**: Vercel (unified frontend + backend)

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Supabase account
- Vercel account

### Development Setup

1. **Clone and install dependencies:**
   ```bash
   git clone <your-repo>
   cd supa-vercel-infra
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your actual values
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) to see the application.

## Project Structure

```
/
├── src/                          # Next.js frontend
│   ├── app/                     # App router (Next.js 14)
│   ├── components/              # React components
│   ├── lib/                     # Frontend utilities
│   └── hooks/                   # Custom React hooks
├── api/                         # Python serverless functions
│   ├── agents/                  # AI agent processing functions
│   ├── integrations/            # Integration management
│   ├── lib/                     # Shared Python utilities
│   ├── oauth/                   # OAuth flow handlers
│   └── webhooks/                # Webhook handlers
├── supabase/                    # Database migrations
│   └── migrations/              # SQL migration files
└── requirements.txt             # Python dependencies
```

## Features

- 🔐 **Secure Authentication** with Supabase
- 🔗 **OAuth Integrations** with Pipedrive and Microsoft Outlook
- 🤖 **AI-Powered Analysis** for sales opportunity detection
- ⚡ **Real-time Updates** via Supabase subscriptions
- 📊 **Live Dashboard** for monitoring automation activity
- 🛡️ **GDPR Compliant** data handling

## Next Steps

1. Set up Supabase project and configure environment variables
2. Implement authentication pages
3. Set up OAuth integrations
4. Build the dashboard UI
5. Implement AI processing functions
6. Deploy to Vercel

## License

MIT 