#!/usr/bin/env python3
"""
스케줄 데이터 확인 및 현재 주 스케줄 생성
"""
import os
import sys
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv('.env.example')  # 실제 .env가 없으므로 예시에서 로드

def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST', 'aws-0-ap-northeast-2.pooler.supabase.com'),
            port=int(os.getenv('PG_PORT', 5432)),
            database=os.getenv('PG_DATABASE', 'postgres'),
            user=os.getenv('PG_USER', 'postgres.lhqzjnpwuftaicjurqxq'),
            password=os.getenv('PG_PASSWORD', 'your_supabase_password_here')
        )
        return conn
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")
        return None

def check_database_schedules():
    """데이터베이스의 스케줄 데이터 확인"""
    print("=== 데이터베이스 스케줄 데이터 확인 ===")
    
    conn = get_db_connection()
    if not conn:
        print("❌ 데이터베이스에 연결할 수 없습니다.")
        return
    
    try:
        with conn.cursor() as cursor:
            # 스키마 설정
            cursor.execute("SET search_path TO unble, public")
            
            # 현재 데이터베이스에 있는 모든 스케줄 데이터 확인
            cursor.execute("""
                SELECT DISTINCT week_start_date, COUNT(*) as schedule_count
                FROM publishing_schedule 
                GROUP BY week_start_date
                ORDER BY week_start_date
            """)
            
            results = cursor.fetchall()
            
            if results:
                print("현재 데이터베이스에 있는 스케줄:")
                for week_start, count in results:
                    print(f"  - 주 시작일: {week_start}, 스케줄 개수: {count}")
            else:
                print("데이터베이스에 스케줄 데이터가 없습니다!")
            
            # 현재 주와 다음 주 확인
            today = datetime.now().date()
            current_week_start = today - timedelta(days=today.weekday())
            next_week_start = current_week_start + timedelta(weeks=1)
            
            print(f"\n현재 주 시작일: {current_week_start}")
            print(f"다음 주 시작일: {next_week_start}")
            
            # 현재 주 데이터 확인
            cursor.execute("""
                SELECT day_of_week, site, specific_topic, status
                FROM publishing_schedule 
                WHERE week_start_date = %s
                ORDER BY day_of_week, site
            """, (current_week_start,))
            
            current_week_data = cursor.fetchall()
            
            if current_week_data:
                print(f"\n현재 주({current_week_start}) 스케줄:")
                for day, site, topic, status in current_week_data:
                    print(f"  - {day}요일 {site}: {topic[:50]}... (상태: {status})")
            else:
                print(f"\n⚠️  현재 주({current_week_start})에 대한 스케줄이 없습니다!")
                create_current_week_schedule(cursor, current_week_start)
                    
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def create_current_week_schedule(cursor, week_start):
    """현재 주 스케줄 생성"""
    print("\n현재 주 스케줄을 생성합니다...")
    
    # 기본 주제 데이터
    topics = {
        'unpre': [
            {"category": "프로그래밍", "topic": "Redis 캐싱 전략과 성능 튜닝", "keywords": ["redis", "cache", "performance"], "length": "medium"},
            {"category": "프로그래밍", "topic": "Docker 컨테이너 운영 실무", "keywords": ["docker", "container", "devops"], "length": "long"},
            {"category": "프로그래밍", "topic": "React Hook 고급 활용법", "keywords": ["react", "hooks", "frontend"], "length": "medium"},
            {"category": "프로그래밍", "topic": "Python 데이터 분석 마스터", "keywords": ["python", "data", "analysis"], "length": "long"},
            {"category": "프로그래밍", "topic": "TypeScript 고급 타입 시스템", "keywords": ["typescript", "types", "javascript"], "length": "medium"},
            {"category": "프로그래밍", "topic": "GraphQL API 설계와 최적화", "keywords": ["graphql", "api", "optimization"], "length": "long"},
            {"category": "프로그래밍", "topic": "Kubernetes 클러스터 관리", "keywords": ["kubernetes", "cluster", "orchestration"], "length": "medium"}
        ],
        'untab': [
            {"category": "투자", "topic": "친환경 부동산 그린 리모델링 트렌드", "keywords": ["친환경", "리모델링", "부동산"], "length": "medium"},
            {"category": "투자", "topic": "고령화 사회와 실버타운 투자", "keywords": ["고령화", "실버타운", "투자"], "length": "long"},
            {"category": "투자", "topic": "인플레이션 시대의 투자 가이드", "keywords": ["인플레이션", "투자", "전략"], "length": "medium"},
            {"category": "투자", "topic": "공모주 투자 전략 분석", "keywords": ["공모주", "IPO", "투자"], "length": "long"},
            {"category": "투자", "topic": "메타버스 부동산 투자", "keywords": ["메타버스", "디지털", "부동산"], "length": "medium"},
            {"category": "투자", "topic": "ESG 투자의 미래 전망", "keywords": ["ESG", "지속가능", "투자"], "length": "long"},
            {"category": "투자", "topic": "리츠(REITs) 투자의 장단점", "keywords": ["REITs", "부동산", "투자신탁"], "length": "medium"}
        ],
        'skewese': [
            {"category": "역사", "topic": "신라 통일의 과정과 역사적 의미", "keywords": ["신라", "통일", "고대사"], "length": "long"},
            {"category": "역사", "topic": "4.19혁명과 민주주의 발전", "keywords": ["4.19", "혁명", "민주주의"], "length": "medium"},
            {"category": "역사", "topic": "임진왜란과 이순신의 활약", "keywords": ["임진왜란", "이순신", "조선"], "length": "long"},
            {"category": "역사", "topic": "한국 전통 건축의 아름다움과 과학", "keywords": ["전통건축", "한옥", "과학"], "length": "medium"},
            {"category": "역사", "topic": "정조의 개혁 정치와 화성 건설", "keywords": ["정조", "개혁", "화성"], "length": "long"},
            {"category": "역사", "topic": "고구려의 영토 확장과 광개토대왕", "keywords": ["고구려", "광개토대왕", "영토"], "length": "medium"},
            {"category": "역사", "topic": "조선 후기 실학사상의 발전", "keywords": ["실학", "조선후기", "사상"], "length": "long"}
        ]
    }
    
    try:
        # 각 요일별로 스케줄 생성
        for day in range(7):  # 0=월요일, 6=일요일
            for site in ['unpre', 'untab', 'skewese']:
                topic_data = topics[site][day % len(topics[site])]
                
                cursor.execute("""
                    INSERT INTO publishing_schedule 
                    (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    week_start, day, site,
                    topic_data['category'], topic_data['topic'],
                    topic_data['keywords'], topic_data['length'],
                    'planned'  # scheduler.py와 일치하도록 'planned'로 설정
                ))
        
        cursor.connection.commit()
        print("✅ 현재 주 스케줄이 성공적으로 생성되었습니다!")
        
        # 생성된 스케줄 확인
        cursor.execute("""
            SELECT day_of_week, site, specific_topic, status
            FROM publishing_schedule 
            WHERE week_start_date = %s
            ORDER BY day_of_week, site
        """, (week_start,))
        
        new_schedule = cursor.fetchall()
        print(f"\n새로 생성된 스케줄:")
        for day, site, topic, status in new_schedule:
            print(f"  - {day}요일 {site}: {topic[:50]}... (상태: {status})")
            
    except Exception as e:
        print(f"❌ 스케줄 생성 실패: {e}")
        cursor.connection.rollback()

def test_today_topic_query():
    """오늘의 주제를 직접 쿼리해서 테스트"""
    print("\n=== 오늘의 주제 쿼리 테스트 ===")
    
    conn = get_db_connection()
    if not conn:
        print("❌ 데이터베이스에 연결할 수 없습니다.")
        return
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO unble, public")
            
            today = datetime.now().date()
            weekday = today.weekday()  # 0=월요일, 6=일요일
            week_start = today - timedelta(days=weekday)
            
            print(f"오늘: {today} (요일: {weekday})")
            print(f"이번 주 시작일: {week_start}")
            
            sites = ['unpre', 'untab', 'skewese']
            
            for site in sites:
                cursor.execute("""
                    SELECT specific_topic, topic_category, keywords, target_length
                    FROM publishing_schedule 
                    WHERE week_start_date = %s AND day_of_week = %s AND site = %s
                    AND status = 'planned'
                """, (week_start, weekday, site))
                
                result = cursor.fetchone()
                if result:
                    print(f"✅ {site}: {result[0][:50]}... (카테고리: {result[1]})")
                else:
                    print(f"❌ {site}: 오늘의 계획된 주제를 찾을 수 없습니다.")
    
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    check_database_schedules()
    test_today_topic_query()