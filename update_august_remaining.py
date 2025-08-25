#!/usr/bin/env python3
"""
8월 남은 기간 발행 계획표 새 카테고리로 업데이트
- 8월 26일부터 31일까지 새로운 카테고리 적용
"""

import psycopg2
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv('.env.example')

# 새로운 사이트별 카테고리 및 8월 남은 기간 주제
AUGUST_REMAINING_TOPICS = {
    "unpre": {
        "primary": {
            "category": "기술/디지털",
            "topics": [
                "Python 웹 크롤링 마스터하기",
                "React 18 새로운 기능 완벽 정리", 
                "VS Code 생산성 200% 높이는 익스텐션",
                "Docker로 개발환경 통일하기",
                "Git 브랜치 전략 실무 가이드",
                "AWS Lambda 서버리스 입문"
            ]
        },
        "secondary": {
            "category": "교육/자기계발",
            "topics": [
                "개발자 이력서 작성 완벽 가이드",
                "코딩테스트 빈출 알고리즘 정리",
                "JLPT N2 한 번에 합격하기", 
                "기술 면접 단골 질문 100선",
                "영어 회화 스피킹 연습법",
                "개발자 포트폴리오 만들기"
            ]
        }
    },
    "untab": {
        "primary": {
            "category": "재정/투자",
            "topics": [
                "월 100만원 배당금 포트폴리오",
                "부동산 경매 초보자 가이드",
                "비트코인 ETF 투자 전략",
                "ISA 계좌 200% 활용법",
                "미국 주식 세금 절약 팁",
                "리츠(REITs) 투자 완벽 가이드"
            ]
        },
        "secondary": {
            "category": "라이프스타일", 
            "topics": [
                "원룸 인테리어 10만원으로 변신",
                "에어프라이어 만능 레시피 30선",
                "유럽 배낭여행 2주 코스",
                "미니멀 라이프 시작하기",
                "홈카페 분위기 만들기",
                "캠핑 초보자 장비 리스트"
            ]
        }
    },
    "skewese": {
        "primary": {
            "category": "건강/웰니스",
            "topics": [
                "피부 타입별 스킨케어 루틴",
                "홈트레이닝 4주 프로그램", 
                "단백질 보충제 선택 가이드",
                "수면의 질 높이는 10가지 방법",
                "글루텐프리 다이어트 효과",
                "요가 초보자 기본 자세"
            ]
        },
        "secondary": {
            "category": "역사/문화",
            "topics": [
                "한국 전쟁 숨겨진 이야기",
                "세종대왕의 리더십 분석",
                "임진왜란 7년 전쟁 연대기",
                "고구려 광개토대왕 정복사",
                "신라 화랑도 정신과 문화",
                "백제 문화재의 아름다움"
            ]
        }
    },
    "tistory": {
        "primary": {
            "category": "엔터테인먼트", 
            "topics": [
                "넷플릭스 숨은 명작 추천",
                "아이돌 서바이벌 프로그램 정리",
                "웹툰 원작 드라마 성공 비결",
                "K-POP 4세대 그룹 분석",
                "OTT 플랫폼별 특징 비교",
                "한국 영화 역대 흥행 TOP 20"
            ]
        },
        "secondary": {
            "category": "트렌드/이슈",
            "topics": [
                "AI가 바꾸는 일상생활",
                "친환경 라이프스타일 실천법",
                "메타버스 플랫폼 비교",
                "Z세대 신조어 사전",
                "리셀 시장 인기 아이템",
                "숏폼 콘텐츠 제작 팁"
            ]
        }
    }
}

