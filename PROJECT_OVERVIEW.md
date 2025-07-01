# Vercel Hybrid Frontend + Python Serverless Setup Guide

## Project Overview
Build a single-user SaaS application using Next.js frontend with Python serverless functions, deployed entirely on Vercel. Features Supabase auth/database and AI-driven sales opportunity detection between sent emails and Pipedrive CRM.

## Architecture Stack
- **Frontend**: Next.js, TypeScript, Tailwind CSS, Shadcn/ui components
- **Backend**: Python serverless functions (Vercel)
- **Database & Auth**: Supabase
- **Integrations**: Pipedrive CRM, Microsoft Outlook
- **AI**: LLM API for sales opportunity detection
- **Deployment**: Vercel (unified frontend + backend)
- **Triggers**: Webhook-driven when user sends emails
- **Real-time**: Supabase subscriptions for live dashboard updates

## Project Structure
## Benefits of This Architecture
/my-saas-app
├── src/                              # Next.js frontend
│   ├── app/                         # App router (Next.js 14)
│   │   ├── (auth)/                  # Auth pages (login, signup)
│   │   ├── dashboard/               # Main dashboard
│   │   ├── integrations/            # Integration management
│   │   └── settings/                # Organization settings
│   ├── components/                  # React components
│   │   ├── ui/                      # Shadcn/ui components
│   │   ├── auth/                    # Auth-related components
│   │   ├── integrations/            # Integration cards/forms
│   │   ├── dashboard/               # Dashboard components
│   │   └── agents/                  # Agent status/logs components
│   ├── lib/                         # Frontend utilities
│   │   ├── supabase.ts             # Supabase client
│   │   ├── api.ts                  # API client for Python functions
│   │   ├── utils.ts                # General utilities
│   │   └── types.ts                # Shared TypeScript types
│   ├── hooks/                       # Custom React hooks
│   └── styles/                      # Tailwind CSS
├── api/                             # Python serverless functions
│   ├── requirements.txt             # Python dependencies
│   ├── lib/                         # Shared Python utilities
│   │   ├── supabase_client.py      # Supabase Python client
│   │   ├── oauth_manager.py        # OAuth token management
│   │   ├── encryption.py           # Token encryption/decryption
│   │   ├── llm_client.py           # LLM API integration
│   │   └── models.py               # Pydantic models
│   ├── webhooks/                    # Webhook handlers
│   │   └── outlook.py              # Outlook sent email webhook
│   ├── oauth/                       # OAuth flow handlers
│   │   ├── pipedrive.py            # Pipedrive OAuth callback
│   │   └── outlook.py              # Outlook OAuth callback
│   ├── agents/                      # AI agent processing functions
│   │   ├── analyze_email.py        # AI sales opportunity analysis
│   │   ├── check_deal_exists.py    # Check if deal exists in Pipedrive
│   │   └── create_deal.py          # Create new deal in Pipedrive
│   └── integrations/                # Integration management
│       ├── connect.py              # Start OAuth flows
│       ├── status.py               # Check connection status
│       └── disconnect.py           # Revoke connections
├── supabase/                        # Database migrations
│   ├── migrations/                  # SQL migration files
│   │   ├── 001_initial_schema.sql  # Initial database setup
│   │   ├── 002_add_indexes.sql     # Performance indexes
│   │   └── 003_add_constraints.sql # Additional constraints
│   └── config.toml                 # Supabase configuration
├── package.json                     # Frontend dependencies
├── requirements.txt                 # Root Python dependencies (same as api/)
├── tailwind.config.js              # Tailwind configuration
├── components.json                  # Shadcn/ui configuration
├── next.config.js                  # Next.js configuration
├── vercel.json                     # Vercel deployment config
└── README.md
```

## Database Schema (Supabase)

### Core Tables
```sql
-- OAuth integrations (single user)
CREATE TABLE integrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  provider VARCHAR(50) NOT NULL, -- 'pipedrive', 'outlook'
  provider_user_id VARCHAR(255),
  provider_user_email VARCHAR(255),
  access_token TEXT NOT NULL,     -- encrypted
  refresh_token TEXT,             -- encrypted
  token_expires_at TIMESTAMP,
  scopes TEXT[],
  webhook_subscription_id VARCHAR(255), -- for Outlook webhook subscriptions
  webhook_endpoint_url TEXT,      -- constructed webhook URL
  metadata JSONB DEFAULT '{}',    -- provider-specific data
  is_active BOOLEAN DEFAULT true,
  last_sync_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, provider)
);

