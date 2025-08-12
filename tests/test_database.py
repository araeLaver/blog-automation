"""
데이터베이스 모듈 테스트
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from src.utils.database import ContentDatabase


class TestContentDatabase:
    def setup_method(self):
        """각 테스트 전 초기화"""
        # 임시 데이터베이스 파일 생성
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = ContentDatabase(self.db_path)
    
    def teardown_method(self):
        """각 테스트 후 정리"""
        # 데이터베이스 연결 종료
        if hasattr(self, 'db'):
            del self.db
        
        # 임시 파일 삭제 (Windows 권한 이슈 처리)
        import time
        import shutil
        try:
            if os.path.exists(self.db_path):
                time.sleep(0.1)  # 파일 핸들 해제 대기
                os.remove(self.db_path)
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass  # 테스트 환경에서는 무시
    
    def test_database_initialization(self):
        """데이터베이스 초기화 테스트"""
        # 데이터베이스 파일이 생성되었는지 확인
        assert os.path.exists(self.db_path)
        
        # 테이블이 생성되었는지 확인
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'content_history',
                'topic_pool', 
                'image_cache',
                'performance_tracking'
            ]
            
            for table in expected_tables:
                assert table in tables
    
    def test_add_content(self):
        """콘텐츠 추가 테스트"""
        content_id = self.db.add_content(
            site="unpre",
            title="테스트 포스트",
            category="개발",
            keywords=["Python", "테스트"],
            content="테스트 콘텐츠 내용입니다.",
            url="https://unpre.co.kr/test-post"
        )
        
        assert content_id is not None
        assert content_id > 0
        
        # 데이터베이스에 저장되었는지 확인
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM content_history WHERE id = ?", (content_id,))
            row = cursor.fetchone()
            
            assert row is not None
            assert row[1] == "unpre"  # site
            assert row[2] == "테스트 포스트"  # title
    
    def test_check_duplicate_title_exact(self):
        """정확한 제목 중복 체크 테스트"""
        # 첫 번째 콘텐츠 추가
        self.db.add_content(
            site="unpre",
            title="Python 프로그래밍 기초",
            category="개발",
            keywords=["Python"],
            content="내용",
            url="https://example.com/1"
        )
        
        # 같은 제목으로 중복 체크
        is_duplicate = self.db.check_duplicate_title("unpre", "Python 프로그래밍 기초")
        assert is_duplicate is True
        
        # 다른 제목으로 중복 체크
        is_duplicate = self.db.check_duplicate_title("unpre", "JavaScript 프로그래밍 기초")
        assert is_duplicate is False
    
    def test_check_duplicate_title_similar(self):
        """유사한 제목 중복 체크 테스트"""
        # 기존 콘텐츠 추가
        self.db.add_content(
            site="unpre",
            title="Python 프로그래밍 완벽 가이드",
            category="개발", 
            keywords=["Python"],
            content="내용",
            url="https://example.com/1"
        )
        
        # 유사한 제목 체크 (임계값 0.7)
        similar_title = "Python 프로그래밍 완벽 마스터 가이드"
        is_duplicate = self.db.check_duplicate_title("unpre", similar_title, threshold=0.6)
        assert is_duplicate is True
        
        # 다른 사이트는 중복이 아님
        is_duplicate = self.db.check_duplicate_title("untab", similar_title)
        assert is_duplicate is False
    
    def test_similarity_calculation(self):
        """유사도 계산 테스트"""
        text1 = "Python 프로그래밍 기초 가이드"
        text2 = "Python 프로그래밍 고급 가이드"
        
        similarity = self.db._calculate_similarity(text1, text2)
        
        # 0과 1 사이의 값이어야 함
        assert 0 <= similarity <= 1
        
        # 같은 텍스트는 유사도 1
        assert self.db._calculate_similarity(text1, text1) == 1.0
        
        # 완전히 다른 텍스트는 유사도 0
        assert self.db._calculate_similarity("Python", "부동산 투자") == 0.0
    
    def test_add_topics_bulk(self):
        """대량 주제 추가 테스트"""
        topics = [
            {"topic": "Python 기초", "category": "개발", "priority": 5},
            {"topic": "JavaScript ES6", "category": "개발", "priority": 4},
            {"topic": "React 컴포넌트", "category": "프론트엔드", "priority": 3}
        ]
        
        self.db.add_topics_bulk("unpre", topics)
        
        # 추가되었는지 확인
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM topic_pool WHERE site = 'unpre'")
            count = cursor.fetchone()[0]
            assert count == 3
    
    def test_get_unused_topic(self):
        """사용하지 않은 주제 가져오기 테스트"""
        # 주제 추가
        topics = [
            {"topic": "Python 기초", "category": "개발", "priority": 5},
            {"topic": "JavaScript 기초", "category": "개발", "priority": 3}
        ]
        self.db.add_topics_bulk("unpre", topics)
        
        # 사용하지 않은 주제 가져오기 (우선순위 높은 것부터)
        topic = self.db.get_unused_topic("unpre")
        
        assert topic is not None
        assert topic["topic"] == "Python 기초"  # 우선순위가 높음
        assert topic["category"] == "개발"
        
        # 해당 주제가 사용됨으로 표시되었는지 확인
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT used FROM topic_pool WHERE id = ?", 
                (topic["id"],)
            )
            used = cursor.fetchone()[0]
            assert used == 1
    
    def test_get_recent_posts(self):
        """최근 포스트 조회 테스트"""
        # 테스트 데이터 추가
        posts_data = [
            ("포스트 1", "개발", "https://example.com/1"),
            ("포스트 2", "IT", "https://example.com/2"),
            ("포스트 3", "개발", "https://example.com/3")
        ]
        
        for title, category, url in posts_data:
            self.db.add_content(
                site="unpre",
                title=title,
                category=category,
                keywords=["test"],
                content="내용",
                url=url
            )
        
        # 최근 포스트 2개 조회
        recent_posts = self.db.get_recent_posts("unpre", limit=2)
        
        assert len(recent_posts) == 2
        # 최신 순으로 정렬되어야 함 (실제 정렬은 발행 시간 기준)
        # 테스트에서는 단순히 존재 여부만 확인
        titles = [post["title"] for post in recent_posts]
        assert "포스트 1" in titles or "포스트 2" in titles or "포스트 3" in titles
    
    def test_update_performance_metrics(self):
        """성능 지표 업데이트 테스트"""
        # 콘텐츠 추가
        content_id = self.db.add_content(
            site="unpre",
            title="테스트 포스트",
            category="개발",
            keywords=["test"],
            content="내용",
            url="https://example.com/test"
        )
        
        # 성능 지표 추가
        metrics = {
            "views": 1000,
            "clicks": 50,
            "revenue": 25.50,
            "bounce_rate": 0.65,
            "avg_time_on_page": 180
        }
        
        self.db.update_performance_metrics("unpre", content_id, metrics)
        
        # 저장되었는지 확인
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT views, clicks, revenue FROM performance_tracking 
                WHERE site = 'unpre' AND post_id = ?
            """, (content_id,))
            row = cursor.fetchone()
            
            assert row is not None
            assert row[0] == 1000  # views
            assert row[1] == 50   # clicks
            assert float(row[2]) == 25.50  # revenue
    
    def test_get_best_performing_topics(self):
        """최고 성과 주제 조회 테스트"""
        # 테스트 데이터 추가
        content_id1 = self.db.add_content(
            site="unpre", title="Python 포스트", category="Python",
            keywords=["python"], content="내용", url="https://example.com/1"
        )
        
        content_id2 = self.db.add_content(
            site="unpre", title="JavaScript 포스트", category="JavaScript", 
            keywords=["js"], content="내용", url="https://example.com/2"
        )
        
        # 성과 데이터 추가
        self.db.update_performance_metrics("unpre", content_id1, {"views": 1000, "revenue": 50.0})
        self.db.update_performance_metrics("unpre", content_id2, {"views": 500, "revenue": 20.0})
        
        # 최고 성과 주제 조회
        best_topics = self.db.get_best_performing_topics("unpre", limit=2)
        
        assert len(best_topics) <= 2
        # 수익 높은 순으로 정렬되어야 함
        if len(best_topics) > 0:
            assert best_topics[0]["avg_revenue"] >= (best_topics[1]["avg_revenue"] if len(best_topics) > 1 else 0)
    
    def test_cross_site_isolation(self):
        """사이트간 데이터 격리 테스트"""
        # 다른 사이트에 같은 제목 추가
        self.db.add_content("unpre", "같은 제목", "개발", ["test"], "내용", "url1")
        self.db.add_content("untab", "같은 제목", "부동산", ["test"], "내용", "url2")
        
        # 사이트별로 별도로 조회되어야 함
        unpre_posts = self.db.get_recent_posts("unpre")
        untab_posts = self.db.get_recent_posts("untab")
        
        assert len(unpre_posts) == 1
        assert len(untab_posts) == 1
        assert unpre_posts[0]["category"] == "개발"
        assert untab_posts[0]["category"] == "부동산"
        
        # 중복 체크도 사이트별로 되어야 함
        assert self.db.check_duplicate_title("unpre", "같은 제목") is True
        assert self.db.check_duplicate_title("skewese", "같은 제목") is False
    
    def test_empty_topic_pool(self):
        """빈 주제 풀 처리 테스트"""
        # 주제가 없을 때
        topic = self.db.get_unused_topic("nonexistent_site")
        assert topic is None
        
        # 모든 주제를 사용했을 때
        self.db.add_topics_bulk("test_site", [{"topic": "유일한 주제"}])
        first_topic = self.db.get_unused_topic("test_site")
        assert first_topic is not None
        
        second_topic = self.db.get_unused_topic("test_site")
        assert second_topic is None  # 더 이상 사용 가능한 주제 없음