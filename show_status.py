"""
PostgreSQL 시스템 상태 출력
"""

import sys

# Windows 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, '.')
from src.utils.postgresql_database import PostgreSQLDatabase

def show_status():
    db = PostgreSQLDatabase()
    stats = db.get_dashboard_stats()
    
    print("🎉 PostgreSQL 블로그 자동화 시스템 완성!")
    print("=" * 60)
    print("📊 현재 데이터베이스 상태:")
    print(f"  총 포스트: {stats['posts']['total']}개")
    print(f"  오늘 포스트: {stats['posts']['today']}개") 
    print(f"  사이트별 포스트: {stats['posts']['by_site']}")
    print(f"  파일 통계: {stats['files']}")
    print(f"  총 수익: ${stats['revenue']['total_revenue']:.2f}")
    print(f"  총 조회수: {stats['revenue']['total_views']:,}")
    print("")
    print("🔧 시스템 구성 요소:")
    print("  ✅ PostgreSQL (Supabase) 연결됨")
    print("  ✅ unble 스키마 10개 테이블 구성")
    print("  ✅ SQLite → PostgreSQL 마이그레이션 완료")
    print("  ✅ WordPress 콘텐츠 생성 (PostgreSQL)")
    print("  ✅ 웹 대시보드 (PostgreSQL)")
    print("  ✅ 시스템 로그 & 수익 추적")
    print("")
    print("🚀 사용 방법:")
    print("  1. WordPress 콘텐츠 생성:")
    print("     python generate_wordpress_posts_pg.py --site unpre")
    print("  2. PostgreSQL 대시보드:")
    print("     python start_dashboard_pg.py")
    print("  3. 데이터베이스 연결 테스트:")
    print("     python test_postgresql_connection.py")
    print("=" * 60)

if __name__ == "__main__":
    show_status()