-- Sales opportunity processing logs (GDPR-compliant)
CREATE TABLE opportunity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  email_hash VARCHAR(64) NOT NULL,        -- SHA-256 hash of email content for deduplication
  recipient_email VARCHAR(255) NOT NULL,  -- who the email was sent to
  opportunity_detected BOOLEAN NOT NULL,  -- AI analysis result
  deal_existed BOOLEAN,                   -- whether deal already existed in Pipedrive
  deal_created BOOLEAN DEFAULT false,     -- whether new deal was created
  pipedrive_deal_id VARCHAR(50),         -- reference to created deal
  ai_confidence_score DECIMAL(3,2),      -- AI confidence (0.00 to 1.00)
  ai_reasoning TEXT,                      -- AI explanation for decision
  error_message TEXT,                     -- any processing errors
  processed_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Processing activity logs
CREATE TABLE activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  activity_type VARCHAR(50) NOT NULL,     -- 'email_analyzed', 'deal_created', 'error'
  status VARCHAR(20) NOT NULL,            -- 'success', 'error', 'warning'
  message TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  webhook_id VARCHAR(255),                -- to trace webhook processing
  created_at TIMESTAMP DEFAULT NOW()
);

-- RLS Policies for single-user per account
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can only access their own data" ON integrations
  FOR ALL USING (user_id = auth.uid());

CREATE POLICY "Users can only access their own logs" ON opportunity_logs
  FOR ALL USING (user_id = auth.uid());

CREATE POLICY "Users can only access their own activity" ON activity_logs
  FOR ALL USING (user_id = auth.uid());

-- Performance indexes
CREATE INDEX idx_opportunity_logs_user_id ON opportunity_logs(user_id);
CREATE INDEX idx_opportunity_logs_email_hash ON opportunity_logs(email_hash);
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at DESC);
```

## Technology Dependencies

### Frontend Dependencies (package.json)
```json
{
  "name": "my-saas-app",
  "dependencies": {
    "next": "latest",
    "react": "latest",
    "typescript": "latest",
    "@supabase/supabase-js": "latest",
    "tailwindcss": "latest",
    "class-variance-authority": "latest",
    "clsx": "latest",
    "tailwind-merge": "latest",
    "lucide-react": "latest",
    "axios": "latest",
    "react-hook-form": "latest",
    "@hookform/resolvers": "latest",
    "zod": "latest",
    "date-fns": "latest"
  }
}
```

### Python Dependencies (api/requirements.txt)
```txt
# Supabase and database
supabase

# HTTP client for API calls
httpx
requests

# Token encryption
cryptography

# OpenAI for sales opportunity analysis
openai

# Pydantic for data models
pydantic

# Environment utilities
python-dotenv

# Logging and error handling
structlog
```

## Real-time Dashboard Updates

### Supabase Subscriptions
```typescript
// src/hooks/useRealtime.ts
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'

