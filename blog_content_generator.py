#!/usr/bin/env python3
"""
키워드 기반 블로그 컨텐츠 자동 생성기
수익화에 최적화된 블로그 포스팅 생성
"""

import json
import os
from datetime import datetime
from pathlib import Path
import random

class BlogContentGenerator:
    """수익화 최적화 블로그 컨텐츠 생성기"""
    
    def __init__(self):
        self.keywords_dir = Path("data/keywords")
        self.output_dir = Path("data/blog_drafts")
        self.output_dir.mkdir(exist_ok=True)
        
        # 수익화 전략별 글 템플릿
        self.templates = {
            'review': {
                'title_format': [
                    "{keyword} 완벽 리뷰 | 실제 사용 후기",
                    "{keyword} 장단점 비교 | 솔직 후기",
                    "{keyword} 구매 가이드 | 가격 비교"
                ],
                'intro': "실제로 사용해본 {keyword}에 대한 솔직한 후기입니다.",
                'sections': ['특징', '장점', '단점', '가격비교', '추천대상', '결론'],
                'monetization': ['쿠팡파트너스', '네이버쇼핑', '애드센스']
            },
            'guide': {
                'title_format': [
                    "{keyword} 완벽 가이드 | 2024년 최신",
                    "{keyword} A to Z | 초보자 가이드",
                    "{keyword} 하는법 | 단계별 가이드"
                ],
                'intro': "{keyword}에 대해 알아야 할 모든 것을 정리했습니다.",
                'sections': ['개요', '준비사항', '단계별가이드', '주의사항', '팁', 'FAQ'],
                'monetization': ['애드센스', '관련상품추천', '온라인강의']
            },
            'comparison': {
                'title_format': [
                    "{keyword} TOP 10 비교 | 2024년",
                    "{keyword} 순위 | 전문가 추천",
                    "{keyword} 베스트 5 | 가성비 비교"
                ],
                'intro': "2024년 최고의 {keyword}를 비교 분석했습니다.",
                'sections': ['선정기준', 'TOP10리스트', '상세비교', '가격비교', '추천순위'],
                'monetization': ['쿠팡파트너스', '제휴마케팅', '애드센스']
            },
            'tips': {
                'title_format': [
                    "{keyword} 꿀팁 10가지 | 전문가 노하우",
                    "{keyword} 성공 비결 | 실전 팁",
                    "{keyword} 노하우 | 초보자 필독"
                ],
                'intro': "{keyword}를 더 잘하기 위한 실전 팁을 공유합니다.",
                'sections': ['기본팁', '고급팁', '실전사례', '주의사항', '추가자료'],
                'monetization': ['애드센스', '전자책판매', '코칭프로그램']
            }
        }
    
    def analyze_keyword_intent(self, keyword):
        """키워드 의도 분석 및 최적 템플릿 선택"""
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ['추천', '순위', 'TOP', '베스트']):
            return 'comparison'
        elif any(word in keyword_lower for word in ['후기', '리뷰', '사용기', '경험']):
            return 'review'
        elif any(word in keyword_lower for word in ['방법', '가이드', '하는법', '튜토리얼']):
            return 'guide'
        elif any(word in keyword_lower for word in ['꿀팁', '노하우', '비결', '팁']):
            return 'tips'
        else:
            return 'guide'  # 기본값
    
    def generate_blog_outline(self, keyword_data):
        """키워드 기반 블로그 아웃라인 생성"""
        keyword = keyword_data['keyword']
        template_type = self.analyze_keyword_intent(keyword)
        template = self.templates[template_type]
        
        # 제목 생성
        title = random.choice(template['title_format']).format(keyword=keyword)
        
        # SEO 최적화 메타 설명
        meta_description = f"{keyword}에 대한 완벽한 가이드. 실제 경험과 전문가 팁을 바탕으로 작성된 {datetime.now().year}년 최신 정보."
        
        # 아웃라인 구성
        outline = {
            'keyword': keyword,
            'title': title,
            'meta_description': meta_description,
            'template_type': template_type,
            'search_volume': keyword_data.get('search_volume', 0),
            'competition': keyword_data.get('competition', 'Medium'),
            'intro': template['intro'].format(keyword=keyword),
            'sections': [],
            'monetization': template['monetization'],
            'seo_tips': self.generate_seo_tips(keyword_data),
            'created_at': datetime.now().isoformat()
        }
        
        # 섹션별 상세 구성
        for section in template['sections']:
            section_detail = {
                'title': section,
                'keywords_to_include': keyword_data.get('related_keywords', [])[:3],
                'word_count_target': 300 if section in ['개요', '결론'] else 500
            }
            outline['sections'].append(section_detail)
        
        return outline
    
    def generate_seo_tips(self, keyword_data):
        """SEO 최적화 팁 생성"""
        keyword = keyword_data['keyword']
        related = keyword_data.get('related_keywords', [])
        
        return {
            'main_keyword': keyword,
            'keyword_density': '1-2%',
            'use_in_title': True,
            'use_in_h2': f"최소 2개 이상의 H2에 '{keyword}' 포함",
            'use_in_first_paragraph': True,
            'use_in_meta': True,
            'related_keywords': related[:5],
            'internal_links': '관련 포스트 3개 이상 링크',
            'external_links': '권위있는 사이트 1-2개 링크',
            'image_alt': f"모든 이미지 alt 텍스트에 '{keyword}' 관련 설명",
            'url_slug': keyword.replace(' ', '-').lower(),
            'target_word_count': '최소 2000자 이상'
        }
    
    def generate_monetization_strategy(self, keyword_data):
        """키워드별 수익화 전략 생성"""
        keyword = keyword_data['keyword']
        category = keyword_data.get('category', '')
        
        strategies = []
        
        # 카테고리별 수익화 전략
        if '투자' in category or '경제' in category:
            strategies.extend([
                '증권사 제휴 링크',
                '투자 관련 도서 추천 (쿠팡파트너스)',
                '재테크 온라인 강의 추천'
            ])
        elif 'IT' in category or '기술' in category:
            strategies.extend([
                '개발 도구 추천 (제휴링크)',
                '온라인 코딩 강의 추천',
                'IT 기기 리뷰 (쿠팡파트너스)'
            ])
        elif '건강' in category:
            strategies.extend([
                '건강기능식품 추천 (쿠팡파트너스)',
                '운동기구 리뷰',
                '다이어트 프로그램 소개'
            ])
        elif '여행' in category:
            strategies.extend([
                '호텔 예약 제휴 (아고다, 부킹닷컴)',
                '여행용품 추천 (쿠팡파트너스)',
                '렌터카/항공권 비교'
            ])
        
        # 기본 전략
        strategies.extend([
            '구글 애드센스 광고',
            '네이버 애드포스트',
            '관련 전자책 판매'
        ])
        
        return {
            'primary': strategies[:2],
            'secondary': strategies[2:4],
            'placement': {
                'top': '첫 단락 후 광고',
                'middle': '중간 섹션 후 제품 추천',
                'bottom': '결론 전 CTA(Call-to-Action)',
                'sidebar': '사이드바 제휴 배너'
            }
        }
    
    def create_content_calendar(self, keywords_list, days=30):
        """30일 컨텐츠 캘린더 생성"""
        calendar = []
        
        # 검색량 높은 순으로 정렬
        sorted_keywords = sorted(keywords_list, 
                                key=lambda x: x.get('search_volume', 0), 
                                reverse=True)
        
        for i, keyword_data in enumerate(sorted_keywords[:days]):
            day = i + 1
            outline = self.generate_blog_outline(keyword_data)
            monetization = self.generate_monetization_strategy(keyword_data)
            
            calendar_entry = {
                'day': day,
                'date': f"Day {day}",
                'keyword': keyword_data['keyword'],
                'title': outline['title'],
                'template': outline['template_type'],
                'search_volume': keyword_data.get('search_volume', 0),
                'competition': keyword_data.get('competition', 'Medium'),
                'expected_traffic': self.estimate_traffic(keyword_data),
                'monetization': monetization['primary'],
                'outline': outline,
                'priority': 'HIGH' if keyword_data.get('search_volume', 0) > 10000 else 'MEDIUM'
            }
            calendar.append(calendar_entry)
        
        return calendar
    
    def estimate_traffic(self, keyword_data):
        """예상 트래픽 계산"""
        search_volume = keyword_data.get('search_volume', 1000)
        competition = keyword_data.get('competition', 'Medium')
        
        # 경쟁도에 따른 CTR 추정
        ctr_map = {
            'Low': 0.05,    # 5% CTR
            'Medium': 0.02,  # 2% CTR  
            'High': 0.01     # 1% CTR
        }
        
        ctr = ctr_map.get(competition, 0.02)
        estimated_traffic = int(search_volume * ctr)
        
        return {
            'monthly': estimated_traffic,
            'daily': estimated_traffic // 30,
            'potential_revenue': f"${estimated_traffic * 0.01:.2f} - ${estimated_traffic * 0.05:.2f}"
        }
    
    def save_content_plan(self, keyword_data):
        """컨텐츠 계획 저장"""
        outline = self.generate_blog_outline(keyword_data)
        monetization = self.generate_monetization_strategy(keyword_data)
        
        # 완전한 컨텐츠 계획
        content_plan = {
            'keyword_data': keyword_data,
            'outline': outline,
            'monetization': monetization,
            'estimated_traffic': self.estimate_traffic(keyword_data),
            'created_at': datetime.now().isoformat()
        }
        
        # 파일명 생성
        safe_keyword = keyword_data['keyword'].replace(' ', '_').replace('/', '_')
        filename = f"{safe_keyword}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.output_dir / filename
        
        # JSON으로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content_plan, f, ensure_ascii=False, indent=2)
        
        print(f"[완료] 컨텐츠 계획 저장: {filepath}")
        return filepath

