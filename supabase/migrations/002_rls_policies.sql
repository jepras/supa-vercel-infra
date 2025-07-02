-- Enable Row Level Security
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- RLS policies for integrations
CREATE POLICY "Users can only access their own integrations" ON integrations
  FOR ALL USING (user_id = auth.uid());

-- RLS policies for opportunity_logs
CREATE POLICY "Users can only access their own opportunity logs" ON opportunity_logs
  FOR ALL USING (user_id = auth.uid());

-- RLS policies for activity_logs
CREATE POLICY "Users can only access their own activity logs" ON activity_logs
  FOR ALL USING (user_id = auth.uid()); 