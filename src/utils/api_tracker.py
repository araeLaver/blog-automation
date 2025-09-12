"""
API 사용 내역 추적 시스템 - PostgreSQL 버전
Claude API 사용량과 비용을 실시간으로 추적하고 기록
"""

import json
import psycopg2
import psycopg2.extras
from datetime import datetime, date
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class APITracker:
    def __init__(self):
        """API 추적기 초기화 - PostgreSQL 사용"""
        # PostgreSQL 연결 정보
        self.connection_params = {
            'host': os.getenv('PG_HOST', 'ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app'),
            'port': int(os.getenv('PG_PORT', 5432)),
            'database': os.getenv('PG_DATABASE', 'unble'),
            'user': os.getenv('PG_USER', 'unble'),
            'password': os.getenv('PG_PASSWORD', 'npg_1kjV0mhECxqs'),
        }
        self.schema = os.getenv('PG_SCHEMA', 'blog_automation')
        self._init_database()
        
        # Claude API 가격 (1M 토큰당)
        self.pricing = {
            "claude-3-opus": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
            "claude-3.5-sonnet": {"input": 3.0, "output": 15.0}
        }
    
    def _init_database(self):
        """PostgreSQL 데이터베이스 초기화"""
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                cursor = conn.cursor()
                
                # API 사용 내역 테이블
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.api_usage (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        service TEXT NOT NULL,
                        model TEXT NOT NULL,
                        endpoint TEXT,
                        input_tokens INTEGER,
                        output_tokens INTEGER,
                        total_tokens INTEGER,
                        cost_usd NUMERIC(10,6),
                        site TEXT,
                        purpose TEXT,
                        success BOOLEAN,
                        error_message TEXT,
                        metadata JSONB
                    )
                """)
                
                # 인덱스 생성
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp 
                    ON {self.schema}.api_usage(timestamp)
                """)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_api_usage_site 
                    ON {self.schema}.api_usage(site)
                """)
                
                conn.commit()
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
    
    def track_usage(self, 
                    service: str,
                    model: str,
                    input_tokens: int,
                    output_tokens: int,
                    site: str = None,
                    endpoint: str = None,
                    purpose: str = None,
                    success: bool = True,
                    error_message: str = None,
                    metadata: Dict = None):
        """API 사용량 추적"""
        try:
            total_tokens = input_tokens + output_tokens
            cost_usd = self.calculate_cost(model, input_tokens, output_tokens)
            
            with psycopg2.connect(**self.connection_params) as conn:
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    INSERT INTO {self.schema}.api_usage (
                        service, model, endpoint, input_tokens, output_tokens, 
                        total_tokens, cost_usd, site, purpose, success, error_message, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    service, model, endpoint, input_tokens, output_tokens,
                    total_tokens, cost_usd, site, purpose, success, error_message,
                    json.dumps(metadata) if metadata else None
                ))
                
                conn.commit()
                logger.info(f"API 사용량 기록: {service} {model} - {total_tokens} 토큰, ${cost_usd:.4f}")
                
        except Exception as e:
            logger.error(f"API 사용량 추적 오류: {e}")
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """토큰 사용량을 기반으로 비용 계산"""
        if model not in self.pricing:
            return 0.0
        
        prices = self.pricing[model]
        input_cost = (input_tokens / 1_000_000) * prices["input"]
        output_cost = (output_tokens / 1_000_000) * prices["output"]
        
        return input_cost + output_cost
    
    def get_today_usage(self) -> Dict:
        """오늘의 API 사용량 조회"""
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total_requests,
                        SUM(input_tokens) as total_input_tokens,
                        SUM(output_tokens) as total_output_tokens,
                        SUM(total_tokens) as total_tokens,
                        SUM(cost_usd) as total_cost_usd
                    FROM {self.schema}.api_usage 
                    WHERE DATE(timestamp) = CURRENT_DATE
                """)
                
                result = cursor.fetchone()
                return {
                    'total_requests': result['total_requests'] or 0,
                    'total_input_tokens': result['total_input_tokens'] or 0,
                    'total_output_tokens': result['total_output_tokens'] or 0,
                    'total_tokens': result['total_tokens'] or 0,
                    'total_cost_usd': float(result['total_cost_usd'] or 0)
                }
        except Exception as e:
            logger.error(f"오늘 사용량 조회 오류: {e}")
            return {
                'total_requests': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_tokens': 0,
                'total_cost_usd': 0.0
            }
    
    def get_usage_by_site(self, site: str, days: int = 7) -> Dict:
        """사이트별 API 사용량 조회"""
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total_requests,
                        SUM(input_tokens) as total_input_tokens,
                        SUM(output_tokens) as total_output_tokens,
                        SUM(total_tokens) as total_tokens,
                        SUM(cost_usd) as total_cost_usd
                    FROM {self.schema}.api_usage 
                    WHERE site = %s AND timestamp >= CURRENT_DATE - INTERVAL '%s days'
                """, (site, days))
                
                result = cursor.fetchone()
                return {
                    'site': site,
                    'total_requests': result['total_requests'] or 0,
                    'total_input_tokens': result['total_input_tokens'] or 0,
                    'total_output_tokens': result['total_output_tokens'] or 0,
                    'total_tokens': result['total_tokens'] or 0,
                    'total_cost_usd': float(result['total_cost_usd'] or 0)
                }
        except Exception as e:
            logger.error(f"사이트별 사용량 조회 오류: {e}")
            return {
                'site': site,
                'total_requests': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_tokens': 0,
                'total_cost_usd': 0.0
            }
    
    def get_monthly_usage(self, year: int = None, month: int = None) -> Dict:
        """월별 API 사용량 조회"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
            
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total_requests,
                        SUM(input_tokens) as total_input_tokens,
                        SUM(output_tokens) as total_output_tokens,
                        SUM(total_tokens) as total_tokens,
                        SUM(cost_usd) as total_cost_usd
                    FROM {self.schema}.api_usage 
                    WHERE EXTRACT(YEAR FROM timestamp) = %s 
                    AND EXTRACT(MONTH FROM timestamp) = %s
                """, (year, month))
                
                result = cursor.fetchone()
                return {
                    'year': year,
                    'month': month,
                    'total_requests': result['total_requests'] or 0,
                    'total_input_tokens': result['total_input_tokens'] or 0,
                    'total_output_tokens': result['total_output_tokens'] or 0,
                    'total_tokens': result['total_tokens'] or 0,
                    'total_cost_usd': float(result['total_cost_usd'] or 0)
                }
        except Exception as e:
            logger.error(f"월별 사용량 조회 오류: {e}")
            return {
                'year': year,
                'month': month,
                'total_requests': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_tokens': 0,
                'total_cost_usd': 0.0
            }
    
    def get_detailed_usage(self, limit: int = 100) -> List[Dict]:
        """상세 사용 내역 조회"""
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                cursor.execute(f"""
                    SELECT * FROM {self.schema}.api_usage 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """, (limit,))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"상세 사용 내역 조회 오류: {e}")
            return []

# 전역 인스턴스
api_tracker = APITracker()