def get_db_connection():
    """데이터베이스 연결"""
    return psycopg2.connect(
        host=os.getenv('PG_HOST'),
        database=os.getenv('PG_DATABASE'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD'),
        port=os.getenv('PG_PORT', 5432)
    )

def update_august_remaining():
    """8월 남은 기간 계획표 업데이트"""
    
    # 8월 26일부터 31일까지
    start_date = date(2025, 8, 26)
    end_date = date(2025, 8, 31)
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 현재 8월 계획 확인
        cursor.execute("""
            SELECT DISTINCT week_start_date, day_of_week, site, topic_category, specific_topic
            FROM unble.publishing_schedule 
            WHERE week_start_date >= '2025-08-25' 
            AND day_of_week >= 1
            ORDER BY week_start_date, day_of_week, site, topic_category
        """)
        
        current_plans = cursor.fetchall()
        print(f"현재 8월 계획: {len(current_plans)}개")
        
        # 사이트별 주제 인덱스
        topic_indices = {
            site: {"primary": 0, "secondary": 0}
            for site in AUGUST_REMAINING_TOPICS.keys()
        }
        
        updates = []
        current_date = start_date
        
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            week_start = current_date - timedelta(days=day_of_week)
            
            for site in AUGUST_REMAINING_TOPICS.keys():
                site_config = AUGUST_REMAINING_TOPICS[site]
                
                # Primary 카테고리
                primary_topics = site_config["primary"]["topics"]
                primary_idx = topic_indices[site]["primary"]
                primary_topic = primary_topics[primary_idx % len(primary_topics)]
                topic_indices[site]["primary"] += 1
                
                updates.append({
                    "week_start_date": week_start,
                    "day_of_week": day_of_week,
                    "site": site,
                    "topic_category": site_config["primary"]["category"],
                    "specific_topic": primary_topic,
                    "keywords": primary_topic.split()[:3]
                })
                
                # Secondary 카테고리
                secondary_topics = site_config["secondary"]["topics"]
                secondary_idx = topic_indices[site]["secondary"]
                secondary_topic = secondary_topics[secondary_idx % len(secondary_topics)]
                topic_indices[site]["secondary"] += 1
                
                updates.append({
                    "week_start_date": week_start,
                    "day_of_week": day_of_week,
                    "site": site,
                    "topic_category": site_config["secondary"]["category"],
                    "specific_topic": secondary_topic,
                    "keywords": secondary_topic.split()[:3]
                })
            
            current_date += timedelta(days=1)
        
        print(f"\n8월 남은 기간 업데이트 계획: {len(updates)}개")
        
        # 업데이트 실행
        updated_count = 0
        for update in updates:
            try:
                cursor.execute("""
                    INSERT INTO unble.publishing_schedule 
                    (week_start_date, day_of_week, site, topic_category, specific_topic, 
                     keywords, target_length, status, scheduled_date)
                    VALUES (%s, %s, %s, %s, %s, %s, 'medium', 'planned', %s)
                    ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
                    DO UPDATE SET 
                        specific_topic = EXCLUDED.specific_topic,
                        keywords = EXCLUDED.keywords,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    update["week_start_date"],
                    update["day_of_week"],
                    update["site"],
                    update["topic_category"],
                    update["specific_topic"],
                    update["keywords"],
                    update["week_start_date"] + timedelta(days=update["day_of_week"])
                ))
                updated_count += 1
                
            except Exception as e:
                print(f"업데이트 오류: {e}")
                continue
        
        conn.commit()
        print(f"성공: {updated_count}개 계획이 새로운 카테고리로 업데이트되었습니다.")
        
        # 업데이트 결과 확인
        cursor.execute("""
            SELECT week_start_date, day_of_week, site, topic_category, specific_topic
            FROM unble.publishing_schedule 
            WHERE week_start_date >= '2025-08-25' 
            AND day_of_week >= 1
            ORDER BY week_start_date, day_of_week, site, topic_category
        """)
        
        updated_plans = cursor.fetchall()
        print(f"\n=== 업데이트된 8월 남은 계획 ===")
        
        current_day = None
        for plan in updated_plans:
            week_start, day_of_week, site, category, topic = plan
            plan_date = week_start + timedelta(days=day_of_week)
            
            if current_day != plan_date:
                current_day = plan_date
                day_names = ['월', '화', '수', '목', '금', '토', '일']
                print(f"\n📅 {plan_date.strftime('%m/%d')}({day_names[day_of_week]}):")
            
            print(f"  {site.upper()}: [{category}] {topic}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"오류: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """메인 실행"""
    print("=== 8월 남은 기간 발행 계획표 업데이트 ===")
    print("기간: 2025-08-26 ~ 2025-08-31")
    print("새로운 카테고리 적용")
    print()
    
    confirm = input("업데이트를 진행하시겠습니까? (y/n): ")
    if confirm.lower() != 'y':
        print("업데이트를 취소했습니다.")
        return
    
    update_august_remaining()
    print("\n완료: 8월 남은 기간이 새로운 카테고리로 업데이트되었습니다!")

if __name__ == "__main__":
    main()