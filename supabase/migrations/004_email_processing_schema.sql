-- Email processing schema for Microsoft Graph webhook integration
-- Migration: 004_email_processing_schema.sql

-- Emails table for storing email metadata
CREATE TABLE emails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  microsoft_email_id VARCHAR(255) NOT NULL,
  subject TEXT,
  sender_email VARCHAR(255),
  recipient_email VARCHAR(255),
  sent_at TIMESTAMP,
  webhook_received_at TIMESTAMP DEFAULT NOW(),
  processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
  content_retrieved BOOLEAN DEFAULT false,
  ai_analyzed BOOLEAN DEFAULT false,
  opportunity_detected BOOLEAN,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(microsoft_email_id)
);

-- Webhook subscriptions table for managing Microsoft Graph subscriptions
CREATE TABLE webhook_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  subscription_id VARCHAR(255) NOT NULL,
  resource VARCHAR(255) NOT NULL, -- e.g., '/me/messages'
  change_type VARCHAR(50) NOT NULL, -- e.g., 'created'
  notification_url TEXT NOT NULL,
  expiration_date TIMESTAMP NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(subscription_id)
);

-- Row Level Security (RLS) policies for emails table
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;

-- Users can only access their own emails
CREATE POLICY "Users can view their own emails" ON emails
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own emails" ON emails
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own emails" ON emails
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own emails" ON emails
  FOR DELETE USING (auth.uid() = user_id);

-- Row Level Security (RLS) policies for webhook_subscriptions table
ALTER TABLE webhook_subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can only access their own webhook subscriptions
CREATE POLICY "Users can view their own webhook subscriptions" ON webhook_subscriptions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own webhook subscriptions" ON webhook_subscriptions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own webhook subscriptions" ON webhook_subscriptions
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own webhook subscriptions" ON webhook_subscriptions
  FOR DELETE USING (auth.uid() = user_id);

-- Performance indexes for emails table
CREATE INDEX idx_emails_user_id ON emails(user_id);
CREATE INDEX idx_emails_microsoft_email_id ON emails(microsoft_email_id);
CREATE INDEX idx_emails_processing_status ON emails(processing_status);
CREATE INDEX idx_emails_webhook_received_at ON emails(webhook_received_at DESC);
CREATE INDEX idx_emails_opportunity_detected ON emails(opportunity_detected);
CREATE INDEX idx_emails_ai_analyzed ON emails(ai_analyzed);
CREATE INDEX idx_emails_content_retrieved ON emails(content_retrieved);
CREATE INDEX idx_emails_sender_email ON emails(sender_email);
CREATE INDEX idx_emails_recipient_email ON emails(recipient_email);

-- Performance indexes for webhook_subscriptions table
CREATE INDEX idx_webhook_subscriptions_user_id ON webhook_subscriptions(user_id);
CREATE INDEX idx_webhook_subscriptions_subscription_id ON webhook_subscriptions(subscription_id);
CREATE INDEX idx_webhook_subscriptions_is_active ON webhook_subscriptions(is_active);
CREATE INDEX idx_webhook_subscriptions_expiration_date ON webhook_subscriptions(expiration_date);
CREATE INDEX idx_webhook_subscriptions_resource ON webhook_subscriptions(resource);

-- Trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the trigger to both tables
CREATE TRIGGER update_emails_updated_at BEFORE UPDATE ON emails
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_webhook_subscriptions_updated_at BEFORE UPDATE ON webhook_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 