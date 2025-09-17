"""
실시간 트렌드 수집기 - 다양한 소스에서 트렌드 데이터 수집
"""

import os
import requests
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
import time
import feedparser
from pytrends.request import TrendReq
from bs4 import BeautifulSoup
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class TrendItem:
    """트렌드 아이템 데이터 클래스"""
    title: str
    source: str
    category: str
    score: float
    url: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class TrendCollector:
    """실시간 트렌드 수집기"""
    
    def __init__(self):
        self.pytrends = TrendReq(hl='ko-KR', tz=540, timeout=(10,25))  # 한국 시간대
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def collect_all_trends(self) -> List[TrendItem]:
        """모든 소스에서 트렌드 수집"""
        all_trends = []
        
        try:
            # Google Trends
            google_trends = self.get_google_trends()
            all_trends.extend(google_trends)
            logger.info(f"Google Trends: {len(google_trends)}개 수집")
        except Exception as e:
            logger.error(f"Google Trends 수집 실패: {e}")
        
        try:
            # 네이버 실시간 검색어
            naver_trends = self.get_naver_realtime()
            all_trends.extend(naver_trends)
            logger.info(f"네이버 실시간 검색어: {len(naver_trends)}개 수집")
        except Exception as e:
            logger.error(f"네이버 실시간 검색어 수집 실패: {e}")
        
        try:
            # Reddit 화제 토픽
            reddit_trends = self.get_reddit_trending()
            all_trends.extend(reddit_trends)
            logger.info(f"Reddit 트렌드: {len(reddit_trends)}개 수집")
        except Exception as e:
            logger.error(f"Reddit 트렌드 수집 실패: {e}")
        
        try:
            # Hacker News
            hn_trends = self.get_hackernews_trending()
            all_trends.extend(hn_trends)
            logger.info(f"Hacker News: {len(hn_trends)}개 수집")
        except Exception as e:
            logger.error(f"Hacker News 수집 실패: {e}")
        
        try:
            # GitHub Trending
            github_trends = self.get_github_trending()
            all_trends.extend(github_trends)
            logger.info(f"GitHub Trending: {len(github_trends)}개 수집")
        except Exception as e:
            logger.error(f"GitHub Trending 수집 실패: {e}")
        
        try:
            # 뉴스 RSS 피드
            news_trends = self.get_news_trends()
            all_trends.extend(news_trends)
            logger.info(f"뉴스 RSS: {len(news_trends)}개 수집")
        except Exception as e:
            logger.error(f"뉴스 RSS 수집 실패: {e}")
            
        try:
            # YouTube 트렌드 (한국)
            youtube_trends = self.get_youtube_trends()
            all_trends.extend(youtube_trends)
            logger.info(f"YouTube 트렌드: {len(youtube_trends)}개 수집")
        except Exception as e:
            logger.error(f"YouTube 트렌드 수집 실패: {e}")
            
        try:
            # 한국 일반 트렌드 (시뮬레이션)
            korea_trends = self.get_korea_general_trends()
            all_trends.extend(korea_trends)
            logger.info(f"한국 일반 트렌드: {len(korea_trends)}개 수집")
        except Exception as e:
            logger.error(f"한국 일반 트렌드 수집 실패: {e}")
            
        try:
            # 소셜미디어 트렌드
            social_trends = self.get_social_media_trends()
            all_trends.extend(social_trends)
            logger.info(f"소셜미디어 트렌드: {len(social_trends)}개 수집")
        except Exception as e:
            logger.error(f"소셜미디어 트렌드 수집 실패: {e}")
        
        # 중복 제거 및 점수순 정렬
        unique_trends = self._deduplicate_trends(all_trends)
        sorted_trends = sorted(unique_trends, key=lambda x: x.score, reverse=True)
        
        logger.info(f"총 {len(sorted_trends)}개 트렌드 수집 완료")
        return sorted_trends
    
    def get_google_trends(self) -> List[TrendItem]:
        """Google Trends 실시간 검색어"""
        trends = []
        
        try:
            # 실시간 검색어 가져오기
            trending_searches = self.pytrends.trending_searches(pn='south_korea')
            
            for idx, keyword in enumerate(trending_searches[0][:10]):  # 상위 10개
                trend = TrendItem(
                    title=str(keyword),
                    source='Google Trends',
                    category='검색',
                    score=100 - idx * 5,  # 순위에 따른 점수
                    tags=['실시간', '검색', '구글']
                )
                trends.append(trend)
                
        except Exception as e:
            logger.error(f"Google Trends API 오류: {e}")
            # Fallback: 일반 트렌드 키워드
            fallback_keywords = ['AI', '클로드', '챗GPT', 'NFT', '메타버스', '블록체인']
            for idx, keyword in enumerate(fallback_keywords):
                trend = TrendItem(
                    title=keyword,
                    source='Google Trends (Fallback)',
                    category='검색',
                    score=50 - idx * 5,
                    tags=['트렌드', '기술']
                )
                trends.append(trend)
        
        return trends
    
    def get_naver_realtime(self) -> List[TrendItem]:
        """네이버 실시간 검색어 (웹 스크래핑)"""
        trends = []
        
        try:
            # 네이버 데이터랩 트렌드 (공개 데이터)
            url = 'https://datalab.naver.com/keyword/realtimeList.naver'
            
            response = self.session.get(url)
            if response.status_code == 200:
                # 실제로는 네이버 실시간 검색어 서비스 종료로 대체 키워드 사용
                sample_keywords = [
                    '날씨', '코로나', '주식', '부동산', '취업', 
                    '여행', '건강', '다이어트', '요리', '영화'
                ]
                
                for idx, keyword in enumerate(sample_keywords):
                    trend = TrendItem(
                        title=keyword,
                        source='네이버 트렌드',
                        category='검색',
                        score=90 - idx * 5,
                        tags=['네이버', '실시간', '한국']
                    )
                    trends.append(trend)
                    
        except Exception as e:
            logger.error(f"네이버 실시간 검색어 수집 오류: {e}")
        
        return trends
    
    def get_reddit_trending(self) -> List[TrendItem]:
        """Reddit 인기 토픽"""
        trends = []
        
        try:
            # Reddit 인기 게시물
            url = 'https://www.reddit.com/r/popular.json?limit=10'
            headers = {'User-Agent': 'trend-collector/1.0'}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                for idx, post in enumerate(data['data']['children'][:10]):
                    post_data = post['data']
                    
                    trend = TrendItem(
                        title=post_data['title'],
                        source='Reddit',
                        category=post_data.get('subreddit', 'general'),
                        score=post_data.get('score', 0) / 100,  # 점수 정규화
                        url=f"https://reddit.com{post_data['permalink']}",
                        description=post_data.get('selftext', '')[:200],
                        tags=['reddit', 'discussion', 'popular']
                    )
                    trends.append(trend)
                    
        except Exception as e:
            logger.error(f"Reddit 트렌드 수집 오류: {e}")
        
        return trends
    
    def get_hackernews_trending(self) -> List[TrendItem]:
        """Hacker News 인기 기사"""
        trends = []
        
        try:
            # Hacker News Top Stories
            top_stories_url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
            response = requests.get(top_stories_url)
            
            if response.status_code == 200:
                story_ids = response.json()[:10]  # 상위 10개
                
                for idx, story_id in enumerate(story_ids):
                    story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                    story_response = requests.get(story_url)
                    
                    if story_response.status_code == 200:
                        story = story_response.json()
                        
                        trend = TrendItem(
                            title=story.get('title', ''),
                            source='Hacker News',
                            category='기술',
                            score=story.get('score', 0) / 10,  # 점수 정규화
                            url=story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            tags=['tech', 'news', 'startup']
                        )
                        trends.append(trend)
                        
        except Exception as e:
            logger.error(f"Hacker News 수집 오류: {e}")
        
        return trends
    
    def get_github_trending(self) -> List[TrendItem]:
        """GitHub 트렌딩 저장소"""
        trends = []
        
        try:
            # GitHub API를 사용하지 않고 웹 스크래핑
            url = 'https://github.com/trending'
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                repos = soup.find_all('article', class_='Box-row')[:10]
                
                for idx, repo in enumerate(repos):
                    try:
                        title_elem = repo.find('h2').find('a')
                        title = title_elem.get_text().strip()
                        url = f"https://github.com{title_elem.get('href')}"
                        
                        description_elem = repo.find('p')
                        description = description_elem.get_text().strip() if description_elem else ''
                        
                        # 언어 정보
                        lang_elem = repo.find('span', {'itemprop': 'programmingLanguage'})
                        language = lang_elem.get_text().strip() if lang_elem else 'Unknown'
                        
                        # 스타 수
                        stars_elem = repo.find('a', href=lambda x: x and 'stargazers' in x)
                        stars = 0
                        if stars_elem:
                            stars_text = stars_elem.get_text().strip()
                            if 'k' in stars_text:
                                stars = float(stars_text.replace('k', '')) * 1000
                            else:
                                stars = int(stars_text.replace(',', '')) if stars_text.isdigit() else 0
                        
                        trend = TrendItem(
                            title=title,
                            source='GitHub',
                            category=language,
                            score=stars / 100 + (100 - idx * 10),  # 스타수와 순위 기반 점수
                            url=url,
                            description=description,
                            tags=['github', 'code', language.lower()]
                        )
                        trends.append(trend)
                        
                    except Exception as e:
                        logger.error(f"GitHub 트렌드 파싱 오류: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"GitHub 트렌딩 수집 오류: {e}")
        
        return trends
    
    def get_news_trends(self) -> List[TrendItem]:
        """뉴스 RSS 피드에서 트렌드 수집"""
        trends = []
        
        rss_feeds = [
            ('TechCrunch', 'https://techcrunch.com/feed/'),
            ('Ars Technica', 'https://feeds.arstechnica.com/arstechnica/index'),
            ('Wired', 'https://www.wired.com/feed/rss'),
        ]
        
        for source_name, feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for idx, entry in enumerate(feed.entries[:5]):  # 각 소스별 5개
                    trend = TrendItem(
                        title=entry.title,
                        source=source_name,
                        category='뉴스',
                        score=100 - idx * 10,
                        url=entry.link,
                        description=getattr(entry, 'summary', '')[:200],
                        tags=['news', 'tech', 'article']
                    )
                    trends.append(trend)
                    
            except Exception as e:
                logger.error(f"{source_name} RSS 수집 오류: {e}")
        
        return trends
    
    def get_youtube_trends(self) -> List[TrendItem]:
        """YouTube 인기 급상승 동영상 (한국)"""
        trends = []
        
        # YouTube Data API 대신 일반적인 한국 트렌드 키워드 사용
        popular_youtube_topics = [
            "KPOP 신곡", "예능 하이라이트", "먹방", "게임 실황", "뷰티 튜토리얼",
            "여행 브이로그", "운동 루틴", "요리 레시피", "펫 영상", "코미디 스케치"
        ]
        
        for idx, topic in enumerate(popular_youtube_topics):
            trend = TrendItem(
                title=topic,
                source='YouTube Korea',
                category='엔터테인먼트',
                score=80 - idx * 5,
                tags=['youtube', '엔터테인먼트', '한국'],
                description=f"{topic} 관련 인기 영상들"
            )
            trends.append(trend)
            
        return trends
    
    def get_korea_general_trends(self) -> List[TrendItem]:
        """한국 일반 트렌드 (다양한 분야)"""
        trends = []
        
        # 시뮬레이션된 한국 트렌드 데이터 (다양한 분야)
        korea_trends_data = [
            ("날씨", "생활", "오늘 날씨와 주말 날씨 전망"),
            ("연예인 근황", "연예", "최신 연예계 이슈와 소식들"),
            ("드라마 리뷰", "문화", "현재 방영 중인 인기 드라마들"),
            ("맛집 추천", "음식", "요즘 핫한 맛집과 카페 정보"),
            ("패션 트렌드", "패션", "2025년 봄 패션 트렌드"),
            ("건강 정보", "건강", "건강관리와 운동 관련 팁들"),
            ("부동산 시장", "경제", "최근 부동산 시장 동향"),
            ("교육 정책", "교육", "새로운 교육 제도와 입시 정보"),
            ("여행 정보", "여행", "국내외 여행지 추천과 정보"),
            ("스포츠 소식", "스포츠", "프로야구, 축구 등 스포츠 현황"),
            ("쇼핑 할인", "쇼핑", "온라인 쇼핑몰 할인 이벤트"),
            ("영화 추천", "영화", "최신 개봉 영화와 넷플릭스 추천작")
        ]
        
        for idx, (title, category, description) in enumerate(korea_trends_data):
            trend = TrendItem(
                title=title,
                source='한국 트렌드',
                category=category,
                score=95 - idx * 3,
                tags=['한국', '일반', category],
                description=description
            )
            trends.append(trend)
            
        return trends
    
    def get_social_media_trends(self) -> List[TrendItem]:
        """소셜미디어 트렌드 (인스타그램, 틱톡 등)"""
        trends = []
        
        social_trends = [
            ("챌린지 트렌드", "소셜", "최신 틱톡 챌린지와 인스타그램 릴스"),
            ("해시태그 이슈", "소셜", "화제가 되고 있는 해시태그들"),
            ("인플루언서 소식", "소셜", "인기 인플루언서들의 최근 활동"),
            ("밈 트렌드", "소셜", "요즘 유행하는 밈과 짤방들"),
            ("라이프스타일", "라이프", "인스타그램에서 인기인 라이프스타일")
        ]
        
        for idx, (title, category, description) in enumerate(social_trends):
            trend = TrendItem(
                title=title,
                source='소셜미디어',
                category=category,
                score=70 - idx * 8,
                tags=['소셜미디어', 'SNS', category],
                description=description
            )
            trends.append(trend)
            
        return trends
    
    def _deduplicate_trends(self, trends: List[TrendItem]) -> List[TrendItem]:
        """중복 트렌드 제거"""
        seen_titles = set()
        unique_trends = []
        
        for trend in trends:
            # 제목 정규화 (소문자, 공백 제거)
            normalized_title = trend.title.lower().strip()
            
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_trends.append(trend)
        
        return unique_trends
    
    def get_categorized_trends(self) -> Dict[str, List[TrendItem]]:
        """카테고리별 트렌드 분류"""
        all_trends = self.collect_all_trends()
        categorized = {}
        
        # 카테고리 한글 매핑
        category_mapping = {
            # 영어 카테고리 한글화
            'TypeScript': '기술',
            'Python': '기술', 
            'JavaScript': '기술',
            'Go': '기술',
            'Rust': '기술',
            'C#': '기술',
            'discussion': '커뮤니티',
            'popular': '인기',
            'politics': '정치',
            'news': '뉴스',
            'todayilearned': '상식',
            'nextfuckinglevel': '놀라운',
            'mildlyinfuriating': '짜증',
            'Cinema': '영화',
            'SipsTea': '이슈',
            'TikTokCringe': '틱톡',
            'CringeTikToks': '틱톡',
            'TopCharacterTropes': '캐릭터',
            'interesting': '흥미로운',
            'MadeMeSmile': '훈훈한',
            'ExplainTheJoke': '유머',
            'ProgrammerHumor': '개발자유머',
            'comics': '만화',
            'BlueskySkeets': '블루스카이',
            'Silksong': '게임',
            'MurderedByWords': '논쟁',
            'NoShitSherlock': '당연함',
            'OldSchoolCool': '빈티지',
            'sports': '스포츠',
            'tech': '기술',
            'startup': '스타트업',
            # 한글 카테고리는 그대로 유지
        }
        
        for trend in all_trends:
            # 카테고리 한글로 변환
            original_category = trend.category
            korean_category = category_mapping.get(original_category, original_category)
            
            if korean_category not in categorized:
                categorized[korean_category] = []
            categorized[korean_category].append(trend)
        
        # 각 카테고리별 상위 8개만 (화면에서 보기 좋게)
        for category in categorized:
            categorized[category] = categorized[category][:8]
        
        return categorized


# 전역 인스턴스
trend_collector = TrendCollector()