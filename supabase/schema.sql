-- =============================================================================
-- SUPABASE DATABASE SCHEMA
-- Current schema after all migrations (001-008)
-- Generated: $(date)
-- Updated: 2025-07-08 (Added monitoring tables)
-- =============================================================================

-- =============================================================================
-- TABLE: integrations
-- Purpose: Store OAuth integration data for Pipedrive and Microsoft Outlook
-- =============================================================================
CREATE TABLE "public"."integrations" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "provider" text NOT NULL,                    -- 'pipedrive', 'outlook'
    "access_token" text NOT NULL,                -- encrypted
    "refresh_token" text,                        -- encrypted
    "token_expires_at" timestamp with time zone,
    "microsoft_user_id" text,                    -- Microsoft Graph user ID
    "scopes" text[] DEFAULT '{}',
    "metadata" jsonb DEFAULT '{}',               -- provider-specific data
    "is_active" boolean DEFAULT true,
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "integrations_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "integrations_user_id_provider_key" UNIQUE ("user_id", "provider")
);

-- =============================================================================
-- TABLE: activity_logs
-- Purpose: Track all system activities for monitoring and debugging
-- =============================================================================
CREATE TABLE "public"."activity_logs" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "activity_type" text NOT NULL,               -- 'email_analyzed', 'deal_created', 'error'
    "description" text,                          -- human-readable description
    "status" text DEFAULT 'pending',             -- 'success', 'error', 'warning', 'pending'
    "metadata" jsonb DEFAULT '{}',               -- additional activity data
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "activity_logs_pkey" PRIMARY KEY ("id")
);

-- =============================================================================
-- TABLE: opportunity_logs
-- Purpose: GDPR-compliant logging of sales opportunities detected by AI
-- =============================================================================
CREATE TABLE "public"."opportunity_logs" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "email_hash" text,                           -- SHA-256 hash for deduplication
    "sender_email" text,                         -- who sent the email
    "recipient_email" text,                      -- who received the email
    "subject" text,                              -- email subject line
    "opportunity_detected" boolean,              -- AI analysis result
    "confidence_score" numeric,                  -- AI confidence (0.00 to 1.00)
    "reasoning" text,                            -- AI explanation for decision
    "metadata" jsonb DEFAULT '{}',               -- additional opportunity data
    "created_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "opportunity_logs_pkey" PRIMARY KEY ("id")
);

-- =============================================================================
-- TABLE: emails
-- Purpose: Store email metadata from Microsoft Graph webhooks
-- =============================================================================
CREATE TABLE "public"."emails" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "microsoft_email_id" text NOT NULL,          -- Microsoft Graph email ID
    "subject" text,                              -- email subject
    "sender_email" text,                         -- sender email address
    "recipient_emails" text[],                   -- array of recipient emails
    "sent_at" timestamp with time zone,          -- when email was sent
    "received_at" timestamp with time zone,      -- when webhook was received
    "body_content" text,                         -- email body content
    "body_content_type" text,                    -- content type (text/html, text/plain)
    "webhook_received_at" timestamp with time zone,
    "processing_status" text DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    "content_retrieved" boolean DEFAULT false,   -- whether content was retrieved from Graph
    "ai_analyzed" boolean DEFAULT false,         -- whether AI analysis was performed
    "opportunity_detected" boolean,              -- AI analysis result
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "emails_pkey" PRIMARY KEY ("id")
);

-- =============================================================================
-- TABLE: webhook_subscriptions
-- Purpose: Manage Microsoft Graph webhook subscriptions
-- =============================================================================
CREATE TABLE "public"."webhook_subscriptions" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "subscription_id" text NOT NULL,             -- Microsoft Graph subscription ID
    "provider" text NOT NULL DEFAULT 'microsoft',
    "notification_url" text NOT NULL,            -- webhook endpoint URL
    "expiration_date" timestamp with time zone,  -- subscription expiration
    "is_active" boolean DEFAULT true,
    "metadata" jsonb DEFAULT '{}',               -- subscription metadata
    "change_type" text,                          -- 'created', 'updated', 'deleted'
    "resource" text,                             -- '/me/messages', '/users/{id}/messages'
    "application_id" text,                       -- Microsoft application ID
    "creator_id" text,                           -- subscription creator ID
    "notification_query_options" jsonb,          -- query options for notifications
    "lifecycle_notification_url" text,           -- lifecycle notification URL
    "include_resource_data" boolean,             -- whether to include resource data
    "latest_supported_tls_version" text,         -- TLS version requirement
    "encryption_certificate" text,               -- encryption certificate
    "encryption_certificate_id" text,            -- encryption certificate ID
    "notification_url_app_id" text,              -- notification URL app ID
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "webhook_subscriptions_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "webhook_subscriptions_subscription_id_key" UNIQUE ("subscription_id")
);