export function useRealtimeLogs(userId: string) {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Initial fetch
    fetchLogs()
    
    // Real-time subscription
    const subscription = supabase
      .channel('activity_logs')
      .on('postgres_changes', 
        { 
          event: 'INSERT', 
          schema: 'public', 
          table: 'activity_logs',
          filter: `user_id=eq.${userId}`
        }, 
        (payload) => {
          setLogs(prev => [payload.new, ...prev])
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [userId])

  return { logs, loading }
}
```

## AI-Driven Sales Opportunity Processing Flow

### Email Processing Flow
```
1. User sends email in Outlook
   ↓
2. Microsoft sends webhook to /api/webhooks/outlook (sent email event)
   ↓
3. Webhook extracts email data (recipient, subject, snippet)
   ↓
4. Calls /api/agents/analyze_email with email content
   ↓
5. OpenAI analyzes email content for sales opportunity
   ↓
6. If opportunity detected → calls /api/agents/check_deal_exists
   ↓
7. Searches Pipedrive for existing deal with this contact
   ↓
8. If no deal exists → calls /api/agents/create_deal
   ↓
9. Creates new deal in Pipedrive with extracted info
   ↓
10. Logs GDPR-compliant summary (no email content stored)
   ↓
11. Real-time update sent to dashboard via Supabase subscription
```

### Key Python Functions

#### AI Email Analysis with Error Handling
```python
# api/agents/analyze_email.py
import openai
from ..lib.supabase_client import supabase
from ..lib.error_handler import handle_errors
from ..lib.logger import get_logger
import hashlib
import json

logger = get_logger(__name__)

@handle_errors
def handler(request):
    """Analyze sent email for sales opportunities using AI"""
    
    data = request.json()
    user_id = data['user_id']
    email_content = data['email_content']
    recipient_email = data['recipient_email']
    
    logger.info("Starting email analysis", extra={
        "user_id": user_id,
        "recipient_email": recipient_email,
        "content_length": len(email_content)
    })
    
    # Create hash for deduplication (GDPR-compliant)
    email_hash = hashlib.sha256(email_content.encode()).hexdigest()
    
    # Check if we've already processed this email
    existing = supabase.table('opportunity_logs').select('*').eq('email_hash', email_hash).execute()
    if existing.data:
        logger.info("Email already processed", extra={"email_hash": email_hash})
        return {"already_processed": True}
    
    # AI analysis
    ai_prompt = f"""
    Analyze this email to determine if it represents a sales opportunity:
    
    Email content: {email_content}
    Recipient: {recipient_email}
    
    Respond with JSON:
    {{
        "is_opportunity": true/false,
        "confidence": 0.0-1.0,
        "reasoning": "explanation",
        "deal_title": "suggested deal name",
        "deal_value": estimated_value_or_null,
        "deal_stage": "prospecting/proposal/negotiation"
    }}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": ai_prompt}],
        response_format={"type": "json_object"}
    )
    
    ai_result = json.loads(response.choices[0].message.content)
    
    # Log the analysis (without storing email content)
    log_data = {
        "user_id": user_id,
        "email_hash": email_hash,
        "recipient_email": recipient_email,
        "opportunity_detected": ai_result["is_opportunity"],
        "ai_confidence_score": ai_result["confidence"],
        "ai_reasoning": ai_result["reasoning"]
    }
    
    supabase.table('opportunity_logs').insert(log_data).execute()
    
    # Log activity for real-time updates
    activity_data = {
        "user_id": user_id,
        "activity_type": "email_analyzed",
        "status": "success",
        "message": f"Email analyzed for {recipient_email}",
        "metadata": {
            "opportunity_detected": ai_result["is_opportunity"],
            "confidence": ai_result["confidence"]
        }
    }
    supabase.table('activity_logs').insert(activity_data).execute()
    
    logger.info("Email analysis completed", extra={
        "opportunity_detected": ai_result["is_opportunity"],
        "confidence": ai_result["confidence"]
    })
    
    if ai_result["is_opportunity"]:
        return {
            "opportunity_detected": True,
            "ai_analysis": ai_result,
            "next_step": "check_deal_exists"
        }
    
    return {"opportunity_detected": False}
```

## OAuth Integration Configurations

### Pipedrive OAuth
```python
# api/lib/oauth_manager.py
PIPEDRIVE_CONFIG = {
    "auth_url": "https://oauth.pipedrive.com/oauth/authorize",
    "token_url": "https://oauth.pipedrive.com/oauth/token",
    "api_base": "https://api.pipedrive.com/v1",
    "scopes": ["deals:read", "deals:write", "persons:read", "persons:write"],
    "redirect_uri": f"{os.environ['VERCEL_URL']}/api/oauth/pipedrive"
}
```

### Microsoft Outlook OAuth
```python
# api/lib/oauth_manager.py
OUTLOOK_CONFIG = {
    "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
    "api_base": "https://graph.microsoft.com/v1.0",
    "scopes": [
        "https://graph.microsoft.com/Mail.Read",
        "https://graph.microsoft.com/Mail.ReadWrite",
        "https://graph.microsoft.com/User.Read"
    ],
    "redirect_uri": f"{os.environ['VERCEL_URL']}/api/oauth/outlook"
}
```

## Environment Configuration


### Vercel Configuration (vercel.json)
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9"
    }
  },
  "env": {
    "SUPABASE_URL": "@supabase_url",
    "SUPABASE_SERVICE_ROLE_KEY": "@supabase_service_key"
  }
}
```

## Development Workflow

### Initial Setup
```bash
# 1. Create Next.js project
npx create-next-app@latest my-saas-app --typescript --tailwind --app
cd my-saas-app

# 2. Install Shadcn/ui and required components
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card form input label select switch tabs toast alert-dialog dialog dropdown-menu avatar accordion badge

# 3. Install frontend dependencies
npm install @supabase/supabase-js axios react-hook-form @hookform/resolvers zod

# 4. Set up Python environment (for local development)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r api/requirements.txt

# 5. Initialize Supabase with migrations
npx supabase init
npx supabase start
npx supabase db reset
npx supabase migration up
```

### Development Commands
```bash
# Start development (runs both frontend and serverless functions)
vercel dev

# Alternative: separate terminals
npm run dev              # Frontend only
vercel dev --listen 3001 # Functions only

# Database migrations
npx supabase migration new migration_name
npx supabase migration up
npx supabase db reset    # Reset to latest migration
```

### OAuth Provider Setup
1. **Pipedrive Developer Hub**: Create app, set redirect URI to `https://your-vercel-app.vercel.app/api/oauth/pipedrive`
2. **Microsoft Azure AD**: Register app, set redirect URI to `https://your-vercel-app.vercel.app/api/oauth/outlook`
3. **OpenAI**: Get API key from OpenAI platform
4. Configure Outlook webhook for sent emails (Mail.Send scope)

### Deployment
```bash
# Deploy to Vercel (automatically deploys frontend + Python functions)
vercel --prod

# Set environment variables
vercel env add SUPABASE_URL
vercel env add PIPEDRIVE_CLIENT_ID
# ... etc

# Deploy database migrations
npx supabase db push
```

## Success Criteria
1. Users can authenticate via Supabase (single-user accounts)
2. Users can connect Pipedrive and Outlook via OAuth  
3. System detects when user sends emails via Outlook webhook
4. AI analyzes sent emails and identifies sales opportunities
5. System checks Pipedrive for existing deals with email recipients
6. New deals are automatically created in Pipedrive when opportunities are detected
7. All activity is logged with GDPR-compliant data (no email content stored)
8. Users can view opportunity detection and deal creation activity in dashboard
9. Dashboard updates in real-time via Supabase subscriptions
10. Comprehensive error handling and logging throughout the system

## UI Components (Shadcn/ui Implementation)

### Required Shadcn Components
```bash
# Core components for auth and forms
npx shadcn-ui@latest add button card form input label select

# Navigation and layout
npx shadcn-ui@latest add tabs dropdown-menu avatar badge

# Feedback and status
npx shadcn-ui@latest add toast alert-dialog dialog

# Data display
npx shadcn-ui@latest add accordion table

# Interactive elements
npx shadcn-ui@latest add switch checkbox
```

### Key Component Usage

#### Authentication Pages
- **Button**: Primary/secondary actions, OAuth connection buttons
- **Card**: Login/signup form containers
- **Form**: React Hook Form integration with validation
- **Input**: Email, password, organization name fields
- **Label**: Form field labels with proper accessibility

#### Dashboard Components
- **Badge**: Status indicators for integrations (connected/disconnected)
- **Tabs**: Organize dashboard sections (overview, integrations, logs)
- **Avatar**: User profile display
- **Toast**: Success/error notifications for actions

#### Integration Management
- **Card**: Integration provider cards (Pipedrive, Outlook)
- **Switch**: Enable/disable automation rules
- **Dialog**: OAuth connection flows, confirmation modals
- **Alert Dialog**: Disconnect confirmations, error states
- **Dropdown Menu**: Integration settings, user menu

#### Agent Activity & Logs
- **Table**: Display automation logs and action history
- **Accordion**: Expandable log details and error messages
- **Select**: Filter logs by integration, status, date range

### Component Examples

#### Integration Card Component
```typescript
// src/components/integrations/IntegrationCard.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"

interface IntegrationCardProps {
  provider: string
  isConnected: boolean
  onConnect: () => void
  onDisconnect: () => void
  automationEnabled: boolean
  onToggleAutomation: (enabled: boolean) => void
}

export function IntegrationCard({ 
  provider, 
  isConnected, 
  onConnect, 
  onDisconnect,
  automationEnabled,
  onToggleAutomation 
}: IntegrationCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="capitalize">{provider}</CardTitle>
          <Badge variant={isConnected ? "default" : "secondary"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
        </div>
        <CardDescription>
          {provider === 'outlook' ? 'Email automation triggers' : 'CRM data management'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isConnected ? (
          <>
            <div className="flex items-center justify-between">
              <span className="text-sm">Automation</span>
              <Switch 
                checked={automationEnabled} 
                onCheckedChange={onToggleAutomation}
              />
            </div>
            <Button variant="outline" onClick={onDisconnect} className="w-full">
              Disconnect
            </Button>
          </>
        ) : (
          <Button onClick={onConnect} className="w-full">
            Connect {provider}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
```

#### Real-time Agent Logs Component
```typescript
// src/components/agents/AgentLogs.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useRealtimeLogs } from "@/hooks/useRealtime"

interface LogEntry {
  id: string
  timestamp: string
  agent_type: string
  level: 'info' | 'warning' | 'error'
  message: string
  metadata?: any
}

export function AgentLogs({ userId }: { userId: string }) {
  const { logs, loading } = useRealtimeLogs(userId)

  if (loading) {
    return <div>Loading logs...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Automation Activity (Live)</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Time</TableHead>
              <TableHead>Agent</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Message</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id}>
                <TableCell className="text-sm text-muted-foreground">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </TableCell>
                <TableCell className="capitalize">{log.agent_type}</TableCell>
                <TableCell>
                  <Badge variant={
                    log.level === 'error' ? 'destructive' : 
                    log.level === 'warning' ? 'secondary' : 'default'
                  }>
                    {log.level}
                  </Badge>
                </TableCell>
                <TableCell>{log.message}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
```

## Benefits of This Architecture
- **Unified Deployment**: Single `vercel deploy` handles everything
- **Automatic Scaling**: Serverless functions scale with demand
- **Cost Effective**: Pay only for execution time
- **Real-time Processing**: Webhook-driven, no polling required
- **Live Dashboard**: Real-time updates via Supabase subscriptions
- **Type Safety**: Shared types between frontend and backend
- **Developer Experience**: Hot reload for both frontend and functions
- **Database Versioning**: Proper migration system for schema changes
- **Error Handling**: Comprehensive logging and error management