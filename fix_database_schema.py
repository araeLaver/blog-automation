#!/usr/bin/env python3
"""
데이터베이스 스키마 오류 수정 스크립트
- content_files 테이블의 status 제약조건 수정
- 누락된 테이블 생성 (content_history, system_logs 등)
- 트랜잭션 오류 방지를 위한 연결 최적화
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 시스템 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.postgresql_database import PostgreSQLDatabase
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """데이터베이스 스키마 오류 수정 실행"""
    
    try:
        # DB 연결
        db = PostgreSQLDatabase()
        if not db.is_connected:
            logger.error("데이터베이스 연결 실패")
            return False
        
        logger.info("데이터베이스 스키마 수정 시작...")
        
        # 스키마 수정 SQL 실행
        sql_file = project_root / "database" / "fix_schema_errors.sql"
        if not sql_file.exists():
            logger.error(f"SQL 파일을 찾을 수 없습니다: {sql_file}")
            return False
            
        db.execute_schema_sql(str(sql_file))
        logger.info("✅ 데이터베이스 스키마 수정 완료")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 스키마 수정 중 오류 발생: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close_connection()

if __name__ == "__main__":
    success = fix_database_schema()
    if success:
        print("✅ 데이터베이스 스키마 수정이 완료되었습니다.")
        print("이제 Koyeb에서 애플리케이션이 정상 작동해야 합니다.")
    else:
        print("❌ 데이터베이스 스키마 수정에 실패했습니다.")
        print("로그를 확인하고 다시 시도하세요.")
        sys.exit(1)