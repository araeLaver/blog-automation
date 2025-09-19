"""
자동 주간계획 생성기 - 실시간 트렌드와 수익률 데이터 기반 주간계획 자동 생성
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.utils.trend_collector import TrendCollector
from src.utils.postgresql_database import PostgreSQLDatabase
from src.generators.content_generator import ContentGenerator
from src.utils.high_traffic_keyword_manager import HighTrafficKeywordManager
from src.utils.profit_keyword_manager import ProfitKeywordManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfitWeeklyPlanner:
    """자동 주간계획 생성기"""
    
    def __init__(self):
        self.trend_collector = TrendCollector()
        self.db = PostgreSQLDatabase()
        self.content_generator = ContentGenerator()
        self.high_traffic_manager = HighTrafficKeywordManager()
        self.profit_manager = ProfitKeywordManager()
        
        # 사이트별 선호 카테고리
        self.site_preferences = {
            'unpre': ['기술', 'AI/머신러닝', '프로그래밍', '스타트업', '투자'],
            'untab': ['라이프스타일', '여행', '음식', '건강', '취미'],
            'skewese': ['비즈니스', '마케팅', '자기계발', '경제', '트렌드'],
            'tistory': ['일반', '후기', '정보', '팁', '가이드']
        }
        
    def get_trending_topics(self) -> List[Dict]:
        """🔥 2025년 실시간 검색 트렌드 + SEO 최적화 키워드 수집"""
        all_topics = []

        try:
            # 1. 최고 수익성 + 트렌드 키워드 (2025 검색 트렌드 반영)
            ultra_profit_keywords = self.profit_manager.get_ultra_profit_keywords(15)
            for kw in ultra_profit_keywords:
                all_topics.append({
                    'title': kw['keyword'],
                    'category': 'ultra_profit',
                    'score': kw['profit_score'],
                    'source': 'ultra_profit',
                    'volume': kw['volume'],
                    'cpc': kw['cpc'],
                    'profit_score': kw['profit_score']
                })
            logger.info(f"2025 트렌드 키워드 {len(ultra_profit_keywords)}개 수집 (평균 검색량: {sum([kw['volume'] for kw in ultra_profit_keywords])//len(ultra_profit_keywords)//1000}K)")
            
            # 2. 실시간 검색 급상승 키워드 (현재 월 특화)
            month_profit_keywords = self.profit_manager.get_current_month_profit_keywords(10)
            for kw in month_profit_keywords:
                all_topics.append({
                    'title': kw['keyword'],
                    'category': 'trending_monthly',
                    'score': kw['profit_score'],
                    'source': 'monthly_trending',
                    'volume': kw['volume'],
                    'cpc': kw['cpc'],
                    'profit_score': kw['profit_score']
                })
            logger.info(f"1월 트렌드 키워드 {len(month_profit_keywords)}개 수집")
            
            # 3. 롭테일 키워드 + 제휴 가능 상품
            for category in ['금융', '쇼핑', '여행', '교육']:
                affiliate_keywords = self.profit_manager.get_affiliate_keywords_by_category(category, 3)
                for kw in affiliate_keywords:
                    all_topics.append({
                        'title': kw['keyword'],
                        'category': 'longtail_seo',
                        'score': min(99, kw['total_profit'] // 1000),
                        'source': f'longtail_{category}',
                        'volume': kw['volume'],
                        'cpc': kw['cpc'],
                        'commission': kw.get('commission', 0),
                        'profit_score': min(99, kw['total_profit'] // 1000)
                    })
            logger.info(f"롭테일 SEO 키워드 추가 완료")
            
            # 4. Google/네이버 실시간 트렌드 병합
            try:
                trends = self.trend_collector.collect_all_trends()
                for trend in trends[:10]:  # 실시간 트렌드 활용
                    # 트렌드에 SEO 키워드 결합
                    seo_title = self._enhance_with_seo_keywords(trend.title)
                    all_topics.append({
                        'title': seo_title,
                        'category': 'realtime_trend',
                        'score': 85,  # 실시간 트렌드 점수
                        'source': 'realtime_search',
                        'volume': 200000,  # 트렌드 기본 검색량
                        'profit_score': 85
                    })
                logger.info(f"실시간 트렌드 {len(trends[:10])}개 추가")
            except:
                logger.warning("실시간 트렌드 수집 실패")
            
            # 🔥 SEO 점수 + 검색량 기준 정렬 (실제 트래픽 예상)
            all_topics.sort(key=lambda x: (x.get('profit_score', 0) * 0.7 + min(x.get('volume', 0)/10000, 100) * 0.3), reverse=True)
            logger.info(f"총 {len(all_topics)}개 주제 SEO 최적화 정렬 완료")

            # 중복 제거 후 상위 30개 선택
            unique_topics = []
            seen_keywords = set()
            for topic in all_topics:
                base_keyword = topic['title'].split()[0]
                if base_keyword not in seen_keywords:
                    unique_topics.append(topic)
                    seen_keywords.add(base_keyword)
                    if len(unique_topics) >= 30:
                        break

            return unique_topics
            
        except Exception as e:
            logger.error(f"수익성 키워드 수집 실패: {e}")
            return self._get_profit_fallback_topics()
    
    def _get_profit_fallback_topics(self) -> List[Dict]:
        """2025년 기본 SEO 키워드 (실패 시 대체용)"""
        return [
            {'title': '무직자 대출 가능한 곳 TOP 10', 'category': 'seo', 'score': 92, 'volume': 850000, 'profit_score': 92},
            {'title': '부업 추천 순위 2025 월 100만원', 'category': 'seo', 'score': 95, 'volume': 920000, 'profit_score': 95},
            {'title': 'ChatGPT 활용법 돈버는 방법', 'category': 'seo', 'score': 90, 'volume': 780000, 'profit_score': 90},
            {'title': '테슬라 주식 전망 2025 매수타이밍', 'category': 'seo', 'score': 88, 'volume': 650000, 'profit_score': 88},
            {'title': '다이어트 보조제 순위 효과 있는', 'category': 'seo', 'score': 85, 'volume': 540000, 'profit_score': 85},
        ]
    
    def _get_fallback_topics(self) -> List[Dict]:
        """트렌드 수집 실패시 대체 주제"""
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        fallback_topics = [
            {'title': f'2025년 {current_month}월 주목해야 할 기술 트렌드', 'category': '기술', 'score': 100},
            {'title': '성공하는 사람들의 아침 루틴 5가지', 'category': '자기계발', 'score': 95},
            {'title': f'{current_month}월 제철 음식으로 건강 챙기기', 'category': '건강', 'score': 90},
            {'title': '부동산 투자 초보자를 위한 가이드', 'category': '투자', 'score': 85},
            {'title': '재택근무 효율성을 높이는 방법', 'category': '라이프스타일', 'score': 80},
            {'title': '인공지능 시대, 살아남는 직업들', 'category': 'AI', 'score': 75},
        ]
        
        return fallback_topics
    
    def categorize_topic_for_site(self, topic: Dict, site: str) -> str:
        """사이트에 맞는 카테고리로 변환"""
        topic_category = topic.get('category', '일반').lower()
        site_prefs = self.site_preferences.get(site, ['일반'])
        
        # 카테고리 매핑
        category_mapping = {
            'technology': '기술',
            'tech': '기술', 
            'ai': 'AI/머신러닝',
            'business': '비즈니스',
            'lifestyle': '라이프스타일',
            'health': '건강',
            'food': '음식',
            'travel': '여행',
            'finance': '투자',
            'programming': '프로그래밍'
        }
        
        mapped_category = category_mapping.get(topic_category, topic_category)
        
        # 사이트 선호도에 맞는 카테고리 찾기
        for pref in site_prefs:
            if pref in mapped_category or mapped_category in pref:
                return pref
                
        return site_prefs[0]  # 기본값
    
    def generate_weekly_plan(self, start_date: datetime = None, target_week: str = 'current') -> Dict:
        """주간계획 생성 - 에러 방지 강화"""
        try:
            if start_date is None:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
            # 이번 주 또는 다음주 월요일 계산 (에러 방지)
            try:
                if target_week == 'next':
                    # 다음주 월요일 계산
                    days_since_monday = start_date.weekday()
                    days_to_next_monday = 7 - days_since_monday
                    start_date = start_date + timedelta(days=days_to_next_monday)
                else:
                    # 이번 주 월요일 계산
                    days_since_monday = start_date.weekday()
                    start_date = start_date - timedelta(days=days_since_monday)
                    
                logger.info(f"계획 생성 대상주: {target_week}, 시작일: {start_date.strftime('%Y-%m-%d')}")
            except Exception as date_calc_error:
                logger.error(f"날짜 계산 에러: {date_calc_error}")
                raise ValueError(f"날짜 계산 실패: {date_calc_error}")
        except Exception as init_error:
            logger.error(f"주간계획 초기화 실패: {init_error}")
            raise
        
        logger.info(f"주간계획 생성 시작: {start_date.strftime('%Y-%m-%d')} ~ {(start_date + timedelta(days=6)).strftime('%Y-%m-%d')}")
        
        # 트렌딩 주제 수집 (강력한 에러 방지)
        try:
            trending_topics = self.get_trending_topics()
            if not trending_topics:
                logger.warning("트렌딩 주제가 없음, 기본 수익성 주제 사용")
                trending_topics = self._get_profit_fallback_topics()
            logger.info(f"{len(trending_topics)}개 트렌딩 주제 수집 완료")
        except Exception as trend_error:
            logger.error(f"트렌딩 주제 수집 실패: {trend_error}")
            logger.info("기본 수익성 주제로 대체")
            trending_topics = self._get_profit_fallback_topics()
        
        sites = ['unpre', 'untab', 'skewese', 'tistory']
        weekly_plan = {
            'week_start': start_date.strftime('%Y-%m-%d'),
            'week_end': (start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'plans': []
        }
        
        # 요일별 계획 생성 (월-일, 7일) - 강력한 에러 방지
        topic_idx = 0
        successful_plans = 0
        
        try:
            for day_offset in range(7):
                try:
                    current_date = start_date + timedelta(days=day_offset)
                    day_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
                    day_name = day_names[day_offset] if day_offset < len(day_names) else f'Day_{day_offset}'
                    
                    # 하루에 모든 사이트(4개)에 포스팅
                    sites_for_day = sites  # 모든 사이트에 매일 포스팅
                    
                    for site in sites_for_day:
                        try:
                            # 🔥 SEO 최적화 주제 선택 (모든 사이트 공통)
                            if topic_idx >= len(trending_topics):
                                topic_idx = 0  # 주제 순환

                            topic = trending_topics[topic_idx]

                            # SEO 카테고리 분류 (검색 트렌드 반영)
                            if 'realtime' in topic.get('source', ''):
                                category = 'trending_now'
                            elif topic.get('profit_score', 0) >= 90:
                                category = 'top_search'
                            elif topic.get('profit_score', 0) >= 80:
                                category = 'popular'
                            else:
                                category = 'seo_optimized'

                            logger.info(f"{site} SEO 주제 적용 (검색량: {topic.get('volume', 0)//1000}K): {topic['title'][:50]}...")

                            # SEO 최적화 제목 생성
                            try:
                                title = self._create_profit_optimized_title(topic['title'], topic.get('profit_score', 0))
                            except Exception as title_error:
                                logger.warning(f"제목 생성 실패, 원본 사용: {title_error}")
                                title = topic['title']
                            
                            try:
                                keywords = self._extract_keywords(title)
                            except Exception as keyword_error:
                                logger.warning(f"키워드 추출 실패: {keyword_error}")
                                keywords = [topic['title'][:20]]
                            
                            plan_item = {
                                'date': current_date.strftime('%Y-%m-%d'),
                                'day_name': day_name,
                                'site': site,
                                'title': title,
                                'category': category,
                                'original_topic': topic.get('title', 'Unknown Topic'),
                                'trend_score': topic.get('score', 0),
                                'profit_score': topic.get('profit_score', 0),
                                'cpc': topic.get('cpc', 0),
                                'volume': topic.get('volume', 0),
                                'source': topic.get('source', 'Unknown'),
                                'keywords': keywords,
                                'status': 'planned',
                                'priority': 'ultra' if topic.get('profit_score', 0) >= 90 else ('high' if topic.get('profit_score', 0) >= 80 else 'medium')
                            }
                            
                            weekly_plan['plans'].append(plan_item)
                            successful_plans += 1
                            topic_idx += 1
                            
                        except Exception as site_error:
                            logger.error(f"{site} 사이트 계획 생성 실패: {site_error}")
                            continue  # 다음 사이트로 계속
                            
                except Exception as day_error:
                    logger.error(f"{day_name} 계획 생성 실패: {day_error}")
                    continue  # 다음 날로 계속
                    
        except Exception as main_loop_error:
            logger.error(f"주간계획 생성 루프 실패: {main_loop_error}")
            
        # 최소 계획 검증
        if successful_plans == 0:
            logger.error("주간계획 생성 완전 실패, 기본 계획 생성")
            # 기본 계획이라도 만들어야 함
            for i in range(7):
                try:
                    basic_date = start_date + timedelta(days=i)
                    basic_plan = {
                        'date': basic_date.strftime('%Y-%m-%d'),
                        'day_name': ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'][i],
                        'site': 'unpre',
                        'title': f'수익성 키워드 기본 계획 {basic_date.strftime("%m월 %d일")}',
                        'category': 'profit_optimized',
                        'original_topic': '기본 수익성 주제',
                        'profit_score': 70,
                        'status': 'planned',
                        'priority': 'medium'
                    }
                    weekly_plan['plans'].append(basic_plan)
                    successful_plans += 1
                except:
                    continue
        
        logger.info(f"주간계획 생성 완료: {len(weekly_plan['plans'])}개 아이템")
        return weekly_plan
    
    def _translate_to_korean(self, title: str) -> str:
        """영어 제목을 한국어로 변환"""
        # 자주 나오는 영어 키워드들을 한국어로 매핑
        translations = {
            'AI': 'AI',
            'artificial intelligence': '인공지능',
            'machine learning': '머신러닝',
            'blockchain': '블록체인',
            'cryptocurrency': '암호화폐',
            'bitcoin': '비트코인',
            'technology': '기술',
            'startup': '스타트업',
            'business': '비즈니스',
            'marketing': '마케팅',
            'finance': '금융',
            'investment': '투자',
            'health': '건강',
            'lifestyle': '라이프스타일',
            'travel': '여행',
            'food': '음식',
            'programming': '프로그래밍',
            'development': '개발',
            'web': '웹',
            'mobile': '모바일',
            'cloud': '클라우드',
            'data': '데이터',
            'security': '보안',
            'productivity': '생산성',
            'remote work': '재택근무',
            'social media': '소셜미디어',
            'ecommerce': '전자상거래',
            'education': '교육',
            'learning': '학습',
            'tips': '팁',
            'guide': '가이드',
            'tutorial': '튜토리얼',
            'review': '리뷰',
            'news': '뉴스',
            'trend': '트렌드',
            'future': '미래',
            'innovation': '혁신',
            'digital': '디지털'
        }
        
        # 영어가 포함된 제목인 경우 한국어로 변환 시도
        korean_title = title.lower()
        for eng, kor in translations.items():
            korean_title = korean_title.replace(eng, kor)
            
        # 첫 글자 대문자로 복원 및 정리
        korean_title = korean_title.capitalize()
        
        # 영어 제목이면 한국어 스타일로 재작성
        if not any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in title):
            # 완전 영어 제목인 경우 한국어 주제로 변환
            korean_topics = [
                f"2025년 주목해야 할 {korean_title} 트렌드",
                f"{korean_title} 완벽 가이드",
                f"{korean_title}로 성공하는 방법",
                f"{korean_title} 초보자를 위한 실전 팁",
                f"{korean_title}의 모든 것",
                f"{korean_title} 전문가가 되는 5단계"
            ]
            import random
            return random.choice(korean_topics)
            
        return korean_title.strip()

    def get_today_profit_topics(self):
        """오늘의 수익 최우선 주제 반환"""
        today = datetime.now().date()
        
        # 이번 주 계획 가져오기
        weekday = today.weekday()  
        week_start = today - timedelta(days=weekday)
        
        # 이번 주 계획 찾기 또는 생성
        weekly_plan = self.generate_weekly_plan(week_start)
        
        # 오늘 날짜에 해당하는 계획들 필터링
        today_str = today.strftime('%Y-%m-%d')
        today_topics = []
        
        for plan in weekly_plan.get('plans', []):
            if plan.get('date') == today_str:
                today_topics.append({
                    'site': plan.get('site'),
                    'title': plan.get('title'),
                    'category': plan.get('category', 'profit_optimized'),
                    'keywords': plan.get('keywords', []),
                    'trend_score': plan.get('profit_score', 0)
                })
        
        return today_topics
    
    def _adjust_title_for_site(self, original_title: str, site: str) -> str:
        """사이트별 제목 조정"""
        # 먼저 한국어로 변환
        title = self._translate_to_korean(original_title)
        
        if site == 'unpre':
            # 기술/스타트업 스타일
            if not any(word in title for word in ['기술', '개발', 'AI', '스타트업', 'IT']):
                return f"{title}이 IT 업계에 미치는 영향"
        elif site == 'untab':
            # 라이프스타일 스타일  
            if '방법' not in title and '가이드' not in title and '팁' not in title:
                return f"{title}, 알아야 할 5가지"
        elif site == 'skewese':
            # 비즈니스 스타일
            if '비즈니스' not in title and '전략' not in title and '성공' not in title:
                return f"{title}로 비즈니스 기회 찾기"
        elif site == 'tistory':
            # 일반 블로그 스타일
            if '방법' not in title and '가이드' not in title:
                return f"{title} 완벽 정리"
                
        return title
    
    def _create_profit_optimized_title(self, keyword: str, profit_score: int) -> str:
        """🔥 SEO 최적화 제목 생성 - 2025년 검색 트렌드 반영"""

        # 초고수익 키워드용 SEO 최적화 제목 (profit_score 90+)
        if profit_score >= 90:
            ultra_templates = [
                f"{keyword} TOP 10 순위 (실시간 업데이트) 꼭 알아야 할 팁",
                f"{keyword} 최신 정보 2025년 1월 버전 (전문가 검증)",
                f"{keyword} 가격비교 총정리 | 최대 90% 할인받는 방법",
                f"{keyword} 실사용 후기 모음 (장단점 비교분석) 2025",
                f"{keyword} 완벽가이드 | 10분만에 이해하는 핵심정리",
                f"{keyword} 추천순위 BEST 7 | 실패없는 선택법",
            ]
            return random.choice(ultra_templates)
        
        # 고수익 키워드용 SEO 제목 (profit_score 80-89)
        elif profit_score >= 80:
            high_templates = [
                f"{keyword} 비교분석 2025 | 가성비 1위는?",
                f"{keyword} 완벽정리 | 초보자도 이해하는 A to Z",
                f"{keyword} 추천 TOP 5 (실패없는 선택) 2025년",
                f"{keyword} 총정리 | 장점 단점 솔직한 비교",
                f"{keyword} 가이드 2025 | 5분만에 마스터하기",
            ]
            return random.choice(high_templates)
        
        # 중간 수익 키워드용 SEO 제목 (profit_score 70-79)
        elif profit_score >= 70:
            medium_templates = [
                f"{keyword} 정리 | 꼭 알아야 할 핵심 5가지",
                f"{keyword} 비교 2025 | 어떤게 선택하면 좋을까?",
                f"{keyword} 가이드 | 처음이라면 이것만 알아도 OK",
                f"{keyword} 추천 2025 | 실패하지 않는 팁",
            ]
            return random.choice(medium_templates)
        
        # 기본 수익성 키워드용 SEO 제목 (profit_score 70 미만)
        else:
            basic_templates = [
                f"{keyword} 기초가이드 | 처음 시작하는 분들을 위해",
                f"{keyword} 정보 2025 | 꼭 알아야 할 것들",
                f"{keyword} 이해하기 | 5분 요약정리",
                f"{keyword} 실전가이드 | 바로 적용하는 팁",
            ]
            return random.choice(basic_templates)
    
    def _extract_keywords(self, title: str) -> List[str]:
        """SEO 최적화 키워드 추출"""
        import re
        words = re.findall(r'[가-힣a-zA-Z0-9]+', title)

        # SEO 핵심 키워드 우선 추출
        seo_keywords = []
        priority_words = ['2025', 'TOP', 'BEST', '순위', '비교', '추천', '가이드', '후기', '정리']

        # 우선 키워드 먼저 추가
        for word in words:
            if word in priority_words:
                seo_keywords.append(word)

        # 나머지 주요 키워드
        stopwords = ['이', '가', '을', '를', '의', '에', '와', '과', '로', '으로', '은', '는']
        for word in words:
            if len(word) > 1 and word not in stopwords and word not in seo_keywords:
                seo_keywords.append(word)

        return seo_keywords[:7]  # SEO 키워드 7개
    
    def _enhance_with_seo_keywords(self, title: str) -> str:
        """SEO 키워드로 타이틀 강화"""
        seo_enhancers = ['2025', '최신', '실시간', '업데이트', '총정리']

        # 이미 SEO 키워드가 있는지 확인
        has_seo = any(enhancer in title for enhancer in seo_enhancers)

        if not has_seo:
            # SEO 키워드 추가
            import random
            enhancer = random.choice(['2025 최신', '실시간 업데이트', '2025년 1월'])
            return f"{title} {enhancer}"

        return title

    def save_weekly_plan(self, weekly_plan: Dict) -> bool:
        """주간계획을 데이터베이스에 저장 - 강력한 에러 방지"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                conn = self.db.get_connection()
                if not conn:
                    raise Exception("데이터베이스 연결 실패")
                
                with conn.cursor() as cursor:
                    # 1. 기존 같은 주차 계획이 있는지 확인
                    try:
                        cursor.execute('''
                        SELECT id FROM blog_automation.weekly_plans 
                        WHERE week_start = %s
                        ''', (weekly_plan['week_start'],))
                        
                        existing = cursor.fetchone()
                    except Exception as check_error:
                        logger.warning(f"기존 계획 체크 실패: {check_error}")
                        existing = None
                    
                    # 2. JSON 데이터 검증
                    try:
                        plan_json = json.dumps(weekly_plan, ensure_ascii=False, indent=2)
                        if len(plan_json) > 1000000:  # 1MB 제한
                            logger.warning("계획 데이터가 너무 큼, 압축")
                            # 필요한 데이터만 저장
                            compressed_plan = {
                                'week_start': weekly_plan['week_start'],
                                'week_end': weekly_plan['week_end'],
                                'generated_at': weekly_plan['generated_at'],
                                'plans': weekly_plan['plans'][:28]  # 최대 28개 계획만
                            }
                            plan_json = json.dumps(compressed_plan, ensure_ascii=False)
                    except Exception as json_error:
                        logger.error(f"JSON 변환 실패: {json_error}")
                        return False
                    
                    # 3. 저장 실행
                    if existing:
                        logger.info(f"기존 주간계획 업데이트: {weekly_plan['week_start']}")
                        cursor.execute('''
                        UPDATE blog_automation.weekly_plans 
                        SET plan_data = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE week_start = %s
                        ''', (plan_json, weekly_plan['week_start']))
                    else:
                        logger.info(f"새 주간계획 생성: {weekly_plan['week_start']}")
                        cursor.execute('''
                        INSERT INTO blog_automation.weekly_plans (week_start, week_end, plan_data, created_at)
                        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                        ''', (weekly_plan['week_start'], weekly_plan['week_end'], plan_json))
                    
                    conn.commit()
                    logger.info(f"✅ 주간계획 데이터베이스 저장 완료 ({len(weekly_plan['plans'])}개 항목)")
                    return True
                    
            except Exception as e:
                retry_count += 1
                logger.error(f"주간계획 저장 실패 (시도 {retry_count}/{max_retries}): {e}")
                
                if retry_count == 1:
                    # 첫 실패시 테이블 생성 시도
                    try:
                        logger.info("테이블 생성 시도")
                        self._create_weekly_plans_table()
                        continue  # 재시도
                    except Exception as table_error:
                        logger.error(f"테이블 생성 실패: {table_error}")
                
                if retry_count < max_retries:
                    import time
                    time.sleep(2)  # 2초 대기 후 재시도
                    continue
                else:
                    logger.error("주간계획 저장 최종 실패")
                    return False
    
    def _create_weekly_plans_table(self):
        """weekly_plans 테이블 생성"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS blog_automation.weekly_plans (
                    id SERIAL PRIMARY KEY,
                    week_start DATE NOT NULL,
                    week_end DATE NOT NULL,
                    plan_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(week_start)
                )
                ''')
                conn.commit()
                logger.info("weekly_plans 테이블 생성 완료")
        except Exception as e:
            logger.error(f"테이블 생성 실패: {e}")


def main():
    """메인 실행 함수 - 현재주 수익성 최우선 계획 생성"""
    try:
        planner = ProfitWeeklyPlanner()

        # 🔥 현재주 계획 생성 (수익성 최우선)
        logger.info("🔥 현재주 수익성 최우선 주간계획 생성 시작")
        weekly_plan = planner.generate_weekly_plan(target_week='current')
        
        if not weekly_plan or not weekly_plan.get('plans'):
            logger.error("주간계획 생성 실패 또는 빈 계획")
            return False
            
        logger.info(f"현재주 계획 생성 완료: {len(weekly_plan['plans'])}개 계획")
        
    except Exception as e:
        logger.error(f"주간계획 생성 메인 에러: {e}")
        return False
    
    print("자동 생성된 주간계획:")
    print(f"기간: {weekly_plan['week_start']} ~ {weekly_plan['week_end']}")
    print(f"총 {len(weekly_plan['plans'])}개 포스팅 계획")
    
    print("\n상세 계획:")
    for plan in weekly_plan['plans']:
        print(f"- {plan['date']} ({plan['day_name']}) - {plan['site'].upper()}")
        print(f"  제목: {plan['title']}")
        print(f"  카테고리: {plan['category']} | 우선도: {plan['priority']} | 트렌드점수: {plan['trend_score']}")
        print()
    
    # 데이터베이스에 저장 (강력한 에러 방지)
    try:
        if planner.save_weekly_plan(weekly_plan):
            print("🎉 현재주 수익성 최우선 주간계획이 데이터베이스에 저장되었습니다!")
            logger.info("현재주 주간계획 자동생성 및 저장 완료")
            return True
        else:
            print("❌ 주간계획 저장 실패")
            logger.error("주간계획 저장 실패")
            return False
    except Exception as save_error:
        print(f"❌ 주간계획 저장 중 에러: {save_error}")
        logger.error(f"주간계획 저장 중 에러: {save_error}")
        return False


if __name__ == "__main__":
    main()