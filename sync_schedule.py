#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
from src.utils.postgresql_database import PostgreSQLDatabase

def sync_weekly_plan_to_db():
    """주간 계획표와 PostgreSQL DB 동기화"""
    
    # PostgreSQL 연결
    db = PostgreSQLDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()

    print('[SYNC] 오늘(9/7) PostgreSQL 테이블을 주간계획표와 동기화...')

    # 기존 데이터 조회
    cursor.execute('''
        SELECT topic_category, specific_topic 
        FROM blog_automation.monthly_publishing_schedule 
        WHERE year = 2025 AND month = 9 AND day = 7 AND site = 'unpre'
        ORDER BY topic_category
    ''')
    existing = cursor.fetchall()
    print('[기존] 현재 DB 데이터:')
    for row in existing:
        print(f'  - {row[0]}: {row[1]}')

    # 1. Primary 주제를 주간계획표와 일치시키기 (연말정산 절세 꿀팁)
    cursor.execute('''
        UPDATE blog_automation.monthly_publishing_schedule 
        SET specific_topic = %s, keywords = %s 
        WHERE year = 2025 AND month = 9 AND day = 7 AND site = 'unpre' 
        AND topic_category = (
            SELECT topic_category 
            FROM blog_automation.monthly_publishing_schedule 
            WHERE year = 2025 AND month = 9 AND day = 7 AND site = 'unpre'
            ORDER BY topic_category 
            LIMIT 1
        )
    ''', ('연말정산 절세 꿀팁', ['연말정산', '절세', '꿀팁']))

    print(f'[업데이트] Primary 업데이트: {cursor.rowcount}건')

    # 2. Secondary 주제도 관련 주제로 변경
    cursor.execute('''
        UPDATE blog_automation.monthly_publishing_schedule 
        SET specific_topic = %s, keywords = %s 
        WHERE year = 2025 AND month = 9 AND day = 7 AND site = 'unpre' 
        AND topic_category = (
            SELECT topic_category 
            FROM blog_automation.monthly_publishing_schedule 
            WHERE year = 2025 AND month = 9 AND day = 7 AND site = 'unpre'
            ORDER BY topic_category DESC
            LIMIT 1
        )
    ''', ('2025년 세금혜택 정리', ['세금혜택', '2025년', '세테크']))

    print(f'[업데이트] Secondary 업데이트: {cursor.rowcount}건')

    conn.commit()

    # 확인
    cursor.execute('''
        SELECT topic_category, specific_topic, keywords 
        FROM blog_automation.monthly_publishing_schedule 
        WHERE year = 2025 AND month = 9 AND day = 7 AND site = 'unpre'
        ORDER BY topic_category
    ''')

    results = cursor.fetchall()
    print('[완료] 업데이트 결과:')
    for row in results:
        print(f'  - {row[0]}: {row[1]} (키워드: {row[2]})')

    cursor.close()
    conn.close()
    
    return True

if __name__ == "__main__":
    sync_weekly_plan_to_db()