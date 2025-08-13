#!/usr/bin/env python3
"""
운영 데이터베이스 스키마 초기화 스크립트
"""

import os
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from src.utils.postgresql_database import PostgreSQLDatabase
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def init_schema():
    """데이터베이스 스키마 초기화"""
    try:
        # PostgreSQL 연결
        db = PostgreSQLDatabase()
        
        if not db.is_connected:
            print("❌ 데이터베이스 연결 실패")
            return False
            
        print("✅ 데이터베이스 연결 성공")
        
        # 스키마 파일 실행
        schema_file = Path(__file__).parent / "database" / "postgresql_schema.sql"
        
        if not schema_file.exists():
            print(f"❌ 스키마 파일을 찾을 수 없습니다: {schema_file}")
            return False
            
        print(f"📄 스키마 파일 실행: {schema_file}")
        
        # 스키마 실행
        db.execute_schema_sql(str(schema_file))
        
        print("✅ 스키마 초기화 완료")
        return True
        
    except Exception as e:
        print(f"❌ 스키마 초기화 실패: {e}")
        return False
    finally:
        try:
            db.close_connection()
        except:
            pass

if __name__ == "__main__":
    print("🚀 데이터베이스 스키마 초기화 시작...")
    success = init_schema()
    
    if success:
        print("🎉 스키마 초기화 성공!")
        sys.exit(0)
    else:
        print("💥 스키마 초기화 실패!")
        sys.exit(1)