-- DANGER: This migration will drop and recreate all relevant tables.

-- Drop tables if they exist
DROP TABLE IF EXISTS "public"."activity_logs" CASCADE;
DROP TABLE IF EXISTS "public"."integrations" CASCADE;
DROP TABLE IF EXISTS "public"."opportunity_logs" CASCADE;
DROP TABLE IF EXISTS "public"."emails" CASCADE;
DROP TABLE IF EXISTS "public"."webhook_subscriptions" CASCADE;

-- Recreate integrations table
CREATE TABLE "public"."integrations" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "provider" text NOT NULL,
    "access_token" text NOT NULL,
    "refresh_token" text,
    "token_expires_at" timestamp with time zone,
    "microsoft_user_id" text,
    "scopes" text[] DEFAULT '{}',
    "metadata" jsonb DEFAULT '{}',
    "is_active" boolean DEFAULT true,
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "integrations_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "integrations_user_id_provider_key" UNIQUE ("user_id", "provider")
);

-- Recreate activity_logs table
CREATE TABLE "public"."activity_logs" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "activity_type" text NOT NULL,
    "description" text,
    "status" text DEFAULT 'pending',
    "metadata" jsonb DEFAULT '{}',
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "activity_logs_pkey" PRIMARY KEY ("id")
);

-- Recreate opportunity_logs table
CREATE TABLE "public"."opportunity_logs" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "email_hash" text,
    "sender_email" text,
    "recipient_email" text,
    "subject" text,
    "opportunity_detected" boolean,
    "confidence_score" numeric,
    "reasoning" text,
    "metadata" jsonb DEFAULT '{}',
    "created_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "opportunity_logs_pkey" PRIMARY KEY ("id")
);

-- Recreate emails table
CREATE TABLE "public"."emails" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "microsoft_email_id" text NOT NULL,
    "subject" text,
    "sender_email" text,
    "recipient_emails" text[],
    "sent_at" timestamp with time zone,
    "received_at" timestamp with time zone,
    "body_content" text,
    "body_content_type" text,
    "webhook_received_at" timestamp with time zone,
    "processing_status" text DEFAULT 'pending',
    "content_retrieved" boolean DEFAULT false,
    "ai_analyzed" boolean DEFAULT false,
    "opportunity_detected" boolean,
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "emails_pkey" PRIMARY KEY ("id")
);

-- Recreate webhook_subscriptions table (with provider column)
CREATE TABLE "public"."webhook_subscriptions" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "subscription_id" text NOT NULL,
    "provider" text NOT NULL,
    "notification_url" text NOT NULL,
    "expires_at" timestamp with time zone,
    "is_active" boolean DEFAULT true,
    "metadata" jsonb DEFAULT '{}',
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now(),
    CONSTRAINT "webhook_subscriptions_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "webhook_subscriptions_subscription_id_key" UNIQUE ("subscription_id")
);

-- Add indexes
CREATE INDEX "idx_integrations_user_id" ON "public"."integrations" ("user_id");
CREATE INDEX "idx_integrations_provider" ON "public"."integrations" ("provider");
CREATE INDEX "idx_integrations_is_active" ON "public"."integrations" ("is_active");
CREATE INDEX "idx_integrations_microsoft_user_id" ON "public"."integrations" ("microsoft_user_id");

CREATE INDEX "idx_activity_logs_user_id" ON "public"."activity_logs" ("user_id");
CREATE INDEX "idx_activity_logs_activity_type" ON "public"."activity_logs" ("activity_type");
CREATE INDEX "idx_activity_logs_status" ON "public"."activity_logs" ("status");
CREATE INDEX "idx_activity_logs_created_at" ON "public"."activity_logs" ("created_at");

CREATE INDEX "idx_opportunity_logs_user_id" ON "public"."opportunity_logs" ("user_id");
CREATE INDEX "idx_opportunity_logs_email_hash" ON "public"."opportunity_logs" ("email_hash");
CREATE INDEX "idx_opportunity_logs_opportunity_detected" ON "public"."opportunity_logs" ("opportunity_detected");
CREATE INDEX "idx_opportunity_logs_recipient_email" ON "public"."opportunity_logs" ("recipient_email");
CREATE INDEX "idx_opportunity_logs_created_at" ON "public"."opportunity_logs" ("created_at");

CREATE INDEX "idx_emails_user_id" ON "public"."emails" ("user_id");
CREATE INDEX "idx_emails_microsoft_email_id" ON "public"."emails" ("microsoft_email_id");
CREATE INDEX "idx_emails_processing_status" ON "public"."emails" ("processing_status");

CREATE INDEX "idx_webhook_subscriptions_user_id" ON "public"."webhook_subscriptions" ("user_id");
CREATE INDEX "idx_webhook_subscriptions_provider" ON "public"."webhook_subscriptions" ("provider");
CREATE INDEX "idx_webhook_subscriptions_is_active" ON "public"."webhook_subscriptions" ("is_active");

-- Enable Row Level Security
ALTER TABLE "public"."integrations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."activity_logs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."opportunity_logs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."emails" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."webhook_subscriptions" ENABLE ROW LEVEL SECURITY;

-- Add RLS policies
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