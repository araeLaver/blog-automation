#!/usr/bin/env python3
"""
기존 주별 계획표를 월별 계획표 구조로 마이그레이션
"""

import psycopg2
from datetime import datetime, date, timedelta

def get_db_connection():
    """데이터베이스 연결"""
    return psycopg2.connect(
        host="aws-0-ap-northeast-2.pooler.supabase.com",
        database="postgres", 
        user="postgres.lhqzjnpwuftaicjurqxq",
        password="Unbleyum1106!",
        port=5432
    )

def migrate_to_monthly():
    """월별 계획표 구조로 마이그레이션"""
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("데이터베이스 연결 성공")
        
        # 1. 새로운 월별 계획표 테이블 생성
        print("\n1. 새로운 월별 계획표 테이블 생성...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unble.monthly_publishing_schedule (
                id SERIAL PRIMARY KEY,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                site VARCHAR(50) NOT NULL,
                topic_category VARCHAR(100) NOT NULL,
                specific_topic TEXT NOT NULL,
                keywords TEXT[],
                target_length VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'planned',
                generated_content_id INTEGER,
                published_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- 날짜별 사이트별 카테고리별 유니크 제약
                UNIQUE(year, month, day, site, topic_category)
            )
        """)
        
        print("월별 계획표 테이블 생성 완료")
        
        # 2. 기존 데이터를 월별 구조로 변환하여 복사
        print("\n2. 기존 데이터를 월별 구조로 변환...")
        
        cursor.execute("""
            SELECT week_start_date, day_of_week, site, topic_category, 
                   specific_topic, keywords, target_length, status,
                   generated_content_id, published_url, created_at, updated_at
            FROM unble.publishing_schedule
            ORDER BY week_start_date, day_of_week, site
        """)
        
        old_data = cursor.fetchall()
        
        migrated_count = 0
        for item in old_data:
            week_start, day_of_week, site, category, topic, keywords, length, status, content_id, url, created, updated = item
            
            # week_start_date + day_of_week로 실제 날짜 계산
            actual_date = week_start + timedelta(days=day_of_week)
            
            try:
                cursor.execute("""
                    INSERT INTO unble.monthly_publishing_schedule 
                    (year, month, day, site, topic_category, specific_topic, keywords, 
                     target_length, status, generated_content_id, published_url, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (year, month, day, site, topic_category) 
                    DO UPDATE SET 
                        specific_topic = EXCLUDED.specific_topic,
                        keywords = EXCLUDED.keywords,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    actual_date.year, actual_date.month, actual_date.day,
                    site, category, topic, keywords, length, status,
                    content_id, url, created, updated
                ))
                migrated_count += 1
            except Exception as e:
                print(f"데이터 변환 오류: {e} - {item}")
                continue
        
        print(f"마이그레이션된 데이터: {migrated_count}개")
        
        # 3. 8월 남은 기간 새 카테고리로 업데이트
        print("\n3. 8월 남은 기간 새 카테고리 적용...")
        
        august_schedule = [
            # 8월 26일
            (2025, 8, 26, 'unpre', '기술/디지털', 'Python 웹 크롤링 마스터하기', ['Python', '웹', '크롤링']),
            (2025, 8, 26, 'unpre', '교육/자기계발', '개발자 이력서 작성 완벽 가이드', ['개발자', '이력서', '작성']),
            (2025, 8, 26, 'untab', '재정/투자', '월 100만원 배당금 포트폴리오', ['월', '100만원', '배당금']),
            (2025, 8, 26, 'untab', '라이프스타일', '원룸 인테리어 10만원으로 변신', ['원룸', '인테리어', '10만원으로']),
            (2025, 8, 26, 'skewese', '건강/웰니스', '피부 타입별 스킨케어 루틴', ['피부', '타입별', '스킨케어']),
            (2025, 8, 26, 'skewese', '역사/문화', '한국 전쟁 숨겨진 이야기', ['한국', '전쟁', '숨겨진']),
            (2025, 8, 26, 'tistory', '엔터테인먼트', '넷플릭스 숨은 명작 추천', ['넷플릭스', '숨은', '명작']),
            (2025, 8, 26, 'tistory', '트렌드/이슈', 'AI가 바꾸는 일상생활', ['AI가', '바꾸는', '일상생활']),
            
            # 8월 27일
            (2025, 8, 27, 'unpre', '기술/디지털', 'React 18 새로운 기능 완벽 정리', ['React', '18', '새로운']),
            (2025, 8, 27, 'unpre', '교육/자기계발', '코딩테스트 빈출 알고리즘 정리', ['코딩테스트', '빈출', '알고리즘']),
            (2025, 8, 27, 'untab', '재정/투자', '부동산 경매 초보자 가이드', ['부동산', '경매', '초보자']),
            (2025, 8, 27, 'untab', '라이프스타일', '에어프라이어 만능 레시피 30선', ['에어프라이어', '만능', '레시피']),
            (2025, 8, 27, 'skewese', '건강/웰니스', '홈트레이닝 4주 프로그램', ['홈트레이닝', '4주', '프로그램']),
            (2025, 8, 27, 'skewese', '역사/문화', '세종대왕의 리더십 분석', ['세종대왕의', '리더십', '분석']),
            (2025, 8, 27, 'tistory', '엔터테인먼트', '아이돌 서바이벌 프로그램 정리', ['아이돌', '서바이벌', '프로그램']),
            (2025, 8, 27, 'tistory', '트렌드/이슈', '친환경 라이프스타일 실천법', ['친환경', '라이프스타일', '실천법']),
            
            # 8월 28일
            (2025, 8, 28, 'unpre', '기술/디지털', 'VS Code 생산성 200% 높이는 익스텐션', ['VS', 'Code', '생산성']),
            (2025, 8, 28, 'unpre', '교육/자기계발', 'JLPT N2 한 번에 합격하기', ['JLPT', 'N2', '한']),
            (2025, 8, 28, 'untab', '재정/투자', '비트코인 ETF 투자 전략', ['비트코인', 'ETF', '투자']),
            (2025, 8, 28, 'untab', '라이프스타일', '유럽 배낭여행 2주 코스', ['유럽', '배낭여행', '2주']),
            (2025, 8, 28, 'skewese', '건강/웰니스', '단백질 보충제 선택 가이드', ['단백질', '보충제', '선택']),
            (2025, 8, 28, 'skewese', '역사/문화', '임진왜란 7년 전쟁 연대기', ['임진왜란', '7년', '전쟁']),
            (2025, 8, 28, 'tistory', '엔터테인먼트', '웹툰 원작 드라마 성공 비결', ['웹툰', '원작', '드라마']),
            (2025, 8, 28, 'tistory', '트렌드/이슈', '메타버스 플랫폼 비교', ['메타버스', '플랫폼', '비교']),
            
            # 8월 29일
            (2025, 8, 29, 'unpre', '기술/디지털', 'Docker로 개발환경 통일하기', ['Docker로', '개발환경', '통일하기']),
            (2025, 8, 29, 'unpre', '교육/자기계발', '기술 면접 단골 질문 100선', ['기술', '면접', '단골']),
            (2025, 8, 29, 'untab', '재정/투자', 'ISA 계좌 200% 활용법', ['ISA', '계좌', '200%']),
            (2025, 8, 29, 'untab', '라이프스타일', '미니멀 라이프 시작하기', ['미니멀', '라이프', '시작하기']),
            (2025, 8, 29, 'skewese', '건강/웰니스', '수면의 질 높이는 10가지 방법', ['수면의', '질', '높이는']),
            (2025, 8, 29, 'skewese', '역사/문화', '고구려 광개토대왕 정복사', ['고구려', '광개토대왕', '정복사']),
            (2025, 8, 29, 'tistory', '엔터테인먼트', 'K-POP 4세대 그룹 분석', ['K-POP', '4세대', '그룹']),
            (2025, 8, 29, 'tistory', '트렌드/이슈', 'Z세대 신조어 사전', ['Z세대', '신조어', '사전']),
            
            # 8월 30일
            (2025, 8, 30, 'unpre', '기술/디지털', 'Git 브랜치 전략 실무 가이드', ['Git', '브랜치', '전략']),
            (2025, 8, 30, 'unpre', '교육/자기계발', '영어 회화 스피킹 연습법', ['영어', '회화', '스피킹']),
            (2025, 8, 30, 'untab', '재정/투자', '미국 주식 세금 절약 팁', ['미국', '주식', '세금']),
            (2025, 8, 30, 'untab', '라이프스타일', '홈카페 분위기 만들기', ['홈카페', '분위기', '만들기']),
            (2025, 8, 30, 'skewese', '건강/웰니스', '글루텐프리 다이어트 효과', ['글루텐프리', '다이어트', '효과']),
            (2025, 8, 30, 'skewese', '역사/문화', '신라 화랑도 정신과 문화', ['신라', '화랑도', '정신과']),
            (2025, 8, 30, 'tistory', '엔터테인먼트', 'OTT 플랫폼별 특징 비교', ['OTT', '플랫폼별', '특징']),
            (2025, 8, 30, 'tistory', '트렌드/이슈', '리셀 시장 인기 아이템', ['리셀', '시장', '인기']),
            
            # 8월 31일
            (2025, 8, 31, 'unpre', '기술/디지털', 'AWS Lambda 서버리스 입문', ['AWS', 'Lambda', '서버리스']),
            (2025, 8, 31, 'unpre', '교육/자기계발', '개발자 포트폴리오 만들기', ['개발자', '포트폴리오', '만들기']),
            (2025, 8, 31, 'untab', '재정/투자', '리츠(REITs) 투자 완벽 가이드', ['리츠(REITs)', '투자', '완벽']),
            (2025, 8, 31, 'untab', '라이프스타일', '캠핑 초보자 장비 리스트', ['캠핑', '초보자', '장비']),
            (2025, 8, 31, 'skewese', '건강/웰니스', '요가 초보자 기본 자세', ['요가', '초보자', '기본']),
            (2025, 8, 31, 'skewese', '역사/문화', '백제 문화재의 아름다움', ['백제', '문화재의', '아름다움']),
            (2025, 8, 31, 'tistory', '엔터테인먼트', '한국 영화 역대 흥행 TOP 20', ['한국', '영화', '역대']),
            (2025, 8, 31, 'tistory', '트렌드/이슈', '숏폼 콘텐츠 제작 팁', ['숏폼', '콘텐츠', '제작'])
        ]
        
        august_count = 0
        for item in august_schedule:
            year, month, day, site, category, topic, keywords = item
            
            cursor.execute("""
                INSERT INTO unble.monthly_publishing_schedule 
                (year, month, day, site, topic_category, specific_topic, keywords, target_length, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'medium', 'planned')
                ON CONFLICT (year, month, day, site, topic_category) 
                DO UPDATE SET 
                    specific_topic = EXCLUDED.specific_topic,
                    keywords = EXCLUDED.keywords,
                    updated_at = CURRENT_TIMESTAMP
            """, (year, month, day, site, category, topic, keywords))
            august_count += 1
        
        print(f"8월 새 카테고리 적용: {august_count}개")
        
        conn.commit()
        
        # 4. 결과 확인
        print("\n4. 월별 계획표 결과 확인...")
        
        cursor.execute("""
            SELECT year, month, day, site, topic_category, specific_topic
            FROM unble.monthly_publishing_schedule
            WHERE year = 2025 AND month = 8 AND day >= 26
            ORDER BY day, site, topic_category
        """)
        
        results = cursor.fetchall()
        print(f"\n월별 계획표 확인 (8월 26-31일): {len(results)}개")
        
        current_day = None
        for result in results:
            year, month, day, site, category, topic = result
            if current_day != day:
                current_day = day
                day_names = ['월', '화', '수', '목', '금', '토', '일']
                date_obj = date(year, month, day)
                weekday = date_obj.weekday()
                print(f"\n📅 {month:02d}/{day:02d}({day_names[weekday]}):")
            print(f"  {site.upper()}: [{category}] {topic}")
        
        print(f"\n✅ 월별 계획표 마이그레이션 완료!")
        print(f"   - 기존 데이터: {migrated_count}개 변환")
        print(f"   - 8월 새 계획: {august_count}개 적용")
        print(f"   - 새 테이블: monthly_publishing_schedule")
        
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

if __name__ == "__main__":
    migrate_to_monthly()