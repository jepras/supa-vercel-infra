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