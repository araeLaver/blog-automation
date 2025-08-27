-- Blog Automation 전체 스키마 설계
-- 유료 DB에서 전용으로 사용할 스키마 및 테이블 생성

-- 1. 스키마 생성
CREATE SCHEMA IF NOT EXISTS blog_automation;

-- 스키마 권한 설정
GRANT ALL PRIVILEGES ON SCHEMA blog_automation TO unble;

-- 2. 월별 발행 계획표 테이블
CREATE TABLE IF NOT EXISTS blog_automation.monthly_publishing_schedule (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    site VARCHAR(20) NOT NULL CHECK (site IN ('unpre', 'untab', 'skewese', 'tistory')),
    topic_category VARCHAR(50) NOT NULL,
    specific_topic TEXT NOT NULL,
    keywords TEXT[],
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'published', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, day, site, topic_category)
);

-- 3. 생성된 컨텐츠 파일 테이블
CREATE TABLE IF NOT EXISTS blog_automation.content_files (
    id SERIAL PRIMARY KEY,
    site VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    category VARCHAR(50),
    tags TEXT[],
    categories TEXT[],
    meta_description TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'published', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    schedule_id INTEGER REFERENCES blog_automation.monthly_publishing_schedule(id),
    wordpress_post_id INTEGER,
    tistory_post_id VARCHAR(100),
    publish_url TEXT,
    INDEX idx_site_status (site, status),
    INDEX idx_created (created_at),
    INDEX idx_published (published_at)
);

-- 4. 실시간 트렌딩 토픽 테이블
CREATE TABLE IF NOT EXISTS blog_automation.trending_topics (
    id SERIAL PRIMARY KEY,
    week_start_date DATE NOT NULL,
    site VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    trend_type VARCHAR(20) NOT NULL CHECK (trend_type IN ('hot', 'rising', 'predicted')),
    title TEXT NOT NULL,
    description TEXT,
    keywords TEXT[],
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    source_url TEXT,
    is_realtime BOOLEAN DEFAULT FALSE,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_start_date, site, title),
    INDEX idx_week_site (week_start_date, site),
    INDEX idx_category (category),
    INDEX idx_priority (priority DESC)
);

-- 5. 외부 API 데이터 캐시 테이블
CREATE TABLE IF NOT EXISTS blog_automation.api_cache (
    id SERIAL PRIMARY KEY,
    api_name VARCHAR(50) NOT NULL,
    endpoint TEXT NOT NULL,
    cache_key VARCHAR(255) NOT NULL,
    response_data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(api_name, cache_key),
    INDEX idx_api_key (api_name, cache_key),
    INDEX idx_expires (expires_at)
);

-- 6. 발행 이력 테이블
CREATE TABLE IF NOT EXISTS blog_automation.publish_history (
    id SERIAL PRIMARY KEY,
    site VARCHAR(20) NOT NULL,
    content_file_id INTEGER REFERENCES blog_automation.content_files(id),
    publish_type VARCHAR(20) CHECK (publish_type IN ('auto', 'manual', 'scheduled')),
    publish_status VARCHAR(20) NOT NULL CHECK (publish_status IN ('success', 'failed')),
    error_message TEXT,
    published_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    wordpress_post_id INTEGER,
    tistory_post_id VARCHAR(100),
    publish_url TEXT,
    response_data JSONB,
    INDEX idx_site_date (site, published_at),
    INDEX idx_status (publish_status)
);

-- 7. 시스템 상태 및 모니터링 테이블
CREATE TABLE IF NOT EXISTS blog_automation.system_status (
    id SERIAL PRIMARY KEY,
    component VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('healthy', 'warning', 'error', 'down')),
    message TEXT,
    details JSONB,
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_component (component),
    INDEX idx_checked (checked_at DESC)
);

-- 8. 스케줄러 작업 로그 테이블
CREATE TABLE IF NOT EXISTS blog_automation.scheduler_logs (
    id SERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    site VARCHAR(20),
    status VARCHAR(20) NOT NULL CHECK (status IN ('started', 'completed', 'failed')),
    error_message TEXT,
    execution_time_ms INTEGER,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    details JSONB,
    INDEX idx_job_status (job_name, status),
    INDEX idx_started (started_at DESC)
);

-- 9. 사용자 설정 테이블
CREATE TABLE IF NOT EXISTS blog_automation.user_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(20) CHECK (setting_type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50) DEFAULT 'system'
);

