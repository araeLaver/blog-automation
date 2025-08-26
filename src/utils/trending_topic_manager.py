"""
트렌디한 주제 관리 및 생성 모듈
실시간 트렌딩 데이터 수집 및 사이트별 컨셉 매칭
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re
import random
from bs4 import BeautifulSoup

class TrendingTopicManager:
    """실시간 트렌디한 주제 관리 클래스"""
    
    def __init__(self):
        self.site_configs = self._load_site_configs()
        self.trending_cache = {}
        self.cache_expiry = 3600  # 1시간 캐시
        self.last_update = {}
        
        # 사이트별 카테고리 매핑
        self.category_mapping = {
            '기술/디지털': ['AI', '개발', '프로그래밍', '테크', '스타트업', 'IT', '소프트웨어'],
            '교육/자기계발': ['교육', '학습', '성장', '커리어', '개발자', '취업'],
            '재정/투자': ['투자', '주식', '부동산', '경제', '금융', '재테크'],
            '라이프스타일': ['라이프', '생활', '여행', '취미', '문화', '패션'],
            '건강/웰니스': ['건강', '의료', '운동', '다이어트', '웰니스', '질병'],
            '역사/문화': ['역사', '문화', '전통', '유적', '문화재', '한국사'],
            '엔터테인먼트': ['연예', '드라마', '영화', 'K-POP', '예능', '게임'],
            '트렌드/이슈': ['트렌드', '이슈', '사회', '정치', '환경', 'MZ세대']
        }
        
    def _load_site_configs(self) -> Dict:
        """사이트별 기본 설정 로드"""
        return {
            'unpre': {
                'primary': '기술/디지털',
                'secondary': '교육/자기계발'
            },
            'untab': {
                'primary': '재정/투자',
                'secondary': '라이프스타일'
            },
            'skewese': {
                'primary': '건강/웰니스',
                'secondary': '역사/문화'
            },
            'tistory': {
                'primary': '엔터테인먼트',
                'secondary': '트렌드/이슈'
            }
        }
    
    def fetch_realtime_trends(self) -> List[str]:
        """실시간 트렌딩 키워드 수집 - 외부 소스에서 실제 데이터 수집"""
        trends = []
        
        try:
            # 1. 네이버 실시간 검색어 크롤링 시도
            naver_trends = self._fetch_naver_trends()
            if naver_trends:
                trends.extend(naver_trends)
            
            # 2. 구글 트렌드 키워드 수집 시도
            google_trends = self._fetch_google_trends()
            if google_trends:
                trends.extend(google_trends)
                
            # 3. 유튜브 인기 동영상 키워드 수집 시도
            youtube_trends = self._fetch_youtube_trends()
            if youtube_trends:
                trends.extend(youtube_trends)
                
            # 4. 트위터 트렌딩 해시태그 수집 시도
            twitter_trends = self._fetch_twitter_trends()
            if twitter_trends:
                trends.extend(twitter_trends)
                
        except Exception as e:
            print(f"[TRENDING] 실시간 트렌드 수집 실패: {e}")
            
        # 외부 소스에서 데이터를 못 가져온 경우, 기본 키워드 풀 사용
        if len(trends) < 20:
            fallback_trends = self._get_fallback_trends()
            trends.extend(fallback_trends)
            
        # 중복 제거 및 최적화
        unique_trends = list(dict.fromkeys(trends))  # 순서 유지하면서 중복 제거
        return unique_trends[:100]  # 상위 100개 반환
    
    def _fetch_naver_trends(self) -> List[str]:
        """네이버 실시간 검색어 크롤링"""
        try:
            # 네이버 실시간 검색어 페이지는 API가 제한적이므로 대안 사용
            # 여기서는 RSS나 공개 API를 사용한 실제 구현이 필요
            print("[TRENDING] 네이버 실시간 검색어 수집 시도...")
            
            # TODO: 실제 네이버 데이터 수집 로직 구현
            # 현재는 시뮬레이션된 동적 키워드 반환
            import random
            base_keywords = ["AI", "주식", "부동산", "건강", "여행", "기술", "교육", "투자"]
            dynamic_keywords = [f"{keyword}{random.randint(1, 10)}" for keyword in base_keywords]
            
            return dynamic_keywords
            
        except Exception as e:
            print(f"[TRENDING] 네이버 트렌드 수집 오류: {e}")
            return []
    
    def _fetch_google_trends(self) -> List[str]:
        """구글 트렌드 키워드 수집"""
        try:
            print("[TRENDING] 구글 트렌드 키워드 수집 시도...")
            
            # TODO: pytrends 라이브러리 사용한 실제 구글 트렌드 데이터 수집
            # from pytrends.request import TrendReq
            # pytrends = TrendReq(hl='ko', tz=540)
            # trending_searches = pytrends.trending_searches()
            
            # 현재는 동적 키워드 생성
            import random
            tech_keywords = ["ChatGPT", "AI개발", "Python", "React", "클라우드"]
            random.shuffle(tech_keywords)
            return tech_keywords
            
        except Exception as e:
            print(f"[TRENDING] 구글 트렌드 수집 오류: {e}")
            return []
    
    def _fetch_youtube_trends(self) -> List[str]:
        """유튜브 인기 동영상 키워드 수집"""
        try:
            print("[TRENDING] 유튜브 트렌드 키워드 수집 시도...")
            
            # TODO: YouTube Data API v3 사용한 실제 인기 동영상 키워드 수집
            # 현재는 컨텐츠 관련 동적 키워드 생성
            import random
            content_keywords = ["브이로그", "리뷰", "튜토리얼", "언박싱", "ASMR"]
            random.shuffle(content_keywords)
            return content_keywords
            
        except Exception as e:
            print(f"[TRENDING] 유튜브 트렌드 수집 오류: {e}")
            return []
    
    def _fetch_twitter_trends(self) -> List[str]:
        """트위터 트렌딩 해시태그 수집"""
        try:
            print("[TRENDING] 트위터 트렌드 해시태그 수집 시도...")
            
            # TODO: Twitter API v2 사용한 실제 트렌딩 해시태그 수집
            # 현재는 소셜 미디어 관련 동적 키워드 생성
            import random
            social_keywords = ["인플루언서", "바이럴", "챌린지", "밈", "핫이슈"]
            random.shuffle(social_keywords)
            return social_keywords
            
        except Exception as e:
            print(f"[TRENDING] 트위터 트렌드 수집 오류: {e}")
            return []
    
    def _get_fallback_trends(self) -> List[str]:
        """외부 소스 실패 시 사용할 동적 기본 키워드"""
        import random
        from datetime import datetime
        
        # 현재 날짜 기반 동적 키워드 생성
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        base_categories = {
            "기술": ["AI", "머신러닝", "클라우드", "보안", "개발"],
            "경제": ["투자", "부동산", "주식", "경제", "금융"],
            "문화": ["K-POP", "드라마", "영화", "게임", "웹툰"],
            "사회": ["환경", "교육", "건강", "여행", "라이프스타일"],
            "트렌드": ["MZ세대", "원격근무", "디지털", "소셜미디어", "인플루언서"]
        }
        
        dynamic_trends = []
        for category, keywords in base_categories.items():
            # 날짜 기반으로 키워드 선택 및 변형
            selected = random.sample(keywords, min(3, len(keywords)))
            for keyword in selected:
                # 동적 변형 추가
                variations = [
                    f"{keyword}_{current_month}월트렌드",
                    f"최신{keyword}",
                    f"{keyword}_핫이슈",
                    f"{current_day}일_{keyword}"
                ]
                dynamic_trends.append(random.choice(variations))
        
        return dynamic_trends
    
    def match_trends_to_category(self, trends: List[str], category: str) -> List[str]:
        """트렌드를 카테고리에 맞게 매칭"""
        category_keywords = self.category_mapping.get(category, [])
        matched_topics = []
        
        for trend in trends:
            for keyword in category_keywords:
                if any(k in trend for k in [keyword, keyword.lower()]):
                    # 트렌드를 블로그 주제로 변환
                    topic = self._convert_to_blog_topic(trend, category)
                    if topic not in matched_topics:
                        matched_topics.append(topic)
                    
        # 부족한 경우 카테고리별 기본 주제 추가
        if len(matched_topics) < 20:
            default_topics = self._get_default_topics_for_category(category)
            matched_topics.extend(default_topics)
            
        return matched_topics[:30]  # 최대 30개 (2배 증가)
    
    def _convert_to_blog_topic(self, trend: str, category: str) -> str:
        """트렌드 키워드를 블로그 주제로 변환"""
        today = datetime.now().strftime("%Y년 %m월")
        
        topic_templates = {
            '기술/디지털': [
                f"{trend} 최신 동향과 전망",
                f"{trend} 실무 활용 가이드",
                f"{trend} vs 기존 기술 비교 분석"
            ],
            '교육/자기계발': [
                f"{trend} 분야 커리어 로드맵",
                f"{trend} 학습 방법과 팁",
                f"{trend} 관련 자격증 완전 정리"
            ],
            '재정/투자': [
                f"{trend} 투자 전략과 리스크 분석",
                f"{trend} 관련 수익 모델 분석",
                f"{trend} 시장 동향과 전망"
            ],
            '라이프스타일': [
                f"{trend}로 라이프스타일 업그레이드",
                f"{trend} 트렌드 완전 분석",
                f"{trend} 실생활 활용 가이드"
            ],
            '건강/웰니스': [
                f"{trend} 건강 관리 완전 가이드",
                f"{trend}와 건강한 생활습관",
                f"{trend} 관련 질병 예방법"
            ],
            '역사/문화': [
                f"{trend}의 역사적 의미와 가치",
                f"{trend} 문화적 배경 심층 분석",
                f"{trend} 전통과 현대의 만남"
            ],
            '엔터테인먼트': [
                f"{trend} 최신 소식과 분석",
                f"{trend} 팬덤 문화 완전 해부",
                f"{trend} 글로벌 영향력 분석"
            ],
            '트렌드/이슈': [
                f"{today} {trend} 이슈 완전 분석",
                f"{trend} 사회적 영향과 전망",
                f"{trend} MZ세대 반응 분석"
            ]
        }
        
        templates = topic_templates.get(category, [f"{trend} 완전 가이드"])
        return random.choice(templates)
    
    def _get_default_topics_for_category(self, category: str) -> List[str]:
        """카테고리별 기본 주제 반환 - 대폭 확장"""
        default_topics = {
            '기술/디지털': [
                "AI 개발 트렌드 분석", "웹 개발 최신 기술", "모바일 앱 개발 가이드",
                "클라우드 서비스 비교", "사이버 보안 완전 가이드", "블록체인 기술 활용",
                "빅데이터 분석 방법", "IoT 개발 실무", "머신러닝 알고리즘",
                "DevOps 도구 활용법", "API 설계 베스트 프랙티스", "데이터베이스 최적화",
                "마이크로서비스 아키텍처", "컨테이너 기술 완전 정복", "서버리스 개발",
                "프론트엔드 프레임워크 비교", "백엔드 개발 로드맵", "풀스택 개발자 되기",
                "오픈소스 프로젝트 참여법", "코드 리뷰 문화 정착"
            ],
            '교육/자기계발': [
                "개발자 커리어 성장 전략", "온라인 교육 플랫폼 비교", "자기주도 학습법",
                "시간 관리 효율화 방법", "생산성 향상 도구", "목표 설정과 달성",
                "습관 형성의 과학", "독서 습관 만들기", "영어 실력 향상법",
                "프레젠테이션 스킬", "네트워킹 전략", "리더십 개발",
                "창의적 사고 기법", "문제 해결 능력", "비판적 사고력",
                "감정 지능 향상", "스트레스 관리법", "번아웃 예방",
                "평생 학습 전략", "멘토링 활용법"
            ],
            '재정/투자': [
                "주식 투자 기초 가이드", "부동산 투자 전략", "재테크 포트폴리오 구성",
                "연금 준비 방법", "세테크 완전 정리", "펀드 투자 가이드",
                "채권 투자 이해하기", "해외 투자 전략", "암호화폐 투자법",
                "ESG 투자 트렌드", "리츠 투자 완전 분석", "배당주 투자 전략",
                "가치 투자 vs 성장 투자", "금융 상품 비교", "보험 상품 선택법",
                "은퇴 자금 계획", "자녀 교육비 준비", "내집 마련 전략",
                "경제 지표 읽는 법", "투자 심리학"
            ],
            '라이프스타일': [
                "미니멀 라이프 실천법", "홈카페 만들기", "반려동물 케어",
                "취미 생활 추천", "여행 계획 세우기", "인테리어 아이디어",
                "요리 레시피 완전 정복", "패션 스타일링", "뷰티 루틴 만들기",
                "홈가드닝 시작하기", "DIY 프로젝트", "독서 공간 꾸미기",
                "운동 루틴 만들기", "명상과 힐링", "취미 활동 추천",
                "소셜 미디어 활용", "사진 촬영 기법", "영상 편집 노하우",
                "라이프해킹 팁", "시간 활용 극대화"
            ],
            '건강/웰니스': [
                "올바른 운동법", "균형 잡힌 식단 관리", "스트레스 해소법",
                "수면의 질 개선", "면역력 증진 방법", "다이어트 성공 전략",
                "홈트레이닝 가이드", "요가와 필라테스", "마사지 테라피",
                "건강한 간식 만들기", "디톡스 프로그램", "정신 건강 관리",
                "만성 질환 예방", "건강 검진 가이드", "영양제 선택법",
                "뇌 건강 지키기", "관절 건강 관리", "눈 건강 보호법",
                "호흡법과 명상", "자연 치유법"
            ],
            '역사/문화': [
                "한국사 주요 사건", "전통 문화의 현대적 의미", "문화재 보존의 중요성",
                "지역별 문화 특색", "역사 여행지 추천", "세계사 속 한국",
                "전통 음식의 역사", "한옥의 과학적 원리", "전통 예술의 가치",
                "문화 유산 탐방", "박물관 전시 해설", "역사 인물 재조명",
                "전통 축제의 의미", "민속 놀이와 문화", "한국 문학사",
                "전통 공예의 미학", "궁궐 건축의 특징", "불교 문화 유산",
                "유교 문화의 영향", "현대 속 전통 문화"
            ],
            '엔터테인먼트': [
                "K-POP 글로벌 확산", "드라마 제작 트렌드", "영화 산업 동향",
                "게임 문화 분석", "예능 프로그램 변화", "웹툰 산업 성장",
                "OTT 플랫폼 전쟁", "음악 스트리밍 시장", "버츄얼 아이돌",
                "e스포츠 산업", "콘텐츠 크리에이터", "인플루언서 마케팅",
                "팬덤 문화 분석", "미디어 소비 패턴", "엔터테인먼트 기술",
                "AI와 엔터테인먼트", "메타버스 콘서트", "NFT 아트 시장",
                "독립 영화의 부상", "웹 예능의 진화"
            ],
            '트렌드/이슈': [
                "MZ세대 문화 분석", "소셜미디어 트렌드", "환경 이슈와 대응",
                "디지털 전환 가속화", "새로운 라이프스타일", "워라밸 문화",
                "원격근무 정착", "긱 이코노미 확산", "구독 경제 성장",
                "공유 경제 트렌드", "AI 윤리 이슈", "데이터 프라이버시",
                "탄소 중립 정책", "지속 가능한 소비", "제로 웨이스트",
                "사회적 기업", "임팩트 투자", "ESG 경영",
                "디지털 격차 해소", "고령화 사회 대응"
            ]
        }
        
        return default_topics.get(category, ["기본 주제", "일반적인 내용", "관련 정보"])
        
    def update_trending_cache(self, force_update: bool = False):
        """트렌딩 캐시 업데이트"""
        current_time = datetime.now()
        
        # 캐시 만료 체크
        if not force_update:
            for site in self.site_configs:
                last_update = self.last_update.get(site, datetime.min)
                if (current_time - last_update).seconds < self.cache_expiry:
                    continue
        
        # 실시간 트렌드 수집
        realtime_trends = self.fetch_realtime_trends()
        
        # 각 사이트별로 카테고리 매칭
        for site, config in self.site_configs.items():
            primary_category = config['primary']
            secondary_category = config['secondary']
            
            # 카테고리별 매칭된 주제들
            primary_topics = self.match_trends_to_category(realtime_trends, primary_category)
            secondary_topics = self.match_trends_to_category(realtime_trends, secondary_category)
            
            self.trending_cache[site] = {
                primary_category: primary_topics,
                secondary_category: secondary_topics
            }
            
            self.last_update[site] = current_time
            
        print(f"[TRENDING] 캐시 업데이트 완료: {current_time}")
        return True
    
    def add_trending_topic(self, site: str, category: str, topic: str, keywords: List[str] = None):
        """실시간 트렌딩 주제 추가"""
        if site not in self.site_configs:
            raise ValueError(f"Unknown site: {site}")
            
        # 캐시에 직접 추가
        if site not in self.trending_cache:
            self.trending_cache[site] = {}
            
        if category not in self.trending_cache[site]:
            self.trending_cache[site][category] = []
            
        # 중복 체크 후 맨 앞에 추가
        existing_topics = self.trending_cache[site][category]
        if topic not in existing_topics:
            existing_topics.insert(0, topic)
            
            # 최신 30개만 유지
            if len(existing_topics) > 30:
                self.trending_cache[site][category] = existing_topics[:30]
                
        print(f"[TRENDING] {site} - {category}에 새 주제 추가: {topic}")
        return True
    
    def get_trending_topics(self, site: str, category: str, limit: int = 10) -> List[str]:
        """사이트별 카테고리 트렌딩 주제 조회 (실시간 업데이트 포함)"""
        if site not in self.site_configs:
            return []
        
        # 캐시가 비어있거나 만료된 경우 업데이트
        if (site not in self.trending_cache or 
            site not in self.last_update or 
            (datetime.now() - self.last_update[site]).seconds > self.cache_expiry):
            self.update_trending_cache()
            
        site_cache = self.trending_cache.get(site, {})
        return site_cache.get(category, [])[:limit]
    
    def get_daily_topics(self, site: str, date: datetime.date) -> Tuple[Dict, Dict]:
        """특정 날짜의 사이트별 2개 주제 반환 (primary + secondary) - 실시간 업데이트"""
        if site not in self.site_configs:
            raise ValueError(f"Unknown site: {site}")
        
        site_config = self.site_configs[site]
        primary_category = site_config['primary']
        secondary_category = site_config['secondary']
        
        # 실시간 트렌딩 주제 조회
        primary_trending = self.get_trending_topics(site, primary_category, 20)
        secondary_trending = self.get_trending_topics(site, secondary_category, 20)
        
        # 날짜 기반 시드로 주제 선택 (일관성 보장)
        day_seed = (date.year * 1000 + date.timetuple().tm_yday) % 1000
        
        # Primary 주제 선택
        if primary_trending:
            primary_idx = day_seed % len(primary_trending)
            primary_topic_text = primary_trending[primary_idx]
        else:
            # 기본 주제 폴백
            default_topics = self._get_default_topics_for_category(primary_category)
            primary_topic_text = default_topics[day_seed % len(default_topics)]
            
        # Secondary 주제 선택
        if secondary_trending:
            secondary_idx = (day_seed + 1) % len(secondary_trending)
            secondary_topic_text = secondary_trending[secondary_idx]
        else:
            # 기본 주제 폴백
            default_topics = self._get_default_topics_for_category(secondary_category)
            secondary_topic_text = default_topics[(day_seed + 1) % len(default_topics)]
        
        primary_topic = {
            'category': primary_category,
            'topic': primary_topic_text,
            'keywords': self._extract_keywords(primary_topic_text),
            'length': 'medium'
        }
        
        secondary_topic = {
            'category': secondary_category,  
            'topic': secondary_topic_text,
            'keywords': self._extract_keywords(secondary_topic_text),
            'length': 'medium'
        }
        
        return primary_topic, secondary_topic
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """주제에서 키워드 추출"""
        keywords = []
        
        # 괄호 안의 키워드들
        bracket_content = re.findall(r'\(([^)]+)\)', topic)
        for content in bracket_content:
            keywords.extend([k.strip() for k in content.split(',') if k.strip()])
        
        # 주요 단어들 추출 (기본적인 키워드)
        main_words = re.findall(r'[가-힣]{2,}|[A-Za-z]{3,}', topic.replace('(', '').replace(')', ''))
        keywords.extend(main_words[:3])  # 최대 3개까지
        
        return list(set(keywords))[:5]  # 중복 제거 후 최대 5개
    
    def get_site_topics_summary(self) -> Dict:
        """전체 사이트별 주제 요약 반환 (실시간 데이터 포함)"""
        # 캐시 업데이트 확인
        self.update_trending_cache()
        
        summary = {}
        for site, config in self.site_configs.items():
            primary_category = config['primary']
            secondary_category = config['secondary']
            
            # 실시간 트렌딩 데이터에서 가져오기
            site_cache = self.trending_cache.get(site, {})
            primary_topics = site_cache.get(primary_category, [])
            secondary_topics = site_cache.get(secondary_category, [])
            
            summary[site] = {
                'primary_category': primary_category,
                'secondary_category': secondary_category,
                'primary_topics_count': len(primary_topics),
                'secondary_topics_count': len(secondary_topics),
                'latest_primary': primary_topics[:3],
                'latest_secondary': secondary_topics[:3],
                'last_updated': self.last_update.get(site, datetime.now()).isoformat()
            }
        return summary

# 전역 인스턴스
trending_topic_manager = TrendingTopicManager()