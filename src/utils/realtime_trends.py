#!/usr/bin/env python3
"""
실시간 트렌드 데이터 수집 및 분석
- 구글 트렌드 API
- 네이버 실시간 검색어
- 트렌드를 블로그 주제로 변환
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from typing import List, Dict
import random
import time
import re
import logging

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("⚠️ pytrends 라이브러리가 필요합니다: pip install pytrends")

class RealtimeTrends:
    """실시간 트렌드 수집 및 분석 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if PYTRENDS_AVAILABLE:
            self.pytrends = TrendReq(hl='ko-KR', tz=540)  # 한국 시간대
        
    def get_google_trends(self, timeframe='now 1-d') -> List[Dict]:
        """구글 트렌드 데이터 수집"""
        if not PYTRENDS_AVAILABLE:
            return self._fallback_google_trends()
            
        try:
            # 실시간 트렌드 (한국)
            trending_searches = self.pytrends.trending_searches(pn='south_korea')
            
            trends = []
            if not trending_searches.empty:
                for i, trend in enumerate(trending_searches[0][:20]):  # 상위 20개
                    trends.append({
                        'keyword': trend,
                        'rank': i + 1,
                        'source': 'google',
                        'category': self._categorize_keyword(trend)
                    })
            
            self.logger.info(f"구글 트렌드 {len(trends)}개 수집 완료")
            return trends
            
        except Exception as e:
            self.logger.error(f"구글 트렌드 수집 오류: {e}")
            return self._fallback_google_trends()
    
    def get_naver_realtime_keywords(self) -> List[Dict]:
        """네이버 실시간 검색어 수집 (대안 방법)"""
        try:
            # 네이버 데이터랩 API 대신 공개 데이터 활용
            # 실제로는 네이버 검색 트렌드나 뉴스 키워드 수집
            keywords = self._get_naver_news_keywords()
            
            trends = []
            for i, keyword in enumerate(keywords[:15]):  # 상위 15개
                trends.append({
                    'keyword': keyword,
                    'rank': i + 1,
                    'source': 'naver',
                    'category': self._categorize_keyword(keyword)
                })
            
            self.logger.info(f"네이버 키워드 {len(trends)}개 수집 완료")
            return trends
            
        except Exception as e:
            self.logger.error(f"네이버 키워드 수집 오류: {e}")
            return self._fallback_naver_trends()
    
    def _get_naver_news_keywords(self) -> List[str]:
        """네이버 뉴스에서 인기 키워드 추출"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # 네이버 뉴스 랭킹 페이지
            url = 'https://news.naver.com/main/ranking/popularDay.naver'
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 뉴스 제목에서 키워드 추출
            headlines = soup.select('.list_title')
            keywords = []
            
            for headline in headlines[:20]:
                title = headline.get_text().strip()
                # 제목에서 의미있는 키워드 추출
                extracted = self._extract_keywords_from_title(title)
                keywords.extend(extracted)
            
            # 중복 제거 및 정리
            unique_keywords = list(dict.fromkeys(keywords))
            return unique_keywords[:15]
            
        except Exception as e:
            self.logger.error(f"네이버 뉴스 키워드 추출 오류: {e}")
            return []
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """뉴스 제목에서 키워드 추출"""
        # 불필요한 문자 제거
        title = re.sub(r'[^\w\s가-힣]', ' ', title)
        
        # 의미있는 키워드 패턴 매칭
        keywords = []
        
        # 인명, 지명, 기관명, 브랜드명 등 추출
        patterns = [
            r'\b[A-Z][a-zA-Z]{2,}\b',  # 영문 고유명사
            r'\b[가-힣]{2,4}(?:대통령|장관|의원|대표|회장)\b',  # 직책
            r'\b[가-힣]{2,6}(?:기업|회사|그룹|재단)\b',  # 기업
            r'\b(?:삼성|현대|LG|SK|네이버|카카오|쿠팡)\b',  # 주요 기업
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, title)
            keywords.extend([m.strip() for m in matches if len(m.strip()) > 1])
        
        return keywords[:3]  # 제목당 최대 3개
    
    def _categorize_keyword(self, keyword: str) -> str:
        """키워드를 카테고리로 분류"""
        keyword_lower = keyword.lower()
        
        # 기술/IT
        tech_keywords = ['ai', '인공지능', 'gpt', '로봇', '스마트폰', '애플', '삼성', '구글', 
                        '메타버스', '암호화폐', '비트코인', '블록체인', 'vr', 'ar']
        
        # 정치/사회
        politics_keywords = ['대통령', '정부', '국회', '선거', '정책', '법안', '시위', '집회']
        
        # 경제/투자
        economy_keywords = ['주식', '투자', '부동산', '금리', '인플레이션', '경제', '시장', 
                           '코스피', '달러', '원화', '증시']
        
        # 연예/문화
        entertainment_keywords = ['아이돌', 'k-pop', '드라마', '영화', '연예인', '방탄소년단', 
                                 'bts', '블랙핑크', '배우', '가수']
        
        # 스포츠
        sports_keywords = ['축구', '야구', '농구', '올림픽', '월드컵', '손흥민', '김연아', 
                          '프로야구', 'k리그']
        
        if any(word in keyword_lower for word in tech_keywords):
            return 'tech'
        elif any(word in keyword_lower for word in politics_keywords):
            return 'politics'
        elif any(word in keyword_lower for word in economy_keywords):
            return 'economy'
        elif any(word in keyword_lower for word in entertainment_keywords):
            return 'entertainment'
        elif any(word in keyword_lower for word in sports_keywords):
            return 'sports'
        else:
            return 'social'
    
    def convert_trends_to_blog_topics(self, trends: List[Dict]) -> Dict[str, List[str]]:
        """트렌드 키워드를 블로그 주제로 변환"""
        
        # 카테고리별로 그룹화
        categorized = {}
        for trend in trends:
            category = trend['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(trend['keyword'])
        
        # 카테고리별 블로그 주제 생성
        blog_topics = {}
        
        for category, keywords in categorized.items():
            topics = []
            for keyword in keywords[:5]:  # 카테고리당 최대 5개
                topic = self._generate_blog_topic(keyword, category)
                if topic:
                    topics.append(topic)
            
            if topics:
                blog_topics[category] = topics
        
        return blog_topics
    
    def _generate_blog_topic(self, keyword: str, category: str) -> str:
        """키워드와 카테고리를 기반으로 블로그 주제 생성"""
        
        templates = {
            'tech': [
                f'{keyword}의 기술적 혁신과 미래 전망',
                f'{keyword}가 바꾸는 우리의 일상',
                f'{keyword} 완벽 가이드와 활용법',
                f'{keyword}의 장단점 분석',
            ],
            'politics': [
                f'{keyword} 정책 변화와 우리 생활 영향',
                f'{keyword} 이슈 완전 분석',
                f'{keyword}을 둘러싼 찬반 논란',
                f'{keyword} 관련 최신 동향',
            ],
            'economy': [
                f'{keyword} 투자 전략과 시장 분석',
                f'{keyword}이 경제에 미치는 영향',
                f'{keyword} 관련 투자 기회 포착',
                f'{keyword} 시장 동향과 전망',
            ],
            'entertainment': [
                f'{keyword}의 글로벌 성공 비결',
                f'{keyword} 열풍 분석과 문화적 의미',
                f'{keyword}가 만든 새로운 트렌드',
                f'{keyword}의 팬덤 문화와 영향력',
            ],
            'sports': [
                f'{keyword} 경기 하이라이트와 분석',
                f'{keyword}의 성과와 의미',
                f'{keyword} 관련 스포츠 트렌드',
                f'{keyword}이 스포츠계에 미친 영향',
            ],
            'social': [
                f'{keyword} 현상 분석과 사회적 의미',
                f'{keyword}을 통해 본 현대 사회',
                f'{keyword} 이슈의 모든 것',
                f'{keyword} 트렌드와 우리 삶의 변화',
            ]
        }
        
        if category in templates:
            template = random.choice(templates[category])
            return template
        
        return f'{keyword} 관련 최신 트렌드 분석'
    
    def _fallback_google_trends(self) -> List[Dict]:
        """구글 트렌드 API 실패 시 대체 데이터"""
        fallback_data = [
            {'keyword': 'ChatGPT', 'rank': 1, 'source': 'google_fallback', 'category': 'tech'},
            {'keyword': '비트코인', 'rank': 2, 'source': 'google_fallback', 'category': 'economy'},
            {'keyword': '부동산', 'rank': 3, 'source': 'google_fallback', 'category': 'economy'},
            {'keyword': '테슬라', 'rank': 4, 'source': 'google_fallback', 'category': 'tech'},
            {'keyword': 'K-POP', 'rank': 5, 'source': 'google_fallback', 'category': 'entertainment'},
        ]
        return fallback_data
    
    def _fallback_naver_trends(self) -> List[Dict]:
        """네이버 트렌드 수집 실패 시 대체 데이터"""
        fallback_data = [
            {'keyword': '정부 정책', 'rank': 1, 'source': 'naver_fallback', 'category': 'politics'},
            {'keyword': '주식 시장', 'rank': 2, 'source': 'naver_fallback', 'category': 'economy'},
            {'keyword': '드라마', 'rank': 3, 'source': 'naver_fallback', 'category': 'entertainment'},
            {'keyword': '아이폰', 'rank': 4, 'source': 'naver_fallback', 'category': 'tech'},
            {'keyword': '축구', 'rank': 5, 'source': 'naver_fallback', 'category': 'sports'},
        ]
        return fallback_data
    
    def get_combined_trends(self) -> Dict[str, List[str]]:
        """구글과 네이버 트렌드를 결합하여 블로그 주제 생성"""
        
        print("🔍 실시간 트렌드 데이터 수집 중...")
        
        # 구글 트렌드 수집
        google_trends = self.get_google_trends()
        time.sleep(1)  # API 호출 간격 조절
        
        # 네이버 트렌드 수집
        naver_trends = self.get_naver_realtime_keywords()
        
        # 트렌드 결합
        all_trends = google_trends + naver_trends
        
        # 블로그 주제로 변환
        blog_topics = self.convert_trends_to_blog_topics(all_trends)
        
        print(f"✅ 총 {len(all_trends)}개 트렌드에서 {sum(len(topics) for topics in blog_topics.values())}개 블로그 주제 생성")
        
        return blog_topics

def test_realtime_trends():
    """실시간 트렌드 수집 테스트"""
    
    trends_collector = RealtimeTrends()
    
    print("=" * 60)
    print("🌐 실시간 트렌드 수집 테스트")
    print("=" * 60)
    
    # 트렌드 수집 및 주제 생성
    blog_topics = trends_collector.get_combined_trends()
    
    print("\n📝 생성된 블로그 주제:")
    print("-" * 40)
    
    for category, topics in blog_topics.items():
        print(f"\n📍 {category.upper()} 카테고리:")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic}")
    
    # 티스토리용 주제 선별
    tech_topics = blog_topics.get('tech', [])
    social_topics = blog_topics.get('social', []) + blog_topics.get('politics', [])
    
    print(f"\n🎯 티스토리 추천 주제:")
    print(f"  [tech] {tech_topics[0] if tech_topics else '테슬라 자율주행 기술 발전'}")
    print(f"  [social] {social_topics[0] if social_topics else 'MZ세대 소비 트렌드 변화'}")

if __name__ == '__main__':
    test_realtime_trends()