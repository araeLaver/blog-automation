#!/usr/bin/env python3
"""
기존 데이터 삭제 후 8월 남은 기간 계획표 적용
"""

import psycopg2

def get_db_connection():
    """데이터베이스 연결"""
    return psycopg2.connect(
        host="aws-0-ap-northeast-2.pooler.supabase.com",
        database="postgres", 
        user="postgres.lhqzjnpwuftaicjurqxq",
        password="Unbleyum1106!",
        port=5432
    )

def clean_and_apply():
    """기존 데이터 삭제 후 새 계획표 적용"""
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("데이터베이스 연결 성공")
        
        # 1. 기존 8월 26-31일 데이터 삭제
        print("\n1. 기존 8월 26-31일 데이터 삭제...")
        cursor.execute("DELETE FROM unble.publishing_schedule WHERE week_start_date = '2025-08-25' AND day_of_week >= 1")
        deleted_count = cursor.rowcount
        print(f"삭제된 기존 데이터: {deleted_count}개")
        
        # 2. 새로운 계획표 데이터 삽입
        print("\n2. 새로운 계획표 데이터 삽입...")
        
        # 8/26-31 새 계획표 데이터
        new_schedule = [
            # 8월 26일 (화요일, day_of_week=1)
            ('2025-08-25', 1, 'unpre', '기술/디지털', 'Python 웹 크롤링 마스터하기', ['Python', '웹', '크롤링']),
            ('2025-08-25', 1, 'untab', '재정/투자', '월 100만원 배당금 포트폴리오', ['월', '100만원', '배당금']),
            ('2025-08-25', 1, 'skewese', '건강/웰니스', '피부 타입별 스킨케어 루틴', ['피부', '타입별', '스킨케어']),
            ('2025-08-25', 1, 'tistory', '엔터테인먼트', '넷플릭스 숨은 명작 추천', ['넷플릭스', '숨은', '명작']),
            
            # 8월 27일 (수요일, day_of_week=2)
            ('2025-08-25', 2, 'unpre', '기술/디지털', 'React 18 새로운 기능 완벽 정리', ['React', '18', '새로운']),
            ('2025-08-25', 2, 'untab', '재정/투자', '부동산 경매 초보자 가이드', ['부동산', '경매', '초보자']),
            ('2025-08-25', 2, 'skewese', '건강/웰니스', '홈트레이닝 4주 프로그램', ['홈트레이닝', '4주', '프로그램']),
            ('2025-08-25', 2, 'tistory', '엔터테인먼트', '아이돌 서바이벌 프로그램 정리', ['아이돌', '서바이벌', '프로그램']),
            
            # 8월 28일 (목요일, day_of_week=3)
            ('2025-08-25', 3, 'unpre', '기술/디지털', 'VS Code 생산성 200% 높이는 익스텐션', ['VS', 'Code', '생산성']),
            ('2025-08-25', 3, 'untab', '재정/투자', '비트코인 ETF 투자 전략', ['비트코인', 'ETF', '투자']),
            ('2025-08-25', 3, 'skewese', '건강/웰니스', '단백질 보충제 선택 가이드', ['단백질', '보충제', '선택']),
            ('2025-08-25', 3, 'tistory', '엔터테인먼트', '웹툰 원작 드라마 성공 비결', ['웹툰', '원작', '드라마']),
            
            # 8월 29일 (금요일, day_of_week=4)
            ('2025-08-25', 4, 'unpre', '기술/디지털', 'Docker로 개발환경 통일하기', ['Docker로', '개발환경', '통일하기']),
            ('2025-08-25', 4, 'untab', '재정/투자', 'ISA 계좌 200% 활용법', ['ISA', '계좌', '200%']),
            ('2025-08-25', 4, 'skewese', '건강/웰니스', '수면의 질 높이는 10가지 방법', ['수면의', '질', '높이는']),
            ('2025-08-25', 4, 'tistory', '엔터테인먼트', 'K-POP 4세대 그룹 분석', ['K-POP', '4세대', '그룹']),
            
            # 8월 30일 (토요일, day_of_week=5)
            ('2025-08-25', 5, 'unpre', '기술/디지털', 'Git 브랜치 전략 실무 가이드', ['Git', '브랜치', '전략']),
            ('2025-08-25', 5, 'untab', '재정/투자', '미국 주식 세금 절약 팁', ['미국', '주식', '세금']),
            ('2025-08-25', 5, 'skewese', '건강/웰니스', '글루텐프리 다이어트 효과', ['글루텐프리', '다이어트', '효과']),
            ('2025-08-25', 5, 'tistory', '엔터테인먼트', 'OTT 플랫폼별 특징 비교', ['OTT', '플랫폼별', '특징']),
            
            # 8월 31일 (일요일, day_of_week=6)
            ('2025-08-25', 6, 'unpre', '기술/디지털', 'AWS Lambda 서버리스 입문', ['AWS', 'Lambda', '서버리스']),
            ('2025-08-25', 6, 'untab', '재정/투자', '리츠(REITs) 투자 완벽 가이드', ['리츠(REITs)', '투자', '완벽']),
            ('2025-08-25', 6, 'skewese', '건강/웰니스', '요가 초보자 기본 자세', ['요가', '초보자', '기본']),
            ('2025-08-25', 6, 'tistory', '엔터테인먼트', '한국 영화 역대 흥행 TOP 20', ['한국', '영화', '역대'])
        ]
        
        # 각 사이트별 secondary 카테고리
        secondary_schedule = [
            # 8월 26일 Secondary
            ('2025-08-25', 1, 'unpre', '교육/자기계발', '개발자 이력서 작성 완벽 가이드', ['개발자', '이력서', '작성']),
            ('2025-08-25', 1, 'untab', '라이프스타일', '원룸 인테리어 10만원으로 변신', ['원룸', '인테리어', '10만원으로']),
            ('2025-08-25', 1, 'skewese', '역사/문화', '한국 전쟁 숨겨진 이야기', ['한국', '전쟁', '숨겨진']),
            ('2025-08-25', 1, 'tistory', '트렌드/이슈', 'AI가 바꾸는 일상생활', ['AI가', '바꾸는', '일상생활']),
            
            # 8월 27일 Secondary
            ('2025-08-25', 2, 'unpre', '교육/자기계발', '코딩테스트 빈출 알고리즘 정리', ['코딩테스트', '빈출', '알고리즘']),
            ('2025-08-25', 2, 'untab', '라이프스타일', '에어프라이어 만능 레시피 30선', ['에어프라이어', '만능', '레시피']),
            ('2025-08-25', 2, 'skewese', '역사/문화', '세종대왕의 리더십 분석', ['세종대왕의', '리더십', '분석']),
            ('2025-08-25', 2, 'tistory', '트렌드/이슈', '친환경 라이프스타일 실천법', ['친환경', '라이프스타일', '실천법']),
            
            # 8월 28일 Secondary
            ('2025-08-25', 3, 'unpre', '교육/자기계발', 'JLPT N2 한 번에 합격하기', ['JLPT', 'N2', '한']),
            ('2025-08-25', 3, 'untab', '라이프스타일', '유럽 배낭여행 2주 코스', ['유럽', '배낭여행', '2주']),
            ('2025-08-25', 3, 'skewese', '역사/문화', '임진왜란 7년 전쟁 연대기', ['임진왜란', '7년', '전쟁']),
            ('2025-08-25', 3, 'tistory', '트렌드/이슈', '메타버스 플랫폼 비교', ['메타버스', '플랫폼', '비교']),
            
            # 8월 29일 Secondary
            ('2025-08-25', 4, 'unpre', '교육/자기계발', '기술 면접 단골 질문 100선', ['기술', '면접', '단골']),
            ('2025-08-25', 4, 'untab', '라이프스타일', '미니멀 라이프 시작하기', ['미니멀', '라이프', '시작하기']),
            ('2025-08-25', 4, 'skewese', '역사/문화', '고구려 광개토대왕 정복사', ['고구려', '광개토대왕', '정복사']),
            ('2025-08-25', 4, 'tistory', '트렌드/이슈', 'Z세대 신조어 사전', ['Z세대', '신조어', '사전']),
            
            # 8월 30일 Secondary
            ('2025-08-25', 5, 'unpre', '교육/자기계발', '영어 회화 스피킹 연습법', ['영어', '회화', '스피킹']),
            ('2025-08-25', 5, 'untab', '라이프스타일', '홈카페 분위기 만들기', ['홈카페', '분위기', '만들기']),
            ('2025-08-25', 5, 'skewese', '역사/문화', '신라 화랑도 정신과 문화', ['신라', '화랑도', '정신과']),
            ('2025-08-25', 5, 'tistory', '트렌드/이슈', '리셀 시장 인기 아이템', ['리셀', '시장', '인기']),
            
            # 8월 31일 Secondary
            ('2025-08-25', 6, 'unpre', '교육/자기계발', '개발자 포트폴리오 만들기', ['개발자', '포트폴리오', '만들기']),
            ('2025-08-25', 6, 'untab', '라이프스타일', '캠핑 초보자 장비 리스트', ['캠핑', '초보자', '장비']),
            ('2025-08-25', 6, 'skewese', '역사/문화', '백제 문화재의 아름다움', ['백제', '문화재의', '아름다움']),
            ('2025-08-25', 6, 'tistory', '트렌드/이슈', '숏폼 콘텐츠 제작 팁', ['숏폼', '콘텐츠', '제작'])
        ]
        
        # Primary 카테고리 삽입
        for item in new_schedule:
            cursor.execute("""
                INSERT INTO unble.publishing_schedule 
                (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status) 
                VALUES (%s, %s, %s, %s, %s, %s, 'medium', 'planned')
            """, item)
        
        print(f"Primary 카테고리 삽입: {len(new_schedule)}개")
        
        conn.commit()
        print(f"성공: 총 {len(new_schedule)}개 Primary 계획이 데이터베이스에 업데이트되었습니다.")
        
        print("\n⚠️ Secondary 카테고리는 현재 테이블 구조상 별도 처리 필요")
        print("각 사이트별로 하루에 2개 포스팅(Primary + Secondary)을 원한다면")
        print("테이블 구조 변경이나 별도 처리 방식이 필요합니다.")
        
        # 결과 확인
        cursor.execute("""
            SELECT week_start_date + INTERVAL '1 day' * day_of_week as calc_date, 
                   site, topic_category, specific_topic
            FROM unble.publishing_schedule 
            WHERE week_start_date = '2025-08-25' AND day_of_week >= 1
            ORDER BY day_of_week, site
        """)
        
        results = cursor.fetchall()
        print(f"\n업데이트된 계획표 확인: {len(results)}개")
        
        current_date = None
        for result in results:
            date, site, category, topic = result
            if current_date != date:
                current_date = date
                day_names = ['월', '화', '수', '목', '금', '토', '일']
                weekday = date.weekday()
                print(f"\n📅 {date.strftime('%m/%d')}({day_names[weekday]}):")
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

if __name__ == "__main__":
    clean_and_apply()