-- =============================================================================
-- MONITORING TABLES
-- Purpose: Database persistence for cost tracking, performance metrics, and rate limiting
-- =============================================================================

-- =============================================================================
-- TABLE: cost_records
-- Purpose: Records of OpenRouter API costs for AI operations
-- =============================================================================
CREATE TABLE "public"."cost_records" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "timestamp" timestamp with time zone NOT NULL DEFAULT now(),
    "model" varchar(100) NOT NULL,
    "input_tokens" integer NOT NULL,
    "output_tokens" integer NOT NULL,
    "cost_usd" decimal(10,6) NOT NULL,
    "operation" varchar(100) NOT NULL,
    "correlation_id" uuid NOT NULL,
    "user_id" uuid REFERENCES auth.users(id) ON DELETE SET NULL,
    "created_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "cost_records_pkey" PRIMARY KEY ("id")
);

-- =============================================================================
-- TABLE: performance_metrics
-- Purpose: Performance metrics for system operations
-- =============================================================================
CREATE TABLE "public"."performance_metrics" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "timestamp" timestamp with time zone NOT NULL DEFAULT now(),
    "operation" varchar(100) NOT NULL,
    "duration_ms" integer NOT NULL,
    "success" boolean NOT NULL,
    "correlation_id" uuid NOT NULL,
    "user_id" uuid REFERENCES auth.users(id) ON DELETE SET NULL,
    "metadata" jsonb DEFAULT '{}',
    "created_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "performance_metrics_pkey" PRIMARY KEY ("id")
);

-- =============================================================================
-- TABLE: system_metrics
-- Purpose: System-level metrics like CPU, memory usage
-- =============================================================================
CREATE TABLE "public"."system_metrics" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "timestamp" timestamp with time zone NOT NULL DEFAULT now(),
    "metric_name" varchar(100) NOT NULL,
    "metric_value" decimal(10,4) NOT NULL,
    "metric_unit" varchar(50) NOT NULL,
    "created_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "system_metrics_pkey" PRIMARY KEY ("id")
);

-- =============================================================================
-- TABLE: rate_limit_records
-- Purpose: Records of rate limit checks and blocks
-- =============================================================================
CREATE TABLE "public"."rate_limit_records" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "timestamp" timestamp with time zone NOT NULL DEFAULT now(),
    "operation" varchar(100) NOT NULL,
    "user_id" uuid REFERENCES auth.users(id) ON DELETE SET NULL,
    "ip_address" inet,
    "user_agent" text,
    "correlation_id" uuid NOT NULL,
    "was_blocked" boolean NOT NULL DEFAULT false,
    "created_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "rate_limit_records_pkey" PRIMARY KEY ("id")
);

-- =============================================================================
-- TABLE: rate_limit_windows
-- Purpose: Current rate limit windows and usage counts
-- =============================================================================
CREATE TABLE "public"."rate_limit_windows" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "operation" varchar(100) NOT NULL,
    "user_id" uuid REFERENCES auth.users(id) ON DELETE SET NULL,
    "window_start" timestamp with time zone NOT NULL,
    "window_end" timestamp with time zone NOT NULL,
    "requests_count" integer NOT NULL DEFAULT 0,
    "max_requests" integer NOT NULL,
    "window_seconds" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "rate_limit_windows_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "rate_limit_windows_unique" UNIQUE ("operation", "user_id", "window_start")
);

-- =============================================================================
-- INDEXES
-- Performance optimization indexes
-- =============================================================================

-- Integrations indexes
CREATE INDEX "idx_integrations_user_id" ON "public"."integrations" ("user_id");
CREATE INDEX "idx_integrations_provider" ON "public"."integrations" ("provider");
CREATE INDEX "idx_integrations_is_active" ON "public"."integrations" ("is_active");
CREATE INDEX "idx_integrations_microsoft_user_id" ON "public"."integrations" ("microsoft_user_id");

-- Activity logs indexes
CREATE INDEX "idx_activity_logs_user_id" ON "public"."activity_logs" ("user_id");
CREATE INDEX "idx_activity_logs_activity_type" ON "public"."activity_logs" ("activity_type");
CREATE INDEX "idx_activity_logs_status" ON "public"."activity_logs" ("status");
CREATE INDEX "idx_activity_logs_created_at" ON "public"."activity_logs" ("created_at");

