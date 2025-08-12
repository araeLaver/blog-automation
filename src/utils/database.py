"""
데이터베이스 관리 모듈 - 중복 체크 및 콘텐츠 히스토리 관리
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import hashlib
from pathlib import Path


class ContentDatabase:
    def __init__(self, db_path: str = "./data/blog_content.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 콘텐츠 히스토리 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    title_hash VARCHAR(64) NOT NULL,
                    category VARCHAR(100),
                    keywords TEXT,
                    content_hash VARCHAR(64),
                    url VARCHAR(255),
                    published_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    performance_metrics TEXT,
                    status VARCHAR(20) DEFAULT 'published',
                    UNIQUE(site, title_hash)
                )
            """)
            
            # 주제 풀 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topic_pool (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site VARCHAR(50) NOT NULL,
                    topic VARCHAR(255) NOT NULL,
                    category VARCHAR(100),
                    priority INTEGER DEFAULT 5,
                    used BOOLEAN DEFAULT 0,
                    used_date DATETIME,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 이미지 캐시 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS image_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword VARCHAR(255) NOT NULL,
                    image_url TEXT NOT NULL,
                    source VARCHAR(50),
                    used_count INTEGER DEFAULT 0,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME
                )
            """)
            
            # 성능 추적 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site VARCHAR(50) NOT NULL,
                    post_id INTEGER,
                    views INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    revenue DECIMAL(10,2) DEFAULT 0,
                    bounce_rate DECIMAL(5,2),
                    avg_time_on_page INTEGER,
                    tracked_date DATE DEFAULT CURRENT_DATE
                )
            """)
            
            # 콘텐츠 파일 테이블 (WordPress/Tistory 백업파일)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    file_type VARCHAR(20) NOT NULL, -- 'wordpress', 'tistory'
                    word_count INTEGER,
                    reading_time INTEGER,
                    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'published', 'archived'
                    tags TEXT,
                    categories TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    published_at DATETIME,
                    file_size INTEGER
                )
            """)
            
            # 시스템 로그 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_level VARCHAR(20) NOT NULL, -- 'INFO', 'ERROR', 'WARNING'
                    component VARCHAR(50) NOT NULL, -- 'scheduler', 'publisher', 'generator'
                    message TEXT NOT NULL,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    site VARCHAR(50)
                )
            """)
            
            # 수익 추적 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revenue_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    ad_revenue DECIMAL(10,2) DEFAULT 0,
                    affiliate_revenue DECIMAL(10,2) DEFAULT 0,
                    page_views INTEGER DEFAULT 0,
                    unique_visitors INTEGER DEFAULT 0,
                    ctr DECIMAL(5,4) DEFAULT 0,
                    rpm DECIMAL(10,2) DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # API 사용량 추적 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_provider VARCHAR(30) NOT NULL, -- 'anthropic', 'openai', 'unsplash'
                    endpoint VARCHAR(100),
                    tokens_used INTEGER DEFAULT 0,
                    cost DECIMAL(8,4) DEFAULT 0,
                    success BOOLEAN DEFAULT 1,
                    response_time DECIMAL(6,3),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    site VARCHAR(50)
                )
            """)
            
            conn.commit()
    
    def check_duplicate_title(self, site: str, title: str, threshold: float = 0.7) -> bool:
        """제목 중복 체크"""
        title_hash = hashlib.sha256(title.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 정확히 같은 제목 체크
            cursor.execute("""
                SELECT COUNT(*) FROM content_history 
                WHERE site = ? AND title_hash = ?
            """, (site, title_hash))
            
            if cursor.fetchone()[0] > 0:
                return True
            
            # 유사 제목 체크 (간단한 방법)
            cursor.execute("""
                SELECT title FROM content_history 
                WHERE site = ? AND status = 'published'
                ORDER BY published_date DESC LIMIT 100
            """, (site,))
            
            existing_titles = [row[0] for row in cursor.fetchall()]
            
            for existing in existing_titles:
                similarity = self._calculate_similarity(title, existing)
                if similarity > threshold:
                    return True
            
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
                    keywords: List[str], content: str, url: str) -> int:
        """새 콘텐츠 추가"""
        title_hash = hashlib.sha256(title.encode()).hexdigest()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        keywords_json = json.dumps(keywords, ensure_ascii=False)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO content_history 
                (site, title, title_hash, category, keywords, content_hash, url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (site, title, title_hash, category, keywords_json, content_hash, url))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_unused_topic(self, site: str) -> Optional[Dict]:
        """사용하지 않은 주제 가져오기"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, topic, category 
                FROM topic_pool 
                WHERE site = ? AND used = 0 
                ORDER BY priority DESC, RANDOM() 
                LIMIT 1
            """, (site,))
            
            row = cursor.fetchone()
            if row:
                # 사용 표시
                cursor.execute("""
                    UPDATE topic_pool 
                    SET used = 1, used_date = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (row[0],))
                conn.commit()
                
                return {
                    "id": row[0],
                    "topic": row[1],
                    "category": row[2]
                }
            
            return None
    
    def add_topics_bulk(self, site: str, topics: List[Dict]):
        """대량 주제 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for topic in topics:
                cursor.execute("""
                    INSERT INTO topic_pool (site, topic, category, priority)
                    VALUES (?, ?, ?, ?)
                """, (site, topic['topic'], topic.get('category', ''), 
                      topic.get('priority', 5)))
            
            conn.commit()
    
    def get_recent_posts(self, site: str, limit: int = 10) -> List[Dict]:
        """최근 발행 포스트 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT title, category, url, published_date
                FROM content_history
                WHERE site = ? AND status = 'published'
                ORDER BY published_date DESC
                LIMIT ?
            """, (site, limit))
            
            posts = []
            for row in cursor.fetchall():
                posts.append({
                    "title": row[0],
                    "category": row[1],
                    "url": row[2],
                    "published_date": row[3]
                })
            
            return posts
    
    def update_performance_metrics(self, site: str, post_id: int, metrics: Dict):
        """성능 지표 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO performance_tracking 
                (site, post_id, views, clicks, revenue, bounce_rate, avg_time_on_page)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (site, post_id, 
                  metrics.get('views', 0),
                  metrics.get('clicks', 0),
                  metrics.get('revenue', 0),
                  metrics.get('bounce_rate'),
                  metrics.get('avg_time_on_page')))
            
            conn.commit()
    
    def get_best_performing_topics(self, site: str, limit: int = 5) -> List[Dict]:
        """최고 성과 주제 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ch.title, ch.category, 
                       AVG(pt.views) as avg_views,
                       AVG(pt.revenue) as avg_revenue
                FROM content_history ch
                JOIN performance_tracking pt ON ch.id = pt.post_id
                WHERE ch.site = ?
                GROUP BY ch.category
                ORDER BY avg_revenue DESC, avg_views DESC
                LIMIT ?
            """, (site, limit))
            
            topics = []
            for row in cursor.fetchall():
                topics.append({
                    "title": row[0],
                    "category": row[1],
                    "avg_views": row[2],
                    "avg_revenue": row[3]
                })
            
            return topics
    
    def add_content_file(self, site: str, title: str, file_path: str, 
                        file_type: str, metadata: Dict[str, Any]) -> int:
        """콘텐츠 파일 정보 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO content_files 
                (site, title, file_path, file_type, word_count, reading_time, 
                 tags, categories, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                site, title, file_path, file_type,
                metadata.get('word_count', 0),
                metadata.get('reading_time', 0),
                json.dumps(metadata.get('tags', []), ensure_ascii=False),
                json.dumps(metadata.get('categories', []), ensure_ascii=False),
                metadata.get('file_size', 0)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_content_files(self, site: str = None, file_type: str = None, 
                         limit: int = 50) -> List[Dict]:
        """콘텐츠 파일 목록 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM content_files WHERE 1=1"
            params = []
            
            if site:
                query += " AND site = ?"
                params.append(site)
            
            if file_type:
                query += " AND file_type = ?"
                params.append(file_type)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            files = []
            for row in cursor.fetchall():
                files.append({
                    'id': row[0],
                    'site': row[1],
                    'title': row[2],
                    'file_path': row[3],
                    'file_type': row[4],
                    'word_count': row[5],
                    'reading_time': row[6],
                    'status': row[7],
                    'tags': json.loads(row[8]) if row[8] else [],
                    'categories': json.loads(row[9]) if row[9] else [],
                    'created_at': row[10],
                    'published_at': row[11],
                    'file_size': row[12]
                })
            
            return files
    
    def update_content_file_status(self, file_id: int, status: str, 
                                   published_at: str = None):
        """콘텐츠 파일 상태 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE content_files 
                SET status = ?, published_at = ?
                WHERE id = ?
            """, (status, published_at, file_id))
            conn.commit()
    
    def add_system_log(self, level: str, component: str, message: str, 
                       details: str = None, site: str = None):
        """시스템 로그 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (log_level, component, message, details, site)
                VALUES (?, ?, ?, ?, ?)
            """, (level, component, message, details, site))
            conn.commit()
    
    def get_system_logs(self, level: str = None, component: str = None, 
                       limit: int = 100) -> List[Dict]:
        """시스템 로그 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM system_logs WHERE 1=1"
            params = []
            
            if level:
                query += " AND log_level = ?"
                params.append(level)
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'id': row[0],
                    'log_level': row[1],
                    'component': row[2],
                    'message': row[3],
                    'details': row[4],
                    'timestamp': row[5],
                    'site': row[6]
                })
            
            return logs
    
    def add_revenue_data(self, site: str, date: str, revenue_data: Dict[str, Any]):
        """수익 데이터 추가/업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기존 데이터 확인
            cursor.execute("""
                SELECT id FROM revenue_tracking WHERE site = ? AND date = ?
            """, (site, date))
            
            if cursor.fetchone():
                # 업데이트
                cursor.execute("""
                    UPDATE revenue_tracking 
                    SET ad_revenue = ?, affiliate_revenue = ?, page_views = ?,
                        unique_visitors = ?, ctr = ?, rpm = ?
                    WHERE site = ? AND date = ?
                """, (
                    revenue_data.get('ad_revenue', 0),
                    revenue_data.get('affiliate_revenue', 0),
                    revenue_data.get('page_views', 0),
                    revenue_data.get('unique_visitors', 0),
                    revenue_data.get('ctr', 0),
                    revenue_data.get('rpm', 0),
                    site, date
                ))
            else:
                # 삽입
                cursor.execute("""
                    INSERT INTO revenue_tracking 
                    (site, date, ad_revenue, affiliate_revenue, page_views,
                     unique_visitors, ctr, rpm)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    site, date,
                    revenue_data.get('ad_revenue', 0),
                    revenue_data.get('affiliate_revenue', 0),
                    revenue_data.get('page_views', 0),
                    revenue_data.get('unique_visitors', 0),
                    revenue_data.get('ctr', 0),
                    revenue_data.get('rpm', 0)
                ))
            
            conn.commit()
    
    def get_revenue_summary(self, site: str = None, days: int = 30) -> Dict[str, Any]:
        """수익 요약 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    SUM(ad_revenue + affiliate_revenue) as total_revenue,
                    SUM(ad_revenue) as ad_revenue,
                    SUM(affiliate_revenue) as affiliate_revenue,
                    SUM(page_views) as total_views,
                    SUM(unique_visitors) as total_visitors,
                    AVG(ctr) as avg_ctr,
                    AVG(rpm) as avg_rpm
                FROM revenue_tracking
                WHERE date >= DATE('now', '-{} days')
            """.format(days)
            
            if site:
                query += " AND site = ?"
                cursor.execute(query, (site,))
            else:
                cursor.execute(query)
            
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
    
    def track_api_usage(self, provider: str, endpoint: str, tokens: int, 
                       cost: float, success: bool, response_time: float, 
                       site: str = None):
        """API 사용량 추적"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_usage 
                (api_provider, endpoint, tokens_used, cost, success, 
                 response_time, site)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (provider, endpoint, tokens, cost, success, response_time, site))
            conn.commit()
    
    def get_api_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """API 사용량 요약"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    api_provider,
                    SUM(tokens_used) as total_tokens,
                    SUM(cost) as total_cost,
                    COUNT(*) as total_calls,
                    AVG(response_time) as avg_response_time,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_calls
                FROM api_usage
                WHERE timestamp >= DATE('now', '-{} days')
                GROUP BY api_provider
            """.format(days))
            
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
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """대시보드용 종합 통계"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기본 통계
            cursor.execute("SELECT COUNT(*) FROM content_history")
            total_posts = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM content_history 
                WHERE DATE(published_date) = DATE('now')
            """)
            today_posts = cursor.fetchone()[0]
            
            # 사이트별 통계
            cursor.execute("""
                SELECT site, COUNT(*) FROM content_history GROUP BY site
            """)
            site_stats = dict(cursor.fetchall())
            
            # 파일 통계
            cursor.execute("""
                SELECT file_type, COUNT(*) FROM content_files GROUP BY file_type
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
    
    def delete_content_file(self, file_id: int) -> bool:
        """콘텐츠 파일 삭제"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM content_files WHERE id = ?", (file_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Delete content file error: {e}")
            return False
    
    def update_content_file_status(self, file_id: int, status: str, 
                                 published_at: str = None) -> bool:
        """콘텐츠 파일 상태 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if published_at:
                    cursor.execute("""
                        UPDATE content_files 
                        SET status = ?, published_at = ? 
                        WHERE id = ?
                    """, (status, published_at, file_id))
                else:
                    cursor.execute("""
                        UPDATE content_files 
                        SET status = ? 
                        WHERE id = ?
                    """, (status, file_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Update content file status error: {e}")
            return False
    
    def get_topic_stats(self, site: str = None) -> Dict[str, int]:
        """주제 통계 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if site:
                    cursor.execute("""
                        SELECT 
                            SUM(CASE WHEN used = 1 THEN 1 ELSE 0 END) as used_count,
                            SUM(CASE WHEN used = 0 THEN 1 ELSE 0 END) as unused_count,
                            COUNT(*) as total_count
                        FROM topic_pool WHERE site = ?
                    """, (site,))
                else:
                    cursor.execute("""
                        SELECT 
                            SUM(CASE WHEN used = 1 THEN 1 ELSE 0 END) as used_count,
                            SUM(CASE WHEN used = 0 THEN 1 ELSE 0 END) as unused_count,
                            COUNT(*) as total_count
                        FROM topic_pool
                    """)
                
                row = cursor.fetchone()
                return {
                    'used_count': row[0] or 0,
                    'unused_count': row[1] or 0,
                    'total_count': row[2] or 0
                }
        except Exception as e:
            print(f"Get topic stats error: {e}")
            return {'used_count': 0, 'unused_count': 0, 'total_count': 0}
    
    def get_content_files(self, file_type: str = None, limit: int = 50) -> List[Dict]:
        """콘텐츠 파일 목록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = """
                    SELECT id, site, title, file_path, file_type, word_count, 
                           reading_time, status, tags, categories, created_at, 
                           published_at, file_size
                    FROM content_files
                """
                params = []
                
                if file_type:
                    query += " WHERE file_type = ?"
                    params.append(file_type)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                files = []
                for row in cursor.fetchall():
                    # JSON 필드 파싱
                    try:
                        tags = json.loads(row['tags']) if row['tags'] else []
                    except:
                        tags = []
                    
                    try:
                        categories = json.loads(row['categories']) if row['categories'] else []
                    except:
                        categories = []
                    
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
                        'created_at': row['created_at'],
                        'published_at': row['published_at'],
                        'file_size': row['file_size'],
                        'category': categories[0] if categories else 'N/A',  # 호환성을 위해
                        'filename': row['file_path'].split('/')[-1] if row['file_path'] else 'unknown'  # 호환성을 위해
                    })
                
                return files
                
        except Exception as e:
            print(f"Get content files error: {e}")
            return []
    
    def get_content_file_by_id(self, file_id: int) -> Dict:
        """ID로 콘텐츠 파일 정보 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, site, title, file_path, file_type, word_count, 
                           reading_time, status, tags, categories, created_at, 
                           published_at, file_size
                    FROM content_files
                    WHERE id = ?
                """, (file_id,))
                
                row = cursor.fetchone()
                if row:
                    # JSON 필드 파싱
                    try:
                        tags = json.loads(row['tags']) if row['tags'] else []
                    except:
                        tags = []
                    
                    try:
                        categories = json.loads(row['categories']) if row['categories'] else []
                    except:
                        categories = []
                    
                    return {
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
                        'created_at': row['created_at'],
                        'published_at': row['published_at'],
                        'file_size': row['file_size']
                    }
                return None
                
        except Exception as e:
            print(f"Get content file by id error: {e}")
            return None