def main():
    """메인 실행 함수"""
    generator = BlogContentGenerator()
    
    # 최신 키워드 파일 찾기 (카테고리 파일들)
    keywords_files = [f for f in generator.keywords_dir.glob("*.json") 
                      if not 'report' in f.name and not 'calendar' in f.name]
    if not keywords_files:
        print("[오류] 키워드 파일을 찾을 수 없습니다.")
        return
    
    latest_file = max(keywords_files, key=lambda x: x.stat().st_mtime)
    print(f"키워드 파일 로드: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 데이터 구조 확인
    if isinstance(data, list):
        keywords = data
    elif isinstance(data, dict) and 'keywords' in data:
        keywords = data['keywords']
    else:
        print("[오류] 올바른 키워드 데이터 형식이 아닙니다.")
        return
    
    # 상위 10개 키워드로 컨텐츠 계획 생성
    print(f"\n{len(keywords[:10])}개 키워드로 컨텐츠 계획 생성 중...")
    
    for keyword_data in keywords[:10]:
        generator.save_content_plan(keyword_data)
    
    # 30일 캘린더 생성
    calendar = generator.create_content_calendar(keywords)
    calendar_file = generator.output_dir / f"content_calendar_{datetime.now().strftime('%Y%m%d')}.json"
    
    with open(calendar_file, 'w', encoding='utf-8') as f:
        json.dump(calendar, f, ensure_ascii=False, indent=2)
    
    print(f"\n30일 컨텐츠 캘린더 생성 완료: {calendar_file}")
    
    # 예상 수익 계산
    total_traffic = sum([entry['expected_traffic']['monthly'] for entry in calendar])
    print(f"\n예상 월간 트래픽: {total_traffic:,}명")
    print(f"예상 월 수익: ${total_traffic * 0.01:.2f} ~ ${total_traffic * 0.05:.2f}")

if __name__ == "__main__":
    main()