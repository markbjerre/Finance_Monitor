-- Finance Dashboard - Supabase Schema
-- Run these SQL commands in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============= STOCKS TABLE =============
CREATE TABLE IF NOT EXISTS stocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    change_percent NUMERIC(6, 2),
    high NUMERIC(10, 2),
    low NUMERIC(10, 2),
    volume BIGINT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_stocks_ticker ON stocks(ticker);
CREATE INDEX IF NOT EXISTS idx_stocks_timestamp ON stocks(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stocks_ticker_timestamp ON stocks(ticker, timestamp DESC);

-- ============= NEWS TABLE =============
CREATE TABLE IF NOT EXISTS news (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    summary TEXT,
    url TEXT UNIQUE NOT NULL,
    source TEXT,
    published_at TIMESTAMPTZ NOT NULL,
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_source ON news(source);

-- ============= AI INSIGHTS TABLE =============
CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    insight_type TEXT DEFAULT 'daily',
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_ai_insights_generated_at ON ai_insights(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_insights_type ON ai_insights(insight_type);

-- ============= ROW LEVEL SECURITY (Optional) =============
-- Enable RLS if you want to add authentication later
-- ALTER TABLE stocks ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE news ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;

-- ============= POLICIES (Optional) =============
-- Allow anonymous read access (public dashboard)
-- CREATE POLICY "Allow anonymous read access" ON stocks FOR SELECT USING (true);
-- CREATE POLICY "Allow anonymous read access" ON news FOR SELECT USING (true);
-- CREATE POLICY "Allow anonymous read access" ON ai_insights FOR SELECT USING (true);

-- ============= CLEANUP FUNCTION =============
-- Function to automatically delete old records
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete stock data older than 30 days
    DELETE FROM stocks WHERE timestamp < NOW() - INTERVAL '30 days';
    
    -- Delete news older than 7 days
    DELETE FROM news WHERE published_at < NOW() - INTERVAL '7 days';
    
    -- Delete AI insights older than 30 days
    DELETE FROM ai_insights WHERE generated_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- ============= HELPER FUNCTIONS =============

-- Get latest stock price for a ticker
CREATE OR REPLACE FUNCTION get_latest_stock_price(ticker_symbol TEXT)
RETURNS TABLE (
    ticker TEXT,
    price NUMERIC,
    change_percent NUMERIC,
    high NUMERIC,
    low NUMERIC,
    volume BIGINT,
    stock_timestamp TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.ticker,
        s.price,
        s.change_percent,
        s.high,
        s.low,
        s.volume,
        s.timestamp
    FROM stocks s
    WHERE s.ticker = ticker_symbol
    ORDER BY s.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Get stock price history for chart
CREATE OR REPLACE FUNCTION get_stock_history(ticker_symbol TEXT, days INTEGER DEFAULT 7)
RETURNS TABLE (
    ticker TEXT,
    price NUMERIC,
    stock_timestamp TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.ticker,
        s.price,
        s.timestamp
    FROM stocks s
    WHERE s.ticker = ticker_symbol
        AND s.timestamp > NOW() - (days || ' days')::INTERVAL
    ORDER BY s.timestamp ASC;
END;
$$ LANGUAGE plpgsql;

-- ============= COMPANY INFO TABLE =============
-- Stores cached company information to reduce API calls
CREATE TABLE IF NOT EXISTS company_info (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    pe_ratio DECIMAL(10, 2),
    description TEXT,
    website VARCHAR(255),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient lookup by last_updated
CREATE INDEX IF NOT EXISTS idx_company_info_last_updated ON company_info(last_updated);

-- Helper function to check if company info is stale (older than 24 hours)
CREATE OR REPLACE FUNCTION is_company_info_stale(ticker_symbol VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    last_update TIMESTAMP WITH TIME ZONE;
BEGIN
    SELECT last_updated INTO last_update
    FROM company_info
    WHERE ticker = ticker_symbol;
    
    IF last_update IS NULL THEN
        RETURN TRUE;  -- No data exists, considered stale
    END IF;
    
    RETURN (CURRENT_TIMESTAMP - last_update) > INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE stocks IS 'Stores historical stock price data';
COMMENT ON TABLE news IS 'Stores financial news articles';
COMMENT ON TABLE ai_insights IS 'Stores AI-generated market insights and commentary';
COMMENT ON TABLE company_info IS 'Stores cached company information with 24hr TTL to reduce API calls';
