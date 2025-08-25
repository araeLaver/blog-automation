#!/usr/bin/env python3
"""
테이블 제약조건 확인
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

def check_constraints():
    """제약조건 확인"""
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("데이터베이스 연결 성공")
        
        # 유니크 제약조건 확인
        cursor.execute("""
            SELECT 
                tc.constraint_name, 
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'unble' 
                AND tc.table_name = 'publishing_schedule'
                AND tc.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
            ORDER BY tc.constraint_name, kcu.ordinal_position
        """)
        
        constraints = cursor.fetchall()
        print(f"\n제약조건:")
        for constraint in constraints:
            print(f"{constraint[0]} ({constraint[1]}): {constraint[2]}")
        
        # 인덱스 확인
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes 
            WHERE schemaname = 'unble' AND tablename = 'publishing_schedule'
        """)
        
        indexes = cursor.fetchall()
        print(f"\n인덱스:")
        for index in indexes:
            print(f"{index[0]}: {index[1]}")
            
    except Exception as e:
        print(f"오류: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    check_constraints()