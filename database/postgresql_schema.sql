-- ============================================================================
-- 블로그 자동화 시스템 PostgreSQL 스키마 (unble 스키마)
-- ============================================================================

-- 스키마 생성 (존재하지 않는 경우)
CREATE SCHEMA IF NOT EXISTS unble;

-- 스키마 설정
SET search_path TO unble, public;

-- ============================================================================
-- 1. 콘텐츠 히스토리 테이블 - 발행된 모든 콘텐츠 추적
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.content_history (
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
    
    -- 추가된 메타데이터
    meta_description TEXT,
    tags JSONB DEFAULT '[]',
    word_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    seo_score DECIMAL(4,2) DEFAULT 0,
    
    -- 인덱스 및 제약조건
    CONSTRAINT unique_site_title UNIQUE(site, title_hash),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'published', 'archived', 'failed'))
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_content_history_site ON unble.content_history(site);
CREATE INDEX IF NOT EXISTS idx_content_history_published_date ON unble.content_history(published_date);
CREATE INDEX IF NOT EXISTS idx_content_history_status ON unble.content_history(status);
CREATE INDEX IF NOT EXISTS idx_content_history_keywords ON unble.content_history USING GIN(keywords);

-- ============================================================================
-- 2. 주제 풀 테이블 - 콘텐츠 주제 관리
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.topic_pool (
    id BIGSERIAL PRIMARY KEY,
    site VARCHAR(50) NOT NULL,
    topic VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    used BOOLEAN DEFAULT FALSE,
    used_date TIMESTAMPTZ,
    created_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    -- 추가된 필드
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 5),
    estimated_length INTEGER DEFAULT 2000,
    target_keywords JSONB DEFAULT '[]',
    seasonal_boost DECIMAL(3,2) DEFAULT 1.00,
    
    -- 인덱스
    CONSTRAINT unique_site_topic UNIQUE(site, topic)
);

CREATE INDEX IF NOT EXISTS idx_topic_pool_site_used ON unble.topic_pool(site, used);
CREATE INDEX IF NOT EXISTS idx_topic_pool_priority ON unble.topic_pool(priority);

-- ============================================================================
-- 3. 이미지 캐시 테이블 - 생성된 이미지 관리
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.image_cache (
    id BIGSERIAL PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    image_url TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,
    used_count INTEGER DEFAULT 0,
    created_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMPTZ,
    
    -- 추가된 메타데이터
    file_size INTEGER,
    width INTEGER,
    height INTEGER,
    alt_text TEXT,
    copyright_info TEXT,
    quality_score DECIMAL(3,2) DEFAULT 0,
    
    CONSTRAINT valid_source CHECK (source IN ('unsplash', 'pexels', 'dall-e', 'custom', 'pixabay'))
);

CREATE INDEX IF NOT EXISTS idx_image_cache_keyword ON unble.image_cache(keyword);
CREATE INDEX IF NOT EXISTS idx_image_cache_source ON unble.image_cache(source);
CREATE INDEX IF NOT EXISTS idx_image_cache_used_count ON unble.image_cache(used_count);

-- ============================================================================
-- 4. 성능 추적 테이블 - 포스트 성과 분석
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.performance_tracking (
    id BIGSERIAL PRIMARY KEY,
    site VARCHAR(50) NOT NULL,
    post_id BIGINT REFERENCES unble.content_history(id) ON DELETE CASCADE,
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    revenue DECIMAL(12,4) DEFAULT 0,
    bounce_rate DECIMAL(5,2),
    avg_time_on_page INTEGER,
    tracked_date DATE DEFAULT CURRENT_DATE,
    
    -- 추가된 성과 지표
    search_impressions INTEGER DEFAULT 0,
    search_clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5,4) DEFAULT 0,
    position DECIMAL(4,1) DEFAULT 0,
    social_shares INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    
    CONSTRAINT unique_post_date UNIQUE(post_id, tracked_date)
);

CREATE INDEX IF NOT EXISTS idx_performance_site_date ON unble.performance_tracking(site, tracked_date);
CREATE INDEX IF NOT EXISTS idx_performance_post_id ON unble.performance_tracking(post_id);

