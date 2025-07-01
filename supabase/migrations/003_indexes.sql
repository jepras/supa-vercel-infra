-- Performance indexes for integrations
CREATE INDEX idx_integrations_user_id ON integrations(user_id);
CREATE INDEX idx_integrations_provider ON integrations(provider);
CREATE INDEX idx_integrations_is_active ON integrations(is_active);

-- Performance indexes for opportunity_logs
CREATE INDEX idx_opportunity_logs_user_id ON opportunity_logs(user_id);
CREATE INDEX idx_opportunity_logs_email_hash ON opportunity_logs(email_hash);
CREATE INDEX idx_opportunity_logs_recipient_email ON opportunity_logs(recipient_email);
CREATE INDEX idx_opportunity_logs_created_at ON opportunity_logs(created_at DESC);
CREATE INDEX idx_opportunity_logs_opportunity_detected ON opportunity_logs(opportunity_detected);

-- Performance indexes for activity_logs
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at DESC);
CREATE INDEX idx_activity_logs_activity_type ON activity_logs(activity_type);
CREATE INDEX idx_activity_logs_status ON activity_logs(status); 