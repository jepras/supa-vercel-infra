-- Add microsoft_user_id column to integrations table
ALTER TABLE integrations 
ADD COLUMN microsoft_user_id TEXT;

-- Add index for efficient lookups
CREATE INDEX idx_integrations_microsoft_user_id ON integrations(microsoft_user_id);

-- Add comment for documentation
COMMENT ON COLUMN integrations.microsoft_user_id IS 'Microsoft Graph user ID for Microsoft integrations'; 