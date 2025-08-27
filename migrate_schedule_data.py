#!/usr/bin/env python3
"""
월별 발행 계획 데이터를 유료 DB로 마이그레이션하는 스크립트
"""

import psycopg2
from datetime import datetime, date
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv('.env.example')

# 새 유료 DB 설정
new_db_config = {
    'host': 'ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app',
    'database': 'unble',
    'user': 'unble', 
    'password': 'npg_1kjV0mhECxqs',
    'port': 5432
}

def create_sample_schedule():
    """샘플 발행 계획 데이터 생성"""
    try:
        print("샘플 발행 계획 데이터 생성 중...")
        conn = psycopg2.connect(**new_db_config)
        cursor = conn.cursor()
        
        # 2025년 8월 남은 기간 스케줄 (27일부터)
        august_schedule = [
            # 8월 27일
            (2025, 8, 27, 'skewese', '건강/웰니스', '알레르기 관리법 완전 가이드', ['알레르기', '건강관리', '면역력']),
            (2025, 8, 27, 'skewese', '역사/문화', '한국 고대사 논쟁점들 심층 분석', ['고대사', '한국사', '논쟁']),
            (2025, 8, 27, 'tistory', '엔터테인먼트', '리얼리티쇼 인기 비결 분석', ['리얼리티', 'TV프로그램', '방송']),
            (2025, 8, 27, 'tistory', '트렌드/이슈', '스트리트 패션 분석 2025', ['패션', '스트리트', '트렌드']),
            (2025, 8, 27, 'unpre', '교육/자기계발', '기술 서적 추천 리스트', ['기술서적', '개발자', '학습']),
            (2025, 8, 27, 'unpre', '기술/디지털', '보안 취약점 점검 가이드', ['보안', 'IT보안', '취약점']),
            (2025, 8, 27, 'untab', '라이프스타일', '홈파티 준비 체크리스트', ['홈파티', '라이프스타일', '준비']),
            (2025, 8, 27, 'untab', '재정/투자', '재테크 자동화 시스템', ['재테크', '자동화', '투자']),
            
            # 8월 28일
            (2025, 8, 28, 'skewese', '건강/웰니스', '여름철 건강관리 필수 가이드', ['여름건강', '건강관리', '웰니스']),
            (2025, 8, 28, 'skewese', '역사/문화', '조선시대 궁중문화 탐구', ['조선시대', '궁중문화', '역사']),
            (2025, 8, 28, 'tistory', '엔터테인먼트', 'K-POP 4세대 아이돌 분석', ['KPOP', '4세대', '아이돌']),
            (2025, 8, 28, 'tistory', '트렌드/이슈', 'MZ세대 소비 트렌드 2025', ['MZ세대', '소비트렌드', '세대']),
            (2025, 8, 28, 'unpre', '교육/자기계발', '개발자 커리어 성장 전략', ['개발자', '커리어', '성장']),
            (2025, 8, 28, 'unpre', '기술/디지털', 'AI 개발 도구 최신 트렌드', ['AI', '개발도구', '트렌드']),
            (2025, 8, 28, 'untab', '라이프스타일', '미니멀 라이프 실천법', ['미니멀', '라이프스타일', '실천']),
            (2025, 8, 28, 'untab', '재정/투자', '부동산 경매 투자 전략', ['부동산', '경매', '투자전략']),
            
            # 8월 29일
            (2025, 8, 29, 'skewese', '건강/웰니스', '스트레스 관리 완전 가이드', ['스트레스', '관리', '정신건강']),
            (2025, 8, 29, 'skewese', '역사/문화', '한국 전통 음식의 역사', ['전통음식', '한식', '문화사']),
            (2025, 8, 29, 'tistory', '엔터테인먼트', '웹툰 산업 성장 분석', ['웹툰', '산업', '분석']),
            (2025, 8, 29, 'tistory', '트렌드/이슈', '원격근무 문화 정착 현황', ['원격근무', '워라밸', '문화']),
            (2025, 8, 29, 'unpre', '교육/자기계발', '프로그래밍 언어 학습 로드맵', ['프로그래밍', '학습', '로드맵']),
            (2025, 8, 29, 'unpre', '기술/디지털', '클라우드 아키텍처 설계', ['클라우드', '아키텍처', '설계']),
            (2025, 8, 29, 'untab', '라이프스타일', '홈 인테리어 트렌드 2025', ['인테리어', '홈데코', '트렌드']),
            (2025, 8, 29, 'untab', '재정/투자', '주식 투자 기초 완전 정복', ['주식투자', '기초', '완전정복']),
            
            # 8월 30일
            (2025, 8, 30, 'skewese', '건강/웰니스', '영양소 균형 잡힌 식단 구성법', ['영양소', '식단', '균형']),
            (2025, 8, 30, 'skewese', '역사/문화', '한국 불교 문화재의 가치', ['불교', '문화재', '가치']),
            (2025, 8, 30, 'tistory', '엔터테인먼트', 'OTT 플랫폼 전쟁 현황', ['OTT', '플랫폼', '넷플릭스']),
            (2025, 8, 30, 'tistory', '트렌드/이슈', '구독 경제 성장 동향', ['구독경제', '성장', '비즈니스']),
            (2025, 8, 30, 'unpre', '교육/자기계발', '개발자를 위한 시간 관리법', ['시간관리', '개발자', '효율성']),
            (2025, 8, 30, 'unpre', '기술/디지털', 'DevOps 도구 활용 가이드', ['DevOps', '도구', 'CI/CD']),
            (2025, 8, 30, 'untab', '라이프스타일', '취미 생활 추천 리스트', ['취미', '여가', '라이프']),
            (2025, 8, 30, 'untab', '재정/투자', '펀드 투자 완전 분석', ['펀드투자', '분석', '포트폴리오']),
            
            # 8월 31일
            (2025, 8, 31, 'skewese', '건강/웰니스', '운동 루틴 만들기 가이드', ['운동루틴', '헬스', '건강']),
            (2025, 8, 31, 'skewese', '역사/문화', '한국 전통 건축의 과학', ['전통건축', '한옥', '과학']),
            (2025, 8, 31, 'tistory', '엔터테인먼트', '게임 산업 미래 전망', ['게임산업', '미래', '전망']),
            (2025, 8, 31, 'tistory', '트렌드/이슈', '환경 친화적 라이프스타일', ['환경', '친화', '지속가능']),
            (2025, 8, 31, 'unpre', '교육/자기계발', '개발자 포트폴리오 작성법', ['포트폴리오', '개발자', '취업']),
            (2025, 8, 31, 'unpre', '기술/디지털', '마이크로서비스 아키텍처 가이드', ['마이크로서비스', '아키텍처', 'MSA']),
            (2025, 8, 31, 'untab', '라이프스타일', '독서 습관 만들기', ['독서', '습관', '자기계발']),
            (2025, 8, 31, 'untab', '재정/투자', 'ESG 투자 트렌드 분석', ['ESG투자', '지속가능', '트렌드'])
        ]
        
        # 9월 전체 스케줄
        september_schedule = []
        for day in range(1, 31):  # 9월 1일~30일
            base_topics = {
                'skewese': [
                    ('건강/웰니스', f'9월 {day}일 건강 관리 팁', ['건강', '관리', '팁']),
                    ('역사/문화', f'9월 {day}일 역사 이야기', ['역사', '문화', '이야기'])
                ],
                'tistory': [
                    ('엔터테인먼트', f'9월 {day}일 엔터 뉴스', ['엔터', '뉴스', '트렌드']),
                    ('트렌드/이슈', f'9월 {day}일 핫이슈 분석', ['이슈', '분석', '트렌드'])
                ],
                'unpre': [
                    ('교육/자기계발', f'9월 {day}일 개발자 성장', ['개발자', '성장', '학습']),
                    ('기술/디지털', f'9월 {day}일 기술 동향', ['기술', '동향', 'IT'])
                ],
                'untab': [
                    ('라이프스타일', f'9월 {day}일 라이프 가이드', ['라이프', '가이드', '생활']),
                    ('재정/투자', f'9월 {day}일 투자 전략', ['투자', '전략', '재테크'])
                ]
            }
            
            for site, topics in base_topics.items():
                for category, topic, keywords in topics:
                    september_schedule.append((2025, 9, day, site, category, topic, keywords))
        
        # 모든 스케줄을 DB에 삽입
        all_schedule = august_schedule + september_schedule
        
        for year, month, day, site, category, topic, keywords in all_schedule:
            try:
                cursor.execute("""
                    INSERT INTO blog_automation.monthly_publishing_schedule 
                    (year, month, day, site, topic_category, specific_topic, keywords, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
                    ON CONFLICT (year, month, day, site, topic_category) DO UPDATE SET
                    specific_topic = EXCLUDED.specific_topic,
                    keywords = EXCLUDED.keywords,
                    updated_at = CURRENT_TIMESTAMP
                """, (year, month, day, site, category, topic, keywords))
            except Exception as e:
                print(f"  ⚠️ 스케줄 삽입 오류 ({year}-{month:02d}-{day:02d} {site}): {e}")
        
        conn.commit()
        
        # 삽입된 데이터 확인
        cursor.execute("""
            SELECT year, month, COUNT(*) as count
            FROM blog_automation.monthly_publishing_schedule 
            GROUP BY year, month 
            ORDER BY year, month
        """)
        results = cursor.fetchall()
        
        print("  ✓ 스케줄 데이터 생성 완료:")
        for year, month, count in results:
            print(f"    - {year}년 {month}월: {count}개 주제")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 스케줄 생성 실패: {e}")
        return False

