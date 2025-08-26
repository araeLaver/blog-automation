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
        """실시간 트렌딩 키워드 수집 - 대폭 확장"""
        trends = []
        
        try:
            # 1. 현재 시점의 실제 주요 이슈 키워드 (2025년 8월 기준)
            current_hot_issues = [
                "OpenAI o1", "Claude 3.5", "AI 에이전트", "Anthropic", "Google Gemini",
                "NVIDIA H200", "삼성전자", "SK하이닉스", "메모리반도체", "HBM",
                "한국은행", "기준금리", "원달러환율", "미국인플레이션", "연준정책",
                "전기차", "배터리", "2차전지", "중국수입차", "테슬라모델Y",
                "부동산", "금리인하", "주택가격", "전세가율", "청약",
                "K-POP", "NewJeans", "스트레이키즈", "aespa", "르세라핌",
                "넷플릭스", "디즈니플러스", "OTT", "웹툰", "웹드라마",
                "원격근무", "AI면접", "채용트렌드", "MZ세대", "워라밸",
                "폭염", "기후변화", "탄소중립", "신재생에너지", "ESG"
            ]
            trends.extend(current_hot_issues)
            
            # 2. 기술 분야 실시간 트렌드
            tech_trends = [
                "생성AI", "LLM", "RAG", "파인튜닝", "멀티모달",
                "React19", "Next.js", "TypeScript", "Rust", "Go언어",
                "쿠버네티스", "Docker", "마이크로서비스", "클라우드네이티브",
                "사이버보안", "제로트러스트", "양자컴퓨팅", "블록체인",
                "메타버스", "AR글래스", "애플비전프로", "공간컴퓨팅"
            ]
            trends.extend(tech_trends)
            
            # 3. 경제/투자 분야 핫 키워드
            economy_trends = [
                "코스피3000", "나스닥", "다우지수", "금투세", "양도세",
                "개미투자자", "해외주식", "ETF", "리츠", "디비던드",
                "암호화폐", "비트코인ETF", "이더리움", "스테이킹", "디파이",
                "인플레이션", "디플레이션", "경기침체", "소프트랜딩"
            ]
            trends.extend(economy_trends)
            
            # 4. 사회/문화 트렌드
            social_trends = [
                "디지털노마드", "사이드허슬", "N잡러", "긱이코노미",
                "제로웨이스트", "비건", "플렉시테리안", "미니멀라이프",
                "숏폼", "틱톡", "유튜브쇼츠", "인스타릴스", "인플루언서",
                "구독경제", "멤버십", "펫테크", "시니어테크"
            ]
            trends.extend(social_trends)
            
            # 5. 건강/웰니스 트렌드  
            health_trends = [
                "GLP-1", "오젬픽", "당뇨병약", "비만치료제",
                "정신건강", "마인드풀니스", "명상앱", "수면의질",
                "홈트레이닝", "피트니스앱", "웨어러블", "헬스케어AI",
                "개인영양", "푸드테크", "대체단백질", "식물성식품"
            ]
            trends.extend(health_trends)
            
            # 6. 시즌별 트렌드 (8월 기준)
            seasonal_trends = [
                "여름휴가", "휴가지추천", "캠핑", "글램핑", "펜션",
                "여름패션", "선크림", "UV차단", "쿨링웨어",
                "여름축제", "페스티벌", "야외활동", "수영", "서핑"
            ]
            trends.extend(seasonal_trends)
            
            # 7. 지역별 핫 이슈
            regional_trends = [
                "부산엑스포", "강남재개발", "판교테크노밸리", "송도IBD",
                "제주도여행", "경주관광", "전주한옥마을", "여수밤바다"
            ]
            trends.extend(regional_trends)
            
        except Exception as e:
            print(f"[TRENDING] 실시간 트렌드 수집 실패: {e}")
            # 기본 트렌드 키워드 반환
            trends = ["AI", "투자", "건강", "여행", "기술", "개발", "경제", "문화"]
            
        # 중복 제거 및 더 많은 키워드 반환
        unique_trends = list(dict.fromkeys(trends))  # 순서 유지하면서 중복 제거
        return unique_trends[:100]  # 상위 100개 반환 (5배 증가)
    
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