#!/usr/bin/env python3
"""
8월 남은 기간 계획표 직접 DB 업데이트
"""

import psycopg2
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv('.env.example')

def get_db_connection():
    """데이터베이스 연결"""
    return psycopg2.connect(
        host="aws-0-ap-northeast-2.pooler.supabase.com",
        database="postgres", 
        user="postgres.lhqzjnpwuftaicjurqxq",
        password="Unbleyum1106!",
        port=5432
    )

def apply_august_schedule():
    """8월 남은 기간 계획표 적용"""
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("데이터베이스 연결 성공")
        
        # SQL 파일 읽기
        with open('august_remaining_final.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 주석과 빈 줄 제거하고 실행
        sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        print(f"실행할 SQL 명령어: {len(sql_commands)}개")
        
        executed = 0
        for sql in sql_commands:
            if sql:
                cursor.execute(sql)
                executed += 1
        
        conn.commit()
        print(f"성공: {executed}개 계획이 데이터베이스에 업데이트되었습니다.")
        
        # 결과 확인 - week_start_date와 day_of_week로 날짜 계산
        cursor.execute("""
            SELECT week_start_date + INTERVAL '1 day' * day_of_week as calc_date, 
                   site, topic_category, specific_topic
            FROM unble.publishing_schedule 
            WHERE week_start_date = '2025-08-25' AND day_of_week >= 1
            ORDER BY day_of_week, site, topic_category
        """)
        
        results = cursor.fetchall()
        print(f"\n업데이트된 계획표 확인: {len(results)}개")
        
        current_date = None
        for result in results:
            date, site, category, topic = result
            if current_date != date:
                current_date = date
                print(f"\n📅 {date.strftime('%m/%d')}:")
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
    apply_august_schedule()