"""
PostgreSQL (Supabase) 연결 테스트 스크립트
"""

import os
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Windows 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()


def test_connection():
    """PostgreSQL 연결 테스트"""
    print("🔗 Supabase PostgreSQL 연결 테스트")
    print("=" * 50)
    
    # 환경변수 확인
    pg_host = os.getenv('PG_HOST')
    pg_port = os.getenv('PG_PORT', '5432')
    pg_database = os.getenv('PG_DATABASE')
    pg_user = os.getenv('PG_USER')
    pg_password = os.getenv('PG_PASSWORD')
    pg_schema = os.getenv('PG_SCHEMA', 'unble')
    
    print("🔧 연결 정보:")
    print(f"  Host: {pg_host}")
    print(f"  Port: {pg_port}")
    print(f"  Database: {pg_database}")
    print(f"  User: {pg_user}")
    print(f"  Schema: {pg_schema}")
    print(f"  Password: {'✅ 설정됨' if pg_password else '❌ 미설정'}")
    print()
    
    # 필수 정보 확인
    if not all([pg_host, pg_database, pg_user, pg_password]):
        print("❌ 필수 연결 정보가 누락되었습니다.")
        print("💡 .env 파일에 다음 항목들을 설정하세요:")
        if not pg_host: print("  - PG_HOST")
        if not pg_database: print("  - PG_DATABASE") 
        if not pg_user: print("  - PG_USER")
        if not pg_password: print("  - PG_PASSWORD")
        return False
    
    # 연결 테스트
    try:
        print("🔄 연결 시도 중...")
        
        connection_params = {
            'host': pg_host,
            'port': int(pg_port),
            'database': pg_database,
            'user': pg_user,
            'password': pg_password,
        }
        
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # 기본 쿼리 테스트
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ 연결 성공!")
        print(f"📊 PostgreSQL 버전: {version[:50]}...")
        
        # 스키마 확인
        cursor.execute("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name = %s
        """, (pg_schema,))
        
        if cursor.fetchone():
            print(f"✅ 스키마 '{pg_schema}' 존재함")
            
            # 스키마 설정
            cursor.execute(f"SET search_path TO {pg_schema}, public")
            
            # 기존 테이블 확인
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = %s
                ORDER BY table_name
            """, (pg_schema,))
            
            tables = [row[0] for row in cursor.fetchall()]
            if tables:
                print(f"📋 기존 테이블 ({len(tables)}개): {', '.join(tables)}")
            else:
                print("ℹ️ 스키마에 테이블이 없습니다. (신규 설치)")
                
        else:
            print(f"⚠️ 스키마 '{pg_schema}'가 존재하지 않습니다.")
            print("💡 마이그레이션 시 자동 생성됩니다.")
        
        # 연결 종료
        cursor.close()
        conn.close()
        
        print()
        print("🎉 PostgreSQL 연결 테스트 성공!")
        print("💡 이제 마이그레이션을 실행할 수 있습니다:")
        print("   python migrate_to_postgresql.py")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ 연결 실패: {e}")
        
        error_str = str(e).lower()
        if 'password authentication failed' in error_str:
            print("💡 비밀번호가 틀렸습니다. PG_PASSWORD를 확인하세요.")
        elif 'could not connect to server' in error_str:
            print("💡 서버에 연결할 수 없습니다. 호스트와 포트를 확인하세요.")
        elif 'database' in error_str and 'does not exist' in error_str:
            print("💡 데이터베이스가 존재하지 않습니다. PG_DATABASE를 확인하세요.")
        else:
            print("💡 연결 설정을 다시 확인해주세요.")
            
        return False
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False


def create_env_template():
    """환경변수 템플릿 생성"""
    env_template = """# PostgreSQL Database (Supabase)
PG_HOST=aws-0-ap-northeast-2.pooler.supabase.com
PG_PORT=5432
PG_DATABASE=postgres
PG_USER=postgres.lhqzjnpwuftaicjurqxq
PG_PASSWORD=YOUR_SUPABASE_PASSWORD_HERE
PG_SCHEMA=unble
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)
        print("✅ .env 파일 생성 완료")
        print("💡 .env 파일에서 PG_PASSWORD를 설정하고 다시 실행하세요.")
    else:
        print("ℹ️ .env 파일이 이미 존재합니다.")


if __name__ == "__main__":
    try:
        # .env 파일 확인
        if not Path(".env").exists():
            print("⚠️ .env 파일이 없습니다.")
            create_template = input("환경변수 템플릿을 생성하시겠습니까? (y/N): ").strip().lower()
            if create_template == 'y':
                create_env_template()
            sys.exit(1)
        
        # 연결 테스트 실행
        success = test_connection()
        
        if success:
            print()
            migrate = input("연결이 성공했습니다. 마이그레이션을 실행하시겠습니까? (y/N): ").strip().lower()
            if migrate == 'y':
                print("🚀 마이그레이션 실행...")
                os.system("python migrate_to_postgresql.py")
        
    except KeyboardInterrupt:
        print("\n👋 테스트를 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 오류: {e}")