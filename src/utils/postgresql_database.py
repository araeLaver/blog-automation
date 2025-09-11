"""
PostgreSQL 데이터베이스 관리 모듈 - Supabase 연동
"""

import os
import json
import psycopg2
import psycopg2.extras
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import hashlib
from pathlib import Path
from dotenv import load_dotenv
import logging

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)


class PostgreSQLDatabase:
    def __init__(self):
        """PostgreSQL 데이터베이스 연결 초기화"""
        # 유료 Koyeb DB 연결 정보
        host = os.getenv('PG_HOST', 'ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app')
        port = int(os.getenv('PG_PORT', 5432))
        database = os.getenv('PG_DATABASE', 'unble')
        user = os.getenv('PG_USER', 'unble')
        password = os.getenv('PG_PASSWORD', 'npg_1kjV0mhECxqs')
        
        # 연결 정보 로깅 (비밀번호는 제외)
        logger.info(f"PostgreSQL 연결 시도: host={host}, port={port}, database={database}, user={user}")
        
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password,
        }
        self.schema = os.getenv('PG_SCHEMA', 'blog_automation')
        self._connection = None
        self.is_connected = False
        
        # 연결 테스트 (실패해도 앱은 실행됨)
        try:
            if not user or not password:
                logger.error("PG_USER 또는 PG_PASSWORD 환경변수가 설정되지 않았습니다!")
                logger.info("Koyeb에서 환경변수를 설정하세요: Settings > Environment variables")
                self.is_connected = False
            else:
                self._test_connection()
                self.is_connected = True
        except Exception as e:
            logger.warning(f"PostgreSQL 연결 실패 (앱은 계속 실행됨): {e}")
            logger.info("연결 정보를 확인하세요. Supabase 대시보드에서 정확한 연결 정보를 확인할 수 있습니다.")
            self.is_connected = False
    
    def _test_connection(self):
        """데이터베이스 연결 테스트"""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        logger.info("PostgreSQL 연결 성공")
    
    def get_connection(self):
        """데이터베이스 연결 반환 (풀링 방식)"""
        try:
            # 트랜잭션 오류 상태인 경우 연결 재설정
            if self._connection and not self._connection.closed:
                try:
                    # 연결 상태 확인
                    with self._connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                except psycopg2.Error:
                    # 연결에 문제가 있으면 재연결
                    logger.warning("기존 연결에 문제가 있어 재연결합니다.")
                    self._connection.close()
                    self._connection = None
            
            if self._connection is None or self._connection.closed:
                self._connection = psycopg2.connect(**self.connection_params)
                self._connection.autocommit = False
                
                # 스키마 설정
                with self._connection.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {self.schema}, public")
                    self._connection.commit()
            
            return self._connection
        except Exception as e:
            logger.error(f"데이터베이스 연결 오류: {e}")
            raise
    
    def close_connection(self):
        """연결 종료"""
        if self._connection and not self._connection.closed:
            self._connection.close()
    
    def _reset_connection_if_needed(self):
        """트랜잭션 오류 상황에서 연결 재설정"""
        try:
            if self._connection and not self._connection.closed:
                self._connection.close()
        except:
            pass
        self._connection = None
    
    def execute_schema_sql(self, sql_file_path: str):
        """SQL 스키마 파일 실행"""
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql_content)
                conn.commit()
                logger.info("✅ 스키마 생성 완료")
        except Exception as e:
            conn.rollback()
            logger.error(f"스키마 생성 오류: {e}")
            raise
    
    # ========================================================================
    # 콘텐츠 히스토리 관리
    # ========================================================================
    
    def check_duplicate_title(self, site: str, title: str, threshold: float = 0.7) -> bool:
        """제목 중복 체크"""
        title_hash = hashlib.sha256(title.encode()).hexdigest()
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # 정확히 같은 제목 체크
                cursor.execute("""
                    SELECT COUNT(*) FROM content_history 
                    WHERE site = %s AND title_hash = %s
                """, (site, title_hash))
                
                if cursor.fetchone()[0] > 0:
                    return True
                
                # 유사 제목 체크
                cursor.execute("""
                    SELECT title FROM content_history 
                    WHERE site = %s AND status = 'published'
                    ORDER BY published_date DESC LIMIT 100
                """, (site,))
                
                existing_titles = [row[0] for row in cursor.fetchall()]
                
                for existing in existing_titles:
                    similarity = self._calculate_similarity(title, existing)
                    if similarity > threshold:
                        return True
                
                return False
        except Exception as e:
            logger.error(f"중복 체크 오류: {e}")
            return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트의 유사도 계산 (간단한 Jaccard 유사도)"""
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union)
    
    def add_content(self, site: str, title: str, category: str, 
                   keywords: List[str], content: str, url: str = None,
                   meta_description: str = None, tags: List[str] = None,
                   word_count: int = 0, reading_time: int = 0) -> int:
        """새 콘텐츠 추가"""
        title_hash = hashlib.sha256(title.encode()).hexdigest()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO content_history 
                    (site, title, title_hash, category, keywords, content_hash, url,
                     meta_description, tags, word_count, reading_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    site, title, title_hash, category, 
                    json.dumps(keywords, ensure_ascii=False),
                    content_hash, url, meta_description,
                    json.dumps(tags or [], ensure_ascii=False),
                    word_count, reading_time
                ))
                
                post_id = cursor.fetchone()[0]
                conn.commit()
                
                logger.info(f"✅ 콘텐츠 추가 완료: {title[:30]}...")
                return post_id
                
        except Exception as e:
            conn.rollback()
            logger.error(f"콘텐츠 추가 오류: {e}")
            raise
    
    def update_content_metadata(self, file_id: int, metadata: Dict):
        """콘텐츠 메타데이터 업데이트 (자동 발행 시 목록 반영용)"""
        try:
            self._reset_connection_if_needed()
            conn = self.get_connection()
            
            with conn.cursor() as cursor:
                # metadata 컬럼을 JSON 형태로 업데이트
                cursor.execute(f"""
                    UPDATE {self.schema}.content_files
                    SET metadata = metadata || %s::jsonb
                    WHERE id = %s
                """, (json.dumps(metadata), file_id))
                
                conn.commit()
                logger.info(f"콘텐츠 메타데이터 업데이트 완료: ID={file_id}")
                
        except Exception as e:
            conn.rollback()
            logger.error(f"메타데이터 업데이트 오류: {e}")
            # 에러를 무시하고 계속 진행 (메타데이터 업데이트는 선택사항)
    
    def get_recent_posts(self, site: str, limit: int = 10) -> List[Dict]:
        """최근 발행 포스트 조회"""
        try:
            # 새로운 연결 사용하여 트랜잭션 오류 방지
            self._reset_connection_if_needed()
            conn = self.get_connection()
            
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # content_history 테이블이 없을 수 있으므로 안전한 쿼리 사용
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = '{self.schema}' 
                        AND table_name = 'content_history'
                    )
                """)
                
                if not cursor.fetchone()[0]:
                    logger.warning(f"{self.schema}.content_history 테이블이 존재하지 않습니다")
                    return []
                
                cursor.execute(f"""
                    SELECT title, category, url, published_date, status, 
                           tags, word_count, reading_time
                    FROM {self.schema}.content_history
                    WHERE site = %s AND status = 'published'
                    ORDER BY published_date DESC
                    LIMIT %s
                """, (site, limit))
                
                posts = []
                for row in cursor.fetchall():
                    post_dict = dict(row)
                    # JSONB 필드를 파이썬 객체로 변환
                    if post_dict.get('tags'):
                        post_dict['tags'] = json.loads(post_dict['tags']) if isinstance(post_dict['tags'], str) else post_dict['tags']
                    posts.append(post_dict)
                
                return posts
                
        except Exception as e:
            logger.error(f"최근 포스트 조회 오류: {e}")
            self._reset_connection_if_needed()
            return []
    
    # ========================================================================
    # 주제 풀 관리
    # ========================================================================
    
    def get_unused_topic(self, site: str) -> Optional[Dict]:
        """사용하지 않은 주제 가져오기"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, topic, category, target_keywords
                    FROM topic_pool 
                    WHERE site = %s AND used = FALSE 
                    ORDER BY priority DESC, RANDOM() 
                    LIMIT 1
                """, (site,))
                
                row = cursor.fetchone()
                if row:
                    # 사용 표시
                    cursor.execute("""
                        UPDATE topic_pool 
                        SET used = TRUE, used_date = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    """, (row['id'],))
                    conn.commit()
                    
                    topic_dict = dict(row)
                    if topic_dict.get('target_keywords'):
                        topic_dict['target_keywords'] = json.loads(topic_dict['target_keywords']) if isinstance(topic_dict['target_keywords'], str) else topic_dict['target_keywords']
                    
                    return topic_dict
                
                return None
                
        except Exception as e:
            logger.error(f"주제 조회 오류: {e}")
            conn.rollback()
            return None
    
    def add_topics_bulk(self, site: str, topics: List[Dict]):
        """대량 주제 추가"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                for topic in topics:
                    cursor.execute("""
                        INSERT INTO topic_pool (site, topic, category, priority, target_keywords)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (site, topic) DO NOTHING
                    """, (
                        site, 
                        topic['topic'], 
                        topic.get('category', ''), 
                        topic.get('priority', 5),
                        json.dumps(topic.get('target_keywords', []), ensure_ascii=False)
                    ))
                
                conn.commit()
                logger.info(f"✅ 주제 {len(topics)}개 추가 완료")
                
        except Exception as e:
            conn.rollback()
            logger.error(f"주제 추가 오류: {e}")
            raise
    
    # ========================================================================
    # 콘텐츠 파일 관리
    # ========================================================================
    
    def add_content_file(self, site: str, title: str, file_path: str, 
                        file_type: str, metadata: Dict[str, Any]) -> int:
        """콘텐츠 파일 정보 추가"""
        # 새로운 연결을 사용하여 트랜잭션 오류 방지
        self._reset_connection_if_needed()
            
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.schema}.content_files 
                    (site, title, file_path, file_type, word_count, reading_time, 
                     tags, categories, file_size, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    site, title, file_path, file_type,
                    metadata.get('word_count', 0),
                    metadata.get('reading_time', 0),
                    metadata.get('tags', []) or [],  # PostgreSQL 배열 타입으로 전달
                    metadata.get('categories', []) or [],  # PostgreSQL 배열 타입으로 전달
                    metadata.get('file_size', 0),
                    metadata.get('status', 'processing')  # processing 상태로 설정
                ))
                
                file_id = cursor.fetchone()[0]
                conn.commit()
                
                logger.info(f"✅ 콘텐츠 파일 추가: {title[:30]}...")
                return file_id
                
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            logger.error(f"콘텐츠 파일 추가 오류: {e}")
            self._reset_connection_if_needed()
            raise
    
    def get_content_files(self, site: str = None, file_type: str = None, 
                         limit: int = 50) -> List[Dict]:
        """콘텐츠 파일 목록 조회"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                query = f"SELECT * FROM {self.schema}.content_files WHERE 1=1"
                params = []
                
                if site:
                    query += " AND site = %s"
                    params.append(site)
                
                if file_type:
                    query += " AND file_type = %s"
                    params.append(file_type)
                
                query += " ORDER BY created_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                
                files = []
                for row in cursor.fetchall():
                    file_dict = dict(row)
                    # JSONB 필드 변환
                    for field in ['tags', 'categories']:
                        if file_dict.get(field):
                            file_dict[field] = json.loads(file_dict[field]) if isinstance(file_dict[field], str) else file_dict[field]
                    
                    # DateTime 필드 포맷팅
                    for field in ['created_at', 'published_at']:
                        if file_dict.get(field):
                            file_dict[field] = self._format_datetime_for_display(file_dict[field])
                    
                    files.append(file_dict)
                
                return files
                
        except Exception as e:
            logger.error(f"콘텐츠 파일 조회 오류: {e}")
            return []
    
    # ========================================================================
    # 시스템 로그 관리
    # ========================================================================
    
    def add_system_log(self, level: str, component: str, message: str, 
                       details: Dict = None, site: str = None, 
                       trace_id: str = None, duration_ms: int = None):
        """시스템 로그 추가"""
        try:
            self._reset_connection_if_needed()
            conn = self.get_connection()
            
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.schema}.system_logs 
                    (level, component, message, details, site, trace_id, duration_ms)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    level, component, message, 
                    json.dumps(details or {}, ensure_ascii=False),
                    site, trace_id, duration_ms
                ))
                conn.commit()
                
        except Exception as e:
            # 로그 기록 실패 시에도 메인 프로세스는 계속 진행
            print(f"로그 기록 실패: {e}")
            self._reset_connection_if_needed()
    
    def get_system_logs(self, level: str = None, component: str = None, 
                       limit: int = 100) -> List[Dict]:
        """시스템 로그 조회"""
        try:
            self._reset_connection_if_needed()
            conn = self.get_connection()
            
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                query = f"SELECT * FROM {self.schema}.system_logs WHERE 1=1"
                params = []
                
                if level:
                    query += " AND level = %s"  # Fixed column name
                    params.append(level)
                
                if component:
                    query += " AND component = %s"
                    params.append(component)
                
                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                
                logs = []
                for row in cursor.fetchall():
                    log_dict = dict(row)
                    if log_dict.get('details'):
                        log_dict['details'] = json.loads(log_dict['details']) if isinstance(log_dict['details'], str) else log_dict['details']
                    logs.append(log_dict)
                
                return logs
                
        except Exception as e:
            logger.error(f"시스템 로그 조회 오류: {e}")
            self._reset_connection_if_needed()
            return []
    
    # ========================================================================
    # 수익 추적 관리
    # ========================================================================
    
    def add_revenue_data(self, site: str, date_str: str, revenue_data: Dict[str, Any]):
        """수익 데이터 추가/업데이트"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO revenue_tracking 
                    (site, date, ad_revenue, affiliate_revenue, page_views,
                     unique_visitors, ctr, rpm, impression_revenue, click_revenue)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (site, date) 
                    DO UPDATE SET
                        ad_revenue = EXCLUDED.ad_revenue,
                        affiliate_revenue = EXCLUDED.affiliate_revenue,
                        page_views = EXCLUDED.page_views,
                        unique_visitors = EXCLUDED.unique_visitors,
                        ctr = EXCLUDED.ctr,
                        rpm = EXCLUDED.rpm,
                        impression_revenue = EXCLUDED.impression_revenue,
                        click_revenue = EXCLUDED.click_revenue,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    site, date_str,
                    revenue_data.get('ad_revenue', 0),
                    revenue_data.get('affiliate_revenue', 0),
                    revenue_data.get('page_views', 0),
                    revenue_data.get('unique_visitors', 0),
                    revenue_data.get('ctr', 0),
                    revenue_data.get('rpm', 0),
                    revenue_data.get('impression_revenue', 0),
                    revenue_data.get('click_revenue', 0)
                ))
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logger.error(f"수익 데이터 추가 오류: {e}")
            raise
    
    def get_revenue_summary(self, site: str = None, days: int = 30) -> Dict[str, Any]:
        """수익 요약 조회"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        COALESCE(SUM(ad_revenue + affiliate_revenue + impression_revenue + click_revenue), 0) as total_revenue,
                        COALESCE(SUM(ad_revenue), 0) as ad_revenue,
                        COALESCE(SUM(affiliate_revenue), 0) as affiliate_revenue,
                        COALESCE(SUM(page_views), 0) as total_views,
                        COALESCE(SUM(unique_visitors), 0) as total_visitors,
                        COALESCE(AVG(ctr), 0) as avg_ctr,
                        COALESCE(AVG(rpm), 0) as avg_rpm
                    FROM revenue_tracking
                    WHERE date >= CURRENT_DATE - INTERVAL '%s days'
                """
                
                params = [days]
                if site:
                    query += " AND site = %s"
                    params.append(site)
                
                cursor.execute(query, params)
                row = cursor.fetchone()
                
                return {
                    'total_revenue': float(row[0] or 0),
                    'ad_revenue': float(row[1] or 0),
                    'affiliate_revenue': float(row[2] or 0),
                    'total_views': row[3] or 0,
                    'total_visitors': row[4] or 0,
                    'avg_ctr': float(row[5] or 0),
                    'avg_rpm': float(row[6] or 0)
                }
                
        except Exception as e:
            logger.error(f"수익 요약 조회 오류: {e}")
            return {
                'total_revenue': 0, 'ad_revenue': 0, 'affiliate_revenue': 0,
                'total_views': 0, 'total_visitors': 0, 'avg_ctr': 0, 'avg_rpm': 0
            }
    
    # ========================================================================
    # API 사용량 추적
    # ========================================================================
    
    def track_api_usage(self, provider: str, endpoint: str, tokens: int, 
                       cost: float, success: bool, response_time: float, 
                       site: str = None, request_id: str = None,
                       http_status: int = None):
        """API 사용량 추적"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_usage 
                    (api_provider, endpoint, tokens_used, cost, success, 
                     response_time, site, request_id, http_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    provider, endpoint, tokens, cost, success, 
                    response_time, site, request_id, http_status
                ))
                conn.commit()
                
        except Exception as e:
            # API 사용량 추적 실패 시에도 메인 프로세스 계속 진행
            print(f"API 사용량 추적 실패: {e}")
    
    def get_api_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """API 사용량 요약"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        api_provider,
                        COALESCE(SUM(tokens_used), 0) as total_tokens,
                        COALESCE(SUM(cost), 0) as total_cost,
                        COUNT(*) as total_calls,
                        COALESCE(AVG(response_time), 0) as avg_response_time,
                        SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) as successful_calls
                    FROM api_usage
                    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '%s days'
                    GROUP BY api_provider
                """, (days,))
                
                usage = {}
                for row in cursor.fetchall():
                    usage[row[0]] = {
                        'total_tokens': row[1] or 0,
                        'total_cost': float(row[2] or 0),
                        'total_calls': row[3] or 0,
                        'avg_response_time': float(row[4] or 0),
                        'successful_calls': row[5] or 0,
                        'success_rate': (row[5] / row[3] * 100) if row[3] > 0 else 0
                    }
                
                return usage
                
        except Exception as e:
            logger.error(f"API 사용량 요약 오류: {e}")
            return {}
    
    # ========================================================================
    # 대시보드 통계
    # ========================================================================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """대시보드용 종합 통계"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # 기본 통계 (content_files 테이블 사용)
                cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.content_files")
                total_posts = cursor.fetchone()[0]
                
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {self.schema}.content_files 
                    WHERE DATE(created_at) = CURRENT_DATE
                """)
                today_posts = cursor.fetchone()[0]
                
                # 사이트별 통계
                cursor.execute(f"""
                    SELECT site, COUNT(*) FROM {self.schema}.content_files GROUP BY site
                """)
                site_stats = dict(cursor.fetchall())
                
                # 파일 통계
                cursor.execute(f"""
                    SELECT file_type, COUNT(*) FROM {self.schema}.content_files GROUP BY file_type
                """)
                file_stats = dict(cursor.fetchall())
                
                # 최근 7일 수익
                revenue_summary = self.get_revenue_summary(days=7)
                
                # API 사용량
                api_summary = self.get_api_usage_summary(days=7)
                
                return {
                    'posts': {
                        'total': total_posts,
                        'today': today_posts,
                        'by_site': site_stats
                    },
                    'files': file_stats,
                    'revenue': revenue_summary,
                    'api_usage': api_summary
                }
                
        except Exception as e:
            logger.error(f"대시보드 통계 조회 오류: {e}")
            return {
                'posts': {'total': 0, 'today': 0, 'by_site': {}},
                'files': {},
                'revenue': {'total_revenue': 0, 'total_views': 0},
                'api_usage': {}
            }
    
    # ========================================================================
    # 유틸리티 메서드
    # ========================================================================
    
    def update_content_file_status(self, file_id: int, status: str, 
                                   published_at: str = None):
        """콘텐츠 파일 상태 업데이트"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE content_files 
                    SET status = %s, published_at = %s
                    WHERE id = %s
                """, (status, published_at, file_id))
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logger.error(f"파일 상태 업데이트 오류: {e}")
    
    def update_file_status(self, file_id: int, status: str, published_at: datetime = None):
        """파일 상태 및 발행 시간 업데이트 (web_dashboard용)"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                if published_at:
                    cursor.execute(f"""
                        UPDATE {self.schema}.content_files 
                        SET status = %s, published_at = %s
                        WHERE id = %s
                    """, (status, published_at, file_id))
                else:
                    cursor.execute(f"""
                        UPDATE {self.schema}.content_files 
                        SET status = %s
                        WHERE id = %s
                    """, (status, file_id))
                conn.commit()
                logger.info(f"파일 상태 업데이트 완료: ID={file_id}, Status={status}")
                
        except Exception as e:
            conn.rollback()
            logger.error(f"파일 상태 업데이트 오류: {e}")
            raise
    
    def get_site_configs(self) -> Dict[str, Dict]:
        """사이트 설정 조회"""
        try:
            self._reset_connection_if_needed()
            conn = self.get_connection()
            
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(f"""
                    SELECT site_code, site_name, site_url, site_type,
                           content_config, publishing_schedule
                    FROM {self.schema}.site_configs
                    WHERE is_active = TRUE
                """)
                
                configs = {}
                for row in cursor.fetchall():
                    config_dict = dict(row)
                    # JSONB 필드 변환
                    if config_dict.get('content_config'):
                        config_dict['content_config'] = json.loads(config_dict['content_config']) if isinstance(config_dict['content_config'], str) else config_dict['content_config']
                    if config_dict.get('publishing_schedule'):
                        config_dict['publishing_schedule'] = json.loads(config_dict['publishing_schedule']) if isinstance(config_dict['publishing_schedule'], str) else config_dict['publishing_schedule']
                    
                    configs[config_dict['site_code']] = config_dict
                
                return configs
                
        except Exception as e:
            logger.error(f"사이트 설정 조회 오류: {e}")
            self._reset_connection_if_needed()
            return {}
    
    def get_topic_stats(self, site: str = None) -> Dict[str, int]:
        """주제 통계 조회"""
        try:
            # topic_pool 테이블이 없을 수 있으므로 새로운 연결로 시도
            if self._connection and not self._connection.closed:
                try:
                    self._connection.close()
                except:
                    pass
            self._connection = None
                
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # 테이블 존재 확인
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = '{self.schema}' 
                        AND table_name = 'topic_pool'
                    )
                """)
                
                if not cursor.fetchone()[0]:
                    logger.warning(f"{self.schema}.topic_pool 테이블이 존재하지 않습니다")
                    return {'used_count': 0, 'unused_count': 0, 'total_count': 0}
                
                if site:
                    cursor.execute(f"""
                        SELECT 
                            SUM(CASE WHEN used = true THEN 1 ELSE 0 END) as used_count,
                            SUM(CASE WHEN used = false THEN 1 ELSE 0 END) as unused_count,
                            COUNT(*) as total_count
                        FROM {self.schema}.topic_pool 
                        WHERE site = %s
                    """, (site,))
                else:
                    cursor.execute(f"""
                        SELECT 
                            SUM(CASE WHEN used = true THEN 1 ELSE 0 END) as used_count,
                            SUM(CASE WHEN used = false THEN 1 ELSE 0 END) as unused_count,
                            COUNT(*) as total_count
                        FROM {self.schema}.topic_pool
                    """)
                
                row = cursor.fetchone()
                return {
                    'used_count': int(row[0] or 0),
                    'unused_count': int(row[1] or 0),
                    'total_count': int(row[2] or 0)
                }
        except Exception as e:
            logger.error(f"주제 통계 조회 오류: {e}")
            # 오류 발생시에도 연결 재설정
            try:
                if self._connection and not self._connection.closed:
                    self._connection.close()
                self._connection = None
            except:
                pass
            return {'used_count': 0, 'unused_count': 0, 'total_count': 0}
    
    def delete_content_file(self, file_id: int) -> bool:
        """콘텐츠 파일 삭제"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    DELETE FROM {self.schema}.content_files 
                    WHERE id = %s
                """, (file_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"파일 삭제 오류: {e}")
            return False
    
    def delete_content_by_path(self, file_path: str) -> bool:
        """파일 경로로 콘텐츠 삭제"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    DELETE FROM {self.schema}.content_files 
                    WHERE file_path = %s
                """, (file_path,))
                conn.commit()
                deleted_count = cursor.rowcount
                logger.info(f"경로로 DB 삭제: {file_path} (삭제된 행: {deleted_count})")
                return deleted_count > 0
        except Exception as e:
            logger.error(f"경로 기반 파일 삭제 오류: {e}")
            return False
    
    def get_content_files(self, file_type: str = None, limit: int = 50) -> List[Dict]:
        """콘텐츠 파일 목록 조회 (오버로드 버전)"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                
                query = f"""
                    SELECT id, site, title, file_path, file_type, word_count, 
                           reading_time, status, tags, categories, created_at, 
                           published_at, file_size
                    FROM {self.schema}.content_files
                    WHERE 1=1
                """
                params = []
                
                if file_type:
                    query += " AND file_type = %s"
                    params.append(file_type)
                
                query += " ORDER BY created_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                
                files = []
                for row in cursor.fetchall():
                    # JSONB 필드 처리
                    tags = row['tags'] if row['tags'] else []
                    categories = row['categories'] if row['categories'] else []
                    
                    files.append({
                        'id': row['id'],
                        'site': row['site'],
                        'title': row['title'],
                        'file_path': row['file_path'],
                        'file_type': row['file_type'],
                        'word_count': row['word_count'],
                        'reading_time': row['reading_time'],
                        'status': row['status'],
                        'tags': tags,
                        'categories': categories,
                        'created_at': self._format_datetime_for_display(row['created_at']),
                        'published_at': self._format_datetime_for_display(row['published_at']),
                        'file_size': row['file_size'],
                        'category': categories[0] if categories else 'N/A',  # 호환성
                        'filename': row['file_path'].split('/')[-1] if row['file_path'] else 'unknown'  # 호환성
                    })
                
                return files
                
        except Exception as e:
            logger.error(f"콘텐츠 파일 목록 조회 오류: {e}")
            return []
    
    def _format_datetime_for_display(self, dt):
        """한국 시간으로 포맷된 날짜/시간 문자열 반환"""
        if not dt:
            return None
        
        from datetime import timezone, timedelta
        
        # PostgreSQL에서 가져온 datetime이 naive인 경우 UTC로 가정
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        # 한국 시간으로 변환 (UTC+9)
        kst = timezone(timedelta(hours=9))
        kst_time = dt.astimezone(kst)
        
        # 사용자 친화적 형식으로 반환
        return kst_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def __del__(self):
        """소멸자 - 연결 정리"""
        self.close_connection()


# 백워드 호환성을 위한 별칭
ContentDatabase = PostgreSQLDatabase