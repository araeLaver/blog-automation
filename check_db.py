#!/usr/bin/env python3
import psycopg2
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv('.env.example')

def check_db():
    try:
        # DB 연결 정보 (실제 비밀번호는 서버에 설정되어 있을 것)
        print("=== DB 연결 정보 ===")
        print(f"Host: {os.getenv('PG_HOST')}")
        print(f"Database: {os.getenv('PG_DATABASE')}")
        print(f"User: {os.getenv('PG_USER')}")
        print(f"Schema: {os.getenv('PG_SCHEMA')}")
        
        # 실제 DB 연결은 비밀번호가 없어서 안될 것
        print("\n❌ 로컬에서는 실제 DB 비밀번호가 없어서 연결 불가")
        print("서버에서 직접 확인해야 함")
        
        # 현재 주 정보
        today = datetime.now().date()
        weekday = today.weekday()
        week_start = today - timedelta(days=weekday)
        
        print(f"\n=== 현재 날짜 정보 ===")
        print(f"오늘: {today}")
        print(f"요일: {weekday} (0=월요일)")
        print(f"주 시작일: {week_start}")
        
        print(f"\n=== 확인해야 할 쿼리 ===")
        print(f"""
SELECT week_start_date, day_of_week, site, specific_topic, status
FROM unble.publishing_schedule 
WHERE week_start_date = '{week_start}' AND day_of_week = {weekday}
ORDER BY site;
        """)
        
        print(f"\n=== 모든 스케줄 확인 쿼리 ===")
        print(f"""
SELECT week_start_date, day_of_week, site, specific_topic, status
FROM unble.publishing_schedule 
ORDER BY week_start_date DESC, day_of_week, site
LIMIT 20;
        """)
        
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_db()