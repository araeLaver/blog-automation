"""
PostgreSQL 데이터 확인
"""
from src.utils.postgresql_database import PostgreSQLDatabase

def check_postgresql_data():
    """PostgreSQL 데이터 확인"""
    try:
        db = PostgreSQLDatabase()
        print("PostgreSQL connection successful")
        
        # 콘텐츠 히스토리 확인
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.content_history")
            content_count = cursor.fetchone()[0]
            print(f"Content history records: {content_count}")
            
            cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.content_files")
            files_count = cursor.fetchone()[0]
            print(f"Content files records: {files_count}")
            
            cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.topic_pool")
            topics_count = cursor.fetchone()[0]
            print(f"Topic pool records: {topics_count}")
            
            cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.system_logs")
            logs_count = cursor.fetchone()[0]
            print(f"System logs records: {logs_count}")
        
        if content_count > 0:
            print("\nData already exists in PostgreSQL!")
            print("The dashboard should show existing data.")
        else:
            print("\nNo data found. You may need to add some data.")
        
    except Exception as e:
        print(f"Error checking data: {e}")

if __name__ == "__main__":
    check_postgresql_data()