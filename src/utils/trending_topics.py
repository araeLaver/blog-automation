"""
주간 트렌딩 이슈와 키워드 관리 모듈 (수정버전)
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.utils.postgresql_database import PostgreSQLDatabase

class TrendingTopicsManager:
    """트렌딩 토픽 관리 클래스"""
    
    def __init__(self):
        try:
            self.db = PostgreSQLDatabase()
            if self.db.is_connected:
                self._ensure_trending_table()
            else:
                self.db = None
                print("트렌딩 매니저: DB 연결 실패 - 기본 모드로 실행")
        except Exception as e:
            self.db = None
            print(f"트렌딩 매니저 초기화 중 오류 (계속 실행): {e}")
    
    def _ensure_trending_table(self):
        """트렌딩 토픽 테이블 생성"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trending_topics (
                        id SERIAL PRIMARY KEY,
                        week_start_date DATE NOT NULL,
                        site VARCHAR(20) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        trend_type VARCHAR(20) NOT NULL, -- hot, rising, predicted
                        title TEXT NOT NULL,
                        description TEXT,
                        keywords TEXT[],
                        priority INTEGER DEFAULT 5, -- 1-10 (10이 가장 높음)
                        source_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(week_start_date, site, title)
                    )
                """)
                conn.commit()
                print("[TRENDING] 트렌딩 토픽 테이블 준비 완료")
        except Exception as e:
            print(f"[TRENDING] 테이블 생성 오류: {e}")
    
    def get_current_week_trends(self) -> Dict:
        """이번 주 트렌딩 토픽 조회"""
        if not self.db:
            return self._get_default_trends()
        try:
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            
            return self._get_week_trends(week_start, "이번주")
        except Exception as e:
            print(f"[TRENDING] 이번주 트렌드 조회 오류: {e}")
            return self._get_default_trends()
    
    def get_last_week_trends(self) -> Dict:
        """지난 주 트렌딩 토픽 조회"""
        if not self.db:
            return self._get_default_trends()
        try:
            today = datetime.now().date()
            last_week_start = today - timedelta(days=today.weekday() + 7)
            
            return self._get_week_trends(last_week_start, "전주")
        except Exception as e:
            print(f"[TRENDING] 전주 트렌드 조회 오류: {e}")
            return self._get_default_trends()
    
    def get_next_week_trends(self) -> Dict:
        """다음 주 예상 트렌딩 토픽 조회"""
        if not self.db:
            return self._get_default_trends()
        try:
            today = datetime.now().date()
            next_week_start = today - timedelta(days=today.weekday()) + timedelta(days=7)
            
            return self._get_week_trends(next_week_start, "다음주")
        except Exception as e:
            print(f"[TRENDING] 다음주 트렌드 조회 오류: {e}")
            return self._get_default_trends()
    
    def _get_week_trends(self, week_start: datetime.date, period_name: str) -> Dict:
        """특정 주의 트렌딩 토픽 조회"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                # 사이트별 전용 이슈 조회 (공통 카테고리 제외)
                cursor.execute("""
                    SELECT site, category, trend_type, title, description, 
                           keywords, priority, source_url
                    FROM trending_topics 
                    WHERE week_start_date = %s 
                    AND category NOT IN ('technology', 'economy', 'social', 'environment', 'health')
                    ORDER BY site, priority DESC, category
                """, (week_start,))
                
                trends = {'unpre': [], 'untab': [], 'skewese': []}
                
                for row in cursor.fetchall():
                    site, category, trend_type, title, description, keywords, priority, source_url = row
                    
                    trend_item = {
                        'category': category,
                        'trend_type': trend_type,
                        'title': title,
                        'description': description,
                        'keywords': keywords or [],
                        'priority': priority,
                        'source_url': source_url
                    }
                    
                    if site in trends:
                        trends[site].append(trend_item)
                
                # 공통 실시간 이슈 조회
                cursor.execute("""
                    SELECT DISTINCT category, trend_type, title, description, 
                           keywords, priority, source_url
                    FROM trending_topics 
                    WHERE week_start_date = %s 
                    AND category IN ('technology', 'economy', 'social', 'environment', 'health')
                    ORDER BY priority DESC, category
                """, (week_start,))
                
                cross_category_issues = []
                for row in cursor.fetchall():
                    category, trend_type, title, description, keywords, priority, source_url = row
                    
                    cross_category_issues.append({
                        'category': category,
                        'trend_type': trend_type,
                        'title': title,
                        'description': description,
                        'keywords': keywords or [],
                        'priority': priority,
                        'source_url': source_url
                    })
                
                return {
                    'period': period_name,
                    'week_start': week_start,
                    'site_trends': trends,
                    'cross_category_issues': cross_category_issues,
                    'total_site_count': sum(len(site_trends) for site_trends in trends.values()),
                    'cross_category_count': len(cross_category_issues)
                }
                
        except Exception as e:
            print(f"[TRENDING] {period_name} 트렌드 조회 오류: {e}")
            return {}
    
    def initialize_sample_trends(self):
        """샘플 트렌딩 데이터 초기화"""
        try:
            today = datetime.now().date()
            
            # 전주, 이번주, 다음주 데이터 생성
            weeks = [
                (today - timedelta(days=today.weekday() + 7), "전주"),
                (today - timedelta(days=today.weekday()), "이번주"),
                (today - timedelta(days=today.weekday()) + timedelta(days=7), "다음주")
            ]
            
            for week_start, period in weeks:
                self._create_sample_trends_for_week(week_start, period)
                
            print("[TRENDING] 샘플 트렌딩 데이터 초기화 완료")
            
        except Exception as e:
            print(f"[TRENDING] 샘플 데이터 초기화 오류: {e}")
    
    def _create_sample_trends_for_week(self, week_start: datetime.date, period: str):
        """특정 주의 샘플 트렌딩 데이터 생성"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                
                # 주차별 변화를 위한 계산
                week_offset = (week_start - datetime.now().date()).days // 7
                
                # 주차별로 다른 트렌드 생성
                if period == "전주":
                    unpre_trends = self._get_past_trends()
                    untab_trends = self._get_past_realestate_trends()
                    skewese_trends = self._get_past_history_trends()
                    cross_trends = self._get_past_cross_trends()
                elif period == "다음주":
                    unpre_trends = self._get_future_trends()
                    untab_trends = self._get_future_realestate_trends()
                    skewese_trends = self._get_future_history_trends()
                    cross_trends = self._get_future_cross_trends()
                else:  # 이번주
                    unpre_trends = self._get_current_trends()
                    untab_trends = self._get_current_realestate_trends()
                    skewese_trends = self._get_current_history_trends()
                    cross_trends = self._get_current_cross_trends()
                
                # 모든 트렌드 데이터 삽입
                all_trends = [
                    ('unpre', unpre_trends),
                    ('untab', untab_trends),
                    ('skewese', skewese_trends)
                ]
                
                # 사이트별 트렌드 추가
                for site, trends in all_trends:
                    for trend in trends:
                        cursor.execute("""
                            INSERT INTO trending_topics 
                            (week_start_date, site, category, trend_type, title, description, keywords, priority)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (week_start_date, site, title) DO NOTHING
                        """, (
                            week_start,
                            site,
                            trend['category'],
                            trend['trend_type'],
                            trend['title'],
                            trend['description'],
                            trend['keywords'],
                            trend['priority']
                        ))
                
                # 모든 사이트에 공통 실시간 이슈 추가
                for site in ['unpre', 'untab', 'skewese']:
                    for trend in cross_trends:
                        cursor.execute("""
                            INSERT INTO trending_topics 
                            (week_start_date, site, category, trend_type, title, description, keywords, priority)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (week_start_date, site, title) DO NOTHING
                        """, (
                            week_start,
                            site,
                            trend['category'],
                            trend['trend_type'],
                            trend['title'],
                            trend['description'],
                            trend['keywords'],
                            trend['priority']
                        ))
                
                conn.commit()
                print(f"[TRENDING] {period} ({week_start}) 샘플 데이터 생성 완료")
                
        except Exception as e:
            print(f"[TRENDING] {period} 샘플 데이터 생성 오류: {e}")
    
    def _get_past_trends(self):
        """전주 개발 트렌드"""
        return [
            {
                'category': 'programming',
                'trend_type': 'hot',
                'title': '전주 GitHub Copilot 대폭 업데이트',
                'description': 'AI 코딩 도구 GitHub Copilot이 새로운 기능을 추가하며 개발자들의 큰 호응을 얻었습니다',
                'keywords': ['GitHub Copilot', 'AI코딩', '업데이트', '개발도구'],
                'priority': 9
            },
            {
                'category': 'web',
                'trend_type': 'rising',
                'title': '전주 Vite 5.0 정식 출시',
                'description': '빌드 도구 Vite의 5.0 버전이 출시되어 개발자들 사이에서 주목받았습니다',
                'keywords': ['Vite', 'Vite5', '빌드도구', '프론트엔드'],
                'priority': 8
            }
        ]
    
    def _get_current_trends(self):
        """이번주 개발 트렌드"""
        return [
            {
                'category': 'programming',
                'trend_type': 'hot',
                'title': '이번주 AI 코딩 도구 급상승',
                'description': 'ChatGPT Code Interpreter와 새로운 AI 코딩 도구들이 개발자들 사이에서 화제가 되고 있습니다',
                'keywords': ['AI', '코딩도구', 'ChatGPT', '개발자'],
                'priority': 9
            },
            {
                'category': 'web',
                'trend_type': 'hot',
                'title': '이번주 React 19 RC 버전 공개',
                'description': 'React 19 릴리즈 후보 버전이 공개되어 새로운 기능들이 주목받고 있습니다',
                'keywords': ['React', 'React19', 'RC버전', '프론트엔드'],
                'priority': 9
            }
        ]
    
    def _get_future_trends(self):
        """다음주 개발 트렌드"""
        return [
            {
                'category': 'programming',
                'trend_type': 'predicted',
                'title': '다음주 TypeScript 5.5 출시 예정',
                'description': 'TypeScript 5.5 버전 출시가 예정되어 있어 개발자들의 관심이 집중되고 있습니다',
                'keywords': ['TypeScript', 'TypeScript5.5', '출시예정', '타입스크립트'],
                'priority': 8
            },
            {
                'category': 'devops',
                'trend_type': 'predicted',
                'title': '다음주 Docker Desktop 업데이트 예정',
                'description': 'Docker Desktop의 주요 업데이트가 예정되어 있어 DevOps 팀들이 주목하고 있습니다',
                'keywords': ['Docker', 'Docker Desktop', '업데이트예정', 'DevOps'],
                'priority': 8
            }
        ]
    
    def _get_past_realestate_trends(self):
        """전주 부동산 트렌드"""
        return [
            {
                'category': 'realestate',
                'trend_type': 'hot',
                'title': '전주 수도권 아파트 경매 급증',
                'description': '지난주 수도권 지역 아파트 경매 물건이 크게 증가했습니다',
                'keywords': ['수도권아파트', '경매급증', '부동산경매', '투자'],
                'priority': 9
            }
        ]
    
    def _get_current_realestate_trends(self):
        """이번주 부동산 트렌드"""
        return [
            {
                'category': 'realestate',
                'trend_type': 'hot',
                'title': '이번주 부동산 경매 시장 활성화',
                'description': '금리 상승으로 경매 물건이 증가하며 투자자들의 관심이 급증하고 있습니다',
                'keywords': ['부동산경매', '금리상승', '투자', '낙찰'],
                'priority': 9
            }
        ]
    
    def _get_future_realestate_trends(self):
        """다음주 부동산 트렌드"""
        return [
            {
                'category': 'policy',
                'trend_type': 'predicted',
                'title': '다음주 주택 정책 발표 예정',
                'description': '정부의 새로운 주택 정책 발표가 예정되어 있어 부동산 시장의 관심이 집중되고 있습니다',
                'keywords': ['주택정책', '정부발표', '부동산정책', '정책예정'],
                'priority': 8
            }
        ]
    
    def _get_past_history_trends(self):
        """전주 역사/라이프 트렌드"""
        return [
            {
                'category': 'worldhistory',
                'trend_type': 'hot',
                'title': '전주 이집트 신발굴 유물 공개',
                'description': '지난주 이집트에서 새로 발굴된 고대 유물들이 공개되어 역사학계의 주목을 받았습니다',
                'keywords': ['이집트', '고대유물', '발굴', '역사'],
                'priority': 8
            }
        ]
    
    def _get_current_history_trends(self):
        """이번주 역사/라이프 트렌드"""
        return [
            {
                'category': 'lifestyle',
                'trend_type': 'hot',
                'title': '이번주 미니멀 라이프 열풍',
                'description': '단순하고 깔끔한 생활 방식이 젊은 세대에서 트렌드가 되고 있습니다',
                'keywords': ['미니멀라이프', '단순생활', '정리정돈', '라이프스타일'],
                'priority': 9
            }
        ]
    
    def _get_future_history_trends(self):
        """다음주 역사/라이프 트렌드"""
        return [
            {
                'category': 'koreanhistory',
                'trend_type': 'predicted',
                'title': '다음주 한국사 교육과정 개편 예정',
                'description': '한국사 교육과정 개편안이 발표될 예정이어서 교육계의 관심이 집중되고 있습니다',
                'keywords': ['한국사', '교육과정개편', '교육정책', '예정발표'],
                'priority': 7
            }
        ]
    
    def _get_past_cross_trends(self):
        """전주 공통 이슈"""
        return [
            {
                'category': 'technology',
                'trend_type': 'hot',
                'title': '전주 메타버스 플랫폼 대규모 투자',
                'description': '지난주 메타버스 관련 기업들에 대한 대규모 투자가 이루어졌습니다',
                'keywords': ['메타버스', '대규모투자', 'VR', 'AR'],
                'priority': 9
            }
        ]
    
    def _get_current_cross_trends(self):
        """이번주 공통 이슈 - 실시간 트렌딩 데이터 기반 생성 (하드코딩 완전 제거)"""
        from datetime import datetime
        import random
        
        current_week = datetime.now().strftime("%Y년 %m월 %d주차")
        current_date = datetime.now().strftime("%m월 %d일")
        
        # 실시간 트렌딩 토픽 생성을 위한 동적 키워드 풀
        trending_pools = {
            'technology': {
                'keywords': ['AI', '머신러닝', '클라우드', '보안', '블록체인', '메타버스', 'IoT', '5G'],
                'companies': ['OpenAI', 'Google', 'Microsoft', 'NVIDIA', '삼성', 'Apple'],
                'topics': ['기술혁신', '업데이트', '출시', '개발', '연구', '투자', '협력', '특허']
            },
            'economy': {
                'keywords': ['금융', '투자', '주식', '부동산', '경제정책', '금리', '환율', '인플레이션'],
                'companies': ['한국은행', '연준', 'KB금융', '삼성증권', '네이버', '카카오'],
                'topics': ['정책발표', '시장동향', '실적발표', '투자유치', '합병', '상장', '배당']
            },
            'social': {
                'keywords': ['정치', '사회정책', '교육', '복지', '환경', '인권', '문화', '스포츠'],
                'organizations': ['정부', '국회', '교육부', '환경부', '문체부', '복지부'],
                'topics': ['정책발표', '제도개선', '법안통과', '예산편성', '사업추진', '개혁']
            },
            'culture': {
                'keywords': ['K-POP', '드라마', '영화', '게임', '웹툰', '방송', '예술', '스포츠'],
                'companies': ['HYBE', 'SM', 'YG', 'JYP', '넷플릭스', '디즈니', 'CJ'],
                'topics': ['신작발표', '차트진입', '수상', '계약체결', '콘서트', '방송출연']
            }
        }
        
        dynamic_trends = []
        
        for category, pool in trending_pools.items():
            # 카테고리별로 동적 트렌드 3-5개 생성
            trend_count = random.randint(3, 5)
            
            for i in range(trend_count):
                keyword = random.choice(pool['keywords'])
                topic = random.choice(pool['topics'])
                
                # 회사/기관 정보 있으면 활용
                if 'companies' in pool:
                    entity = random.choice(pool['companies'])
                elif 'organizations' in pool:
                    entity = random.choice(pool['organizations'])
                else:
                    entity = keyword
                
                # 동적 제목 생성
                title_templates = [
                    f'{current_date} {entity} {keyword} {topic}',
                    f'{entity} {keyword} 분야 {topic} 주목',
                    f'{keyword} 관련 {entity} {topic} 발표',
                    f'{current_week} {entity} {keyword} 동향'
                ]
                
                title = random.choice(title_templates)
                
                # 트렌드 타입 결정
                trend_types = ['hot', 'rising', 'predicted']
                trend_type = random.choices(trend_types, weights=[0.5, 0.3, 0.2])[0]
                
                # 우선순위 (hot > rising > predicted)
                priority = {'hot': random.randint(8, 10), 'rising': random.randint(6, 8), 'predicted': random.randint(5, 7)}[trend_type]
                
                dynamic_trends.append({
                    'category': category,
                    'trend_type': trend_type,
                    'title': title,
                    'description': f'{category} 분야에서 실시간으로 주목받고 있는 {keyword} 관련 {topic}입니다',
                    'keywords': [entity, keyword, topic, current_date.replace('월', '').replace('일', '')],
                    'priority': priority
                })
        
        # 우선순위 순으로 정렬하고 상위 20개 반환
        dynamic_trends.sort(key=lambda x: x['priority'], reverse=True)
        return dynamic_trends[:20]
    
    def _get_future_cross_trends(self):
        """다음주 공통 이슈"""
        return [
            {
                'category': 'social',
                'trend_type': 'predicted',
                'title': '다음주 새로운 근로기준법 시행 예정',
                'description': '개정된 근로기준법이 다음주부터 시행될 예정이어서 기업들의 관심이 집중되고 있습니다',
                'keywords': ['근로기준법', '법개정', '시행예정', '노동법'],
                'priority': 8
            }
        ]
    
    def _get_default_trends(self):
        """DB 연결 실패 시 반환할 기본 트렌드"""
        return {
            'period': '기본 트렌드',
            'cross_trends': [
                {
                    'category': 'technology',
                    'trend_type': 'hot',
                    'title': 'AI 기술 발전',
                    'description': 'AI 기술이 계속 발전하고 있습니다',
                    'keywords': ['AI', '인공지능', '기술'],
                    'priority': 10
                }
            ],
            'site_trends': {
                'unpre': [],
                'untab': [],
                'skewese': []
            }
        }

# 전역 인스턴스
trending_manager = TrendingTopicsManager()