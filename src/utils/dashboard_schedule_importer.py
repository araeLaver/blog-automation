"""
대시보드 기존 스케줄 데이터를 DB로 가져오는 유틸리티
"""

from datetime import datetime, timedelta
from src.utils.postgresql_database import PostgreSQLDatabase

def import_dashboard_schedules():
    """대시보드에서 보여지는 계획표 데이터를 DB에 입력"""
    
    # 이번주와 다음주 계획표 데이터 (대시보드에서 가져온 실제 데이터)
    schedule_data = {
        # 이번주 (2025-08-25 시작)
        "2025-08-25": {
            0: {  # 월요일
                'unpre': {"topic": "PyTorch로 컴퓨터 비전 구현", "category": "프로그래밍"},
                'untab': {"topic": "부동산 계약 시 주의사항 완전정리", "category": "부동산"},
                'skewese': {"topic": "재활용과 업사이클링의 창조적 실천", "category": "환경"},
                'tistory': {"topic": "북한 핵 위협 지속, 한반도 긴장 고조", "category": "정치"}
            },
            1: {  # 화요일
                'unpre': {"topic": "JWT 토큰 기반 시큐리티 구현", "category": "프로그래밍"},
                'untab': {"topic": "친환경 부동산 그린 리모델링 트렌드", "category": "취미"},
                'skewese': {"topic": "임진왜란과 이순신의 활약", "category": "뷰티/패션"},
                'tistory': {"topic": "MZ세대 투자 패턴 분석, 부작용은?", "category": "일반"}
            },
            2: {  # 수요일
                'unpre': {"topic": "React Hook 고급 활용법", "category": "프로그래밍"},
                'untab': {"topic": "고령화 사회와 실버타운 투자", "category": "투자"},
                'skewese': {"topic": "조선시대 과거제도와 교육", "category": "역사"},
                'tistory': {"topic": "전기차 시장 현황과 미래 전망", "category": "기술"}
            },
            3: {  # 목요일
                'unpre': {"topic": "Python 데이터 분석 마스터", "category": "프로그래밍"},
                'untab': {"topic": "인플레이션 시대의 투자 가이드", "category": "투자"},
                'skewese': {"topic": "한국 전통 건축의 아름다움과 과학", "category": "역사"},
                'tistory': {"topic": "인플레이션 재부상? 2025년 전망", "category": "경제"}
            },
            4: {  # 금요일
                'unpre': {"topic": "TypeScript 고급 타입 시스템", "category": "프로그래밍"},
                'untab': {"topic": "공모주 투자 전략 분석", "category": "투자"},
                'skewese': {"topic": "정조의 개혁 정치와 화성 건설", "category": "역사"},
                'tistory': {"topic": "2026 월드컵 공동개최, 한국 축구 재도약", "category": "스포츠"}
            },
            5: {  # 토요일
                'unpre': {"topic": "GraphQL API 설계와 최적화", "category": "프로그래밍"},
                'untab': {"topic": "메타버스 부동산 투자", "category": "투자"},
                'skewese': {"topic": "고구려의 영토 확장과 광개토대왕", "category": "역사"},
                'tistory': {"topic": "K-문화 글로벌 확산 현황", "category": "문화"}
            },
            6: {  # 일요일
                'unpre': {"topic": "Kubernetes 클러스터 관리", "category": "프로그래밍"},
                'untab': {"topic": "ESG 투자의 미래 전망", "category": "투자"},
                'skewese': {"topic": "조선 후기 실학사상의 발전", "category": "역사"},
                'tistory': {"topic": "전기차 배터리 기술 혁신과 미래", "category": "기술"}
            }
        }
    }
    
    try:
        db = PostgreSQLDatabase()
        conn = db.get_connection()
        
        with conn.cursor() as cursor:
            total_inserted = 0
            
            for week_str, week_data in schedule_data.items():
                week_start = datetime.strptime(week_str, '%Y-%m-%d').date()
                
                print(f"[IMPORT] {week_start} 주 스케줄 입력 중...")
                
                # 해당 주 기존 데이터 삭제
                cursor.execute("""
                    DELETE FROM publishing_schedule 
                    WHERE week_start_date = %s
                """, (week_start,))
                
                deleted_count = cursor.rowcount
                print(f"[IMPORT] 기존 데이터 {deleted_count}개 삭제")
                
                # 새 데이터 입력
                for day_of_week, day_data in week_data.items():
                    for site, topic_info in day_data.items():
                        cursor.execute("""
                            INSERT INTO publishing_schedule 
                            (week_start_date, day_of_week, site, topic_category, specific_topic, 
                             keywords, target_length, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            week_start,
                            day_of_week,
                            site,
                            topic_info['category'],
                            topic_info['topic'],
                            [],  # keywords
                            'medium',  # target_length
                            'planned'  # status
                        ))
                        total_inserted += 1
                
                print(f"[IMPORT] {week_start} 주 완료")
            
            conn.commit()
            print(f"[IMPORT] 총 {total_inserted}개 스케줄 DB 입력 완료")
            return True
            
    except Exception as e:
        print(f"[IMPORT] 오류: {e}")
        return False

def verify_import():
    """입력된 스케줄 확인"""
    try:
        db = PostgreSQLDatabase()
        conn = db.get_connection()
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT week_start_date, day_of_week, site, specific_topic
                FROM publishing_schedule 
                WHERE week_start_date >= '2025-08-25'
                ORDER BY week_start_date, day_of_week, site
            """)
            
            schedules = cursor.fetchall()
            
            print("\n=== 입력된 스케줄 확인 ===")
            current_week = None
            current_day = None
            
            for row in schedules:
                week_start, day_of_week, site, topic = row
                
                if week_start != current_week:
                    current_week = week_start
                    print(f"\n주시작: {week_start}")
                
                if day_of_week != current_day:
                    current_day = day_of_week
                    day_name = ['월','화','수','목','금','토','일'][day_of_week]
                    print(f"  {day_of_week}요일({day_name}):")
                
                print(f"    {site.upper():8s}: {topic}")
            
            print(f"\n총 {len(schedules)}개 스케줄 확인")
            
    except Exception as e:
        print(f"확인 오류: {e}")

if __name__ == "__main__":
    print("대시보드 스케줄 데이터를 DB로 가져오기...")
    success = import_dashboard_schedules()
    
    if success:
        verify_import()
        print("\n✅ 스케줄 가져오기 완료!")
    else:
        print("\n❌ 스케줄 가져오기 실패!")