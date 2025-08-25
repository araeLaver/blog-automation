"""
트렌디한 주제 관리 및 생성 모듈
기존 컨셉 기반 + 최신 트렌드 주제 동적 추가
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class TrendingTopicManager:
    """트렌디한 주제 관리 클래스"""
    
    def __init__(self):
        self.base_topics = self._load_base_topics()
        self.trending_keywords = []
        
    def _load_base_topics(self) -> Dict:
        """사이트별 기본 컨셉 주제들 로드"""
        return {
            'unpre': {
                'primary': '프로그래밍/개발',
                'secondary': '기술/디지털',
                'topics': {
                    '프로그래밍/개발': [
                        "JWT 토큰 기반 시큐리티 구현",
                        "Python 데이터 분석 마스터",
                        "React Hook 고급 활용법",
                        "Docker 컨테이너 운영 실무",
                        "GraphQL API 설계와 최적화",
                        "Kubernetes 클러스터 관리",
                        "TypeScript 고급 타입 시스템",
                        "Spring Boot 마이크로서비스 아키텍처",
                        "Vue.js 3 Composition API 활용",
                        "AWS 서버리스 아키텍처 구축"
                    ],
                    '기술/디지털': [
                        "최신 가젯 리뷰 (iPhone 16 Pro 성능 분석)",
                        "AI 프로그래밍 가이드 (ChatGPT API 활용법)",
                        "소프트웨어 튜토리얼 (VS Code 고급 팁)",
                        "디지털 마케팅 SEO 최적화 전략",
                        "개발자 생산성 도구 비교 분석",
                        "클라우드 서비스 선택 가이드",
                        "오픈소스 프로젝트 기여 방법",
                        "코딩 테스트 합격 완전 정복"
                    ]
                }
            },
            'untab': {
                'primary': '재정/투자',
                'secondary': '라이프스타일',
                'topics': {
                    '재정/투자': [
                        "친환경 부동산 그린 리모델링 투자",
                        "수익형 부동산 투자 완전 가이드",
                        "배당주 포트폴리오 구성 전략",
                        "비트코인 ETF 투자 분석",
                        "가계부 작성으로 재정 관리하기",
                        "생활비 절약 실전 꿀팁 20가지",
                        "온라인 부업으로 월 100만원 벌기",
                        "ESG 투자의 미래 전망과 수익성"
                    ],
                    '라이프스타일': [
                        "국내 숨은 여행 명소 TOP 10",
                        "제주도 현지인이 추천하는 진짜 맛집",
                        "원룸 공간 200% 활용하는 인테리어 팁",
                        "북유럽 스타일 홈 데코 꾸미기",
                        "30분 완성 간단 집밥 레시피",
                        "건강식품 성분 분석 및 효능 비교",
                        "데일리 캐주얼 코디 완전 정복",
                        "가성비 브랜드 쇼핑 가이드"
                    ]
                }
            },
            'skewese': {
                'primary': '역사/문화',
                'secondary': '건강/웰니스',
                'topics': {
                    '역사/문화': [
                        "임진왜란과 이순신의 영웅적 활약상",
                        "조선시대 과거제도가 남긴 교육 유산",
                        "한국 전통 건축의 과학적 아름다움",
                        "정조의 개혁 정치와 수원 화성 건설",
                        "고구려 광개토대왕의 영토 확장 전략",
                        "조선 후기 실학사상 발전과 현대적 의의",
                        "한국사 속 여성 인물들의 숨겨진 이야기",
                        "문화재 보존 기술의 현재와 미래"
                    ],
                    '건강/웰니스': [
                        "간헐적 단식 다이어트 완전 가이드",
                        "집에서 하는 홈트레이닝 프로그램",
                        "슈퍼푸드 영양 성분 완전 분석",
                        "단백질 보충제 브랜드별 비교 리뷰",
                        "직장인 스트레스 관리 실전 방법",
                        "명상과 마음챙김으로 멘탈 케어하기",
                        "연령별 스킨케어 루틴 완전 정리",
                        "자연스러운 데일리 메이크업 팁"
                    ]
                }
            },
            'tistory': {
                'primary': '트렌드/이슈',
                'secondary': '교육/엔터테인먼트',
                'topics': {
                    '트렌드/이슈': [
                        "MZ세대 영끌 투자 열풍과 부작용 분석",
                        "2025년 AI 대혁신 ChatGPT-5 출시 전망",
                        "인플레이션 재부상? 경제 전문가 분석",
                        "K-컬처 세계 정복 현황과 미래",
                        "전기차 배터리 혁신 기술 동향",
                        "Z세대가 바꾸는 소비 트렌드 변화",
                        "포스트 코로나 원격근무 정착화",
                        "플랫폼 이코노미와 긱 워커 시대"
                    ],
                    '교육/엔터테인먼트': [
                        "영어 회화 마스터를 위한 학습법",
                        "취업 성공 이력서 작성 완전 공략",
                        "온라인 강의 플랫폼 비교 분석",
                        "노션으로 생산성 200% 높이기",
                        "넷플릭스 숨겨진 명작 추천 리스트",
                        "모바일 게임 고수되는 완전 공략",
                        "K-POP 아이돌 최신 소식 정리",
                        "연예계 이슈 심층 분석"
                    ]
                }
            }
        }
    
    def get_daily_topics(self, site: str, date: datetime.date) -> Tuple[Dict, Dict]:
        """특정 날짜의 사이트별 2개 주제 반환 (primary + secondary)"""
        if site not in self.base_topics:
            raise ValueError(f"Unknown site: {site}")
        
        site_config = self.base_topics[site]
        primary_category = site_config['primary']
        secondary_category = site_config['secondary']
        
        # 날짜 기반 시드로 주제 선택 (일관성 보장)
        day_seed = (date.year * 1000 + date.timetuple().tm_yday) % 1000
        
        primary_topics = site_config['topics'][primary_category]
        secondary_topics = site_config['topics'][secondary_category]
        
        # 시드 기반 주제 선택
        primary_idx = day_seed % len(primary_topics)
        secondary_idx = (day_seed + 1) % len(secondary_topics)
        
        primary_topic = {
            'category': primary_category,
            'topic': primary_topics[primary_idx],
            'keywords': self._extract_keywords(primary_topics[primary_idx]),
            'length': 'medium'
        }
        
        secondary_topic = {
            'category': secondary_category,  
            'topic': secondary_topics[secondary_idx],
            'keywords': self._extract_keywords(secondary_topics[secondary_idx]),
            'length': 'medium'
        }
        
        return primary_topic, secondary_topic
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """주제에서 키워드 추출"""
        # 괄호 안의 내용 추출
        import re
        keywords = []
        
        # 괄호 안의 키워드들
        bracket_content = re.findall(r'\(([^)]+)\)', topic)
        for content in bracket_content:
            keywords.extend([k.strip() for k in content.split(',') if k.strip()])
        
        # 주요 단어들 추출 (기본적인 키워드)
        main_words = re.findall(r'[가-힣]{2,}|[A-Za-z]{3,}', topic.replace('(', '').replace(')', ''))
        keywords.extend(main_words[:3])  # 최대 3개까지
        
        return list(set(keywords))  # 중복 제거
    
    def add_trending_topic(self, site: str, category: str, topic: str, keywords: List[str] = None):
        """트렌디한 주제 동적 추가"""
        if site not in self.base_topics:
            return False
        
        if category not in self.base_topics[site]['topics']:
            return False
        
        # 새 주제 추가
        self.base_topics[site]['topics'][category].append(topic)
        
        print(f"[TRENDING] {site} - {category}에 새 주제 추가: {topic}")
        return True
    
    def get_trending_suggestions(self) -> List[Dict]:
        """현재 트렌드 기반 주제 추천"""
        # 실제 구현시 Google Trends API, 네이버 트렌드 등 활용 가능
        trending_topics = [
            {"site": "unpre", "category": "기술/디지털", "topic": "Apple Vision Pro 2024 리뷰 및 활용법"},
            {"site": "untab", "category": "재정/투자", "topic": "2024년 부동산 PF 사태 분석과 대응법"},
            {"site": "skewese", "category": "건강/웰니스", "topic": "겨울철 면역력 강화 운동법"},
            {"site": "tistory", "category": "트렌드/이슈", "topic": "생성형 AI 시대, 일자리 변화 전망"}
        ]
        
        return trending_topics
    
    def save_topics_to_file(self, filepath: str = None):
        """주제 데이터를 파일로 저장"""
        if not filepath:
            filepath = Path(__file__).parent.parent.parent / "data" / "trending_topics.json"
        
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.base_topics, f, ensure_ascii=False, indent=2)
        
        print(f"[TRENDING] 주제 데이터 저장 완료: {filepath}")
    
    def load_topics_from_file(self, filepath: str = None):
        """파일에서 주제 데이터 로드"""
        if not filepath:
            filepath = Path(__file__).parent.parent.parent / "data" / "trending_topics.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                self.base_topics = json.load(f)
            print(f"[TRENDING] 주제 데이터 로드 완료: {filepath}")
        else:
            print(f"[TRENDING] 파일 없음, 기본 주제 사용: {filepath}")

if __name__ == "__main__":
    # 테스트 실행
    manager = TrendingTopicManager()
    
    # 오늘의 주제 확인
    today = datetime.now().date()
    
    for site in ['unpre', 'untab', 'skewese', 'tistory']:
        primary, secondary = manager.get_daily_topics(site, today)
        print(f"\n{site.upper()} - {today}")
        print(f"  Primary: {primary['topic']} ({primary['category']})")
        print(f"  Secondary: {secondary['topic']} ({secondary['category']})")
    
    # 주제 데이터 저장
    manager.save_topics_to_file()