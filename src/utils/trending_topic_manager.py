"""
트렌디한 주제 관리 및 생성 모듈
각 사이트별 컨셉에 맞는 2025년 8월 최신 트렌딩 주제 관리
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re

class TrendingTopicManager:
    """트렌디한 주제 관리 클래스 - 2025년 8월 최신 업데이트"""
    
    def __init__(self):
        self.base_topics = self._load_base_topics()
        self.trending_keywords = []
        
    def _load_base_topics(self) -> Dict:
        """사이트별 기본 컨셉 주제들 로드 - 2025년 8월 최신 트렌딩 이슈 반영"""
        return {
            'unpre': {
                'primary': '기술/디지털',
                'secondary': '교육/자기계발',
                'trending_topics': {
                    '기술/디지털': [
                        # 2025년 8월 최신 기술 트렌드
                        "Claude 3.5 Sonnet vs GPT-4o 성능 비교",
                        "GitHub Copilot Workspace 정식 출시 리뷰",
                        "Rust로 만드는 웹 어셈블리 성능 최적화",
                        "Anthropic Constitutional AI 실무 적용",
                        "Vercel v0 AI 코딩 도구 완전 가이드",
                        "Bun 1.1 JavaScript 런타임 벤치마크",
                        "Svelte 5 Runes 완전 정복",
                        "Astro 4.0 아일랜드 아키텍처 마스터",
                        "Deno 2.0 Node.js 호환성 분석",
                        "Cloudflare Workers AI 엣지 컴퓨팅",
                        "Meta Llama 3.1 405B 로컬 실행 가이드",
                        "Google Gemini 1.5 Pro 2M 컨텍스트 활용",
                        "Ollama 오픈소스 LLM 셀프 호스팅",
                        "Cursor AI IDE 생산성 200% 향상법",
                        "Replit Agent AI 페어 프로그래밍",
                        "Linear 앱 사용자 경험 분석",
                        "Figma Dev Mode 디자인-개발 연결",
                        "Supabase Edge Functions 실전 활용"
                    ],
                    '교육/자기계발': [
                        # 개발자 커리어 최신 트렌드
                        "2025년 개발자 연봉 현실과 협상법",
                        "AI 시대 개발자 살아남기 전략",
                        "원격근무 개발팀 협업 노하우",
                        "주니어 개발자 성장 로드맵 2025",
                        "시니어 개발자 멘토링 가이드",
                        "테크 리드 역할과 책임 완전 분석",
                        "개발자 사이드 프로젝트 수익화",
                        "코딩 부트캠프 vs 컴공 학위 비교",
                        "GitHub 포트폴리오 완벽 만들기",
                        "개발자 개인 브랜딩 전략",
                        "테크 컨퍼런스 발표 준비 가이드",
                        "오픈소스 기여로 커리어 업그레이드",
                        "개발자 영어 실력 향상 방법",
                        "리더십 있는 개발자 되는 법",
                        "번아웃 극복과 워라밸 찾기"
                    ]
                }
            },
            'untab': {
                'primary': '재정/투자',
                'secondary': '라이프스타일',
                'trending_topics': {
                    '재정/투자': [
                        # 2025년 8월 투자 트렌드
                        "한국 증시 3300선 돌파 후 전략",
                        "미국 기준금리 인하 수혜주 분석",
                        "AI 반도체 투자 버블론과 현실",
                        "원/달러 환율 1300원대 대응법",
                        "2차전지 관련주 급등 이유와 전망",
                        "부동산 PF 부실 투자 리스크 관리",
                        "개인연금 세제 개편안 완전 분석",
                        "K-뱅크 청년 우대 적금 비교",
                        "비트코인 ETF vs 현물 투자 비교",
                        "ESG 투자 의무화 대응 전략",
                        "인플레이션 재부상 대비 자산배분",
                        "일본 여행 엔화 환전 타이밍",
                        "해외주식 양도세 과세 완전 가이드",
                        "ISA 계좌 3000만원 한도 활용법",
                        "중국 부동산 불황 국내 영향 분석",
                        "노인장기요양보험료 인상 대비법",
                        "전세사기 피해 예방 체크리스트"
                    ],
                    '라이프스타일': [
                        # 2025년 8월 라이프스타일 트렌드
                        "무더위 극복 홈 쿨링 아이템",
                        "여름휴가 국내 대체 여행지",
                        "에어컨 없이 시원하게 보내는 법",
                        "방학철 아이와 함께 체험활동",
                        "여름 다이어트 성공 식단 관리",
                        "휴가철 펜션 예약 꿀팁",
                        "여름 피부 트러블 완전 해결법",
                        "물놀이 안전사고 예방 가이드",
                        "캠핑장 예약 전쟁 승리 전략",
                        "여름 장마철 습도 관리법",
                        "휴가 후 일상 복귀 노하우",
                        "여름 야외 활동 필수템",
                        "폭염 속 반려동물 케어",
                        "여름휴가 짐 싸기 체크리스트",
                        "무더위 속 홈가드닝 관리법"
                    ]
                }
            },
            'skewese': {
                'primary': '건강/웰니스',
                'secondary': '역사/문화',
                'trending_topics': {
                    '건강/웰니스': [
                        # 2025년 8월 건강 트렌드
                        "폭염 속 열사병 예방과 응급처치",
                        "여름철 식중독 예방 완전 가이드",
                        "에어컨병 증상과 예방법",
                        "무더위 속 수분 보충 올바른 방법",
                        "여름 휴가철 비만 예방 전략",
                        "자외선 차단 선크림 선택법",
                        "여름철 피부 알레르기 대처법",
                        "물놀이 후 외이도염 예방",
                        "폭염 속 노인 건강 관리법",
                        "여름 감기와 냉방병 구별법",
                        "휴가철 불규칙한 생활 리셋",
                        "여름철 운동 시간대와 강도 조절",
                        "열대야 불면증 해결법",
                        "여름 다이어트 부작용 주의사항",
                        "휴가 후 후유증 극복 방법",
                        "여름철 비타민 D 부족 대처법",
                        "폭염 속 혈압 관리 주의사항"
                    ],
                    '역사/문화': [
                        # 2025년 8월 역사/문화 이슈
                        "광복절 79주년 잊혀진 독립운동가",
                        "일제강점기 강제징용 배상 판결 의미",
                        "한국 전통 음식의 여름 보양식 역사",
                        "조선시대 더위 나는 방법과 지혜",
                        "삼국시대 왕릉 발굴 최신 성과",
                        "고구려 고분벽화 복원 기술 발전",
                        "백제 문화재 유네스코 등재 의의",
                        "신라 금관 제작 기법 재현 성공",
                        "한국 전쟁 참전용사 증언 기록화",
                        "일제강점기 문화재 반환 현황",
                        "조선왕조실록 디지털화 프로젝트",
                        "한글 창제 원리 최신 연구 결과",
                        "전통 건축 온돌 시스템의 과학성",
                        "한국 전통 의학 현대적 재해석",
                        "무형문화재 전승자 고령화 대책"
                    ]
                }
            },
            'tistory': {
                'primary': '엔터테인먼트',
                'secondary': '트렌드/이슈',
                'trending_topics': {
                    '엔터테인먼트': [
                        # 2025년 8월 엔터테인먼트 핫이슈
                        "NewJeans 일본 도쿄돔 콘서트 화제",
                        "(여자)아이들 월드투어 티켓팅 대란",
                        "세븐틴 미국 스타디움 투어 성공",
                        "IVE 새 앨범 빌보드 차트 진입",
                        "방탄소년단 완전체 복귀 루머 분석",
                        "aespa AI 아바타 콘서트 혁신",
                        "스트레이 키즈 해외 팬클럽 급성장",
                        "LE SSERAFIM 브랜드 가치 상승",
                        "ITZY 새로운 컨셉 변화 화제",
                        "에스파 가상현실 팬미팅 성공",
                        "드라마 '선재 업고 튀어' 글로벌 인기",
                        "웹툰 원작 드라마 제작 러쉬",
                        "넷플릭스 한국 콘텐츠 투자 확대",
                        "예능 프로그램 해외 포맷 수출 증가",
                        "K-콘텐츠 아시아 시장 점유율 상승"
                    ],
                    '트렌드/이슈': [
                        # 2025년 8월 사회적 트렌드
                        "MZ세대 주식 투자 패턴 변화",
                        "AI 면접 도입 기업 증가 현상",
                        "원격근무 정착화와 부작용",
                        "개인방송 수익 구조 다양화",
                        "숏폼 콘텐츠 중독 사회 문제화",
                        "Z세대 소비 패턴 완전 분석",
                        "디지털 노마드 라이프 현실과 한계",
                        "메타버스 활용 교육 확산",
                        "NFT 아트 시장 회복 조짐",
                        "웹3.0 기반 서비스 급증",
                        "환경 의식 소비 트렌드 강화",
                        "인플루언서 마케팅 규제 강화",
                        "가상화폐 결제 서비스 확산",
                        "구독 경제 피로감 확산",
                        "리셀 시장 성장과 부작용"
                    ]
                }
            }
        }
    
    def add_trending_topic(self, site: str, category: str, topic: str, keywords: List[str] = None):
        """실시간 트렌딩 주제 추가"""
        if site not in self.base_topics:
            raise ValueError(f"Unknown site: {site}")
            
        if 'trending_topics' not in self.base_topics[site]:
            self.base_topics[site]['trending_topics'] = {}
            
        if category not in self.base_topics[site]['trending_topics']:
            self.base_topics[site]['trending_topics'][category] = []
            
        # 중복 체크 후 추가
        existing_topics = self.base_topics[site]['trending_topics'][category]
        if topic not in existing_topics:
            self.base_topics[site]['trending_topics'][category].insert(0, topic)
            
            # 최신 50개만 유지
            if len(existing_topics) > 50:
                self.base_topics[site]['trending_topics'][category] = existing_topics[:50]
                
        print(f"[TRENDING] {site} - {category}에 새 주제 추가: {topic}")
        return True
    
    def get_trending_topics(self, site: str, category: str, limit: int = 10) -> List[str]:
        """사이트별 카테고리 트렌딩 주제 조회"""
        if site not in self.base_topics:
            return []
            
        trending_topics = self.base_topics[site].get('trending_topics', {})
        return trending_topics.get(category, [])[:limit]
    
    def get_daily_topics(self, site: str, date: datetime.date) -> Tuple[Dict, Dict]:
        """특정 날짜의 사이트별 2개 주제 반환 (primary + secondary)"""
        if site not in self.base_topics:
            raise ValueError(f"Unknown site: {site}")
        
        site_config = self.base_topics[site]
        primary_category = site_config['primary']
        secondary_category = site_config['secondary']
        
        # 트렌딩 주제 조회
        primary_trending = self.get_trending_topics(site, primary_category, 20)
        secondary_trending = self.get_trending_topics(site, secondary_category, 20)
        
        # 날짜 기반 시드로 주제 선택 (일관성 보장)
        day_seed = (date.year * 1000 + date.timetuple().tm_yday) % 1000
        
        # Primary 주제 선택 (트렌딩 우선)
        if primary_trending:
            primary_idx = day_seed % len(primary_trending)
            primary_topic_text = primary_trending[primary_idx]
        else:
            # 기본 주제 폴백
            primary_topic_text = f"{site} 기본 주제"
            
        # Secondary 주제 선택 (트렌딩 우선)  
        if secondary_trending:
            secondary_idx = (day_seed + 1) % len(secondary_trending)
            secondary_topic_text = secondary_trending[secondary_idx]
        else:
            # 기본 주제 폴백
            secondary_topic_text = f"{site} 기본 주제"
        
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
        """전체 사이트별 주제 요약 반환"""
        summary = {}
        for site, config in self.base_topics.items():
            trending_topics = config.get('trending_topics', {})
            summary[site] = {
                'primary_category': config['primary'],
                'secondary_category': config['secondary'],
                'primary_topics_count': len(trending_topics.get(config['primary'], [])),
                'secondary_topics_count': len(trending_topics.get(config['secondary'], [])),
                'latest_primary': trending_topics.get(config['primary'], [])[:3],
                'latest_secondary': trending_topics.get(config['secondary'], [])[:3]
            }
        return summary

# 전역 인스턴스
trending_topic_manager = TrendingTopicManager()