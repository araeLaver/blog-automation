"""
Test script to verify database fix for content_files table
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_stats_query():
    """Test the stats query that was causing errors"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT', 5432),
            database=os.getenv('PG_DATABASE'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            options=f"-c search_path={os.getenv('PG_SCHEMA', 'unble')}"
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test the exact query from the stats endpoint
        cursor.execute("""
            SELECT 
                COUNT(*) as total_posts,
                COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
                COUNT(CASE WHEN status != 'published' THEN 1 END) as scheduled,
                COUNT(CASE WHEN DATE(created_at) = CURRENT_DATE THEN 1 END) as today_posts
            FROM unble.content_files
        """)
        
        stats = cursor.fetchone()
        print("Stats query successful!")
        print(f"Total posts: {stats['total_posts']}")
        print(f"Published: {stats['published']}")
        print(f"Scheduled: {stats['scheduled']}")
        print(f"Today's posts: {stats['today_posts']}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_wordpress_files_query():
    """Test the WordPress files query"""
    try:
        from src.utils.postgresql_database import PostgreSQLDatabase
        
        db = PostgreSQLDatabase()
        files = db.get_content_files(file_type='wordpress', limit=5)
        
        print(f"\nWordPress files query successful!")
        print(f"Retrieved {len(files)} WordPress files")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_tistory_files_query():
    """Test the Tistory files query"""
    try:
        from src.utils.postgresql_database import PostgreSQLDatabase
        
        db = PostgreSQLDatabase()
        files = db.get_content_files(file_type='tistory', limit=5)
        
        print(f"\nTistory files query successful!")
        print(f"Retrieved {len(files)} Tistory files")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing database fixes for content_files table...")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test stats query
    if not test_stats_query():
        all_tests_passed = False
    
    # Test WordPress files query
    if not test_wordpress_files_query():
        all_tests_passed = False
    
    # Test Tistory files query  
    if not test_tistory_files_query():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("All tests passed! Database fix is working correctly.")
    else:
        print("Some tests failed. Please check the errors above.")