#!/usr/bin/env python3
"""
완전한 월별 발행 계획표 생성 (1일~말일)
- 8월, 9월 전체 계획표 생성
- 사이트별 듀얼 카테고리 시스템
"""

import psycopg2
from datetime import datetime, date, timedelta
import calendar

# 새로운 사이트별 카테고리 및 주제 풀
SITE_TOPICS = {
    "unpre": {
        "기술/디지털": [
            "ChatGPT API 활용 실전 가이드", "Python 웹 크롤링 마스터하기", "React 18 새로운 기능 완벽 정리",
            "VS Code 생산성 200% 높이는 익스텐션", "Docker로 개발환경 통일하기", "Git 브랜치 전략 실무 가이드",
            "AWS Lambda 서버리스 입문", "TypeScript 타입 시스템 완벽 이해", "Next.js 14 App Router 실전",
            "PostgreSQL vs MySQL 성능 비교", "Redis 캐싱 전략 구현하기", "GraphQL API 설계 베스트 프랙티스",
            "Kubernetes 입문자 가이드", "CI/CD 파이프라인 구축하기", "마이크로서비스 아키텍처 설계",
            "WebSocket 실시간 통신 구현", "JWT 인증 시스템 만들기", "SEO 최적화 체크리스트",
            "웹 성능 최적화 기법", "모바일 반응형 디자인 팁", "AI 코딩 어시스턴트 비교",
            "오픈소스 기여 시작하기", "테스트 주도 개발(TDD) 실전", "클린 코드 작성법",
            "디자인 패턴 실무 적용", "API 문서화 자동화", "보안 취약점 점검 가이드",
            "데이터베이스 인덱싱 전략", "로그 관리 시스템 구축", "모니터링 대시보드 만들기"
        ],
        "교육/자기계발": [
            "토익 900점 3개월 완성 로드맵", "개발자 이력서 작성 완벽 가이드", "코딩테스트 빈출 알고리즘 정리",
            "JLPT N2 한 번에 합격하기", "기술 면접 단골 질문 100선", "영어 회화 스피킹 연습법",
            "개발자 포트폴리오 만들기", "효과적인 코드 리뷰 방법", "토익 스피킹 레벨7 공략법",
            "일본어 한자 효율적으로 외우기", "개발자 연봉 협상 전략", "온라인 강의 플랫폼 비교",
            "시간 관리 앱 추천 TOP 10", "노션으로 업무 효율 높이기", "개발자 커리어 로드맵",
            "비즈니스 영어 이메일 템플릿", "프로그래밍 독학 가이드", "IT 자격증 우선순위 정리",
            "개발자 번아웃 극복법", "효과적인 스터디 그룹 운영", "해외 취업 준비 체크리스트",
            "프리랜서 개발자 시작하기", "개발 블로그 운영 팁", "오픈소스 포트폴리오 만들기",
            "코딩 부트캠프 선택 가이드", "개발자 네트워킹 방법", "기술 서적 추천 리스트",
            "온라인 코딩 교육 사이트 비교", "개발자 건강 관리법", "재택근무 생산성 향상법"
        ]
    },
    "untab": {
        "재정/투자": [
            "2025년 주목할 성장주 TOP 10", "월 100만원 배당금 포트폴리오", "부동산 경매 초보자 가이드",
            "비트코인 ETF 투자 전략", "ISA 계좌 200% 활용법", "미국 주식 세금 절약 팁",
            "리츠(REITs) 투자 완벽 가이드", "금 투자 vs 달러 투자 비교", "P2P 투자 리스크 관리법",
            "연금저축펀드 선택 가이드", "해외 부동산 투자 입문", "공모주 청약 전략",
            "ETF vs 펀드 수익률 비교", "부동산 분양권 투자법", "암호화폐 스테이킹 수익",
            "채권 투자 기초 지식", "원자재 투자 타이밍", "부업으로 월 300만원 벌기",
            "프리랜서 세금 절약법", "소액 투자 앱 비교", "경제 지표 읽는 법",
            "환율 변동 투자 전략", "노후 자금 계획 세우기", "신용등급 올리는 방법",
            "대출 이자 줄이는 팁", "청약통장 활용 전략", "재테크 자동화 시스템",
            "투자 손실 세금 공제", "부동산 세금 완벽 정리", "파이어족 되는 방법"
        ],
        "라이프스타일": [
            "제주도 한달살기 완벽 가이드", "원룸 인테리어 10만원으로 변신", "에어프라이어 만능 레시피 30선",
            "유럽 배낭여행 2주 코스", "미니멀 라이프 시작하기", "홈카페 분위기 만들기",
            "캠핑 초보자 장비 리스트", "반려식물 키우기 입문", "혼밥 맛집 전국 지도",
            "북유럽 스타일 홈 데코", "일본 료칸 여행 추천", "와인 입문자 가이드",
            "홈베이킹 필수 도구", "부산 로컬 맛집 투어", "스마트홈 구축 가이드",
            "향수 선택하는 법", "커피 홈로스팅 입문", "전국 글램핑 명소",
            "혼자 떠나는 국내 여행", "수납 정리 노하우", "계절별 옷장 정리법",
            "홈트레이닝 공간 만들기", "베란다 텃밭 가꾸기", "명품 가방 관리법",
            "에코백 DIY 아이디어", "강아지와 함께 가는 여행지", "홈파티 준비 체크리스트",
            "독서 공간 꾸미기", "향초 브랜드 추천", "차박 여행 준비물"
        ]
    },
    "skewese": {
        "건강/웰니스": [
            "간헐적 단식 16:8 완벽 가이드", "피부 타입별 스킨케어 루틴", "홈트레이닝 4주 프로그램",
            "단백질 보충제 선택 가이드", "수면의 질 높이는 10가지 방법", "글루텐프리 다이어트 효과",
            "요가 초보자 기본 자세", "비타민 D 부족 증상과 해결법", "MBTI별 운동법 추천",
            "저탄고지 식단 일주일 메뉴", "필라테스 vs 요가 비교", "콜라겐 영양제 효과 분석",
            "스트레스 관리 명상법", "체지방 감량 과학적 방법", "근육량 늘리는 식단",
            "피부 미백 홈케어 방법", "탈모 예방 두피 관리법", "눈 건강 지키는 습관",
            "장 건강 프로바이오틱스", "디톡스 주스 레시피", "폼롤러 사용법 완벽 정리",
            "얼굴 붓기 빼는 마사지", "체형별 운동 루틴", "면역력 높이는 음식",
            "생리통 완화 요가", "금연 성공 전략", "알레르기 관리법",
            "치아 미백 홈케어", "자세 교정 스트레칭", "항산화 음식 리스트"
        ],
        "역사/문화": [
            "조선시대 왕들의 일상생활", "한국 전쟁 숨겨진 이야기", "세종대왕의 리더십 분석",
            "임진왜란 7년 전쟁 연대기", "고구려 광개토대왕 정복사", "신라 화랑도 정신과 문화",
            "백제 문화재의 아름다움", "일제강점기 독립운동가들", "한국 전통 건축의 과학",
            "조선 후기 실학자들", "궁궐 건축물의 숨은 의미", "한국 전통 음식의 역사",
            "전통 혼례 문화 이야기", "한글 창제 비하인드 스토리", "고려 청자의 제작 비법",
            "전통 놀이 문화 탐구", "한국 불교 문화재 순례", "조선시대 과거제도 분석",
            "전통 의학 한의학 이야기", "한국 전통 음악 이해하기", "민속 신앙과 무속 문화",
            "전통 공예 기법 소개", "한국사 미스터리 사건들", "근대화 과정의 빛과 그림자",
            "한국 성씨의 기원", "전통 명절의 유래", "한국 고대사 논쟁점들",
            "문화재 복원 이야기", "전통 시장의 역사", "한국 영토 변천사"
        ]
    },
    "tistory": {
        "엔터테인먼트": [
            "2025년 기대작 K-드라마 라인업", "넷플릭스 숨은 명작 추천", "아이돌 서바이벌 프로그램 정리",
            "웹툰 원작 드라마 성공 비결", "K-POP 4세대 그룹 분석", "OTT 플랫폼별 특징 비교",
            "한국 영화 역대 흥행 TOP 20", "예능 프로그램 시청률 분석", "인기 유튜버 콘텐츠 전략",
            "게임 스트리머 수익 구조", "디즈니플러스 추천작", "음원차트 역주행 곡들",
            "배우 필모그래피 분석", "독립영화 추천 리스트", "뮤지컬 공연 정보",
            "팟캐스트 인기 채널", "트위치 vs 유튜브 비교", "웹드라마 제작 트렌드",
            "버라이어티쇼 비하인드", "연예인 SNS 마케팅", "콘서트 티켓팅 꿀팁",
            "방송 제작 비하인드", "예능 레전드 장면들", "아이돌 덕질 입문 가이드",
            "영화제 수상작 분석", "한류 콘텐츠 해외 반응", "리얼리티쇼 인기 비결",
            "음악 방송 1위 예측", "드라마 OST 명곡들", "예능 유행어 정리"
        ],
        "트렌드/이슈": [
            "MZ세대 소비 트렌드 2025", "AI가 바꾸는 일상생활", "친환경 라이프스타일 실천법",
            "메타버스 플랫폼 비교", "Z세대 신조어 사전", "리셀 시장 인기 아이템",
            "숏폼 콘텐츠 제작 팁", "NFT 아트 투자 가이드", "온라인 커뮤니티 문화",
            "틱톡 챌린지 모음", "ESG 경영 우수 기업", "구독 경제 서비스 정리",
            "언택트 서비스 트렌드", "뉴트로 감성 아이템", "비건 뷰티 브랜드",
            "제로웨이스트 실천법", "디지털 노마드 라이프", "공유경제 서비스 활용",
            "인플루언서 마케팅 분석", "숏츠/릴스 알고리즘", "가상 인플루언서 등장",
            "업사이클링 브랜드", "펫코노미 시장 분석", "홈코노미 트렌드",
            "리빙포인트 인테리어", "K-뷰티 글로벌 트렌드", "스트리트 패션 분석",
            "미닝아웃 소비 문화", "크라우드펀딩 성공 사례", "소셜미디어 알고리즘 변화"
        ]
    }
}