-- Opportunity logs indexes
CREATE INDEX "idx_opportunity_logs_user_id" ON "public"."opportunity_logs" ("user_id");
CREATE INDEX "idx_opportunity_logs_email_hash" ON "public"."opportunity_logs" ("email_hash");
CREATE INDEX "idx_opportunity_logs_opportunity_detected" ON "public"."opportunity_logs" ("opportunity_detected");
CREATE INDEX "idx_opportunity_logs_recipient_email" ON "public"."opportunity_logs" ("recipient_email");
CREATE INDEX "idx_opportunity_logs_created_at" ON "public"."opportunity_logs" ("created_at");

-- Emails indexes
CREATE INDEX "idx_emails_user_id" ON "public"."emails" ("user_id");
CREATE INDEX "idx_emails_microsoft_email_id" ON "public"."emails" ("microsoft_email_id");
CREATE INDEX "idx_emails_processing_status" ON "public"."emails" ("processing_status");

-- Webhook subscriptions indexes
CREATE INDEX "idx_webhook_subscriptions_user_id" ON "public"."webhook_subscriptions" ("user_id");
CREATE INDEX "idx_webhook_subscriptions_provider" ON "public"."webhook_subscriptions" ("provider");
CREATE INDEX "idx_webhook_subscriptions_is_active" ON "public"."webhook_subscriptions" ("is_active");
CREATE INDEX "idx_webhook_subscriptions_expiration_date" ON "public"."webhook_subscriptions" ("expiration_date");
CREATE INDEX "idx_webhook_subscriptions_resource" ON "public"."webhook_subscriptions" ("resource");

-- Monitoring tables indexes
CREATE INDEX "idx_cost_records_timestamp" ON "public"."cost_records" ("timestamp");
CREATE INDEX "idx_cost_records_user_id" ON "public"."cost_records" ("user_id");
CREATE INDEX "idx_cost_records_model" ON "public"."cost_records" ("model");
CREATE INDEX "idx_cost_records_operation" ON "public"."cost_records" ("operation");

CREATE INDEX "idx_performance_metrics_timestamp" ON "public"."performance_metrics" ("timestamp");
CREATE INDEX "idx_performance_metrics_operation" ON "public"."performance_metrics" ("operation");
CREATE INDEX "idx_performance_metrics_user_id" ON "public"."performance_metrics" ("user_id");
CREATE INDEX "idx_performance_metrics_success" ON "public"."performance_metrics" ("success");

CREATE INDEX "idx_system_metrics_timestamp" ON "public"."system_metrics" ("timestamp");
CREATE INDEX "idx_system_metrics_name" ON "public"."system_metrics" ("metric_name");

CREATE INDEX "idx_rate_limit_records_timestamp" ON "public"."rate_limit_records" ("timestamp");
CREATE INDEX "idx_rate_limit_records_operation" ON "public"."rate_limit_records" ("operation");
CREATE INDEX "idx_rate_limit_records_user_id" ON "public"."rate_limit_records" ("user_id");
CREATE INDEX "idx_rate_limit_records_blocked" ON "public"."rate_limit_records" ("was_blocked");

CREATE INDEX "idx_rate_limit_windows_operation_user" ON "public"."rate_limit_windows" ("operation", "user_id");
CREATE INDEX "idx_rate_limit_windows_window_end" ON "public"."rate_limit_windows" ("window_end");

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- Enable RLS and create policies for data isolation
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE "public"."integrations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."activity_logs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."opportunity_logs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."emails" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."webhook_subscriptions" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."cost_records" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."performance_metrics" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."system_metrics" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."rate_limit_records" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."rate_limit_windows" ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can only access their own integrations" ON "public"."integrations"
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own activity logs" ON "public"."activity_logs"
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own opportunity logs" ON "public"."opportunity_logs"
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own emails" ON "public"."emails"
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own webhook subscriptions" ON "public"."webhook_subscriptions"
    FOR ALL USING (auth.uid() = user_id);

-- Monitoring tables RLS policies
CREATE POLICY "Users can view their own cost records" ON "public"."cost_records"
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Service can insert cost records" ON "public"."cost_records"
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view their own performance metrics" ON "public"."performance_metrics"
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Service can insert performance metrics" ON "public"."performance_metrics"
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Authenticated users can view system metrics" ON "public"."system_metrics"
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Service can insert system metrics" ON "public"."system_metrics"
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view their own rate limit records" ON "public"."rate_limit_records"
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Service can insert rate limit records" ON "public"."rate_limit_records"
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view their own rate limit windows" ON "public"."rate_limit_windows"
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Service can insert and update rate limit windows" ON "public"."rate_limit_windows"
    FOR ALL USING (true);