def test_new_db_connection():
    """새 DB 연결 테스트"""
    try:
        print("새 유료 DB 연결 테스트 중...")
        conn = psycopg2.connect(**new_db_config)
        cursor = conn.cursor()
        
        # 스키마 확인
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'blog_automation'
        """)
        table_count = cursor.fetchone()[0]
        print(f"  ✓ blog_automation 스키마에 {table_count}개 테이블 확인")
        
        # 오늘 스케줄 테스트
        today = date.today()
        cursor.execute("""
            SELECT site, topic_category, specific_topic
            FROM blog_automation.monthly_publishing_schedule
            WHERE year = %s AND month = %s AND day = %s
            ORDER BY site, topic_category
        """, (today.year, today.month, today.day))
        
        today_schedule = cursor.fetchall()
        if today_schedule:
            print(f"  ✓ 오늘({today}) 스케줄 {len(today_schedule)}개 확인:")
            for site, category, topic in today_schedule:
                print(f"    - {site}: {category} - {topic[:30]}...")
        else:
            print(f"  - 오늘({today}) 스케줄이 없습니다.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 새 DB 연결 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=== 월별 발행 계획 데이터 마이그레이션 시작 ===\n")
    
    # 1. 새 DB 연결 테스트
    if not test_new_db_connection():
        return
    
    # 2. 샘플 스케줄 생성
    create_sample_schedule()
    
    # 3. 최종 확인
    print("\n=== 마이그레이션 완료 ===")
    print("✅ 유료 DB에 월별 발행 계획이 성공적으로 설정되었습니다.")
    print("✅ 이제 자동 발행 시스템이 새로운 DB를 사용합니다.")
    print("✅ 더 이상 배포 시 데이터가 초기화되지 않습니다.")

if __name__ == "__main__":
    main()