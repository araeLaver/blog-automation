"""
자동 발행 스케줄러
- 새벽 시간에 자동으로 콘텐츠 생성 및 발행
- 스케줄에 따른 자동 실행
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from .schedule_manager import schedule_manager
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

class AutoPublisher:
    """자동 발행 스케줄러"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.setup_schedule()
    
    def setup_schedule(self):
        """발행 스케줄 설정"""
        # 매일 새벽 3시에 자동 발행
        schedule.every().day.at("03:00").do(self.daily_auto_publish)
        
        # 매주 일요일 밤 11시에 다음 주 스케줄 생성
        schedule.every().sunday.at("23:00").do(self.weekly_schedule_prepare)
        
        print("[AUTO_PUBLISHER] 자동 발행 스케줄 설정 완료")
        print("- 매일 새벽 3시: 자동 콘텐츠 생성 및 발행")
        print("- 매주 일요일 23시: 다음 주 스케줄 생성")
    
    def daily_auto_publish(self):
        """일일 자동 발행 실행"""
        try:
            today = datetime.now().date()
            print(f"\n[AUTO_PUBLISH] {today} 자동 발행 시작")
            
            # 스케줄 매니저에서 오늘 발행할 내용 가져오기
            week_start = today - timedelta(days=today.weekday())
            day_of_week = today.weekday()
            
            schedule_data = schedule_manager.get_weekly_schedule(week_start)
            
            if not schedule_data or day_of_week not in schedule_data['schedule']:
                print(f"[AUTO_PUBLISH] {today} 발행할 스케줄이 없습니다")
                return
            
            day_schedule = schedule_data['schedule'][day_of_week]
            sites = day_schedule.get('sites', {})
            
            if not sites:
                print(f"[AUTO_PUBLISH] {today} 발행할 사이트가 없습니다")
                return
            
            print(f"[AUTO_PUBLISH] 총 {len(sites)}개 사이트 발행 예정")
            
            success_count = 0
            
            # 각 사이트별로 순차 발행
            for site, plan in sites.items():
                if plan['status'] == 'published':
                    print(f"[AUTO_PUBLISH] {site} - 이미 발행 완료")
                    success_count += 1
                    continue
                
                try:
                    print(f"\n[AUTO_PUBLISH] {site} 발행 시작")
                    print(f"- 주제: {plan['topic']}")
                    print(f"- 키워드: {', '.join(plan.get('keywords', []))}")
                    
                    # 상태를 'generating'으로 변경
                    schedule_manager.update_schedule_status(
                        week_start, day_of_week, site, 'generating'
                    )
                    
                    # 실제 콘텐츠 생성 및 발행
                    success = self._execute_site_publishing(site, plan)
                    
                    if success:
                        schedule_manager.update_schedule_status(
                            week_start, day_of_week, site, 'published'
                        )
                        success_count += 1
                        print(f"[AUTO_PUBLISH] {site} 발행 성공 ✅")
                    else:
                        schedule_manager.update_schedule_status(
                            week_start, day_of_week, site, 'failed'
                        )
                        print(f"[AUTO_PUBLISH] {site} 발행 실패 ❌")
                    
                    # 사이트 간 간격 (서버 부하 방지)
                    time.sleep(30)
                    
                except Exception as e:
                    print(f"[AUTO_PUBLISH] {site} 발행 오류: {e}")
                    schedule_manager.update_schedule_status(
                        week_start, day_of_week, site, 'failed'
                    )
            
            print(f"\n[AUTO_PUBLISH] 자동 발행 완료: {success_count}/{len(sites)} 성공")
            
        except Exception as e:
            print(f"[AUTO_PUBLISH] 일일 자동 발행 오류: {e}")
    
    def _execute_site_publishing(self, site: str, plan: dict) -> bool:
        """실제 사이트 발행 실행"""
        try:
            # 여기서 실제 콘텐츠 생성 API 호출
            # 기존 generate_wordpress API와 publish_to_wordpress API 활용
            
            import requests
            import json
            
            # 1. 콘텐츠 생성
            generate_payload = {
                'site': site,
                'topic': plan['topic'],
                'keywords': plan.get('keywords', []),
                'category': plan.get('topic_category', 'programming'),
                'content_length': plan.get('target_length', 'medium')
            }
            
            print(f"[PUBLISH] {site} 콘텐츠 생성 중...")
            generate_response = requests.post(
                'http://localhost:5000/api/generate_wordpress',
                headers={'Content-Type': 'application/json'},
                json=generate_payload,
                timeout=300  # 5분 타임아웃
            )
            
            if generate_response.status_code != 200:
                print(f"[PUBLISH] {site} 콘텐츠 생성 실패: {generate_response.status_code}")
                return False
            
            generate_result = generate_response.json()
            if not generate_result.get('success'):
                print(f"[PUBLISH] {site} 콘텐츠 생성 실패: {generate_result.get('error')}")
                return False
            
            # 2. WordPress 발행
            file_path = generate_result.get('file_path')
            if not file_path:
                print(f"[PUBLISH] {site} 파일 경로 없음")
                return False
            
            print(f"[PUBLISH] {site} WordPress 발행 중...")
            publish_payload = {
                'file_path': file_path,
                'site': site
            }
            
            publish_response = requests.post(
                'http://localhost:5000/api/publish_to_wordpress',
                headers={'Content-Type': 'application/json'},
                json=publish_payload,
                timeout=120  # 2분 타임아웃
            )
            
            if publish_response.status_code != 200:
                print(f"[PUBLISH] {site} WordPress 발행 실패: {publish_response.status_code}")
                return False
            
            publish_result = publish_response.json()
            if not publish_result.get('success'):
                print(f"[PUBLISH] {site} WordPress 발행 실패: {publish_result.get('error')}")
                return False
            
            # URL 업데이트
            published_url = publish_result.get('url')
            if published_url:
                schedule_manager.update_schedule_status(
                    datetime.now().date() - timedelta(days=datetime.now().weekday()),
                    datetime.now().weekday(),
                    site,
                    'published',
                    url=published_url
                )
            
            print(f"[PUBLISH] {site} 발행 완료: {published_url}")
            return True
            
        except Exception as e:
            print(f"[PUBLISH] {site} 발행 실행 오류: {e}")
            return False
    
    def weekly_schedule_prepare(self):
        """다음 주 스케줄 준비"""
        try:
            next_week = datetime.now().date() + timedelta(days=7)
            next_monday = next_week - timedelta(days=next_week.weekday())
            
            print(f"[SCHEDULE_PREP] {next_monday} 주 스케줄 준비")
            
            if not schedule_manager._week_schedule_exists(next_monday):
                schedule_manager.create_weekly_schedule(next_monday)
                print(f"[SCHEDULE_PREP] {next_monday} 주 스케줄 생성 완료")
            else:
                print(f"[SCHEDULE_PREP] {next_monday} 주 스케줄 이미 존재")
                
        except Exception as e:
            print(f"[SCHEDULE_PREP] 주간 스케줄 준비 오류: {e}")
    
    def start(self):
        """스케줄러 시작"""
        if self.running:
            print("[AUTO_PUBLISHER] 이미 실행 중입니다")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("[AUTO_PUBLISHER] 자동 발행 스케줄러 시작됨")
    
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        schedule.clear()
        print("[AUTO_PUBLISHER] 자동 발행 스케줄러 중지됨")
    
    def _run_scheduler(self):
        """스케줄러 실행 루프"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    
    def get_next_run_time(self):
        """다음 실행 시간 조회"""
        jobs = schedule.get_jobs()
        if not jobs:
            return None
        
        next_runs = []
        for job in jobs:
            if job.next_run:
                next_runs.append({
                    'job': str(job.job_func.__name__),
                    'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return next_runs

# 전역 인스턴스
auto_publisher = AutoPublisher()