-- =============================================================================
-- TRIGGERS
-- Automatic timestamp updates
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_emails_updated_at BEFORE UPDATE ON emails
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_webhook_subscriptions_updated_at BEFORE UPDATE ON webhook_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rate_limit_windows_updated_at BEFORE UPDATE ON rate_limit_windows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- COMMENTS
-- Documentation for columns and tables
-- =============================================================================

COMMENT ON TABLE "public"."integrations" IS 'OAuth integration data for Pipedrive and Microsoft Outlook';
COMMENT ON COLUMN "public"."integrations"."microsoft_user_id" IS 'Microsoft Graph user ID for Microsoft integrations';
COMMENT ON COLUMN "public"."integrations"."access_token" IS 'Encrypted OAuth access token';
COMMENT ON COLUMN "public"."integrations"."refresh_token" IS 'Encrypted OAuth refresh token';

COMMENT ON TABLE "public"."activity_logs" IS 'System activity tracking for monitoring and debugging';
COMMENT ON COLUMN "public"."activity_logs"."activity_type" IS 'Type of activity: email_analyzed, deal_created, error, etc.';
COMMENT ON COLUMN "public"."activity_logs"."status" IS 'Activity status: success, error, warning, pending';

COMMENT ON TABLE "public"."opportunity_logs" IS 'GDPR-compliant logging of sales opportunities detected by AI';
COMMENT ON COLUMN "public"."opportunity_logs"."email_hash" IS 'SHA-256 hash of email content for deduplication';
COMMENT ON COLUMN "public"."opportunity_logs"."confidence_score" IS 'AI confidence score (0.00 to 1.00)';

COMMENT ON TABLE "public"."emails" IS 'Email metadata from Microsoft Graph webhooks';
COMMENT ON COLUMN "public"."emails"."microsoft_email_id" IS 'Unique Microsoft Graph email identifier';
COMMENT ON COLUMN "public"."emails"."processing_status" IS 'Email processing status: pending, processing, completed, failed';

COMMENT ON TABLE "public"."webhook_subscriptions" IS 'Microsoft Graph webhook subscription management';
COMMENT ON COLUMN "public"."webhook_subscriptions"."subscription_id" IS 'Microsoft Graph subscription identifier';
COMMENT ON COLUMN "public"."webhook_subscriptions"."expiration_date" IS 'Subscription expiration timestamp';

-- Monitoring tables comments
COMMENT ON TABLE "public"."cost_records" IS 'Records of OpenRouter API costs for AI operations';
COMMENT ON TABLE "public"."performance_metrics" IS 'Performance metrics for system operations';
COMMENT ON TABLE "public"."system_metrics" IS 'System-level metrics like CPU, memory usage';
COMMENT ON TABLE "public"."rate_limit_records" IS 'Records of rate limit checks and blocks';
COMMENT ON TABLE "public"."rate_limit_windows" IS 'Current rate limit windows and usage counts';

-- =============================================================================
-- SCHEMA SUMMARY
-- =============================================================================
/*
DATABASE SCHEMA OVERVIEW:

1. integrations - OAuth tokens and connection data for Pipedrive and Microsoft
2. activity_logs - Real-time activity tracking for dashboard monitoring
3. opportunity_logs - GDPR-compliant sales opportunity detection logs
4. emails - Email metadata from Microsoft Graph webhooks
5. webhook_subscriptions - Microsoft Graph webhook subscription management
6. cost_records - OpenRouter API cost tracking for AI operations
7. performance_metrics - System operation performance tracking
8. system_metrics - System-level metrics (CPU, memory, etc.)
9. rate_limit_records - Rate limiting activity and blocked requests
10. rate_limit_windows - Current rate limit usage windows

KEY FEATURES:
- Row Level Security (RLS) enabled on all tables
- Comprehensive indexing for performance
- Automatic timestamp updates via triggers
- GDPR compliance with minimal data storage
- Support for encrypted OAuth tokens
- Real-time activity monitoring capabilities

MIGRATION HISTORY:
- 001: Initial schema (integrations, opportunity_logs, activity_logs)
- 002: RLS policies
- 003: Performance indexes
- 004: Email processing schema (emails, webhook_subscriptions)
- 005: Microsoft user ID support
- 006: Table recreation with improved structure
- 007: Additional webhook subscription columns
- 008: Webhook subscription column fixes
- 009: Monitoring tables (cost_records, performance_metrics, system_metrics, rate_limit_records, rate_limit_windows)
*/ 