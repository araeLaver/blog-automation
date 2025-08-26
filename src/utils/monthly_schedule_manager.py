"""
월별 발행 계획표 관리자
- 새로운 monthly_publishing_schedule 테이블 사용
- 날짜별 듀얼 카테고리 주제 관리
"""

import psycopg2
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv

load_dotenv('.env.example')

class MonthlyScheduleManager:
    """월별 스케줄 관리자"""
    
    def __init__(self):
        # 환경변수 우선, 없으면 하드코딩 값 사용 
        self.db_config = {
            'host': os.getenv('PG_HOST', "aws-0-ap-northeast-2.pooler.supabase.com"),
            'database': os.getenv('PG_DATABASE', "postgres"),
            'user': os.getenv('PG_USER', "postgres.lhqzjnpwuftaicjurqxq"),
            'password': os.getenv('PG_PASSWORD', "Unbleyum1106!"),
            'port': int(os.getenv('PG_PORT', 5432))
        }
    
    def get_db_connection(self):
        """데이터베이스 연결"""
        return psycopg2.connect(**self.db_config)
    
    def get_today_dual_topics(self, site):
        """오늘 날짜의 듀얼 카테고리 주제 가져오기"""
        
        today = date.today()
        
        conn = None
        cursor = None
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # monthly_publishing_schedule 테이블에서만 조회 (정확한 계획표)
            cursor.execute("""
                SELECT topic_category, specific_topic, keywords
                FROM unble.monthly_publishing_schedule
                WHERE year = %s AND month = %s AND day = %s AND site = %s
                ORDER BY topic_category
            """, (today.year, today.month, today.day, site))
            
            topics = cursor.fetchall()
            
            if len(topics) >= 2:
                # Primary와 Secondary 구분 (알파벳 순)
                primary = {
                    'category': topics[0][0],
                    'topic': topics[0][1],
                    'keywords': topics[0][2] or []
                }
                secondary = {
                    'category': topics[1][0],
                    'topic': topics[1][1],
                    'keywords': topics[1][2] or []
                }
                
                return primary, secondary
            elif len(topics) == 1:
                # 1개만 있는 경우
                single = {
                    'category': topics[0][0],
                    'topic': topics[0][1],
                    'keywords': topics[0][2] or []
                }
                return single, None
            else:
                # 주제가 없는 경우 기본값 반환
                default = {
                    'category': 'general',
                    'topic': f'{site} 기본 주제',
                    'keywords': ['기본', '주제']
                }
                return default, None
                
        except Exception as e:
            print(f"[MONTHLY_SCHEDULE] 오늘 주제 조회 오류 ({site}): {e}")
            # DB 연결 실패 시 자동발행 중단 (잘못된 주제로 발행하지 않음)
            raise Exception(f"DB 연결 실패로 {site} 자동발행 불가: {e}")
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_topics_by_date(self, target_date, site=None):
        """특정 날짜의 주제들 가져오기"""
        
        conn = None
        cursor = None
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            if site:
                cursor.execute("""
                    SELECT site, topic_category, specific_topic, keywords, status
                    FROM unble.monthly_publishing_schedule
                    WHERE year = %s AND month = %s AND day = %s AND site = %s
                    ORDER BY site, topic_category
                """, (target_date.year, target_date.month, target_date.day, site))
            else:
                cursor.execute("""
                    SELECT site, topic_category, specific_topic, keywords, status
                    FROM unble.monthly_publishing_schedule
                    WHERE year = %s AND month = %s AND day = %s
                    ORDER BY site, topic_category
                """, (target_date.year, target_date.month, target_date.day))
            
            topics = cursor.fetchall()
            
            result = []
            for topic in topics:
                site_name, category, specific_topic, keywords, status = topic
                result.append({
                    'site': site_name,
                    'category': category,
                    'topic': specific_topic,
                    'keywords': keywords or [],
                    'status': status
                })
            
            return result
            
        except Exception as e:
            print(f"[MONTHLY_SCHEDULE] 날짜별 주제 조회 오류: {e}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_month_schedule(self, year, month):
        """월 전체 스케줄 가져오기"""
        
        conn = None
        cursor = None
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 먼저 monthly_publishing_schedule 테이블 조회
            cursor.execute("""
                SELECT day, site, topic_category, specific_topic, keywords, status
                FROM unble.monthly_publishing_schedule
                WHERE year = %s AND month = %s
                ORDER BY day, site, topic_category
            """, (year, month))
            
            topics = cursor.fetchall()
            
            # 데이터가 없으면 기존 publishing_schedule 테이블에서 조회 (폴백)
            if not topics:
                # 해당 월의 모든 날짜에 대해 publishing_schedule 테이블 조회
                cursor.execute("""
                    SELECT EXTRACT(DAY FROM scheduled_date) as day, site, topic_category, specific_topic, keywords, 'pending' as status
                    FROM unble.publishing_schedule
                    WHERE EXTRACT(YEAR FROM scheduled_date) = %s 
                    AND EXTRACT(MONTH FROM scheduled_date) = %s
                    ORDER BY day, site, topic_category
                """, (year, month))
                
                topics = cursor.fetchall()
            
            # 날짜별로 그룹핑
            schedule = {}
            for topic in topics:
                day, site, category, specific_topic, keywords, status = topic
                
                if day not in schedule:
                    schedule[day] = {}
                if site not in schedule[day]:
                    schedule[day][site] = []
                
                schedule[day][site].append({
                    'category': category,
                    'topic': specific_topic,
                    'keywords': keywords or [],
                    'status': status
                })
            
            return schedule
            
        except Exception as e:
            print(f"[MONTHLY_SCHEDULE] 월별 스케줄 조회 오류: {e}")
            return {}
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def update_topic_status(self, year, month, day, site, topic_category, status):
        """주제 상태 업데이트"""
        
        conn = None
        cursor = None
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE unble.monthly_publishing_schedule
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE year = %s AND month = %s AND day = %s 
                AND site = %s AND topic_category = %s
            """, (status, year, month, day, site, topic_category))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"[MONTHLY_SCHEDULE] 상태 업데이트 성공: {year}-{month:02d}-{day:02d} {site} {topic_category} -> {status}")
                return True
            else:
                print(f"[MONTHLY_SCHEDULE] 업데이트할 주제를 찾을 수 없음")
                return False
                
        except Exception as e:
            print(f"[MONTHLY_SCHEDULE] 상태 업데이트 오류: {e}")
            if conn:
                conn.rollback()
            return False
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_today_dual_topics_for_manual(self, site):
        """수동 발행용 오늘의 듀얼 주제 (기존 호환성)"""
        return self.get_today_dual_topics(site)

# 전역 인스턴스
monthly_schedule_manager = MonthlyScheduleManager()