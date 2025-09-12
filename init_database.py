#!/usr/bin/env python3
"""
PostgreSQL 데이터베이스 초기화 스크립트
운영 환경에서 필요한 테이블들을 생성합니다.
"""

import psycopg2
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """데이터베이스 초기화"""
    
    # 연결 정보
    connection_params = {
        'host': os.getenv('PG_HOST', 'ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app'),
        'port': int(os.getenv('PG_PORT', 5432)),
        'database': os.getenv('PG_DATABASE', 'unble'),
        'user': os.getenv('PG_USER', 'unble'),
        'password': os.getenv('PG_PASSWORD', 'npg_1kjV0mhECxqs'),
    }
    schema = os.getenv('PG_SCHEMA', 'blog_automation')
    
    try:
        logger.info("PostgreSQL 연결 중...")
        with psycopg2.connect(**connection_params) as conn:
            cursor = conn.cursor()
            
            # 스키마 생성
            logger.info(f"스키마 생성: {schema}")
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            
            # content_files 테이블 생성
            logger.info("content_files 테이블 생성")
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {schema}.content_files (
                    id SERIAL PRIMARY KEY,
                    site TEXT NOT NULL,
                    title TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER,
                    word_count INTEGER,
                    reading_time INTEGER,
                    metadata JSONB DEFAULT '{{}}',
                    status TEXT DEFAULT 'draft',
                    published_at TIMESTAMPTZ
                )
            """)
            
            # content_history 테이블 생성
            logger.info("content_history 테이블 생성")
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {schema}.content_history (
                    id SERIAL PRIMARY KEY,
                    site TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT,
                    created_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    published_at TIMESTAMPTZ,
                    status TEXT DEFAULT 'published',
                    url TEXT,
                    metadata JSONB DEFAULT '{{}}'
                )
            """)
            
            # 인덱스 생성
            logger.info("인덱스 생성")
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_content_files_site 
                ON {schema}.content_files(site)
            """)
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_content_files_created_at 
                ON {schema}.content_files(created_at DESC)
            """)
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_content_history_site 
                ON {schema}.content_history(site)
            """)
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_content_history_created_date 
                ON {schema}.content_history(created_date DESC)
            """)
            
            conn.commit()
            logger.info("✅ 데이터베이스 초기화 완료")
            
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}")
        raise

if __name__ == "__main__":
    init_database()