-- Fix webhook_subscriptions table column names to match code expectations

-- Rename expires_at to expiration_date to match code expectations
ALTER TABLE "public"."webhook_subscriptions" 
RENAME COLUMN "expires_at" TO "expiration_date";

-- Add missing columns that the code expects
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "resource" text;

ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "change_type" text;

-- Add provider column if it doesn't exist (for future use)
ALTER TABLE "public"."webhook_subscriptions" 
ADD COLUMN IF NOT EXISTS "provider" text DEFAULT 'microsoft';

-- Update existing records to have the provider
UPDATE "public"."webhook_subscriptions" 
SET "provider" = 'microsoft' 
WHERE "provider" IS NULL;

-- Add index for expiration_date
CREATE INDEX IF NOT EXISTS "idx_webhook_subscriptions_expiration_date" 
ON "public"."webhook_subscriptions" ("expiration_date");

-- Add index for resource
CREATE INDEX IF NOT EXISTS "idx_webhook_subscriptions_resource" 
ON "public"."webhook_subscriptions" ("resource"); 