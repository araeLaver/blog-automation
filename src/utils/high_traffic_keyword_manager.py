"""
고유입 키워드 매니저 - 예비군, 연말정산 같은 검색량 높은 계절성 키워드 관리
"""

from datetime import datetime, date
from typing import List, Dict, Tuple
import calendar
import random

class HighTrafficKeywordManager:
    def __init__(self):
        """고유입 키워드 데이터 초기화"""
        
        # 월별 계절성 고유입 키워드 (실제 검색량 기준)
        self.monthly_keywords = {
            1: [  # 1월 - 연말정산, 새해 결심
                {'keyword': '연말정산 간소화서비스', 'volume': 500000, 'competition': 'medium'},
                {'keyword': '연말정산 의료비 공제', 'volume': 300000, 'competition': 'high'},
                {'keyword': '연말정산 신용카드', 'volume': 250000, 'competition': 'high'},
                {'keyword': '홈택스 연말정산', 'volume': 400000, 'competition': 'high'},
                {'keyword': '신년 다이어트', 'volume': 150000, 'competition': 'medium'},
                {'keyword': '새해 목표 세우기', 'volume': 80000, 'competition': 'low'},
                {'keyword': '정유년 운세', 'volume': 120000, 'competition': 'medium'},
            ],
            2: [  # 2월 - 설날, 입시
                {'keyword': '설날 차례상 음식', 'volume': 200000, 'competition': 'high'},
                {'keyword': '세뱃돈 용돈 기입장', 'volume': 80000, 'competition': 'low'},
                {'keyword': '대학 정시 지원', 'volume': 180000, 'competition': 'high'},
                {'keyword': '수능 정시 배치표', 'volume': 220000, 'competition': 'high'},
                {'keyword': '밸런타인데이 선물', 'volume': 150000, 'competition': 'high'},
            ],
            3: [  # 3월 - 입학, 이사, 화이트데이
                {'keyword': '대학 신입생 오리엔테이션', 'volume': 100000, 'competition': 'medium'},
                {'keyword': '화이트데이 선물 추천', 'volume': 180000, 'competition': 'high'},
                {'keyword': '이사 체크리스트', 'volume': 250000, 'competition': 'medium'},
                {'keyword': '전세자금대출 조건', 'volume': 300000, 'competition': 'high'},
                {'keyword': '봄 알레르기 관리', 'volume': 90000, 'competition': 'medium'},
            ],
            4: [  # 4월 - 벚꽃, 입학식, 새학기
                {'keyword': '벚꽃 명소 추천', 'volume': 200000, 'competition': 'high'},
                {'keyword': '새학기 준비물', 'volume': 150000, 'competition': 'medium'},
                {'keyword': '4월 여행지 추천', 'volume': 120000, 'competition': 'high'},
                {'keyword': '알바 면접 준비', 'volume': 80000, 'competition': 'medium'},
            ],
            5: [  # 5월 - 어린이날, 어버이날, 가정의달
                {'keyword': '어린이날 선물 추천', 'volume': 180000, 'competition': 'high'},
                {'keyword': '어버이날 선물', 'volume': 220000, 'competition': 'high'},
                {'keyword': '카네이션 키우기', 'volume': 60000, 'competition': 'low'},
                {'keyword': '5월 가족여행', 'volume': 150000, 'competition': 'high'},
                {'keyword': '봄나들이 준비물', 'volume': 100000, 'competition': 'medium'},
            ],
            6: [  # 6월 - 현충일, 메르스 등 계절성 이슈
                {'keyword': '여름휴가 계획', 'volume': 200000, 'competition': 'high'},
                {'keyword': '에어컨 청소 방법', 'volume': 180000, 'competition': 'medium'},
                {'keyword': '모기 퇴치법', 'volume': 150000, 'competition': 'medium'},
                {'keyword': '여름 다이어트', 'volume': 120000, 'competition': 'high'},
                {'keyword': '여름 인턴십 지원', 'volume': 100000, 'competition': 'high'},
            ],
            7: [  # 7월 - 여름휴가, 장마
                {'keyword': '여름휴가 국내여행', 'volume': 300000, 'competition': 'high'},
                {'keyword': '제주도 7월 날씨', 'volume': 180000, 'competition': 'high'},
                {'keyword': '장마철 습도 관리', 'volume': 120000, 'competition': 'medium'},
                {'keyword': '여름 캠핑 준비물', 'volume': 150000, 'competition': 'medium'},
                {'keyword': '물놀이 안전수칙', 'volume': 80000, 'competition': 'low'},
            ],
            8: [  # 8월 - 휴가철 절정, 광복절
                {'keyword': '예비군 훈련 일정', 'volume': 400000, 'competition': 'low'},  # 고유입 키워드
                {'keyword': '예비군 불참 사유서', 'volume': 200000, 'competition': 'low'},
                {'keyword': '예비군 복장 규정', 'volume': 150000, 'competition': 'low'},
                {'keyword': '바캉스 짐싸기', 'volume': 100000, 'competition': 'medium'},
                {'keyword': '여름 음식 추천', 'volume': 180000, 'competition': 'high'},
                {'keyword': '폭염 대비책', 'volume': 120000, 'competition': 'medium'},
            ],
            9: [  # 9월 - 개학, 추석, 가을 시작
                {'keyword': '추석 차례상 준비', 'volume': 350000, 'competition': 'high'},
                {'keyword': '추석 선물 추천', 'volume': 280000, 'competition': 'high'},
                {'keyword': '고속도로 교통상황', 'volume': 200000, 'competition': 'medium'},
                {'keyword': '개학 준비물', 'volume': 150000, 'competition': 'medium'},
                {'keyword': '가을 등산 코스', 'volume': 120000, 'competition': 'medium'},
            ],
            10: [  # 10월 - 가을, 단풍, 수능
                {'keyword': '단풍 구경 명소', 'volume': 250000, 'competition': 'high'},
                {'keyword': '수능 D-30 공부법', 'volume': 180000, 'competition': 'high'},
                {'keyword': '가을 여행지', 'volume': 200000, 'competition': 'high'},
                {'keyword': '독감 예방접종', 'volume': 150000, 'competition': 'medium'},
                {'keyword': '환절기 감기 관리', 'volume': 100000, 'competition': 'medium'},
            ],
            11: [  # 11월 - 수능, 김장
                {'keyword': '수능 응원 메시지', 'volume': 200000, 'competition': 'medium'},
                {'keyword': '수능 도시락 메뉴', 'volume': 120000, 'competition': 'medium'},
                {'keyword': '김장 시기', 'volume': 180000, 'competition': 'medium'},
                {'keyword': '김장 재료 준비', 'volume': 150000, 'competition': 'medium'},
                {'keyword': '블랙프라이데이 할인', 'volume': 100000, 'competition': 'high'},
            ],
            12: [  # 12월 - 연말, 크리스마스, 송년회
                {'keyword': '크리스마스 선물', 'volume': 300000, 'competition': 'high'},
                {'keyword': '연말정산 미리보기', 'volume': 200000, 'competition': 'high'},
                {'keyword': '송년회 게임', 'volume': 150000, 'competition': 'medium'},
                {'keyword': '연말 보너스 세금', 'volume': 120000, 'competition': 'medium'},
                {'keyword': '새해 계획 세우기', 'volume': 100000, 'competition': 'low'},
            ]
        }
        
        # 사이트별 특화 고유입 키워드
        self.site_specialized = {
            'unpre': [  # 개발/IT 특화
                {'keyword': '카카오 개발자 채용', 'volume': 80000, 'competition': 'high', 'category': '개발'},
                {'keyword': 'IT 대기업 연봉', 'volume': 120000, 'competition': 'high', 'category': '개발'},
                {'keyword': '개발자 포트폴리오', 'volume': 150000, 'competition': 'high', 'category': '개발'},
                {'keyword': '코딩테스트 문제집', 'volume': 100000, 'competition': 'medium', 'category': '개발'},
                {'keyword': 'Python 독학', 'volume': 200000, 'competition': 'high', 'category': '개발'},
            ],
            'skewese': [  # 역사/문화 특화  
                {'keyword': '조선왕조실록', 'volume': 60000, 'competition': 'low', 'category': '역사'},
                {'keyword': '한국사 능력검정시험', 'volume': 150000, 'competition': 'medium', 'category': '역사'},
                {'keyword': '고구려 역사', 'volume': 80000, 'competition': 'medium', 'category': '역사'},
                {'keyword': '삼국시대', 'volume': 100000, 'competition': 'medium', 'category': '역사'},
                {'keyword': '조선시대 문화', 'volume': 70000, 'competition': 'low', 'category': '역사'},
            ],
            'tistory': [  # 생활/라이프 특화
                {'keyword': '토익 900점 공부법', 'volume': 200000, 'competition': 'high', 'category': '학습'},
                {'keyword': '영어회화 독학', 'volume': 180000, 'competition': 'high', 'category': '학습'},
                {'keyword': '다이어트 성공후기', 'volume': 150000, 'competition': 'high', 'category': '건강'},
                {'keyword': '홈트레이닝 루틴', 'volume': 120000, 'competition': 'medium', 'category': '건강'},
                {'keyword': '간단한 요리 레시피', 'volume': 250000, 'competition': 'high', 'category': '요리'},
            ]
        }
        
        # 연간 반복 이벤트 (매년 검색량 급증)
        self.annual_events = {
            '예비군': {'peak_months': [8, 9], 'volume': 400000},
            '연말정산': {'peak_months': [1, 2], 'volume': 500000},
            '추석': {'peak_months': [9, 10], 'volume': 350000},
            '수능': {'peak_months': [10, 11], 'volume': 300000},
            '벚꽃': {'peak_months': [4, 5], 'volume': 200000},
            '여름휴가': {'peak_months': [7, 8], 'volume': 300000},
            '크리스마스': {'peak_months': [12, 1], 'volume': 300000},
        }

    def get_current_month_high_traffic_keywords(self, limit: int = 10) -> List[Dict]:
        """현재 월의 고유입 키워드 반환"""
        current_month = datetime.now().month
        month_keywords = self.monthly_keywords.get(current_month, [])
        
        # 검색량 순으로 정렬 후 상위 limit개 반환
        sorted_keywords = sorted(month_keywords, key=lambda x: x['volume'], reverse=True)
        return sorted_keywords[:limit]
    
    def get_next_month_predicted_keywords(self, limit: int = 10) -> List[Dict]:
        """다음 월 예상 고유입 키워드"""
        next_month = datetime.now().month + 1
        if next_month > 12:
            next_month = 1
            
        month_keywords = self.monthly_keywords.get(next_month, [])
        sorted_keywords = sorted(month_keywords, key=lambda x: x['volume'], reverse=True)
        return sorted_keywords[:limit]
    
    def get_site_specialized_keywords(self, site: str, limit: int = 5) -> List[Dict]:
        """사이트별 특화 고유입 키워드"""
        site_keywords = self.site_specialized.get(site, [])
        sorted_keywords = sorted(site_keywords, key=lambda x: x['volume'], reverse=True)
        return sorted_keywords[:limit]
    
    def get_annual_event_keywords(self, current_date: date = None) -> List[Dict]:
        """연간 이벤트 기반 키워드 (현재 시기에 맞는)"""
        if not current_date:
            current_date = date.today()
        
        current_month = current_date.month
        relevant_events = []
        
        for event, data in self.annual_events.items():
            if current_month in data['peak_months']:
                relevant_events.append({
                    'keyword': event,
                    'volume': data['volume'],
                    'competition': 'medium',
                    'category': '이벤트',
                    'peak_period': True
                })
                
        return relevant_events
    
    def generate_high_traffic_topics_for_site(self, site: str, date_target: date = None) -> List[Dict]:
        """사이트별 고유입 주제 생성"""
        if not date_target:
            date_target = date.today()
            
        topics = []
        
        # 1. 월별 계절성 키워드
        month_keywords = self.get_current_month_high_traffic_keywords(5)
        for kw in month_keywords:
            topics.append({
                'topic': self._convert_keyword_to_topic(kw['keyword'], site),
                'keywords': [kw['keyword']],
                'category': self._get_category_for_site(kw['keyword'], site),
                'volume': kw['volume'],
                'source': 'monthly_seasonal'
            })
        
        # 2. 사이트 특화 키워드
        site_keywords = self.get_site_specialized_keywords(site, 3)
        for kw in site_keywords:
            topics.append({
                'topic': self._convert_keyword_to_topic(kw['keyword'], site),
                'keywords': [kw['keyword']],
                'category': kw['category'],
                'volume': kw['volume'],
                'source': 'site_specialized'
            })
            
        # 3. 연간 이벤트 키워드
        event_keywords = self.get_annual_event_keywords(date_target)
        for kw in event_keywords:
            topics.append({
                'topic': self._convert_keyword_to_topic(kw['keyword'], site),
                'keywords': [kw['keyword']],
                'category': kw['category'],
                'volume': kw['volume'],
                'source': 'annual_event'
            })
            
        # 검색량 순으로 정렬
        topics.sort(key=lambda x: x['volume'], reverse=True)
        return topics[:10]  # 상위 10개
        
    def _convert_keyword_to_topic(self, keyword: str, site: str) -> str:
        """키워드를 사이트별 주제로 변환"""
        
        # 사이트별 주제 변환 템플릿
        templates = {
            'unpre': {
                '개발': "{keyword} 완벽 가이드 현직 개발자가 알려주는 실전 노하우",
                '기술': "{keyword} 기술 트렌드 2025년 최신 업데이트",
                'default': "{keyword} 프로그래밍 완벽 마스터 가이드"
            },
            'skewese': {
                '역사': "{keyword}의 숨겨진 이야기 역사 전문가가 들려주는 흥미로운 진실",  
                '문화': "{keyword} 문화 깊이 알아보기 전통과 현대의 만남",
                'default': "{keyword} 역사 문화 완벽 해설"
            },
            'tistory': {
                '학습': "{keyword} 성공 후기 실제 경험담과 노하우 공유",
                '건강': "{keyword} 실전 가이드 전문가가 알려주는 핵심 팁",
                '생활': "{keyword} 완벽 정리 일상에서 바로 써먹는 실용 정보",
                'default': "{keyword} 완벽 가이드 2025년 최신 정보"
            }
        }
        
        site_templates = templates.get(site, templates['tistory'])
        
        # 키워드로 카테고리 유추
        category = self._get_category_for_site(keyword, site)
        template = site_templates.get(category, site_templates['default'])
        
        return template.format(keyword=keyword)
    
    def _get_category_for_site(self, keyword: str, site: str) -> str:
        """키워드로부터 사이트별 카테고리 유추"""
        
        category_keywords = {
            'unpre': {
                '개발': ['개발자', '코딩', '프로그래밍', 'IT', '카카오', 'Python', '포트폴리오'],
                '기술': ['AI', 'ChatGPT', '인공지능', '블록체인', '메타버스', '기술']
            },
            'skewese': {
                '역사': ['조선', '고구려', '삼국', '한국사', '왕조', '역사'],
                '문화': ['문화', '전통', '한국', '민족', '예술']  
            },
            'tistory': {
                '학습': ['토익', '영어', '공부법', '시험', '자격증'],
                '건강': ['다이어트', '운동', '건강', '홈트', '요가'],
                '생활': ['요리', '레시피', '인테리어', '정리', '청소'],
                '이벤트': ['예비군', '연말정산', '추석', '수능', '크리스마스']
            }
        }
        
        site_categories = category_keywords.get(site, category_keywords['tistory'])
        
        for category, keywords_list in site_categories.items():
            if any(kw in keyword for kw in keywords_list):
                return category
                
        return 'default'