-- ============================================================================
-- 5. 콘텐츠 파일 테이블 - WordPress/Tistory 백업파일
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.content_files (
    id BIGSERIAL PRIMARY KEY,
    site VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    word_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    tags JSONB DEFAULT '[]',
    categories JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMPTZ,
    file_size INTEGER DEFAULT 0,
    
    -- 추가된 메타데이터
    content_hash VARCHAR(64),
    thumbnail_url TEXT,
    template_version VARCHAR(10) DEFAULT '1.0',
    export_format VARCHAR(20) DEFAULT 'html',
    
    CONSTRAINT valid_file_type CHECK (file_type IN ('wordpress', 'tistory', 'markdown', 'json')),
    CONSTRAINT valid_status_file CHECK (status IN ('draft', 'published', 'archived', 'error', 'processing'))
);

CREATE INDEX IF NOT EXISTS idx_content_files_site_type ON unble.content_files(site, file_type);
CREATE INDEX IF NOT EXISTS idx_content_files_created_at ON unble.content_files(created_at);

-- ============================================================================
-- 6. 시스템 로그 테이블 - 시스템 활동 추적
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.system_logs (
    id BIGSERIAL PRIMARY KEY,
    log_level VARCHAR(20) NOT NULL,
    component VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    site VARCHAR(50),
    
    -- 추가된 로깅 필드
    user_agent TEXT,
    ip_address INET,
    session_id VARCHAR(64),
    trace_id VARCHAR(64),
    duration_ms INTEGER,
    
    CONSTRAINT valid_log_level CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);

-- 파티셔닝을 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON unble.system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON unble.system_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_system_logs_component ON unble.system_logs(component);

-- ============================================================================
-- 7. 수익 추적 테이블 - 일별 수익 데이터
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.revenue_tracking (
    id BIGSERIAL PRIMARY KEY,
    site VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    ad_revenue DECIMAL(12,4) DEFAULT 0,
    affiliate_revenue DECIMAL(12,4) DEFAULT 0,
    page_views INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    ctr DECIMAL(5,4) DEFAULT 0,
    rpm DECIMAL(10,4) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    -- 추가된 수익 지표
    impression_revenue DECIMAL(12,4) DEFAULT 0,
    click_revenue DECIMAL(12,4) DEFAULT 0,
    conversion_revenue DECIMAL(12,4) DEFAULT 0,
    bounce_rate DECIMAL(5,2) DEFAULT 0,
    avg_session_duration INTEGER DEFAULT 0,
    new_visitors_ratio DECIMAL(5,2) DEFAULT 0,
    
    CONSTRAINT unique_site_date_revenue UNIQUE(site, date)
);

CREATE INDEX IF NOT EXISTS idx_revenue_site_date ON unble.revenue_tracking(site, date);
CREATE INDEX IF NOT EXISTS idx_revenue_date ON unble.revenue_tracking(date);

-- ============================================================================
-- 8. API 사용량 추적 테이블 - 외부 API 호출 모니터링
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.api_usage (
    id BIGSERIAL PRIMARY KEY,
    api_provider VARCHAR(30) NOT NULL,
    endpoint VARCHAR(100),
    tokens_used INTEGER DEFAULT 0,
    cost DECIMAL(10,6) DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    response_time DECIMAL(8,3),
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    site VARCHAR(50),
    
    -- 추가된 API 메타데이터
    request_size INTEGER DEFAULT 0,
    response_size INTEGER DEFAULT 0,
    http_status INTEGER,
    error_message TEXT,
    rate_limit_remaining INTEGER,
    request_id VARCHAR(64),
    
    CONSTRAINT valid_api_provider CHECK (
        api_provider IN ('anthropic', 'openai', 'unsplash', 'pexels', 'dall-e', 'wordpress', 'custom')
    )
);

CREATE INDEX IF NOT EXISTS idx_api_usage_provider ON unble.api_usage(api_provider);
CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON unble.api_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_success ON unble.api_usage(success);