-- 10. 수익 데이터 테이블
CREATE TABLE IF NOT EXISTS blog_automation.revenue_data (
    id SERIAL PRIMARY KEY,
    site VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    page_views INTEGER DEFAULT 0,
    visitors INTEGER DEFAULT 0,
    revenue DECIMAL(10, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'KRW',
    source VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(site, date, source),
    INDEX idx_site_date (site, date),
    INDEX idx_date (date DESC)
);

-- 11. 이미지 관리 테이블
CREATE TABLE IF NOT EXISTS blog_automation.image_files (
    id SERIAL PRIMARY KEY,
    content_file_id INTEGER REFERENCES blog_automation.content_files(id),
    image_type VARCHAR(20) CHECK (image_type IN ('thumbnail', 'content', 'generated')),
    file_path TEXT NOT NULL,
    url TEXT,
    alt_text TEXT,
    source VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_content (content_file_id),
    INDEX idx_type (image_type)
);

-- 12. 키워드 분석 테이블
CREATE TABLE IF NOT EXISTS blog_automation.keyword_analysis (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    search_volume INTEGER,
    competition_level VARCHAR(20) CHECK (competition_level IN ('low', 'medium', 'high')),
    trend_score DECIMAL(5, 2),
    last_used DATE,
    use_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword),
    INDEX idx_category (category),
    INDEX idx_trend (trend_score DESC)
);

-- 트리거 함수: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION blog_automation.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
CREATE TRIGGER update_monthly_schedule_updated_at
    BEFORE UPDATE ON blog_automation.monthly_publishing_schedule
    FOR EACH ROW
    EXECUTE FUNCTION blog_automation.update_updated_at();

CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON blog_automation.user_settings
    FOR EACH ROW
    EXECUTE FUNCTION blog_automation.update_updated_at();

CREATE TRIGGER update_keyword_analysis_updated_at
    BEFORE UPDATE ON blog_automation.keyword_analysis
    FOR EACH ROW
    EXECUTE FUNCTION blog_automation.update_updated_at();

-- 초기 시스템 설정 데이터 삽입
INSERT INTO blog_automation.user_settings (setting_key, setting_value, setting_type, description) VALUES
    ('auto_publish_enabled', 'true', 'boolean', '자동 발행 활성화 여부'),
    ('publish_time_unpre', '12:00', 'string', 'unpre 발행 시간'),
    ('publish_time_untab', '09:00', 'string', 'untab 발행 시간'),
    ('publish_time_skewese', '15:00', 'string', 'skewese 발행 시간'),
    ('publish_time_tistory', '18:00', 'string', 'tistory 발행 시간'),
    ('trending_cache_hours', '1', 'number', '트렌딩 데이터 캐시 시간'),
    ('api_cache_minutes', '30', 'number', 'API 응답 캐시 시간'),
    ('max_retry_attempts', '3', 'number', '최대 재시도 횟수')
ON CONFLICT (setting_key) DO NOTHING;

-- 뷰 생성: 오늘 발행 예정 컨텐츠
CREATE OR REPLACE VIEW blog_automation.today_schedule AS
SELECT 
    s.id,
    s.site,
    s.topic_category,
    s.specific_topic,
    s.keywords,
    s.status,
    CASE 
        WHEN s.site = 'unpre' THEN u1.setting_value
        WHEN s.site = 'untab' THEN u2.setting_value
        WHEN s.site = 'skewese' THEN u3.setting_value
        WHEN s.site = 'tistory' THEN u4.setting_value
    END as publish_time
FROM blog_automation.monthly_publishing_schedule s
LEFT JOIN blog_automation.user_settings u1 ON u1.setting_key = 'publish_time_unpre'
LEFT JOIN blog_automation.user_settings u2 ON u2.setting_key = 'publish_time_untab'
LEFT JOIN blog_automation.user_settings u3 ON u3.setting_key = 'publish_time_skewese'
LEFT JOIN blog_automation.user_settings u4 ON u4.setting_key = 'publish_time_tistory'
WHERE s.year = EXTRACT(YEAR FROM CURRENT_DATE)
  AND s.month = EXTRACT(MONTH FROM CURRENT_DATE)
  AND s.day = EXTRACT(DAY FROM CURRENT_DATE)
  AND s.status = 'pending'
ORDER BY s.site, s.topic_category;

-- 뷰 생성: 최근 발행 현황
CREATE OR REPLACE VIEW blog_automation.recent_publishes AS
SELECT 
    c.site,
    c.title,
    c.status,
    c.published_at,
    c.publish_url,
    p.publish_type,
    p.publish_status,
    p.error_message
FROM blog_automation.content_files c
LEFT JOIN blog_automation.publish_history p ON c.id = p.content_file_id
WHERE c.published_at IS NOT NULL
ORDER BY c.published_at DESC
LIMIT 50;

-- 권한 설정
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA blog_automation TO unble;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA blog_automation TO unble;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA blog_automation TO unble;