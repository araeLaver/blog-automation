"""
일주일치 자동 발행 스케줄 관리 모듈
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.web_dashboard_pg import get_database

class ScheduleManager:
    """발행 스케줄 관리 클래스"""
    
    def __init__(self):
        self.db = get_database()
        self._ensure_schedule_table()
        self._auto_initialize_schedules()
    
    def _ensure_schedule_table(self):
        """스케줄 테이블 생성 (없을 경우)"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS publishing_schedule (
                        id SERIAL PRIMARY KEY,
                        week_start_date DATE NOT NULL,
                        day_of_week INTEGER NOT NULL, -- 0=월요일, 6=일요일
                        site VARCHAR(20) NOT NULL,
                        topic_category VARCHAR(50) NOT NULL,
                        specific_topic TEXT NOT NULL,
                        keywords TEXT[], -- 키워드 배열
                        target_length VARCHAR(20) DEFAULT 'medium',
                        status VARCHAR(20) DEFAULT 'planned', -- planned, generated, published, failed
                        generated_content_id INTEGER,
                        published_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(week_start_date, day_of_week, site)
                    )
                """)
                conn.commit()
                print("[SCHEDULE] 발행 스케줄 테이블 준비 완료")
        except Exception as e:
            print(f"[SCHEDULE] 테이블 생성 오류: {e}")
    
    def _auto_initialize_schedules(self):
        """자동으로 이번 주, 다음 주 스케줄 생성"""
        try:
            today = datetime.now().date()
            
            # 이번 주 월요일 계산 (오늘이 포함된 주)
            current_week_start = today - timedelta(days=today.weekday())
            
            # 다음 주 월요일 계산
            next_week_start = current_week_start + timedelta(days=7)
            
            # 이번 주 스케줄 생성 (오늘 포함)
            if not self._week_schedule_exists(current_week_start):
                print(f"[AUTO_SCHEDULE] {current_week_start} 주 (이번주) 자동 스케줄 생성")
                self.create_weekly_schedule(current_week_start)
            
            # 다음 주 스케줄 생성
            if not self._week_schedule_exists(next_week_start):
                print(f"[AUTO_SCHEDULE] {next_week_start} 주 (다음주) 자동 스케줄 생성")
                self.create_weekly_schedule(next_week_start)
                
        except Exception as e:
            print(f"[AUTO_SCHEDULE] 자동 스케줄 초기화 오류: {e}")
    
    def _week_schedule_exists(self, week_start: datetime.date) -> bool:
        """해당 주에 스케줄이 존재하는지 확인"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM publishing_schedule 
                    WHERE week_start_date = %s
                """, (week_start,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"[SCHEDULE] 스케줄 존재 확인 오류: {e}")
            return False
    
    def create_weekly_schedule(self, start_date: datetime = None) -> bool:
        """일주일치 발행 스케줄 생성"""
        try:
            if start_date is None:
                # 다음 월요일부터 시작
                today = datetime.now().date()
                days_ahead = 0 - today.weekday()  # 0 = 월요일
                if days_ahead <= 0:  # 오늘이 월요일이거나 지났으면 다음 주
                    days_ahead += 7
                start_date = today + timedelta(days=days_ahead)
            
            # 3개 사이트 × 7일 = 21개 발행 계획
            sites = ['unpre', 'untab', 'skewese']
            
            # 주제 카테고리와 세부 주제들
            topic_plans = self._generate_topic_plans()
            
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                for day in range(7):  # 월요일(0) ~ 일요일(6)
                    current_date = start_date + timedelta(days=day)
                    
                    for site_idx, site in enumerate(sites):
                        # 각 사이트별로 다른 주제 할당
                        site_topics = self._get_site_topic_plans(site)
                        topic_idx = (day * 3 + site_idx) % len(site_topics)
                        topic_plan = site_topics[topic_idx]
                        
                        # 기존 계획 체크
                        cursor.execute("""
                            SELECT id FROM publishing_schedule 
                            WHERE week_start_date = %s AND day_of_week = %s AND site = %s
                        """, (start_date, day, site))
                        
                        if cursor.fetchone():
                            continue  # 이미 계획 있음
                        
                        # 중복 컨텐츠 검사
                        if self.check_duplicate_content(site, topic_plan['topic'], topic_plan['keywords']):
                            print(f"[SCHEDULE] {site} 중복 주제 제외: {topic_plan['topic']}")
                            # 다른 주제로 대체
                            for alt_idx in range(len(site_topics)):
                                alt_topic = site_topics[alt_idx]
                                if not self.check_duplicate_content(site, alt_topic['topic'], alt_topic['keywords']):
                                    topic_plan = alt_topic
                                    print(f"[SCHEDULE] {site} 대체 주제 선택: {topic_plan['topic']}")
                                    break
                        
                        # 새 계획 추가
                        cursor.execute("""
                            INSERT INTO publishing_schedule 
                            (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            start_date,
                            day,
                            site,
                            topic_plan['category'],
                            topic_plan['topic'],
                            topic_plan['keywords'],
                            topic_plan['length']
                        ))
                
                conn.commit()
                print(f"[SCHEDULE] {start_date} 주 발행 스케줄 생성 완료")
                return True
                
        except Exception as e:
            print(f"[SCHEDULE] 스케줄 생성 오류: {e}")
            return False
    
    def _get_site_topic_plans(self, site: str) -> List[Dict]:
        """사이트별 주제 계획 생성"""
        if site == 'unpre':
            # unpre.co.kr - 개발, IT, 개발 자격증 정보
            return [
                {
                    'category': 'programming',
                    'topic': 'Python 기초 문법과 데이터 타입 완벽 정리',
                    'keywords': ['python', '기초', '문법', '데이터타입'],
                    'length': 'medium'
                },
                {
                    'category': 'programming', 
                    'topic': 'JavaScript ES6+ 새로운 기능과 활용법',
                    'keywords': ['javascript', 'es6', '모던자바스크립트'],
                    'length': 'long'
                },
                {
                    'category': 'web',
                    'topic': 'React vs Vue.js 프레임워크 비교 분석',
                    'keywords': ['react', 'vuejs', '프레임워크'],
                    'length': 'long'
                },
                {
                    'category': 'programming',
                    'topic': '정보처리기사 자격증 취득 가이드',
                    'keywords': ['정보처리기사', '자격증', 'IT자격증'],
                    'length': 'long'
                },
                {
                    'category': 'programming',
                    'topic': 'AWS 클라우드 자격증 (SAA) 합격 후기',
                    'keywords': ['AWS', 'SAA', '클라우드자격증'],
                    'length': 'medium'
                },
                {
                    'category': 'programming',
                    'topic': 'Git 워크플로우와 협업 방법론',
                    'keywords': ['git', '협업', '버전관리'],
                    'length': 'medium'
                },
                {
                    'category': 'programming',
                    'topic': 'Docker와 Kubernetes 컨테이너 기술',
                    'keywords': ['docker', 'kubernetes', '컨테이너'],
                    'length': 'long'
                }
            ]
        elif site == 'untab':
            # untab.co.kr - 부동산, 정책, 주간 경매, 기획재정부 정보
            return [
                {
                    'category': 'realestate',
                    'topic': '부동산 경매 입찰 전 체크포인트 완전정리',
                    'keywords': ['부동산경매', '입찰', '체크포인트'],
                    'length': 'long'
                },
                {
                    'category': 'realestate',
                    'topic': '이주의 주목할만한 경매 물건 소개',
                    'keywords': ['경매물건', '부동산', '투자정보'],
                    'length': 'medium'
                },
                {
                    'category': 'policy',
                    'topic': '2025년 부동산 정책 변화와 시장 전망',
                    'keywords': ['부동산정책', '2025년', '시장전망'],
                    'length': 'long'
                },
                {
                    'category': 'policy',
                    'topic': '기획재정부 발표 주요 경제정책 분석',
                    'keywords': ['기획재정부', '경제정책', '정책분석'],
                    'length': 'medium'
                },
                {
                    'category': 'realestate',
                    'topic': '공매와 경매의 차이점과 투자 전략',
                    'keywords': ['공매', '경매', '투자전략'],
                    'length': 'medium'
                },
                {
                    'category': 'realestate',
                    'topic': '부동산 경매 권리분석 실무 가이드',
                    'keywords': ['권리분석', '부동산경매', '실무'],
                    'length': 'long'
                },
                {
                    'category': 'policy',
                    'topic': '주택공급 확대 정책과 투자 기회',
                    'keywords': ['주택공급', '정책', '투자기회'],
                    'length': 'medium'
                }
            ]
        elif site == 'skewese':
            # skewese.com - 역사(세계사), 라이프, 한국사
            return [
                {
                    'category': 'worldhistory',
                    'topic': '고대 이집트 문명의 신비와 피라미드의 비밀',
                    'keywords': ['고대이집트', '피라미드', '문명'],
                    'length': 'long'
                },
                {
                    'category': 'worldhistory',
                    'topic': '로마 제국의 흥망성쇠와 역사적 교훈',
                    'keywords': ['로마제국', '흥망성쇠', '역사'],
                    'length': 'long'
                },
                {
                    'category': 'koreanhistory',
                    'topic': '조선왕조 500년 역사의 주요 사건들',
                    'keywords': ['조선왕조', '한국사', '역사'],
                    'length': 'long'
                },
                {
                    'category': 'koreanhistory',
                    'topic': '일제강점기 독립운동가들의 숨겨진 이야기',
                    'keywords': ['일제강점기', '독립운동', '한국사'],
                    'length': 'medium'
                },
                {
                    'category': 'lifestyle',
                    'topic': '건강한 생활습관으로 면역력 높이는 방법',
                    'keywords': ['건강', '생활습관', '면역력'],
                    'length': 'medium'
                },
                {
                    'category': 'lifestyle',
                    'topic': '미니멀 라이프로 여유로운 삶 만들기',
                    'keywords': ['미니멀라이프', '라이프스타일', '여유'],
                    'length': 'medium'
                },
                {
                    'category': 'worldhistory',
                    'topic': '중세 유럽의 기사문화와 십자군 전쟁',
                    'keywords': ['중세유럽', '기사문화', '십자군'],
                    'length': 'long'
                }
            ]
        else:
            # 기본 개발 주제 (fallback)
            return [
                {
                    'category': 'programming',
                    'topic': 'Python 기초 프로그래밍',
                    'keywords': ['python', '프로그래밍'],
                    'length': 'medium'
                }
            ]

    def _generate_topic_plans(self) -> List[Dict]:
        """사이트별 다양한 주제 계획 생성"""
        all_topics = []
        
        # 각 사이트별 주제 풀 생성
        unpre_topics = self._get_site_topic_plans('unpre')
        untab_topics = self._get_site_topic_plans('untab')
        skewese_topics = self._get_site_topic_plans('skewese')
        
        # 21개 항목을 사이트별로 순환 배치
        for i in range(21):
            if i % 3 == 0:  # unpre
                topic_idx = (i // 3) % len(unpre_topics)
                all_topics.append(unpre_topics[topic_idx])
            elif i % 3 == 1:  # untab
                topic_idx = (i // 3) % len(untab_topics)
                all_topics.append(untab_topics[topic_idx])
            else:  # skewese
                topic_idx = (i // 3) % len(skewese_topics)
                all_topics.append(skewese_topics[topic_idx])
        
        return all_topics
    
    def get_weekly_schedule(self, start_date: datetime = None) -> Dict:
        """일주일치 스케줄 조회"""
        try:
            if start_date is None:
                # 이번 주 월요일
                today = datetime.now().date()
                days_ahead = 0 - today.weekday()
                start_date = today + timedelta(days=days_ahead)
            
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT day_of_week, site, topic_category, specific_topic, 
                           keywords, target_length, status, published_url
                    FROM publishing_schedule 
                    WHERE week_start_date = %s
                    ORDER BY day_of_week, site
                """, (start_date,))
                
                schedule = {}
                day_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
                
                for day in range(7):
                    schedule[day] = {
                        'day_name': day_names[day],
                        'date': start_date + timedelta(days=day),
                        'sites': {}
                    }
                
                for row in cursor.fetchall():
                    day_of_week, site, category, topic, keywords, length, status, url = row
                    
                    schedule[day_of_week]['sites'][site] = {
                        'category': category,
                        'topic': topic,
                        'keywords': keywords,
                        'length': length,
                        'status': status,
                        'url': url
                    }
                
                return {
                    'week_start': start_date,
                    'schedule': schedule
                }
                
        except Exception as e:
            print(f"[SCHEDULE] 스케줄 조회 오류: {e}")
            return {}
    
    def check_duplicate_content(self, site: str, topic: str, keywords: List[str]) -> bool:
        """발행된 컨텐츠와 중복 여부 확인"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                # 기존 발행된 컨텐츠에서 유사한 주제 검색
                cursor.execute("""
                    SELECT specific_topic, keywords FROM publishing_schedule 
                    WHERE site = %s AND status = 'published'
                """, (site,))
                
                published_content = cursor.fetchall()
                
                for pub_topic, pub_keywords in published_content:
                    # 주제 유사도 검사 (간단한 키워드 매칭)
                    if self._is_similar_content(topic, keywords, pub_topic, pub_keywords):
                        print(f"[DUPLICATE] {site} 중복 컨텐츠 발견: {topic} vs {pub_topic}")
                        return True
                
                return False
                
        except Exception as e:
            print(f"[DUPLICATE] 중복 검사 오류: {e}")
            return False
    
    def _is_similar_content(self, topic1: str, keywords1: List[str], 
                           topic2: str, keywords2: List[str]) -> bool:
        """두 컨텐츠의 유사도 검사"""
        try:
            # 키워드 교집합 확인 (50% 이상 겹치면 중복으로 판단)
            set1 = set([kw.lower().strip() for kw in keywords1] if keywords1 else [])
            set2 = set([kw.lower().strip() for kw in keywords2] if keywords2 else [])
            
            if len(set1) == 0 or len(set2) == 0:
                return False
                
            intersection = set1.intersection(set2)
            similarity = len(intersection) / min(len(set1), len(set2))
            
            return similarity >= 0.5
            
        except Exception as e:
            print(f"[SIMILARITY] 유사도 검사 오류: {e}")
            return False

    def update_schedule_status(self, week_start: datetime, day: int, site: str, 
                              status: str, content_id: int = None, url: str = None) -> bool:
        """스케줄 상태 업데이트"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                update_fields = ["status = %s", "updated_at = CURRENT_TIMESTAMP"]
                params = [status]
                
                if content_id:
                    update_fields.append("generated_content_id = %s")
                    params.append(content_id)
                
                if url:
                    update_fields.append("published_url = %s")
                    params.append(url)
                
                params.extend([week_start, day, site])
                
                cursor.execute(f"""
                    UPDATE publishing_schedule 
                    SET {', '.join(update_fields)}
                    WHERE week_start_date = %s AND day_of_week = %s AND site = %s
                """, params)
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"[SCHEDULE] 상태 업데이트 오류: {e}")
            return False

# 전역 인스턴스
schedule_manager = ScheduleManager()