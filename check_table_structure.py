#!/usr/bin/env python3
"""
테이블 구조 확인
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

def check_table_structure():
    """테이블 구조 확인"""
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("데이터베이스 연결 성공")
        
        # 테이블 구조 확인
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'unble' AND table_name = 'publishing_schedule'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\npublishing_schedule 테이블 구조:")
        print("컬럼명 | 데이터타입 | NULL허용")
        print("-" * 50)
        for col in columns:
            print(f"{col[0]} | {col[1]} | {col[2]}")
        
        # 현재 데이터 샘플 확인
        cursor.execute("""
            SELECT * FROM unble.publishing_schedule 
            WHERE week_start_date >= '2025-08-25'
            LIMIT 5
        """)
        
        sample_data = cursor.fetchall()
        print(f"\n현재 데이터 샘플:")
        for data in sample_data:
            print(data)
            
    except Exception as e:
        print(f"오류: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    check_table_structure()