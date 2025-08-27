#!/usr/bin/env python3
"""
유료 DB 설정 및 스키마 생성 스크립트
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv('.env.example')

# 데이터베이스 연결 설정
db_config = {
    'host': os.getenv('PG_HOST', 'ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app'),
    'database': os.getenv('PG_DATABASE', 'unble'),
    'user': os.getenv('PG_USER', 'unble'),
    'password': os.getenv('PG_PASSWORD', 'npg_1kjV0mhECxqs'),
    'port': int(os.getenv('PG_PORT', 5432))
}

def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        print("데이터베이스 연결 테스트 중...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 버전 확인
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ 연결 성공!")
        print(f"PostgreSQL 버전: {version}")
        
        # 현재 스키마 확인
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name;
        """)
        schemas = cursor.fetchall()
        print(f"\n현재 스키마 목록:")
        for schema in schemas:
            print(f"  - {schema[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

def create_schema_and_tables():
    """스키마 및 테이블 생성"""
    try:
        print("\n스키마 및 테이블 생성 중...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True  # DDL 문장 실행을 위해 autocommit 설정
        cursor = conn.cursor()
        
        # SQL 파일 읽기
        with open('database/create_blog_automation_schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # SQL 문장을 개별적으로 실행 (세미콜론으로 분리)
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements):
            try:
                # INDEX 문법 수정 (PostgreSQL은 CREATE INDEX 사용)
                if 'INDEX' in statement and 'CREATE' not in statement:
                    # INDEX를 CREATE INDEX로 변환
                    statement = statement.replace('INDEX ', 'CREATE INDEX IF NOT EXISTS ')
                    # 테이블명 추출 및 인덱스 이름 생성
                    if 'blog_automation.' in statement:
                        table_part = statement.split('blog_automation.')[1].split('(')[0].strip()
                        idx_name = statement.split('INDEX IF NOT EXISTS ')[1].split(' ')[0]
                        statement = statement.replace(
                            f'CREATE INDEX IF NOT EXISTS {idx_name}',
                            f'CREATE INDEX IF NOT EXISTS {table_part}_{idx_name} ON blog_automation.{table_part}'
                        )
                
                cursor.execute(statement)
                success_count += 1
                
                # 주요 테이블 생성 시 메시지 출력
                if 'CREATE TABLE' in statement:
                    table_name = statement.split('blog_automation.')[1].split(' ')[0] if 'blog_automation.' in statement else 'unknown'
                    print(f"  ✓ 테이블 생성: {table_name}")
                elif 'CREATE SCHEMA' in statement:
                    print("  ✓ 스키마 'blog_automation' 생성")
                    
            except Exception as e:
                error_count += 1
                if 'already exists' not in str(e):
                    print(f"  ⚠️  오류 (문장 {i+1}): {str(e)[:100]}")
        
        print(f"\n완료: 성공 {success_count}, 오류 {error_count}")
        
        # 생성된 테이블 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'blog_automation' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"\n생성된 테이블 목록:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 스키마/테이블 생성 실패: {e}")
        return False

def migrate_existing_data():
    """기존 데이터 마이그레이션"""
    try:
        print("\n기존 데이터 마이그레이션 확인 중...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 기존 unble 스키마에 데이터가 있는지 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'unble' 
                AND table_name = 'monthly_publishing_schedule'
            );
        """)
        
        if cursor.fetchone()[0]:
            print("  ✓ 기존 unble 스키마에서 데이터 발견")
            
            # monthly_publishing_schedule 데이터 복사
            cursor.execute("""
                INSERT INTO blog_automation.monthly_publishing_schedule 
                (year, month, day, site, topic_category, specific_topic, keywords, status, created_at, updated_at)
                SELECT year, month, day, site, topic_category, specific_topic, keywords, status, created_at, updated_at
                FROM unble.monthly_publishing_schedule
                WHERE NOT EXISTS (
                    SELECT 1 FROM blog_automation.monthly_publishing_schedule b
                    WHERE b.year = unble.monthly_publishing_schedule.year
                    AND b.month = unble.monthly_publishing_schedule.month
                    AND b.day = unble.monthly_publishing_schedule.day
                    AND b.site = unble.monthly_publishing_schedule.site
                    AND b.topic_category = unble.monthly_publishing_schedule.topic_category
                );
            """)
            copied_rows = cursor.rowcount
            print(f"  ✓ monthly_publishing_schedule: {copied_rows}개 행 복사")
            
            # content_files 데이터 복사
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'unble' 
                    AND table_name = 'content_files'
                );
            """)
            
            if cursor.fetchone()[0]:
                cursor.execute("""
                    INSERT INTO blog_automation.content_files 
                    (site, title, file_path, category, tags, categories, meta_description, 
                     status, created_at, published_at, wordpress_post_id, tistory_post_id, publish_url)
                    SELECT site, title, file_path, category, tags, categories, meta_description, 
                           status, created_at, published_at, wordpress_post_id, tistory_post_id, publish_url
                    FROM unble.content_files
                    WHERE NOT EXISTS (
                        SELECT 1 FROM blog_automation.content_files b
                        WHERE b.site = unble.content_files.site
                        AND b.title = unble.content_files.title
                        AND b.file_path = unble.content_files.file_path
                    );
                """)
                copied_rows = cursor.rowcount
                print(f"  ✓ content_files: {copied_rows}개 행 복사")
            
            conn.commit()
        else:
            print("  - 기존 데이터가 없습니다. 새로 시작합니다.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"⚠️  마이그레이션 중 오류: {e}")
        return False

def update_postgresql_database_module():
    """PostgreSQL 데이터베이스 모듈 업데이트"""
    try:
        print("\nPostgreSQL 데이터베이스 모듈 업데이트 중...")
        
        # postgresql_database.py 파일 읽기
        with open('src/utils/postgresql_database.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 스키마명 변경
        content = content.replace("self.schema = 'unble'", "self.schema = 'blog_automation'")
        
        # 파일 다시 쓰기
        with open('src/utils/postgresql_database.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("  ✓ postgresql_database.py 스키마 업데이트 완료")
        
        # monthly_schedule_manager.py도 업데이트
        with open('src/utils/monthly_schedule_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # unble. 를 blog_automation. 으로 변경
        content = content.replace('unble.monthly_publishing_schedule', 'blog_automation.monthly_publishing_schedule')
        content = content.replace('unble.publishing_schedule', 'blog_automation.publishing_schedule')
        
        with open('src/utils/monthly_schedule_manager.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("  ✓ monthly_schedule_manager.py 스키마 업데이트 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 모듈 업데이트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=== Blog Automation 유료 DB 설정 시작 ===\n")
    
    # 1. 연결 테스트
    if not test_connection():
        return
    
    # 2. 스키마 및 테이블 생성
    if not create_schema_and_tables():
        return
    
    # 3. 기존 데이터 마이그레이션
    migrate_existing_data()
    
    # 4. 모듈 업데이트
    update_postgresql_database_module()
    
    print("\n=== 설정 완료 ===")
    print("\n다음 단계:")
    print("1. .env.example을 .env로 복사하여 실제 환경에서 사용")
    print("2. 서비스 재시작하여 새 DB 연결 확인")
    print("3. 자동 발행 스케줄러가 정상 작동하는지 확인")

if __name__ == "__main__":
    main()