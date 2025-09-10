#!/usr/bin/env python3
"""
주간 블로그 계획 생성기
- 수익성 높은 키워드 우선 선정
- 실시간 이슈 반영
- 매일 업데이트되는 주간 계획
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import random
import requests
from typing import List, Dict

class WeeklyBlogPlanner:
    """수익 최적화 주간 블로그 플래너"""
    
    def __init__(self):
        self.keywords_dir = Path("data/keywords")
        self.output_dir = Path("data/weekly_plans")
        self.output_dir.mkdir(exist_ok=True)
        
        # 수익성 높은 키워드 패턴
        self.high_revenue_patterns = {
            '구매의도': ['추천', '순위', '베스트', 'TOP', '비교', '리뷰', '후기', '가격'],
            '정보검색': ['방법', '하는법', '가이드', '팁', '노하우', '설명서'],
            '긴급성': ['2024년', '최신', '새로운', '핫한', '인기', '실시간'],
            '문제해결': ['해결', '고치기', '수리', '오류', '문제', '안될때']
        }
        
        # 실시간 이슈 키워드 (매일 업데이트)
        self.trending_topics = []
        
    def get_realtime_issues(self) -> List[str]:
        """실시간 이슈 가져오기"""
        issues = []
        
        # 현재 날짜 기반 이슈
        today = datetime.now()
        
        # 계절별 이슈
        if today.month in [12, 1, 2]:  # 겨울
            issues.extend(['크리스마스', '연말정산', '신년계획', '다이어트'])
        elif today.month in [3, 4, 5]:  # 봄
            issues.extend(['벚꽃', '봄나들이', '신학기', '이직'])
        elif today.month in [6, 7, 8]:  # 여름
            issues.extend(['휴가', '여행', '에어컨', '다이어트'])
        elif today.month in [9, 10, 11]:  # 가을
            issues.extend(['단풍', '수능', '취업', '연말준비'])
        
        # 요일별 이슈
        weekday = today.weekday()
        if weekday == 0:  # 월요일
            issues.append('월요병')
        elif weekday == 4:  # 금요일
            issues.append('불금')
        elif weekday in [5, 6]:  # 주말
            issues.extend(['주말나들이', '데이트'])
        
        # 특별 이벤트 (예시)
        special_events = {
            '1월': ['새해', '신년'],
            '2월': ['설날', '밸런타인'],
            '3월': ['화이트데이', '신학기'],
            '5월': ['어버이날', '어린이날'],
            '9월': ['추석'],
            '11월': ['수능', '빼빼로데이'],
            '12월': ['크리스마스', '연말']
        }
        
        month_str = f"{today.month}월"
        if month_str in special_events:
            issues.extend(special_events[month_str])
        
        return list(set(issues))  # 중복 제거
    
    def calculate_revenue_score(self, keyword_data: Dict) -> float:
        """수익성 점수 계산"""
        score = 0
        keyword = keyword_data.get('keyword', '')
        search_volume = keyword_data.get('search_volume', 0)
        competition = keyword_data.get('competition', 'Medium')
        
        # 검색량 점수 (최대 40점)
        if search_volume > 50000:
            score += 40
        elif search_volume > 20000:
            score += 30
        elif search_volume > 10000:
            score += 20
        elif search_volume > 5000:
            score += 10
        else:
            score += 5
        
        # 경쟁도 점수 (최대 20점)
        competition_scores = {'Low': 20, 'Medium': 10, 'High': 5}
        score += competition_scores.get(competition, 10)
        
        # 구매의도 키워드 보너스 (최대 30점)
        for pattern in self.high_revenue_patterns['구매의도']:
            if pattern in keyword:
                score += 30
                break
        
        # 긴급성 키워드 보너스 (최대 10점)
        for pattern in self.high_revenue_patterns['긴급성']:
            if pattern in keyword:
                score += 10
                break
        
        # 실시간 이슈 연관 보너스 (최대 20점)
        trending = self.get_realtime_issues()
        for issue in trending:
            if issue in keyword:
                score += 20
                break
        
        return score
    
    def select_weekly_keywords(self, all_keywords: List[Dict]) -> List[Dict]:
        """주간 키워드 선정 (수익성 기준)"""
        # 각 키워드에 수익성 점수 추가
        for kw in all_keywords:
            kw['revenue_score'] = self.calculate_revenue_score(kw)
            
            # 예상 일일 수익 계산
            search_volume = kw.get('search_volume', 1000)
            ctr = 0.02  # 평균 CTR 2%
            cpc = 0.05  # 평균 CPC $0.05
            kw['estimated_daily_revenue'] = (search_volume / 30) * ctr * cpc
        
        # 수익성 점수로 정렬
        sorted_keywords = sorted(all_keywords, 
                               key=lambda x: x['revenue_score'], 
                               reverse=True)
        
        # 상위 7개 선정 (일주일치)
        return sorted_keywords[:7]
    
    def create_weekly_plan(self) -> Dict:
        """주간 블로그 계획 생성"""
        # 모든 키워드 파일 로드
        all_keywords = []
        for file in self.keywords_dir.glob("*_2025-*.json"):
            if 'report' not in file.name:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_keywords.extend(data)
        
        if not all_keywords:
            print("[오류] 키워드 데이터가 없습니다.")
            return None
        
        # 주간 키워드 선정
        weekly_keywords = self.select_weekly_keywords(all_keywords)
        
        # 실시간 이슈
        trending_issues = self.get_realtime_issues()
        
        # 주간 계획 생성
        week_plan = {
            'week_start': datetime.now().strftime('%Y-%m-%d'),
            'week_end': (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d'),
            'trending_issues': trending_issues,
            'total_expected_revenue': sum([kw['estimated_daily_revenue'] for kw in weekly_keywords]) * 7,
            'days': []
        }
        
        # 요일별 할당
        days_korean = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        
        for i, keyword_data in enumerate(weekly_keywords):
            date = datetime.now() + timedelta(days=i)
            
            # 블로그 제목 생성
            title = self.generate_optimized_title(keyword_data, trending_issues)
            
            # 수익화 전략
            monetization = self.get_monetization_strategy(keyword_data)
            
            day_plan = {
                'day': days_korean[i],
                'date': date.strftime('%Y-%m-%d'),
                'keyword': keyword_data['keyword'],
                'title': title,
                'search_volume': keyword_data.get('search_volume', 0),
                'revenue_score': keyword_data['revenue_score'],
                'estimated_revenue': f"${keyword_data['estimated_daily_revenue']:.2f}",
                'content_strategy': {
                    'main_keyword': keyword_data['keyword'],
                    'related_keywords': keyword_data.get('related_keywords', []),
                    'trending_angle': self.get_trending_angle(keyword_data, trending_issues),
                    'content_type': self.determine_content_type(keyword_data),
                    'target_length': '2000-3000자',
                    'images_needed': 3,
                },
                'seo_checklist': {
                    'title_keyword': True,
                    'meta_description': f"{keyword_data['keyword']}의 모든 것. {date.year}년 최신 정보",
                    'h2_tags': f"최소 3개, '{keyword_data['keyword']}' 포함",
                    'keyword_density': '1-2%',
                    'internal_links': '3개 이상',
                    'external_links': '권위있는 사이트 1-2개'
                },
                'monetization': monetization,
                'publishing_time': '오전 9시 (골든타임)',
                'promotion': {
                    'naver_blog': True,
                    'facebook': True,
                    'instagram': True,
                    'community': self.get_target_community(keyword_data)
                }
            }
            
            week_plan['days'].append(day_plan)
        
        # 주간 목표
        week_plan['weekly_goals'] = {
            'traffic_target': sum([kw.get('search_volume', 0) for kw in weekly_keywords]) // 100,
            'revenue_target': f"${week_plan['total_expected_revenue']:.2f}",
            'posts_count': 7,
            'engagement_target': '댓글 10개 이상/글'
        }
        
        return week_plan
    
    def generate_optimized_title(self, keyword_data: Dict, trending_issues: List[str]) -> str:
        """SEO + 클릭률 최적화 제목 생성"""
        keyword = keyword_data['keyword']
        templates = []
        
        # 수익성 높은 제목 템플릿
        if any(word in keyword for word in ['추천', '순위', 'TOP']):
            templates = [
                f"{keyword} BEST 10 | 2024년 12월 최신",
                f"{keyword} 완벽정리 | 전문가 선정",
                f"{keyword} 실구매 후기 | 장단점 비교"
            ]
        elif any(word in keyword for word in ['방법', '하는법', '가이드']):
            templates = [
                f"{keyword} 완벽 가이드 | 초보자도 OK",
                f"{keyword} A to Z | 실패없는 방법",
                f"{keyword} 꿀팁 10가지 | 전문가 노하우"
            ]
        else:
            templates = [
                f"{keyword} 모든 것 | 2024년 완벽정리",
                f"{keyword} 솔직 리뷰 | 실제 경험담",
                f"{keyword} 궁금증 해결 | Q&A 총정리"
            ]
        
        # 트렌딩 이슈 반영
        for issue in trending_issues:
            if issue in keyword:
                templates.append(f"[{issue} 특집] {keyword} 총정리")
                break
        
        return random.choice(templates)
    
    def get_monetization_strategy(self, keyword_data: Dict) -> Dict:
        """키워드별 최적 수익화 전략"""
        keyword = keyword_data['keyword']
        category = keyword_data.get('category', '')
        
        strategy = {
            'primary': [],
            'secondary': [],
            'placement': {}
        }
        
        # 카테고리별 수익화
        if 'IT' in category or '기술' in category:
            strategy['primary'] = ['쿠팡파트너스 (전자기기)', '네이버 브랜드스토어']
            strategy['secondary'] = ['구글 애드센스', '온라인 강의 제휴']
        elif '투자' in category or '경제' in category:
            strategy['primary'] = ['증권사 제휴', '투자 서적 추천']
            strategy['secondary'] = ['구글 애드센스', '경제 뉴스레터']
        elif '건강' in category:
            strategy['primary'] = ['쿠팡파트너스 (건강식품)', '운동기구 추천']
            strategy['secondary'] = ['병원 제휴', '헬스장 할인']
        elif '여행' in category:
            strategy['primary'] = ['여행사 제휴', '호텔 예약 커미션']
            strategy['secondary'] = ['항공사 마일리지', '렌터카 할인']
        else:
            strategy['primary'] = ['구글 애드센스', '쿠팡파트너스']
            strategy['secondary'] = ['네이버 애드포스트', '카카오 애드핏']
        
        strategy['placement'] = {
            '상단': '첫 문단 후 네이티브 광고',
            '중간': '핵심 내용 후 제품 추천',
            '하단': 'CTA 버튼 + 관련 상품',
            '사이드바': '플로팅 배너'
        }
        
        return strategy
    
    def get_trending_angle(self, keyword_data: Dict, trending_issues: List[str]) -> str:
        """트렌딩 관점 제시"""
        keyword = keyword_data['keyword']
        
        for issue in trending_issues:
            if issue in ['크리스마스', '연말']:
                return f"{issue} 시즌 특별 가이드"
            elif issue in ['신년', '새해']:
                return "2024년 새해 목표 달성법"
            elif issue in ['다이어트', '여름']:
                return "여름 대비 특별 전략"
        
        # 기본 트렌딩 앵글
        return "2024년 최신 트렌드 반영"
    
    def determine_content_type(self, keyword_data: Dict) -> str:
        """최적 콘텐츠 타입 결정"""
        keyword = keyword_data['keyword']
        
        if any(word in keyword for word in ['추천', '순위', 'TOP', '베스트']):
            return '리스티클 (순위형)'
        elif any(word in keyword for word in ['방법', '하는법', '가이드']):
            return '하우투 가이드'
        elif any(word in keyword for word in ['리뷰', '후기', '경험']):
            return '상세 리뷰'
        elif any(word in keyword for word in ['비교', 'vs']):
            return '비교 분석'
        else:
            return '정보제공형'
    
    def get_target_community(self, keyword_data: Dict) -> List[str]:
        """타겟 커뮤니티 선정"""
        category = keyword_data.get('category', '')
        communities = []
        
        if 'IT' in category or '기술' in category:
            communities = ['클리앙', '루리웹', 'OKKY']
        elif '투자' in category:
            communities = ['네이버 주식카페', '팍스넷']
        elif '건강' in category:
            communities = ['디시 헬스갤', '네이버 다이어트카페']
        elif '여행' in category:
            communities = ['트립어드바이저', '네이버 여행카페']
        else:
            communities = ['네이버카페', '다음카페']
        
        return communities
    
    def save_weekly_plan(self, plan: Dict) -> Path:
        """주간 계획 저장"""
        if not plan:
            return None
        
        filename = f"weekly_plan_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        print(f"[완료] 주간 블로그 계획 저장: {filepath}")
        
        # 간단한 요약도 텍스트로 저장
        self.save_summary(plan)
        
        return filepath
    
    def save_summary(self, plan: Dict):
        """읽기 쉬운 요약 저장"""
        summary_file = self.output_dir / f"weekly_summary_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"=== 주간 블로그 계획 ({plan['week_start']} ~ {plan['week_end']}) ===\n\n")
            f.write(f"예상 주간 수익: ${plan['total_expected_revenue']:.2f}\n")
            f.write(f"트렌딩 이슈: {', '.join(plan['trending_issues'])}\n\n")
            
            for day in plan['days']:
                f.write(f"[{day['day']}] {day['date']}\n")
                f.write(f"  키워드: {day['keyword']}\n")
                f.write(f"  제목: {day['title']}\n")
                f.write(f"  예상 수익: {day['estimated_revenue']}\n")
                f.write(f"  수익화: {', '.join(day['monetization']['primary'])}\n")
                f.write(f"  발행시간: {day['publishing_time']}\n\n")
            
            f.write(f"\n주간 목표:\n")
            f.write(f"  - 트래픽: {plan['weekly_goals']['traffic_target']}명\n")
            f.write(f"  - 수익: {plan['weekly_goals']['revenue_target']}\n")
            f.write(f"  - 포스팅: {plan['weekly_goals']['posts_count']}개\n")
        
        print(f"[완료] 주간 요약 저장: {summary_file}")

def main():
    """메인 실행"""
    planner = WeeklyBlogPlanner()
    
    # 주간 계획 생성
    print("주간 블로그 계획 생성 중...")
    plan = planner.create_weekly_plan()
    
    if plan:
        # 계획 저장
        planner.save_weekly_plan(plan)
        
        # 결과 출력
        print(f"\n=== 주간 블로그 계획 완료 ===")
        print(f"기간: {plan['week_start']} ~ {plan['week_end']}")
        print(f"예상 주간 수익: ${plan['total_expected_revenue']:.2f}")
        print(f"트렌딩 이슈: {', '.join(plan['trending_issues'])}")
        print(f"\n상세 계획은 data/weekly_plans/ 폴더를 확인하세요.")

if __name__ == "__main__":
    main()