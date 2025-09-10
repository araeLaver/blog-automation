"""
수익성 기반 키워드 매니저 - 광고 수익, 제휴 수익, CPC가 높은 키워드 중심
"""

from datetime import datetime, date
from typing import List, Dict, Tuple
import calendar
import random

class ProfitKeywordManager:
    def __init__(self):
        """수익성 높은 키워드 데이터 초기화 - CPC, 광고 수익, 제휴 가능성 기준"""
        
        # 최고 수익성 키워드 (CPC $5-50, 제휴 수익 高)
        self.ultra_profit_keywords = [
            # 금융/투자 (CPC $10-50)
            {'keyword': '주식 투자 앱 추천', 'cpc': 45000, 'volume': 300000, 'profit_score': 95},
            {'keyword': '비트코인 거래소 수수료 비교', 'cpc': 42000, 'volume': 250000, 'profit_score': 94},
            {'keyword': '부동산 투자 플랫폼', 'cpc': 38000, 'volume': 200000, 'profit_score': 92},
            {'keyword': '개인연금 추천 순위', 'cpc': 35000, 'volume': 180000, 'profit_score': 90},
            {'keyword': '신용카드 현금화', 'cpc': 50000, 'volume': 150000, 'profit_score': 98},
            
            # 보험 (CPC $15-30)
            {'keyword': '자동차보험 비교견적', 'cpc': 30000, 'volume': 400000, 'profit_score': 89},
            {'keyword': '실비보험 추천', 'cpc': 28000, 'volume': 350000, 'profit_score': 87},
            {'keyword': '운전자보험 순위', 'cpc': 25000, 'volume': 200000, 'profit_score': 85},
            
            # 대출 (CPC $20-40)
            {'keyword': '신용대출 금리 비교', 'cpc': 40000, 'volume': 500000, 'profit_score': 93},
            {'keyword': '전세자금대출 조건', 'cpc': 35000, 'volume': 300000, 'profit_score': 91},
            {'keyword': '개인사업자 대출', 'cpc': 32000, 'volume': 220000, 'profit_score': 88},
            
            # 교육/자격증 (CPC $8-25)
            {'keyword': '토익 인강 추천', 'cpc': 25000, 'volume': 400000, 'profit_score': 86},
            {'keyword': '공무원 인강 순위', 'cpc': 22000, 'volume': 350000, 'profit_score': 84},
            {'keyword': '코딩 부트캠프 비용', 'cpc': 20000, 'volume': 180000, 'profit_score': 82},
            
            # 건강/의료 (CPC $12-35)
            {'keyword': '다이어트 보조제 추천', 'cpc': 35000, 'volume': 300000, 'profit_score': 90},
            {'keyword': '탈모 치료법', 'cpc': 30000, 'volume': 250000, 'profit_score': 88},
            {'keyword': '단백질 보충제 순위', 'cpc': 18000, 'volume': 200000, 'profit_score': 80},
            
            # IT/소프트웨어 (CPC $15-45)
            {'keyword': 'VPN 추천 순위', 'cpc': 45000, 'volume': 180000, 'profit_score': 94},
            {'keyword': '웹호스팅 비교', 'cpc': 25000, 'volume': 120000, 'profit_score': 83},
            {'keyword': '백신 프로그램 추천', 'cpc': 20000, 'volume': 150000, 'profit_score': 81},
            
            # 쇼핑/제품 (CPC $8-30)
            {'keyword': '공기청정기 추천', 'cpc': 30000, 'volume': 400000, 'profit_score': 87},
            {'keyword': '노트북 가성비 순위', 'cpc': 25000, 'volume': 350000, 'profit_score': 85},
            {'keyword': '무선청소기 비교', 'cpc': 22000, 'volume': 280000, 'profit_score': 84},
            
            # 부업/수익창출 (CPC $20-60)
            {'keyword': '부업 추천 순위', 'cpc': 60000, 'volume': 500000, 'profit_score': 99},
            {'keyword': '재택부업 사이트', 'cpc': 45000, 'volume': 300000, 'profit_score': 95},
            {'keyword': '용돈벌이 앱', 'cpc': 35000, 'volume': 250000, 'profit_score': 92},
        ]
        
        # 월별 계절성 고수익 키워드
        self.monthly_profit_keywords = {
            1: [  # 1월 - 연말정산, 다이어트
                {'keyword': '연말정산 환급금 계산', 'cpc': 15000, 'volume': 800000, 'profit_score': 89},
                {'keyword': '다이어트 보조제 신년 할인', 'cpc': 35000, 'volume': 200000, 'profit_score': 92},
                {'keyword': '헬스장 PT 비용', 'cpc': 20000, 'volume': 150000, 'profit_score': 85},
            ],
            2: [  # 2월 - 밸런타인, 이사
                {'keyword': '밸런타인 선물 쇼핑몰', 'cpc': 25000, 'volume': 180000, 'profit_score': 86},
                {'keyword': '이사업체 비용', 'cpc': 30000, 'volume': 250000, 'profit_score': 88},
                {'keyword': '전세대출 한도', 'cpc': 35000, 'volume': 300000, 'profit_score': 90},
            ],
            3: [  # 3월 - 화이트데이, 새학기
                {'keyword': '화이트데이 선물 추천', 'cpc': 22000, 'volume': 200000, 'profit_score': 84},
                {'keyword': '학원비 대출', 'cpc': 28000, 'volume': 180000, 'profit_score': 87},
                {'keyword': '새학기 노트북', 'cpc': 25000, 'volume': 220000, 'profit_score': 86},
            ],
            4: [  # 4월 - 봄 이사, 알레르기
                {'keyword': '이사 비용 계산기', 'cpc': 30000, 'volume': 300000, 'profit_score': 88},
                {'keyword': '알레르기 약 추천', 'cpc': 20000, 'volume': 150000, 'profit_score': 83},
                {'keyword': '공기청정기 필터', 'cpc': 15000, 'volume': 200000, 'profit_score': 81},
            ],
            5: [  # 5월 - 가정의달, 여행
                {'keyword': '가족여행 보험', 'cpc': 25000, 'volume': 180000, 'profit_score': 86},
                {'keyword': '항공료 할인카드', 'cpc': 30000, 'volume': 220000, 'profit_score': 88},
                {'keyword': '렌터카 보험 비교', 'cpc': 22000, 'volume': 200000, 'profit_score': 84},
            ],
            6: [  # 6월 - 여름휴가 준비
                {'keyword': '여행자보험 비교', 'cpc': 28000, 'volume': 250000, 'profit_score': 87},
                {'keyword': '에어컨 전기료', 'cpc': 18000, 'volume': 300000, 'profit_score': 82},
                {'keyword': '휴가대출 금리', 'cpc': 32000, 'volume': 150000, 'profit_score': 89},
            ],
            7: [  # 7월 - 여름휴가 성수기
                {'keyword': '휴가철 항공료 싸게', 'cpc': 35000, 'volume': 400000, 'profit_score': 90},
                {'keyword': '여행용품 할인', 'cpc': 20000, 'volume': 180000, 'profit_score': 83},
                {'keyword': '리조트 할인카드', 'cpc': 25000, 'volume': 200000, 'profit_score': 85},
            ],
            8: [  # 8월 - 예비군, 방학
                {'keyword': '예비군 대신 참석비', 'cpc': 40000, 'volume': 300000, 'profit_score': 93},  # 수익성 극대화
                {'keyword': '방학 알바 추천', 'cpc': 15000, 'volume': 250000, 'profit_score': 81},
                {'keyword': '여름휴가 대출', 'cpc': 30000, 'volume': 120000, 'profit_score': 88},
            ],
            9: [  # 9월 - 추석, 개학
                {'keyword': '추석 선물 할인', 'cpc': 25000, 'volume': 350000, 'profit_score': 86},
                {'keyword': '개학 노트북 할부', 'cpc': 22000, 'volume': 200000, 'profit_score': 84},
                {'keyword': '고속도로 통행료 카드', 'cpc': 18000, 'volume': 180000, 'profit_score': 82},
            ],
            10: [  # 10월 - 가을 시즌
                {'keyword': '독감 예방접종 비용', 'cpc': 20000, 'volume': 200000, 'profit_score': 83},
                {'keyword': '가을 여행 패키지', 'cpc': 28000, 'volume': 180000, 'profit_score': 87},
                {'keyword': '수능 교재 할인', 'cpc': 15000, 'volume': 150000, 'profit_score': 80},
            ],
            11: [  # 11월 - 김장, 연말 준비
                {'keyword': '김장 재료 주문', 'cpc': 12000, 'volume': 200000, 'profit_score': 78},
                {'keyword': '연말 모임 보험', 'cpc': 25000, 'volume': 100000, 'profit_score': 85},
                {'keyword': '블랙프라이데이 카드', 'cpc': 30000, 'volume': 250000, 'profit_score': 88},
            ],
            12: [  # 12월 - 연말, 크리스마스
                {'keyword': '크리스마스 선물 할인', 'cpc': 28000, 'volume': 400000, 'profit_score': 87},
                {'keyword': '연말정산 미리 계산', 'cpc': 15000, 'volume': 300000, 'profit_score': 81},
                {'keyword': '송년회 보험', 'cpc': 22000, 'volume': 80000, 'profit_score': 84},
            ]
        }
        
        # 업종별 제휴 수익 가능성이 높은 키워드
        self.affiliate_keywords = {
            '금융': [
                {'keyword': '카드 발급 혜택 비교', 'cpc': 40000, 'commission': 50000, 'volume': 500000},
                {'keyword': '대출 한도 계산기', 'cpc': 35000, 'commission': 30000, 'volume': 400000},
                {'keyword': '적금 금리 순위', 'cpc': 25000, 'commission': 20000, 'volume': 300000},
            ],
            '쇼핑': [
                {'keyword': '가전제품 할인', 'cpc': 30000, 'commission': 100000, 'volume': 600000},
                {'keyword': '화장품 추천 순위', 'cpc': 25000, 'commission': 80000, 'volume': 450000},
                {'keyword': '건강식품 후기', 'cpc': 35000, 'commission': 120000, 'volume': 300000},
            ],
            '여행': [
                {'keyword': '항공료 최저가', 'cpc': 30000, 'commission': 50000, 'volume': 800000},
                {'keyword': '호텔 할인 예약', 'cpc': 25000, 'commission': 40000, 'volume': 600000},
                {'keyword': '렌터카 할인', 'cpc': 20000, 'commission': 30000, 'volume': 300000},
            ],
            '교육': [
                {'keyword': '온라인 강의 할인', 'cpc': 20000, 'commission': 100000, 'volume': 400000},
                {'keyword': '어학원 수강료', 'cpc': 18000, 'commission': 80000, 'volume': 250000},
                {'keyword': '자격증 시험 교재', 'cpc': 15000, 'commission': 50000, 'volume': 200000},
            ]
        }

    def get_ultra_profit_keywords(self, limit: int = 15) -> List[Dict]:
        """최고 수익성 키워드 반환 - profit_score 90 이상"""
        ultra_keywords = [kw for kw in self.ultra_profit_keywords if kw['profit_score'] >= 90]
        return sorted(ultra_keywords, key=lambda x: x['profit_score'], reverse=True)[:limit]
    
    def get_current_month_profit_keywords(self, limit: int = 10) -> List[Dict]:
        """현재 월의 고수익 키워드"""
        current_month = datetime.now().month
        month_keywords = self.monthly_profit_keywords.get(current_month, [])
        return sorted(month_keywords, key=lambda x: x['profit_score'], reverse=True)[:limit]
    
    def get_affiliate_keywords_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        """업종별 제휴 수익 키워드"""
        category_keywords = self.affiliate_keywords.get(category, [])
        # 수익성 계산: CPC + 제휴수수료
        for kw in category_keywords:
            kw['total_profit'] = kw['cpc'] + kw['commission']
        return sorted(category_keywords, key=lambda x: x['total_profit'], reverse=True)[:limit]
    
    def get_all_profit_keywords_mixed(self, limit: int = 20) -> List[Dict]:
        """모든 수익성 키워드 통합 - profit_score 기준 정렬"""
        all_keywords = []
        
        # 1. 초고수익 키워드
        ultra_keywords = self.get_ultra_profit_keywords(8)
        all_keywords.extend(ultra_keywords)
        
        # 2. 현재 월 고수익 키워드  
        month_keywords = self.get_current_month_profit_keywords(6)
        all_keywords.extend(month_keywords)
        
        # 3. 제휴 키워드
        for category in self.affiliate_keywords.keys():
            affiliate_kws = self.get_affiliate_keywords_by_category(category, 2)
            for kw in affiliate_kws:
                kw['profit_score'] = min(99, (kw['total_profit'] // 1000))  # 수익성 점수 변환
            all_keywords.extend(affiliate_kws)
        
        # 수익성 점수 기준 정렬
        all_keywords = sorted(all_keywords, key=lambda x: x.get('profit_score', 0), reverse=True)
        
        # 중복 제거
        seen_keywords = set()
        unique_keywords = []
        for kw in all_keywords:
            if kw['keyword'] not in seen_keywords:
                seen_keywords.add(kw['keyword'])
                unique_keywords.append(kw)
                
        return unique_keywords[:limit]
    
    def generate_profit_topics_for_any_site(self, target_date: date = None) -> List[Dict]:
        """모든 사이트에 공통 적용할 수익성 최우선 주제 생성"""
        if not target_date:
            target_date = date.today()
            
        # 수익성 키워드 수집
        profit_keywords = self.get_all_profit_keywords_mixed(25)
        
        topics = []
        for kw in profit_keywords:
            # 수익성 기반 제목 생성 (사이트별 구분 없이)
            title = self._create_profit_optimized_title(kw['keyword'])
            
            topics.append({
                'topic': title,
                'keywords': [kw['keyword']],
                'category': 'profit_optimized',  # 모든 주제를 수익 최적화로 통일
                'volume': kw.get('volume', 100000),
                'cpc': kw.get('cpc', 10000),
                'profit_score': kw.get('profit_score', 80),
                'source': 'profit_keyword_manager'
            })
            
        return topics
        
    def _create_profit_optimized_title(self, keyword: str) -> str:
        """수익성 최적화 제목 생성 - 클릭률과 수익성 모두 고려"""
        
        # 고수익 템플릿 (CTR 높은 단어 포함)
        profit_templates = [
            f"{keyword} 완벽 비교 2025년 최신 순위와 숨겨진 혜택 총정리",
            f"{keyword} 실제 후기 솔직 비교와 할인 혜택 받는 법",
            f"{keyword} 가격 비교 전문가가 알려주는 최저가 찾는 방법",
            f"{keyword} 순위 TOP 10 2025년 베스트 선택과 할인 정보",
            f"{keyword} 추천 리스트 실사용자 리뷰와 특가 혜택 모음",
            f"{keyword} 완전 분석 숨겨진 비용까지 투명 공개",
            f"{keyword} 비교 가이드 전문가 추천과 할인 받는 꿀팁",
            f"{keyword} 총정리 2025년 최신 정보와 최대 혜택 방법",
        ]
        
        # 무작위 선택으로 다양성 확보
        return random.choice(profit_templates)