def get_db_connection():
    """데이터베이스 연결"""
    return psycopg2.connect(
        host="aws-0-ap-northeast-2.pooler.supabase.com",
        database="postgres", 
        user="postgres.lhqzjnpwuftaicjurqxq",
        password="Unbleyum1106!",
        port=5432
    )

def create_full_month_schedule(year, month):
    """특정 월 전체 계획표 생성"""
    
    # 해당 월의 총 일수
    days_in_month = calendar.monthrange(year, month)[1]
    
    schedule_data = []
    
    # 각 사이트별 주제 인덱스 (순환 사용)
    topic_indices = {
        site: {category: 0 for category in SITE_TOPICS[site].keys()}
        for site in SITE_TOPICS.keys()
    }
    
    # 1일부터 말일까지 매일 계획 생성
    for day in range(1, days_in_month + 1):
        for site in SITE_TOPICS.keys():
            site_categories = SITE_TOPICS[site]
            
            for category, topics in site_categories.items():
                # 현재 인덱스의 주제 선택
                topic_idx = topic_indices[site][category]
                topic = topics[topic_idx % len(topics)]
                
                # 인덱스 증가
                topic_indices[site][category] += 1
                
                # 키워드 생성 (주제의 첫 3단어)
                keywords = topic.split()[:3]
                
                schedule_data.append({
                    "year": year,
                    "month": month,
                    "day": day,
                    "site": site,
                    "topic_category": category,
                    "specific_topic": topic,
                    "keywords": keywords,
                    "target_length": "medium",
                    "status": "planned"
                })
    
    return schedule_data

