-- Fix database schema errors for blog automation system
-- Run this on Koyeb PostgreSQL database

-- 1. Fix content_files table status constraint
-- First, check if processing is allowed
ALTER TABLE blog_automation.content_files 
DROP CONSTRAINT IF EXISTS content_files_status_check;

-- Add new constraint that includes 'processing'
ALTER TABLE blog_automation.content_files 
ADD CONSTRAINT content_files_status_check 
CHECK (status IN ('pending', 'published', 'failed', 'processing', 'draft', 'archived', 'error'));

-- 2. Add missing columns to content_files table if they don't exist
ALTER TABLE blog_automation.content_files 
ADD COLUMN IF NOT EXISTS file_type VARCHAR(20) DEFAULT 'wordpress';

ALTER TABLE blog_automation.content_files 
ADD COLUMN IF NOT EXISTS word_count INTEGER DEFAULT 0;

ALTER TABLE blog_automation.content_files 
ADD COLUMN IF NOT EXISTS reading_time INTEGER DEFAULT 0;

ALTER TABLE blog_automation.content_files 
ADD COLUMN IF NOT EXISTS file_size INTEGER DEFAULT 0;

-- 3. Create content_history table in blog_automation schema (missing table)
CREATE TABLE IF NOT EXISTS blog_automation.content_history (
    id BIGSERIAL PRIMARY KEY,
    site VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    title_hash VARCHAR(64) NOT NULL,
    category VARCHAR(100),
    keywords JSONB,
    content_hash VARCHAR(64),
    url TEXT,
    published_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    performance_metrics JSONB,
    status VARCHAR(20) DEFAULT 'published',
    
    -- Additional metadata
    meta_description TEXT,
    tags JSONB DEFAULT '[]',
    word_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    seo_score DECIMAL(4,2) DEFAULT 0,
    
    -- Constraints
    CONSTRAINT unique_site_title UNIQUE(site, title_hash),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'published', 'archived', 'failed'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_content_history_site ON blog_automation.content_history(site);
CREATE INDEX IF NOT EXISTS idx_content_history_published_date ON blog_automation.content_history(published_date);
CREATE INDEX IF NOT EXISTS idx_content_history_status ON blog_automation.content_history(status);
CREATE INDEX IF NOT EXISTS idx_content_history_keywords ON blog_automation.content_history USING GIN(keywords);

-- 4. Create system_logs table in blog_automation schema if not exists
CREATE TABLE IF NOT EXISTS blog_automation.system_logs (
    id BIGSERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,  -- Changed from log_level to level
    component VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    site VARCHAR(50),
    
    -- Additional logging fields
    user_agent TEXT,
    ip_address INET,
    session_id VARCHAR(64),
    trace_id VARCHAR(64),
    duration_ms INTEGER,
    
    CONSTRAINT valid_log_level CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON blog_automation.system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON blog_automation.system_logs(level);  -- Fixed column name
CREATE INDEX IF NOT EXISTS idx_system_logs_component ON blog_automation.system_logs(component);

-- 5. Create site_configs table in blog_automation schema if not exists
CREATE TABLE IF NOT EXISTS blog_automation.site_configs (
    id BIGSERIAL PRIMARY KEY,
    site_code VARCHAR(50) UNIQUE NOT NULL,
    site_name VARCHAR(100) NOT NULL,
    site_url TEXT NOT NULL,
    site_type VARCHAR(20) NOT NULL,
    
    -- API configuration (encrypted)
    api_config JSONB DEFAULT '{}',
    
    -- Content configuration
    content_config JSONB DEFAULT '{}',
    
    -- Publishing schedule
    publishing_schedule JSONB DEFAULT '{}',
    
    -- Status management
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_site_type CHECK (site_type IN ('wordpress', 'tistory', 'custom'))
);

-- Insert default site configs if they don't exist
INSERT INTO blog_automation.site_configs (site_code, site_name, site_url, site_type, content_config, publishing_schedule) 
VALUES 
(
    'unpre', 
    'unpre.co.kr', 
    'https://unpre.co.kr', 
    'wordpress',
    '{"categories": ["개발", "IT", "정보처리기사", "언어학습"], "content_style": "전문적이고 실용적인", "target_audience": "개발자, IT전문가"}',
    '{"time": "12:00", "days": ["monday", "wednesday", "friday"]}'
),
(
    'untab', 
    'untab.co.kr', 
    'https://untab.co.kr', 
    'wordpress',
    '{"categories": ["부동산", "투자", "경제"], "content_style": "신뢰감 있고 전문적인", "target_audience": "부동산 투자자, 일반인"}',
    '{"time": "09:00", "days": ["tuesday", "thursday", "saturday"]}'
),
(
    'skewese', 
    'skewese.com', 
    'https://skewese.com', 
    'wordpress',
    '{"categories": ["역사", "문화", "교육"], "content_style": "교육적이고 흥미로운", "target_audience": "역사 애호가, 학생"}',
    '{"time": "15:00", "days": ["monday", "wednesday", "friday"]}'
),
(
    'tistory', 
    'tistory.com', 
    'https://tistory.com', 
    'tistory',
    '{"categories": ["엔터테인먼트", "라이프스타일"], "content_style": "친근하고 재미있는", "target_audience": "일반 독자"}',
    '{"time": "18:00", "days": ["daily"]}'
)
ON CONFLICT (site_code) DO NOTHING;

-- 6. Create topic_pool table in blog_automation schema if not exists
CREATE TABLE IF NOT EXISTS blog_automation.topic_pool (
    id BIGSERIAL PRIMARY KEY,
    site VARCHAR(50) NOT NULL,
    topic VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    used BOOLEAN DEFAULT FALSE,
    used_date TIMESTAMPTZ,
    created_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional fields
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 5),
    estimated_length INTEGER DEFAULT 2000,
    target_keywords JSONB DEFAULT '[]',
    seasonal_boost DECIMAL(3,2) DEFAULT 1.00,
    
    -- Unique constraint
    CONSTRAINT unique_site_topic UNIQUE(site, topic)
);

CREATE INDEX IF NOT EXISTS idx_topic_pool_site_used ON blog_automation.topic_pool(site, used);
CREATE INDEX IF NOT EXISTS idx_topic_pool_priority ON blog_automation.topic_pool(priority);

-- Success message
SELECT 'Schema fixes applied successfully!' as message;