-- ============================================================================
-- 9. 사이트 설정 테이블 - 동적 사이트 구성
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.site_configs (
    id BIGSERIAL PRIMARY KEY,
    site_code VARCHAR(50) UNIQUE NOT NULL,
    site_name VARCHAR(100) NOT NULL,
    site_url TEXT NOT NULL,
    site_type VARCHAR(20) NOT NULL,
    
    -- API 설정 (암호화된 형태로 저장)
    api_config JSONB DEFAULT '{}',
    
    -- 콘텐츠 설정
    content_config JSONB DEFAULT '{}',
    
    -- 발행 일정
    publishing_schedule JSONB DEFAULT '{}',
    
    -- 상태 관리
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_site_type CHECK (site_type IN ('wordpress', 'tistory', 'custom'))
);

-- ============================================================================
-- 10. 키워드 추적 테이블 - SEO 키워드 성과 분석
-- ============================================================================
CREATE TABLE IF NOT EXISTS unble.keyword_tracking (
    id BIGSERIAL PRIMARY KEY,
    site VARCHAR(50) NOT NULL,
    keyword VARCHAR(255) NOT NULL,
    post_id BIGINT REFERENCES unble.content_history(id) ON DELETE CASCADE,
    
    -- 검색 성과 데이터
    position INTEGER,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5,4) DEFAULT 0,
    
    -- 경쟁 분석
    competition_level INTEGER DEFAULT 1 CHECK (competition_level BETWEEN 1 AND 5),
    search_volume INTEGER DEFAULT 0,
    keyword_difficulty DECIMAL(5,2) DEFAULT 0,
    
    tracked_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_keyword_post_date UNIQUE(keyword, post_id, tracked_date)
);

CREATE INDEX IF NOT EXISTS idx_keyword_tracking_site ON unble.keyword_tracking(site);
CREATE INDEX IF NOT EXISTS idx_keyword_tracking_keyword ON unble.keyword_tracking(keyword);

-- ============================================================================
-- 뷰 생성 - 자주 사용되는 데이터 조회
-- ============================================================================

-- 일별 통계 뷰
CREATE OR REPLACE VIEW unble.daily_stats AS
SELECT 
    site,
    DATE(published_date) as publish_date,
    COUNT(*) as posts_count,
    AVG(word_count) as avg_word_count,
    AVG(reading_time) as avg_reading_time,
    COUNT(CASE WHEN status = 'published' THEN 1 END) as published_count
FROM unble.content_history
WHERE published_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY site, DATE(published_date)
ORDER BY publish_date DESC;

-- 사이트별 성과 뷰
CREATE OR REPLACE VIEW unble.site_performance AS
SELECT 
    ch.site,
    COUNT(DISTINCT ch.id) as total_posts,
    COALESCE(AVG(pt.views), 0) as avg_views,
    COALESCE(SUM(rt.ad_revenue + rt.affiliate_revenue), 0) as total_revenue,
    COALESCE(AVG(pt.bounce_rate), 0) as avg_bounce_rate,
    MAX(ch.published_date) as last_post_date
FROM unble.content_history ch
LEFT JOIN unble.performance_tracking pt ON ch.id = pt.post_id
LEFT JOIN unble.revenue_tracking rt ON ch.site = rt.site 
    AND DATE(ch.published_date) = rt.date
WHERE ch.published_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY ch.site
ORDER BY total_revenue DESC;

-- ============================================================================
-- 트리거 함수 - 자동 업데이트
-- ============================================================================

-- updated_at 자동 업데이트 함수
CREATE OR REPLACE FUNCTION unble.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- revenue_tracking 테이블에 트리거 적용
CREATE TRIGGER update_revenue_tracking_updated_at 
    BEFORE UPDATE ON unble.revenue_tracking
    FOR EACH ROW 
    EXECUTE FUNCTION unble.update_updated_at_column();

-- site_configs 테이블에 트리거 적용
CREATE TRIGGER update_site_configs_updated_at 
    BEFORE UPDATE ON unble.site_configs
    FOR EACH ROW 
    EXECUTE FUNCTION unble.update_updated_at_column();

-- ============================================================================
-- 초기 데이터 삽입
-- ============================================================================

-- 기본 사이트 설정
INSERT INTO unble.site_configs (site_code, site_name, site_url, site_type, content_config, publishing_schedule) 
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
);

-- 성공 메시지
SELECT 'PostgreSQL 스키마 생성 완료!' as message;