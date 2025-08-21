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
        from ..web_dashboard_pg import get_database
        
        today = datetime.now().date()
        start_time = datetime.now()
        
        # 데이터베이스 로그 시작
        db = None
        try:
            db = get_database()
            db.add_system_log(
                level="INFO",
                component="auto_publisher",
                message=f"일일 자동 발행 시작: {today}",
                details={
                    "date": str(today),
                    "start_time": start_time.isoformat(),
                    "day_of_week": today.weekday()
                }
            )
        except Exception as db_error:
            print(f"[AUTO_PUBLISH] 데이터베이스 로그 오류: {db_error}")
        
        try:
            print(f"\n[AUTO_PUBLISH] {today} 자동 발행 시작 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 스케줄 매니저에서 오늘 발행할 내용 가져오기
            week_start = today - timedelta(days=today.weekday())
            day_of_week = today.weekday()
            
            schedule_data = schedule_manager.get_weekly_schedule(week_start)
            
            if not schedule_data or day_of_week not in schedule_data['schedule']:
                message = f"{today} 발행할 스케줄이 없습니다"
                print(f"[AUTO_PUBLISH] {message}")
                
                if db:
                    db.add_system_log(
                        level="WARNING",
                        component="auto_publisher",
                        message=message,
                        details={
                            "date": str(today),
                            "week_start": str(week_start),
                            "day_of_week": day_of_week,
                            "schedule_exists": schedule_data is not None
                        }
                    )
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
                site_start_time = datetime.now()
                
                if plan['status'] == 'published':
                    print(f"[AUTO_PUBLISH] {site} - 이미 발행 완료")
                    success_count += 1
                    continue
                
                try:
                    print(f"\n[AUTO_PUBLISH] {site} 발행 시작 - {site_start_time.strftime('%H:%M:%S')}")
                    print(f"- 주제: {plan['topic']}")
                    print(f"- 키워드: {', '.join(plan.get('keywords', []))}")
                    
                    # 사이트별 시작 로그
                    if db:
                        db.add_system_log(
                            level="INFO",
                            component="auto_publisher",
                            message=f"{site} 자동 발행 시작",
                            details={
                                "site": site,
                                "topic": plan['topic'],
                                "category": plan.get('topic_category', ''),
                                "keywords": plan.get('keywords', []),
                                "start_time": site_start_time.isoformat()
                            },
                            site=site
                        )
                    
                    # 상태를 'generating'으로 변경
                    schedule_manager.update_schedule_status(
                        week_start, day_of_week, site, 'generating'
                    )
                    
                    # 실제 콘텐츠 생성 및 발행
                    success = self._execute_site_publishing(site, plan)
                    
                    site_end_time = datetime.now()
                    duration = (site_end_time - site_start_time).total_seconds()
                    
                    if success:
                        schedule_manager.update_schedule_status(
                            week_start, day_of_week, site, 'published'
                        )
                        success_count += 1
                        print(f"[AUTO_PUBLISH] {site} 발행 성공 ✅ (소요시간: {duration:.1f}초)")
                        
                        if db:
                            db.add_system_log(
                                level="INFO",
                                component="auto_publisher",
                                message=f"{site} 자동 발행 성공",
                                details={
                                    "site": site,
                                    "topic": plan['topic'],
                                    "duration_seconds": duration,
                                    "end_time": site_end_time.isoformat()
                                },
                                site=site,
                                duration_ms=int(duration * 1000)
                            )
                    else:
                        schedule_manager.update_schedule_status(
                            week_start, day_of_week, site, 'failed'
                        )
                        print(f"[AUTO_PUBLISH] {site} 발행 실패 ❌ (소요시간: {duration:.1f}초)")
                        
                        if db:
                            db.add_system_log(
                                level="ERROR",
                                component="auto_publisher",
                                message=f"{site} 자동 발행 실패",
                                details={
                                    "site": site,
                                    "topic": plan['topic'],
                                    "duration_seconds": duration,
                                    "end_time": site_end_time.isoformat(),
                                    "error": "콘텐츠 생성 또는 발행 실패"
                                },
                                site=site,
                                duration_ms=int(duration * 1000)
                            )
                    
                    # 사이트 간 간격 (서버 부하 방지)
                    time.sleep(30)
                    
                except Exception as e:
                    site_end_time = datetime.now()
                    duration = (site_end_time - site_start_time).total_seconds()
                    error_msg = str(e)
                    
                    print(f"[AUTO_PUBLISH] {site} 발행 오류: {error_msg}")
                    schedule_manager.update_schedule_status(
                        week_start, day_of_week, site, 'failed'
                    )
                    
                    if db:
                        db.add_system_log(
                            level="ERROR",
                            component="auto_publisher",
                            message=f"{site} 자동 발행 오류",
                            details={
                                "site": site,
                                "topic": plan.get('topic', ''),
                                "error": error_msg,
                                "duration_seconds": duration,
                                "end_time": site_end_time.isoformat(),
                                "traceback": str(e)
                            },
                            site=site,
                            duration_ms=int(duration * 1000)
                        )
            
            # 전체 완료 시간 및 결과 로그
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            print(f"\n[AUTO_PUBLISH] 자동 발행 완료: {success_count}/{len(sites)} 성공")
            print(f"[AUTO_PUBLISH] 총 소요시간: {total_duration:.1f}초")
            
            if db:
                db.add_system_log(
                    level="INFO",
                    component="auto_publisher",
                    message=f"일일 자동 발행 완료: {success_count}/{len(sites)} 성공",
                    details={
                        "date": str(today),
                        "total_sites": len(sites),
                        "success_count": success_count,
                        "failed_count": len(sites) - success_count,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "total_duration_seconds": total_duration,
                        "sites_processed": list(sites.keys())
                    },
                    duration_ms=int(total_duration * 1000)
                )
            
        except Exception as e:
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            error_msg = str(e)
            
            print(f"[AUTO_PUBLISH] 일일 자동 발행 오류: {error_msg}")
            
            if db:
                import traceback
                db.add_system_log(
                    level="CRITICAL",
                    component="auto_publisher",
                    message="일일 자동 발행 중 치명적 오류 발생",
                    details={
                        "date": str(today),
                        "error": error_msg,
                        "traceback": traceback.format_exc(),
                        "start_time": start_time.isoformat(),
                        "error_time": end_time.isoformat(),
                        "duration_seconds": total_duration
                    },
                    duration_ms=int(total_duration * 1000)
                )
    
    def _execute_site_publishing(self, site: str, plan: dict) -> bool:
        """실제 사이트 발행 실행"""
        from ..web_dashboard_pg import get_database
        
        db = None
        try:
            db = get_database()
        except:
            pass
            
        content_start_time = datetime.now()
        
        try:
            # 직접 콘텐츠 생성 함수 호출 (더 안정적)
            if site in ['unpre', 'untab', 'skewese']:
                # WordPress 사이트 콘텐츠 생성 및 발행
                success = self._generate_and_publish_wordpress(site, plan, db)
                
            elif site == 'tistory':
                # Tistory 콘텐츠 생성
                success = self._generate_tistory_content(site, plan, db)
            else:
                print(f"[PUBLISH] {site} 지원하지 않는 사이트")
                return False
                
            content_end_time = datetime.now()
            duration = (content_end_time - content_start_time).total_seconds()
            
            if success:
                print(f"[PUBLISH] {site} 전체 발행 성공 (소요: {duration:.1f}초)")
            else:
                print(f"[PUBLISH] {site} 전체 발행 실패 (소요: {duration:.1f}초)")
                
            return success
            
        except Exception as e:
            content_end_time = datetime.now()
            duration = (content_end_time - content_start_time).total_seconds()
            
            print(f"[PUBLISH] {site} 발행 중 오류: {str(e)} (소요: {duration:.1f}초)")
            
            if db:
                import traceback
                db.add_system_log(
                    level="ERROR",
                    component="auto_publisher",
                    message=f"{site} 발행 실행 중 예외 발생",
                    details={
                        "site": site,
                        "topic": plan.get('topic', ''),
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                        "duration_seconds": duration
                    },
                    site=site,
                    duration_ms=int(duration * 1000)
                )
            return False

    def _generate_and_publish_wordpress(self, site: str, plan: dict, db) -> bool:
        """WordPress 콘텐츠 생성 및 실제 사이트 발행"""
        try:
            from ..generators.content_generator import ContentGenerator
            from ..generators.wordpress_content_exporter import WordPressContentExporter
            from ..publishers.wordpress_publisher import WordPressPublisher
            
            # 1. 콘텐츠 생성
            print(f"[WP_PUBLISH] {site} AI 콘텐츠 생성 시작")
            
            generator = ContentGenerator()
            exporter = WordPressContentExporter()
            
            site_config = {
                'name': site,
                'categories': [plan.get('topic_category', 'general')],
                'content_style': '전문적이고 신뢰할 수 있는 톤',
                'target_audience': '전문가 및 일반인',
                'keywords_focus': plan.get('keywords', [])
            }
            
            content = generator.generate_content(
                site_config=site_config,
                topic=plan['topic'],
                category=plan.get('topic_category', 'general'),
                content_length=plan.get('target_length', 'medium')
            )
            
            print(f"[WP_PUBLISH] {site} 콘텐츠 생성 완료: {content.get('title', 'Unknown')}")
            
            # 2. 파일 저장
            filepath = exporter.export_content(site, content)
            print(f"[WP_PUBLISH] {site} 파일 저장 완료: {filepath}")
            
            # 3. 데이터베이스에 파일 정보 저장
            if db:
                from pathlib import Path
                file_path_obj = Path(filepath)
                file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
                content_text = content.get('introduction', '') + ' '.join([s.get('content', '') for s in content.get('sections', [])])
                word_count = len(content_text.replace(' ', ''))
                
                file_id = db.add_content_file(
                    site=site,
                    title=content['title'],
                    file_path=filepath,
                    file_type="wordpress",
                    metadata={
                        'tags': content.get('tags', []),
                        'categories': [content.get('category', plan.get('topic_category', 'general'))],
                        'word_count': word_count,
                        'file_size': file_size,
                        'auto_generated': True
                    }
                )
                print(f"[WP_PUBLISH] {site} 데이터베이스 저장 완료 (ID: {file_id})")
                
            # 4. WordPress 사이트에 실제 발행
            print(f"[WP_PUBLISH] {site} WordPress 사이트 발행 시작")
            
            publisher = WordPressPublisher(site)
            
            # 콘텐츠 데이터 준비
            content_data = {
                'title': content['title'],
                'introduction': content.get('introduction', ''),
                'sections': content.get('sections', []),
                'conclusion': content.get('conclusion', ''),
                'meta_description': content.get('meta_description', ''),
                'categories': [content.get('category', plan.get('topic_category', 'general'))],
                'tags': content.get('tags', [])
            }
            
            # WordPress에 실제 발행
            wp_success, wp_result = publisher.publish_post(content_data, images=[], draft=False)
            
            if wp_success:
                print(f"[WP_PUBLISH] {site} WordPress 발행 성공: {wp_result}")
                
                # 파일 상태 업데이트
                if db and 'file_id' in locals():
                    db.update_content_file_status(
                        file_id=file_id,
                        status='published',
                        published_at=datetime.now().isoformat()
                    )
                    
                    db.add_system_log(
                        level="INFO",
                        component="auto_publisher",
                        message=f"{site} WordPress 발행 성공",
                        details={
                            "site": site,
                            "title": content['title'],
                            "wordpress_url": wp_result,
                            "file_id": file_id
                        },
                        site=site
                    )
                
                return True
            else:
                print(f"[WP_PUBLISH] {site} WordPress 발행 실패: {wp_result}")
                
                if db:
                    db.add_system_log(
                        level="ERROR",
                        component="auto_publisher",
                        message=f"{site} WordPress 발행 실패",
                        details={
                            "site": site,
                            "title": content['title'],
                            "error": str(wp_result)
                        },
                        site=site
                    )
                return False
                
        except Exception as e:
            print(f"[WP_PUBLISH] {site} WordPress 발행 중 오류: {str(e)}")
            
            if db:
                import traceback
                db.add_system_log(
                    level="ERROR",
                    component="auto_publisher",
                    message=f"{site} WordPress 발행 중 예외",
                    details={
                        "site": site,
                        "topic": plan.get('topic', ''),
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    },
                    site=site
                )
            return False
    
    def _generate_tistory_content(self, site: str, plan: dict, db) -> bool:
        """Tistory 콘텐츠 생성"""
        try:
            from ..generators.content_generator import ContentGenerator
            from ..generators.tistory_content_exporter import TistoryContentExporter
            
            print(f"[TISTORY_PUBLISH] {site} AI 콘텐츠 생성 시작")
            
            generator = ContentGenerator()
            exporter = TistoryContentExporter()
            
            site_config = {
                'name': 'Tistory 블로그',
                'categories': [plan.get('topic_category', 'general')],
                'content_style': '친근하고 실용적인 톤',
                'target_audience': '일반인',
                'keywords_focus': plan.get('keywords', [])
            }
            
            content = generator.generate_content(
                site_config=site_config,
                topic=plan['topic'],
                category=plan.get('topic_category', 'general'),
                content_length=plan.get('target_length', 'medium')
            )
            
            print(f"[TISTORY_PUBLISH] {site} 콘텐츠 생성 완료: {content.get('title', 'Unknown')}")
            
            # 파일 저장
            filepath = exporter.export_content(content)
            print(f"[TISTORY_PUBLISH] {site} 파일 저장 완료: {filepath}")
            
            # 데이터베이스에 파일 정보 저장
            if db:
                content_text = content.get('introduction', '') + ' '.join([s.get('content', '') for s in content.get('sections', [])])
                word_count = len(content_text.replace(' ', ''))
                
                file_id = db.add_content_file(
                    site='tistory',
                    title=content['title'],
                    file_path=filepath,
                    file_type="tistory",
                    metadata={
                        'tags': content.get('tags', []),
                        'categories': [content.get('category', plan.get('topic_category', 'general'))],
                        'word_count': word_count,
                        'auto_generated': True
                    }
                )
                print(f"[TISTORY_PUBLISH] {site} 데이터베이스 저장 완료 (ID: {file_id})")
                
                db.add_system_log(
                    level="INFO",
                    component="auto_publisher",
                    message=f"{site} Tistory 콘텐츠 생성 성공",
                    details={
                        "site": site,
                        "title": content['title'],
                        "file_id": file_id,
                        "filepath": filepath
                    },
                    site=site
                )
                
            return True
            
        except Exception as e:
            print(f"[TISTORY_PUBLISH] {site} Tistory 콘텐츠 생성 중 오류: {str(e)}")
            
            if db:
                import traceback
                db.add_system_log(
                    level="ERROR",
                    component="auto_publisher",
                    message=f"{site} Tistory 콘텐츠 생성 중 예외",
                    details={
                        "site": site,
                        "topic": plan.get('topic', ''),
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    },
                    site=site
                )
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