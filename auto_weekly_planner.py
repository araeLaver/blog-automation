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

class AutoWeeklyPlanner:
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
        """🔥 수익성 100% 최우선 주제 수집 - 사이트 컨셉 완전 무시"""
        all_topics = []
        
        try:
            # 1. 최고 수익성 키워드 우선 (CPC $10-50, profit_score 90+)
            ultra_profit_keywords = self.profit_manager.get_ultra_profit_keywords(12)
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
            logger.info(f"초고수익 키워드 {len(ultra_profit_keywords)}개 수집 (CPC 평균 ${sum([kw['cpc'] for kw in ultra_profit_keywords])//len(ultra_profit_keywords)/1000:.1f}K)")
            
            # 2. 현재 월 고수익 계절성 키워드
            month_profit_keywords = self.profit_manager.get_current_month_profit_keywords(8)
            for kw in month_profit_keywords:
                all_topics.append({
                    'title': kw['keyword'],
                    'category': 'monthly_profit',
                    'score': kw['profit_score'],
                    'source': 'monthly_profit',
                    'volume': kw['volume'],
                    'cpc': kw['cpc'],
                    'profit_score': kw['profit_score']
                })
            logger.info(f"월별 고수익 키워드 {len(month_profit_keywords)}개 수집")
            
            # 3. 제휴 수익 키워드 (commission 높은 순)
            for category in ['금융', '쇼핑', '여행', '교육']:
                affiliate_keywords = self.profit_manager.get_affiliate_keywords_by_category(category, 2)
                for kw in affiliate_keywords:
                    all_topics.append({
                        'title': kw['keyword'],
                        'category': 'affiliate_profit',
                        'score': min(99, kw['total_profit'] // 1000),  # 총 수익을 점수로 변환
                        'source': f'affiliate_{category}',
                        'volume': kw['volume'],
                        'cpc': kw['cpc'],
                        'commission': kw['commission'],
                        'profit_score': min(99, kw['total_profit'] // 1000)
                    })
            logger.info(f"제휴 수익 키워드 추가 완료")
            
            # 4. 실시간 트렌드는 최후 보완용으로만 (수익성이 떨어질 경우에만)
            if len(all_topics) < 20:
                logger.warning("수익성 키워드가 부족하여 트렌드로 보완")
                trends = self.trend_collector.collect_all_trends()
                korean_trends = []
                for trend in trends[:5]:  # 최소한만
                    korean_trends.append({
                        'title': trend.title,
                        'category': 'low_profit_trend',
                        'score': 30,  # 낮은 수익성 점수
                        'source': 'trend_fallback',
                        'volume': 50000,  # 추정치
                        'profit_score': 30
                    })
                all_topics.extend(korean_trends)
            
            # 🔥 수익성 점수 기준으로만 정렬 (volume, 트렌드 점수 무시)
            all_topics.sort(key=lambda x: x.get('profit_score', 0), reverse=True)
            logger.info(f"총 {len(all_topics)}개 주제 수익성 기준 정렬 완료")
            
            # 상위 25개만 선택 (모두 고수익)
            return all_topics[:25]
            
        except Exception as e:
            logger.error(f"수익성 키워드 수집 실패: {e}")
            return self._get_profit_fallback_topics()
    
    def _get_profit_fallback_topics(self) -> List[Dict]:
        """수익성 키워드 수집 실패시 최소한의 수익성 보장 주제"""
        return [
            {'title': '신용대출 금리 비교', 'category': 'profit', 'score': 85, 'volume': 400000, 'profit_score': 85},
            {'title': '부업 추천 순위', 'category': 'profit', 'score': 90, 'volume': 300000, 'profit_score': 90},
            {'title': '자동차보험 비교견적', 'category': 'profit', 'score': 80, 'volume': 350000, 'profit_score': 80},
            {'title': '다이어트 보조제 추천', 'category': 'profit', 'score': 85, 'volume': 250000, 'profit_score': 85},
            {'title': '토익 인강 추천', 'category': 'profit', 'score': 75, 'volume': 200000, 'profit_score': 75},
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
                            # 🔥 사이트 구분 완전 무시, 수익성 최우선 주제만 사용
                            if topic_idx >= len(trending_topics):
                                topic_idx = 0  # 수익성 주제 순환
                            
                            topic = trending_topics[topic_idx]
                            
                            # 수익성 최적화 카테고리로 통일 (사이트별 카테고리 무시)
                            if topic.get('profit_score', 0) >= 90:
                                category = 'ultra_profit'
                            elif topic.get('profit_score', 0) >= 80:
                                category = 'high_profit' 
                            elif topic.get('profit_score', 0) >= 70:
                                category = 'medium_profit'
                            else:
                                category = 'profit_optimized'
                            
                            logger.info(f"{site} 수익성 주제 적용 (점수: {topic.get('profit_score', 0)}): {topic['title'][:50]}...")
                            
                            # 수익성 최적화 제목 생성 (사이트별 구분 없이)
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
        """🔥 수익성 최적화 제목 생성 - CTR과 수익성 최대화"""
        
        # 초고수익 키워드용 강력한 제목 (profit_score 90+)
        if profit_score >= 90:
            ultra_templates = [
                f"{keyword} 완벽 비교 2025년 TOP 순위 숨겨진 혜택까지 총정리",
                f"{keyword} 실제 후기 전문가가 인정한 베스트 선택과 할인 혜택",
                f"{keyword} 가격 비교 최저가 보장과 특별 할인 받는 완벽 가이드",
                f"{keyword} 추천 순위 실사용자 만족도 1위 업체와 혜택 정보",
                f"{keyword} 완전 분석 숨겨진 수수료까지 투명하게 공개",
            ]
            return random.choice(ultra_templates)
        
        # 고수익 키워드용 (profit_score 80-89)  
        elif profit_score >= 80:
            high_templates = [
                f"{keyword} 순위 비교 2025년 베스트 추천과 할인 혜택",
                f"{keyword} 완벽 가이드 실제 이용자 후기와 특가 정보",
                f"{keyword} 추천 리스트 전문가 선정 TOP 5와 할인 받기",
                f"{keyword} 비교 분석 장단점 정리와 최대 혜택 방법",
            ]
            return random.choice(high_templates)
        
        # 중간 수익 키워드용 (profit_score 70-79)
        elif profit_score >= 70:
            medium_templates = [
                f"{keyword} 추천 2025년 인기 순위와 할인 정보",
                f"{keyword} 비교 가이드 실제 후기와 혜택 정리", 
                f"{keyword} 선택 가이드 전문가 추천과 팁",
                f"{keyword} 완벽 정리 2025년 최신 정보",
            ]
            return random.choice(medium_templates)
        
        # 기본 수익성 키워드용 (profit_score 70 미만)
        else:
            basic_templates = [
                f"{keyword} 가이드 2025년 최신 정보",
                f"{keyword} 추천 정리",
                f"{keyword} 완벽 분석",
                f"{keyword} 총정리",
            ]
            return random.choice(basic_templates)
    
    def _extract_keywords(self, title: str) -> List[str]:
        """제목에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용 가능)
        import re
        words = re.findall(r'[가-힣a-zA-Z]+', title)
        
        # 불용어 제거
        stopwords = ['이', '가', '을', '를', '의', '에', '와', '과', '로', '으로', '은', '는', '입니다', '습니다']
        keywords = [word for word in words if len(word) > 1 and word not in stopwords]
        
        return keywords[:5]  # 상위 5개
    
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
    """메인 실행 함수 - 다음주 수익성 최우선 계획 생성"""
    try:
        planner = AutoWeeklyPlanner()
        
        # 🔥 다음주 계획 생성 (수익성 최우선)
        logger.info("🔥 다음주 수익성 최우선 주간계획 생성 시작")
        weekly_plan = planner.generate_weekly_plan(target_week='next')
        
        if not weekly_plan or not weekly_plan.get('plans'):
            logger.error("주간계획 생성 실패 또는 빈 계획")
            return False
            
        logger.info(f"다음주 계획 생성 완료: {len(weekly_plan['plans'])}개 계획")
        
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
            print("🎉 다음주 수익성 최우선 주간계획이 데이터베이스에 저장되었습니다!")
            logger.info("다음주 주간계획 자동생성 및 저장 완료")
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