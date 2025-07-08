-- Migration 009: Add monitoring tables for cost tracking, performance metrics, and rate limiting
-- This migration adds database persistence for the monitoring system

-- Cost tracking tables
CREATE TABLE IF NOT EXISTS cost_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cost_usd DECIMAL(10,6) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    correlation_id UUID NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Performance metrics tables
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    operation VARCHAR(100) NOT NULL,
    duration_ms INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    correlation_id UUID NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    metric_unit VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Rate limiting tables
CREATE TABLE IF NOT EXISTS rate_limit_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    operation VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    ip_address INET,
    user_agent TEXT,
    correlation_id UUID NOT NULL,
    was_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Rate limit windows table for tracking current usage
CREATE TABLE IF NOT EXISTS rate_limit_windows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    requests_count INTEGER NOT NULL DEFAULT 0,
    max_requests INTEGER NOT NULL,
    window_seconds INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(operation, user_id, window_start)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_cost_records_timestamp ON cost_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_cost_records_user_id ON cost_records(user_id);
CREATE INDEX IF NOT EXISTS idx_cost_records_model ON cost_records(model);
CREATE INDEX IF NOT EXISTS idx_cost_records_operation ON cost_records(operation);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_operation ON performance_metrics(operation);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_user_id ON performance_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_success ON performance_metrics(success);

CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);

CREATE INDEX IF NOT EXISTS idx_rate_limit_records_timestamp ON rate_limit_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_rate_limit_records_operation ON rate_limit_records(operation);
CREATE INDEX IF NOT EXISTS idx_rate_limit_records_user_id ON rate_limit_records(user_id);
CREATE INDEX IF NOT EXISTS idx_rate_limit_records_blocked ON rate_limit_records(was_blocked);

CREATE INDEX IF NOT EXISTS idx_rate_limit_windows_operation_user ON rate_limit_windows(operation, user_id);
CREATE INDEX IF NOT EXISTS idx_rate_limit_windows_window_end ON rate_limit_windows(window_end);

-- Add RLS policies for monitoring tables
ALTER TABLE cost_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE rate_limit_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE rate_limit_windows ENABLE ROW LEVEL SECURITY;

-- RLS policies for cost_records
CREATE POLICY "Users can view their own cost records" ON cost_records
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Service can insert cost records" ON cost_records
    FOR INSERT WITH CHECK (true);

-- RLS policies for performance_metrics
CREATE POLICY "Users can view their own performance metrics" ON performance_metrics
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Service can insert performance metrics" ON performance_metrics
    FOR INSERT WITH CHECK (true);

-- RLS policies for system_metrics (read-only for all authenticated users)
CREATE POLICY "Authenticated users can view system metrics" ON system_metrics
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Service can insert system metrics" ON system_metrics
    FOR INSERT WITH CHECK (true);

-- RLS policies for rate_limit_records
CREATE POLICY "Users can view their own rate limit records" ON rate_limit_records
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Service can insert rate limit records" ON rate_limit_records
    FOR INSERT WITH CHECK (true);

-- RLS policies for rate_limit_windows
CREATE POLICY "Users can view their own rate limit windows" ON rate_limit_windows
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Service can insert and update rate limit windows" ON rate_limit_windows
    FOR ALL USING (true);

-- Add comments for documentation
COMMENT ON TABLE cost_records IS 'Records of OpenRouter API costs for AI operations';
COMMENT ON TABLE performance_metrics IS 'Performance metrics for system operations';
COMMENT ON TABLE system_metrics IS 'System-level metrics like CPU, memory usage';
COMMENT ON TABLE rate_limit_records IS 'Records of rate limit checks and blocks';
COMMENT ON TABLE rate_limit_windows IS 'Current rate limit windows and usage counts'; 