"""
발행 계획표 자동 동기화 모듈
대시보드의 발행 계획표 데이터를 파싱해서 DB에 자동 업데이트
"""

import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.web_dashboard_pg import get_database
except ImportError:
    # 다른 방법으로 데이터베이스 연결
    from src.utils.postgresql_database import PostgreSQLDatabase
    def get_database():
        return PostgreSQLDatabase()

class ScheduleSync:
    def __init__(self):
        self.db = get_database()
        
    def fetch_dashboard_schedule(self) -> Optional[str]:
        """대시보드에서 발행 계획표 HTML 가져오기"""
        try:
            # 실제 대시보드 URL (로컬 또는 운영 서버)
            dashboard_url = "https://sore-kaile-untab-34c55d0a.koyeb.app/"
            
            response = requests.get(dashboard_url, timeout=30)
            if response.status_code == 200:
                return response.text
            else:
                print(f"[SCHEDULE_SYNC] 대시보드 접근 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[SCHEDULE_SYNC] 대시보드 조회 오류: {e}")
            return None
    
    def parse_schedule_from_html(self, html_content: str) -> List[Dict]:
        """HTML에서 발행 계획표 데이터 파싱"""
        schedules = []
        
        try:
            # 발행 계획표 섹션 찾기 (실제 HTML 구조에 맞게 조정 필요)
            # 예: <div class="schedule-item" data-date="2025-08-26" data-site="unpre">
            
            # 날짜별 패턴 매칭
            date_pattern = r'(\d{4}-\d{2}-\d{2})\s*([월화수목금토일]요일)?'
            site_pattern = r'📝\s*(UNPRE|UNTAB|SKEWESE|TISTORY)\s*([^\n]+)\s*([가-힣]+)'
            
            # HTML에서 발행 계획표 텍스트 추출
            # 실제 구조: 
            # 2025-08-26 화요일
            # 📝 UNPRE JWT 토큰 기반 시큐리티 구현 프로그래밍
            
            lines = html_content.split('\n')
            current_date = None
            current_weekday = None
            
            for line in lines:
                line = line.strip()
                
                # 날짜 라인 찾기
                date_match = re.search(date_pattern, line)
                if date_match:
                    current_date = date_match.group(1)
                    continue
                
                # 사이트 주제 라인 찾기
                site_match = re.search(site_pattern, line)
                if site_match and current_date:
                    site = site_match.group(1).lower()
                    topic = site_match.group(2).strip()
                    category = site_match.group(3).strip()
                    
                    # 날짜를 파싱해서 요일 계산
                    date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
                    weekday = date_obj.weekday()  # 0=월요일
                    
                    # 해당 주의 월요일 날짜 계산
                    week_start = date_obj - timedelta(days=weekday)
                    
                    schedules.append({
                        'week_start_date': week_start,
                        'day_of_week': weekday,
                        'site': site,
                        'topic_category': category,
                        'specific_topic': topic,
                        'keywords': [],
                        'target_length': 'medium',
                        'status': 'planned'
                    })
            
            print(f"[SCHEDULE_SYNC] HTML에서 {len(schedules)}개 스케줄 파싱")
            return schedules
            
        except Exception as e:
            print(f"[SCHEDULE_SYNC] HTML 파싱 오류: {e}")
            return []
    
    def parse_schedule_from_text(self, schedule_text: str) -> List[Dict]:
        """텍스트에서 발행 계획표 데이터 파싱 (백업 방식)"""
        schedules = []
        
        # 실제 사용자가 제공한 계획표 형식 파싱
        # 화요일 2025-08-26
        # 📝 UNPRE JWT 토큰 기반 시큐리티 구현 프로그래밍
        
        lines = schedule_text.split('\n')
        current_date = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 날짜 라인 체크
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if date_match:
                current_date = date_match.group(1)
                continue
            
            # 사이트 주제 라인 체크
            site_match = re.search(r'📝\s*(UNPRE|UNTAB|SKEWESE|TISTORY)\s*([^\n]+)', line)
            if site_match and current_date:
                site = site_match.group(1).lower()
                content = site_match.group(2).strip()
                
                # 주제와 카테고리 분리 (마지막 단어를 카테고리로 간주)
                parts = content.rsplit(' ', 1)
                if len(parts) == 2:
                    topic = parts[0].strip()
                    category = parts[1].strip()
                else:
                    topic = content
                    category = "일반"
                
                # 날짜 파싱
                date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
                weekday = date_obj.weekday()
                week_start = date_obj - timedelta(days=weekday)
                
                schedules.append({
                    'week_start_date': week_start,
                    'day_of_week': weekday,
                    'site': site,
                    'topic_category': category,
                    'specific_topic': topic,
                    'keywords': [],
                    'target_length': 'medium',
                    'status': 'planned'
                })
        
        return schedules
    
    def update_database_schedule(self, schedules: List[Dict]) -> bool:
        """파싱된 스케줄 데이터를 DB에 업데이트"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                
                # 업데이트할 주들 수집
                weeks_to_update = set()
                for schedule in schedules:
                    weeks_to_update.add(schedule['week_start_date'])
                
                # 각 주별로 기존 데이터 삭제 후 새로 입력
                for week_start in weeks_to_update:
                    print(f"[SCHEDULE_SYNC] {week_start} 주 스케줄 업데이트")
                    
                    # 기존 데이터 삭제
                    cursor.execute("""
                        DELETE FROM publishing_schedule 
                        WHERE week_start_date = %s
                    """, (week_start,))
                    
                    # 해당 주의 새 데이터 입력
                    week_schedules = [s for s in schedules if s['week_start_date'] == week_start]
                    
                    for schedule in week_schedules:
                        cursor.execute("""
                            INSERT INTO publishing_schedule 
                            (week_start_date, day_of_week, site, topic_category, specific_topic, 
                             keywords, target_length, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            schedule['week_start_date'],
                            schedule['day_of_week'],
                            schedule['site'],
                            schedule['topic_category'],
                            schedule['specific_topic'],
                            schedule['keywords'],
                            schedule['target_length'],
                            schedule['status']
                        ))
                
                conn.commit()
                print(f"[SCHEDULE_SYNC] {len(schedules)}개 스케줄 DB 업데이트 완료")
                return True
                
        except Exception as e:
            print(f"[SCHEDULE_SYNC] DB 업데이트 오류: {e}")
            return False
    
    def sync_schedule_from_text(self, schedule_text: str) -> bool:
        """텍스트 기반 스케줄 동기화"""
        schedules = self.parse_schedule_from_text(schedule_text)
        if schedules:
            return self.update_database_schedule(schedules)
        return False
    
    def sync_schedule_from_dashboard(self) -> bool:
        """대시보드 기반 스케줄 동기화"""
        html_content = self.fetch_dashboard_schedule()
        if html_content:
            schedules = self.parse_schedule_from_html(html_content)
            if schedules:
                return self.update_database_schedule(schedules)
        return False
    
    def manual_sync_current_week(self) -> bool:
        """현재 주 스케줄 수동 동기화 (긴급용)"""
        # 사용자가 제공한 이번주 계획표 데이터
        current_week_schedule = """
        화요일 2025-08-26
        📝 UNPRE JWT 토큰 기반 시큐리티 구현 프로그래밍
        📝 UNTAB 친환경 부동산 그린 리모델링 트렌드 취미
        📝 SKEWESE 임진왜란과 이순신의 활약 뷰티/패션
        📝 TISTORY MZ세대 투자 패턴 분석, 부작용은? 일반
        """
        
        return self.sync_schedule_from_text(current_week_schedule)

# 웹 API 엔드포인트용 함수들
def sync_schedule_api(schedule_text: str = None) -> Dict:
    """API용 스케줄 동기화 함수"""
    sync = ScheduleSync()
    
    try:
        if schedule_text:
            success = sync.sync_schedule_from_text(schedule_text)
        else:
            success = sync.sync_schedule_from_dashboard()
        
        return {
            "success": success,
            "message": "스케줄 동기화 완료" if success else "스케줄 동기화 실패",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"동기화 오류: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def emergency_sync_current_week() -> Dict:
    """긴급 현재 주 동기화"""
    sync = ScheduleSync()
    success = sync.manual_sync_current_week()
    
    return {
        "success": success,
        "message": "긴급 동기화 완료" if success else "긴급 동기화 실패",
        "timestamp": datetime.now().isoformat()
    }