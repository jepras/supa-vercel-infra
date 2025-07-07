-- Add missing columns to webhook_subscriptions table

-- Add change_type column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "change_type" text;

-- Add resource column  
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "resource" text;

-- Add application_id column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "application_id" text;

-- Add creator_id column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "creator_id" text;

-- Add notification_query_options column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "notification_query_options" jsonb;

-- Add lifecycle_notification_url column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "lifecycle_notification_url" text;

-- Add include_resource_data column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "include_resource_data" boolean;

-- Add latest_supported_tls_version column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "latest_supported_tls_version" text;

-- Add encryption_certificate column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "encryption_certificate" text;

-- Add encryption_certificate_id column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "encryption_certificate_id" text;

-- Add notification_url_app_id column
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "notification_url_app_id" text; 