def save_full_month_to_db(schedule_data, year, month):
    """월별 계획표를 데이터베이스에 저장"""
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"데이터베이스 연결 성공")
        
        # 해당 월 기존 데이터 삭제 (덮어쓰기)
        cursor.execute("""
            DELETE FROM unble.monthly_publishing_schedule 
            WHERE year = %s AND month = %s
        """, (year, month))
        
        deleted_count = cursor.rowcount
        print(f"기존 {year}년 {month}월 데이터 삭제: {deleted_count}개")
        
        # 새로운 데이터 삽입
        inserted_count = 0
        for item in schedule_data:
            cursor.execute("""
                INSERT INTO unble.monthly_publishing_schedule 
                (year, month, day, site, topic_category, specific_topic, 
                 keywords, target_length, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item["year"], item["month"], item["day"],
                item["site"], item["topic_category"], item["specific_topic"],
                item["keywords"], item["target_length"], item["status"]
            ))
            inserted_count += 1
        
        conn.commit()
        print(f"성공: {year}년 {month}월 계획 {inserted_count}개 삽입 완료")
        
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"오류: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """메인 실행"""
    
    print("=== 완전한 월별 발행 계획표 생성 ===")
    print("8월, 9월 전체 계획표를 생성합니다.")
    print()
    
    # 8월 전체 계획표 생성
    print("1. 8월 전체 계획표 생성...")
    august_schedule = create_full_month_schedule(2025, 8)
    print(f"8월 계획 생성: {len(august_schedule)}개 (31일 × 4사이트 × 2카테고리)")
    
    # 9월 전체 계획표 생성  
    print("\n2. 9월 전체 계획표 생성...")
    september_schedule = create_full_month_schedule(2025, 9)
    print(f"9월 계획 생성: {len(september_schedule)}개 (30일 × 4사이트 × 2카테고리)")
    
    # 데이터베이스 저장
    confirm = input("\n데이터베이스에 저장하시겠습니까? (y/n): ")
    if confirm.lower() == 'y':
        print("\n데이터베이스에 저장 중...")
        
        # 8월 저장
        if save_full_month_to_db(august_schedule, 2025, 8):
            print("8월 계획표 저장 완료")
        else:
            print("8월 계획표 저장 실패")
            return
        
        # 9월 저장
        if save_full_month_to_db(september_schedule, 2025, 9):
            print("9월 계획표 저장 완료")
        else:
            print("9월 계획표 저장 실패")
            return
        
        print("\n완료: 8월, 9월 완전한 월별 계획표 생성 완료!")
        print("- 8월: 248개 계획 (31일 × 8개/일)")
        print("- 9월: 240개 계획 (30일 × 8개/일)")
        print("- 사이트별 듀얼 카테고리 시스템 적용")
        
    else:
        print("저장을 취소했습니다.")

if __name__ == "__main__":
    main()