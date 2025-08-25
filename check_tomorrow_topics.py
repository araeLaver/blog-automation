#!/usr/bin/env python3
"""
내일(화요일) 발행 주제 확인 스크립트
"""

import sys
import os
sys.path.append('/Users/down/Dev/D/auto/blog-automation')

try:
    from src.utils.schedule_manager import ScheduleManager
    
    # 스케줄 매니저 인스턴스 생성
    schedule_manager = ScheduleManager()
    
    print("=== 내일(2025-08-26 화요일) 발행 주제 확인 ===")
    
    sites = ['unpre', 'untab', 'skewese', 'tistory']
    
    for site in sites:
        try:
            topic_info = schedule_manager.get_today_topic_for_manual(site)
            print(f"{site.upper():8s}: {topic_info['specific_topic']} ({topic_info['category']})")
        except Exception as e:
            print(f"{site.upper():8s}: ERROR - {e}")
    
    print("\n=== DB 연결 테스트 ===")
    try:
        from src.utils.postgresql_database import PostgreSQLDatabase
        db = PostgreSQLDatabase()
        conn = db.get_connection()
        print("✅ DB 연결 성공")
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM publishing_schedule 
                WHERE week_start_date = '2025-08-25'
            """)
            count = cursor.fetchone()[0]
            print(f"✅ 현재 주 스케줄: {count}개")
            
            cursor.execute("""
                SELECT site, specific_topic, topic_category
                FROM publishing_schedule 
                WHERE week_start_date = '2025-08-25' 
                AND day_of_week = 1
                ORDER BY site
            """)
            
            results = cursor.fetchall()
            print(f"✅ 내일(화요일) DB 스케줄: {len(results)}개")
            
            for site, topic, category in results:
                print(f"  {site.upper():8s}: {topic} ({category})")
        
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")

except Exception as e:
    print(f"스크립트 실행 오류: {e}")