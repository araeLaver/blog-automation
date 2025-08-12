"""
SQLite에서 PostgreSQL로 데이터 마이그레이션 스크립트
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Windows 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.database import ContentDatabase as SQLiteDB
from src.utils.postgresql_database import PostgreSQLDatabase
from dotenv import load_dotenv

load_dotenv()


class DatabaseMigrator:
    def __init__(self):
        """데이터 마이그레이션 초기화"""
        self.sqlite_db = SQLiteDB()
        
        # PostgreSQL 연결 정보 확인
        pg_password = os.getenv('PG_PASSWORD')
        if not pg_password:
            print("❌ 환경변수 PG_PASSWORD가 설정되지 않았습니다.")
            print("💡 .env 파일에 PG_PASSWORD를 설정하고 다시 실행하세요.")
            sys.exit(1)
        
        try:
            self.pg_db = PostgreSQLDatabase()
            print("✅ PostgreSQL 연결 성공")
        except Exception as e:
            print(f"❌ PostgreSQL 연결 실패: {e}")
            print("💡 .env 파일의 PostgreSQL 설정을 확인하세요.")
            sys.exit(1)
    
    def setup_postgresql_schema(self):
        """PostgreSQL 스키마 설정"""
        print("🔧 PostgreSQL 스키마 설정 중...")
        
        schema_file = Path("database/postgresql_schema.sql")
        if not schema_file.exists():
            print(f"❌ 스키마 파일이 없습니다: {schema_file}")
            return False
        
        try:
            self.pg_db.execute_schema_sql(str(schema_file))
            print("✅ PostgreSQL 스키마 설정 완료")
            return True
        except Exception as e:
            print(f"❌ 스키마 설정 실패: {e}")
            return False
    
    def migrate_content_history(self):
        """콘텐츠 히스토리 마이그레이션"""
        print("📝 콘텐츠 히스토리 마이그레이션 중...")
        
        try:
            # SQLite에서 데이터 조회
            with sqlite3.connect(self.sqlite_db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT site, title, title_hash, category, keywords, 
                           content_hash, url, published_date, status
                    FROM content_history
                """)
                
                rows = cursor.fetchall()
                print(f"📊 마이그레이션할 콘텐츠: {len(rows)}개")
                
                migrated_count = 0
                for row in rows:
                    try:
                        site, title, title_hash, category, keywords_json, content_hash, url, published_date, status = row
                        
                        # keywords JSON 파싱
                        keywords = json.loads(keywords_json) if keywords_json else []
                        
                        # PostgreSQL에 삽입
                        self.pg_db.add_content(
                            site=site,
                            title=title,
                            category=category,
                            keywords=keywords,
                            content="",  # 실제 콘텐츠는 없음
                            url=url
                        )
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        print(f"⚠️ 콘텐츠 마이그레이션 실패: {title[:30]}... - {e}")
                        continue
                
                print(f"✅ 콘텐츠 히스토리 마이그레이션 완료: {migrated_count}/{len(rows)}")
                return True
                
        except Exception as e:
            print(f"❌ 콘텐츠 히스토리 마이그레이션 실패: {e}")
            return False
    
    def migrate_topic_pool(self):
        """주제 풀 마이그레이션"""
        print("💡 주제 풀 마이그레이션 중...")
        
        try:
            with sqlite3.connect(self.sqlite_db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT site, topic, category, priority, used, used_date
                    FROM topic_pool
                """)
                
                rows = cursor.fetchall()
                print(f"📊 마이그레이션할 주제: {len(rows)}개")
                
                if not rows:
                    print("ℹ️ 주제 풀 데이터가 없습니다. 기본 주제를 생성합니다.")
                    self.create_default_topics()
                    return True
                
                # 주제 데이터 변환
                topics_by_site = {}
                for row in rows:
                    site, topic, category, priority, used, used_date = row
                    
                    if site not in topics_by_site:
                        topics_by_site[site] = []
                    
                    topics_by_site[site].append({
                        'topic': topic,
                        'category': category or '',
                        'priority': priority or 5,
                        'target_keywords': []
                    })
                
                # 사이트별 일괄 추가
                migrated_count = 0
                for site, topics in topics_by_site.items():
                    try:
                        self.pg_db.add_topics_bulk(site, topics)
                        migrated_count += len(topics)
                    except Exception as e:
                        print(f"⚠️ {site} 주제 마이그레이션 실패: {e}")
                
                print(f"✅ 주제 풀 마이그레이션 완료: {migrated_count}개")
                return True
                
        except Exception as e:
            print(f"❌ 주제 풀 마이그레이션 실패: {e}")
            return False
    
    def migrate_content_files(self):
        """콘텐츠 파일 마이그레이션"""
        print("📁 콘텐츠 파일 마이그레이션 중...")
        
        try:
            with sqlite3.connect(self.sqlite_db.db_path) as conn:
                cursor = conn.cursor()
                
                # 콘텐츠 파일 테이블이 존재하는지 확인
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='content_files'
                """)
                
                if not cursor.fetchone():
                    print("ℹ️ content_files 테이블이 없습니다. 건너뜁니다.")
                    return True
                
                cursor.execute("""
                    SELECT site, title, file_path, file_type, word_count, 
                           reading_time, status, tags, categories, created_at, file_size
                    FROM content_files
                """)
                
                rows = cursor.fetchall()
                print(f"📊 마이그레이션할 파일: {len(rows)}개")
                
                migrated_count = 0
                for row in rows:
                    try:
                        site, title, file_path, file_type, word_count, reading_time, status, tags_json, categories_json, created_at, file_size = row
                        
                        # JSON 파싱
                        tags = json.loads(tags_json) if tags_json else []
                        categories = json.loads(categories_json) if categories_json else []
                        
                        metadata = {
                            'word_count': word_count or 0,
                            'reading_time': reading_time or 0,
                            'tags': tags,
                            'categories': categories,
                            'file_size': file_size or 0
                        }
                        
                        self.pg_db.add_content_file(
                            site=site,
                            title=title,
                            file_path=file_path,
                            file_type=file_type,
                            metadata=metadata
                        )
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        print(f"⚠️ 파일 마이그레이션 실패: {title[:30]}... - {e}")
                        continue
                
                print(f"✅ 콘텐츠 파일 마이그레이션 완료: {migrated_count}/{len(rows)}")
                return True
                
        except Exception as e:
            print(f"❌ 콘텐츠 파일 마이그레이션 실패: {e}")
            return False
    
    def create_default_topics(self):
        """기본 주제 생성"""
        print("🎯 기본 주제 생성 중...")
        
        default_topics = {
            "unpre": [
                {"topic": "React Hook 사용법과 최적화", "category": "개발", "priority": 9},
                {"topic": "TypeScript 고급 타입 시스템", "category": "개발", "priority": 8},
                {"topic": "Node.js 성능 최적화 기법", "category": "개발", "priority": 8},
                {"topic": "Docker 컨테이너 실전 활용", "category": "개발", "priority": 7},
                {"topic": "AWS Lambda 서버리스 아키텍처", "category": "개발", "priority": 8},
                {"topic": "정보처리기사 실기 알고리즘 문제", "category": "정보처리기사", "priority": 9},
                {"topic": "정보처리기사 데이터베이스 설계", "category": "정보처리기사", "priority": 8},
                {"topic": "정보처리기사 네트워크 보안", "category": "정보처리기사", "priority": 7},
                {"topic": "영어 회화 실력 향상 방법", "category": "언어학습", "priority": 8},
                {"topic": "TOEIC 고득점 전략과 팁", "category": "언어학습", "priority": 9},
            ],
            "untab": [
                {"topic": "2024년 부동산 시장 전망", "category": "부동산", "priority": 9},
                {"topic": "아파트 투자 전략과 주의사항", "category": "투자", "priority": 8},
                {"topic": "전세 vs 매매 선택 기준", "category": "부동산", "priority": 8},
                {"topic": "부동산 대출 금리 비교 분석", "category": "부동산", "priority": 7},
                {"topic": "재건축 재개발 투자 가이드", "category": "투자", "priority": 8},
                {"topic": "부동산 경매 초보자 가이드", "category": "부동산", "priority": 7},
                {"topic": "상가 임대업 수익률 분석", "category": "투자", "priority": 6},
                {"topic": "부동산 세금 절약 방법", "category": "경제", "priority": 7},
            ],
            "skewese": [
                {"topic": "조선시대 궁중문화와 예법", "category": "역사", "priority": 8},
                {"topic": "삼국시대 문화 교류의 역사", "category": "역사", "priority": 7},
                {"topic": "일제강점기 독립운동사", "category": "역사", "priority": 9},
                {"topic": "고려시대 불교문화의 특징", "category": "문화", "priority": 7},
                {"topic": "한국 전통 건축의 아름다움", "category": "문화", "priority": 6},
                {"topic": "세계사 속 한국의 위치", "category": "교육", "priority": 7},
                {"topic": "역사적 인물로 본 리더십", "category": "교육", "priority": 6},
                {"topic": "전통문화의 현대적 계승", "category": "문화", "priority": 7},
            ]
        }
        
        total_added = 0
        for site, topics in default_topics.items():
            try:
                self.pg_db.add_topics_bulk(site, topics)
                total_added += len(topics)
                print(f"  ✅ {site}: {len(topics)}개 주제 추가")
            except Exception as e:
                print(f"  ❌ {site} 기본 주제 추가 실패: {e}")
        
        print(f"✅ 총 {total_added}개 기본 주제 생성 완료")
    
    def verify_migration(self):
        """마이그레이션 검증"""
        print("🔍 마이그레이션 결과 검증 중...")
        
        try:
            # PostgreSQL 통계 조회
            stats = self.pg_db.get_dashboard_stats()
            
            print("📊 마이그레이션 결과:")
            print(f"  - 총 포스트 수: {stats['posts']['total']}")
            print(f"  - 사이트별 포스트: {stats['posts']['by_site']}")
            print(f"  - 파일 통계: {stats['files']}")
            
            # 주제 풀 확인
            pg_conn = self.pg_db.get_connection()
            with pg_conn.cursor() as cursor:
                cursor.execute("SELECT site, COUNT(*) FROM topic_pool GROUP BY site")
                topic_stats = dict(cursor.fetchall())
                print(f"  - 사이트별 주제: {topic_stats}")
            
            print("✅ 마이그레이션 검증 완료")
            return True
            
        except Exception as e:
            print(f"❌ 검증 실패: {e}")
            return False
    
    def run_migration(self):
        """전체 마이그레이션 실행"""
        print("🚀 SQLite → PostgreSQL 마이그레이션 시작")
        print("=" * 60)
        
        steps = [
            ("PostgreSQL 스키마 설정", self.setup_postgresql_schema),
            ("콘텐츠 히스토리 마이그레이션", self.migrate_content_history),
            ("주제 풀 마이그레이션", self.migrate_topic_pool),
            ("콘텐츠 파일 마이그레이션", self.migrate_content_files),
            ("마이그레이션 검증", self.verify_migration),
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            try:
                if step_func():
                    success_count += 1
                    print(f"✅ {step_name} 완료")
                else:
                    print(f"❌ {step_name} 실패")
            except Exception as e:
                print(f"❌ {step_name} 오류: {e}")
        
        print("\n" + "=" * 60)
        if success_count == len(steps):
            print("🎉 마이그레이션 완료! PostgreSQL 사용 준비됨")
            print("\n💡 다음 단계:")
            print("1. .env 파일에서 PG_PASSWORD 설정 확인")
            print("2. 웹 대시보드에서 PostgreSQL 연동 확인")
            print("3. 기존 SQLite 파일 백업 후 삭제 고려")
        else:
            print(f"⚠️ 마이그레이션 부분 완료: {success_count}/{len(steps)} 성공")
        
        print("=" * 60)


def main():
    """메인 실행 함수"""
    print("📊 블로그 자동화 시스템 - DB 마이그레이션")
    print("SQLite → PostgreSQL (Supabase)")
    print("=" * 60)
    
    # 사용자 확인
    response = input("마이그레이션을 시작하시겠습니까? (y/N): ").strip().lower()
    if response != 'y':
        print("마이그레이션을 취소했습니다.")
        return
    
    try:
        migrator = DatabaseMigrator()
        migrator.run_migration()
        
    except KeyboardInterrupt:
        print("\n👋 마이그레이션을 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 마이그레이션 오류: {e}")
        print("💡 .env 파일과 PostgreSQL 연결 설정을 확인하세요.")


if __name__ == "__main__":
    main()