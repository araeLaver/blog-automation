"""
PostgreSQL 웹 대시보드 시작 스크립트
"""

import os
import sys
import webbrowser
from pathlib import Path

# Windows 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

def start_postgresql_dashboard():
    """PostgreSQL 웹 대시보드 시작"""
    print("🌐 블로그 자동화 PostgreSQL 대시보드 시작...")
    print("=" * 60)
    
    # 필요한 디렉토리 생성
    dirs = ["data", "data/logs", "templates", "static"]
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # 환경변수 확인
    from dotenv import load_dotenv
    load_dotenv()
    
    pg_password = os.getenv('PG_PASSWORD')
    if not pg_password:
        print("❌ 환경변수 PG_PASSWORD가 설정되지 않았습니다.")
        print("💡 .env 파일에 PG_PASSWORD=Unbleyum1106! 를 추가하세요.")
        input("엔터키를 눌러 종료...")
        return
    
    # PostgreSQL 연결 테스트
    try:
        from src.utils.postgresql_database import PostgreSQLDatabase
        db = PostgreSQLDatabase()
        print("✅ PostgreSQL 연결 확인 완료")
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        print("💡 .env 파일의 PostgreSQL 설정을 확인하세요.")
        input("엔터키를 눌러 종료...")
        return
    
    # Flask 앱 시작 (메인 app.py 사용)
    from app import app
    
    print("📊 PostgreSQL 대시보드 주소: http://localhost:5000")
    print("🔧 관리자 기능:")
    print("   - PostgreSQL 기반 실시간 모니터링")
    print("   - Supabase 데이터베이스 연동")
    print("   - WordPress 콘텐츠 생성 및 관리")
    print("   - 수익 추적 및 분석")
    print("   - 시스템 로그 모니터링")
    print("=" * 60)
    print("⚠️  종료하려면 Ctrl+C를 누르세요")
    print("=" * 60)
    
    # 브라우저 자동 열기
    import threading
    import time
    
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Flask 서버 시작
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")


if __name__ == "__main__":
    try:
        start_postgresql_dashboard()
    except KeyboardInterrupt:
        print("\\n👋 PostgreSQL 대시보드를 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        input("엔터키를 눌러 종료하세요...")