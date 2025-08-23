"""
자동 스케줄러 - 시간 기반 콘텐츠 발행
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import pytz
from dotenv import load_dotenv

from config.sites_config import SITE_CONFIGS, PUBLISHING_SCHEDULE
from src.generators.content_generator import ContentGenerator
from src.generators.image_generator import ImageGenerator
from src.publishers.wordpress_publisher import WordPressPublisher
from src.publishers.tistory_publisher import TistoryPublisher
from src.utils.database import ContentDatabase
from src.utils.schedule_manager import ScheduleManager
from src.utils.logger import blog_logger, timing

load_dotenv()


class BlogAutomationScheduler:
    def __init__(self):
        """스케줄러 초기화"""
        self.content_generator = ContentGenerator()
        self.image_generator = ImageGenerator()
        self.database = ContentDatabase()
        self.schedule_manager = ScheduleManager()
        
        # 발행자들 (Tistory API 종료로 WordPress만 사용)
        self.publishers = {
            "unpre": WordPressPublisher("unpre"),
            "untab": WordPressPublisher("untab"), 
            "skewese": WordPressPublisher("skewese")
        }
        
        # APScheduler 설정
        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///data/jobs.sqlite')
        }
        executors = {
            'default': ThreadPoolExecutor(20),
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }
        
        self.scheduler = BlockingScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=pytz.timezone('Asia/Seoul')
        )
        
        # 실패한 작업 재시도 설정
        self.max_retries = 3
        self.retry_delay = 300  # 5분
        
        blog_logger.info("Blog Automation Scheduler initialized")
    
    def setup_schedules(self):
        """일정 설정"""
        for site_key, schedule_config in PUBLISHING_SCHEDULE.items():
            publish_time = schedule_config["time"]
            days = schedule_config["days"]
            
            # 요일 변환
            day_mapping = {
                "mon": 0, "tue": 1, "wed": 2, "thu": 3, 
                "fri": 4, "sat": 5, "sun": 6
            }
            
            weekdays = [day_mapping[day] for day in days if day in day_mapping]
            
            hour, minute = map(int, publish_time.split(":"))
            
            # 각 요일에 대해 작업 스케줄링
            for weekday in weekdays:
                self.scheduler.add_job(
                    func=self.create_and_publish_post,
                    trigger='cron',
                    day_of_week=weekday,
                    hour=hour,
                    minute=minute,
                    args=[site_key],
                    id=f"{site_key}_{weekday}_{hour}_{minute}",
                    replace_existing=True,
                    misfire_grace_time=3600  # 1시간 지연까지 허용
                )
        
        # 일일 리포트 생성 (매일 23:50)
        self.scheduler.add_job(
            func=self.generate_daily_report,
            trigger='cron',
            hour=23,
            minute=50,
            id='daily_report',
            replace_existing=True
        )
        
        # 주간 통계 정리 (매주 일요일 자정)
        self.scheduler.add_job(
            func=self.weekly_maintenance,
            trigger='cron',
            day_of_week=6,  # 일요일
            hour=0,
            minute=0,
            id='weekly_maintenance',
            replace_existing=True
        )
        
        blog_logger.info(f"Scheduled {len(self.scheduler.get_jobs())} jobs")
    
    @timing
    def create_and_publish_post(self, site_key: str, retry_count: int = 0):
        """콘텐츠 생성 및 발행"""
        try:
            blog_logger.info(f"Starting content creation for {site_key}")
            
            # 1. 사이트 설정 가져오기
            site_config = SITE_CONFIGS[site_key]
            
            # 2. 오늘의 계획된 주제 가져오기 (정확한 날짜 매칭)
            scheduled_topic = self.schedule_manager.get_today_scheduled_topic(site_key)
            if scheduled_topic:
                topic = scheduled_topic["topic"]
                category = scheduled_topic["category"]
                blog_logger.info(f"Using scheduled topic for {site_key}: {topic}")
            else:
                # 3. 계획된 주제가 없으면 미사용 주제 가져오기 (fallback)
                blog_logger.warning(f"No scheduled topic for {site_key} today, using fallback")
                scheduled_topic = None  # fallback이므로 None으로 설정
                topic_data = self.database.get_unused_topic(site_key)
                if not topic_data:
                    blog_logger.warning(f"No unused topics for {site_key}")
                    return False
                
                topic = topic_data["topic"]
                category = topic_data["category"] or site_config["categories"][0]
                blog_logger.info(f"Using fallback topic for {site_key}: {topic}")
            
            # 3. 중복 체크
            if self.database.check_duplicate_title(site_key, topic):
                blog_logger.warning(f"Duplicate topic detected: {topic}")
                return False
            
            # 4. 기존 포스트 조회 (중복 방지용)
            recent_posts = self.database.get_recent_posts(site_key, 10)
            existing_titles = [post["title"] for post in recent_posts]
            
            # 5. 콘텐츠 생성
            content = self.content_generator.generate_content(
                site_config=site_config,
                topic=topic,
                category=category,
                existing_posts=existing_titles
            )
            
            # 6. 이미지 생성
            images = self.image_generator.generate_images_for_post(
                site=site_key,
                title=content["title"],
                content=content,
                count=3
            )
            
            # 7. 발행
            publisher = self.publishers[site_key]
            success, result = publisher.publish_post(content, images)
            
            if success:
                # 8. 데이터베이스에 기록
                content_id = self.database.add_content(
                    site=site_key,
                    title=content["title"],
                    category=category,
                    keywords=content.get("keywords", []),
                    content=self._content_to_text(content),
                    url=result
                )
                
                blog_logger.success(
                    f"[{site_key.upper()}] Post published successfully: {content['title'][:50]}..."
                )
                
                # 계획된 주제를 사용됨으로 표시
                if scheduled_topic:
                    self.schedule_manager.mark_topic_as_used(site_key, topic)
                
                blog_logger.log_performance(
                    site=site_key,
                    action="publish_post",
                    duration=0,
                    success=True,
                    metadata={
                        "title": content["title"],
                        "url": result,
                        "content_id": content_id
                    }
                )
                return True
            else:
                raise Exception(f"Publishing failed: {result}")
                
        except Exception as e:
            blog_logger.error(
                f"Failed to create/publish post for {site_key}", 
                error=e
            )
            
            # 재시도 로직
            if retry_count < self.max_retries:
                blog_logger.info(f"Retrying in {self.retry_delay} seconds (attempt {retry_count + 1})")
                time.sleep(self.retry_delay)
                return self.create_and_publish_post(site_key, retry_count + 1)
            
            return False
    
    def _content_to_text(self, content: Dict) -> str:
        """콘텐츠 딕셔너리를 텍스트로 변환"""
        text_parts = [content.get("introduction", "")]
        
        for section in content.get("sections", []):
            text_parts.append(section.get("content", ""))
        
        text_parts.append(content.get("conclusion", ""))
        
        return "\n\n".join(part for part in text_parts if part)
    
    @timing
    def generate_daily_report(self):
        """일일 리포트 생성"""
        try:
            blog_logger.info("Generating daily report")
            
            report = blog_logger.create_daily_report()
            
            # 리포트 요약 로그
            blog_logger.info(
                f"Daily Report - Total: {report['total_posts']}, "
                f"Success: {report['successful_posts']}, "
                f"Failed: {report['failed_posts']}"
            )
            
            # 사이트별 상세 로그
            for site, stats in report["sites"].items():
                blog_logger.info(
                    f"[{site.upper()}] Posts: {stats['posts']}, "
                    f"Success: {stats['success']}, "
                    f"Errors: {stats['errors']}"
                )
            
            return report
            
        except Exception as e:
            blog_logger.error("Failed to generate daily report", error=e)
            return None
    
    @timing
    def weekly_maintenance(self):
        """주간 유지보수 작업"""
        try:
            blog_logger.info("Starting weekly maintenance")
            
            # 1. 오래된 로그 정리
            blog_logger.cleanup_old_logs(days=30)
            
            # 2. 데이터베이스 최적화 (실제 구현시 VACUUM 등)
            blog_logger.info("Database maintenance completed")
            
            # 3. 성과가 좋은 주제 분석 및 새 주제 생성
            self._analyze_and_generate_topics()
            
            # 4. 시스템 통계 로그
            stats = blog_logger.get_stats()
            blog_logger.info(f"System stats: {stats}")
            
        except Exception as e:
            blog_logger.error("Weekly maintenance failed", error=e)
    
    def _analyze_and_generate_topics(self):
        """성과 분석 및 새 주제 생성"""
        for site_key in SITE_CONFIGS.keys():
            try:
                # 성과 좋은 주제 분석
                best_topics = self.database.get_best_performing_topics(site_key, 5)
                
                if best_topics:
                    blog_logger.info(f"[{site_key.upper()}] Best performing topics:")
                    for topic in best_topics:
                        blog_logger.info(f"  - {topic['category']}: {topic['avg_views']:.0f} views, ${topic['avg_revenue']:.2f}")
                
                # 새 주제 생성 (실제로는 AI로 생성)
                # 현재는 기존 설정에서 가져옴
                site_config = SITE_CONFIGS[site_key]
                new_topics = []
                
                for topic in site_config["topics"][:5]:  # 상위 5개만
                    new_topics.append({
                        "topic": topic,
                        "category": site_config["categories"][0],
                        "priority": 5
                    })
                
                if new_topics:
                    self.database.add_topics_bulk(site_key, new_topics)
                    blog_logger.info(f"Added {len(new_topics)} new topics for {site_key}")
                
            except Exception as e:
                blog_logger.error(f"Topic analysis failed for {site_key}", error=e)
    
    def test_connection(self) -> Dict[str, bool]:
        """모든 발행자 연결 테스트"""
        results = {}
        
        for site_key, publisher in self.publishers.items():
            try:
                results[site_key] = publisher.test_connection()
                if results[site_key]:
                    blog_logger.success(f"[{site_key.upper()}] Connection OK")
                else:
                    blog_logger.error(f"[{site_key.upper()}] Connection failed")
            except Exception as e:
                results[site_key] = False
                blog_logger.error(f"[{site_key.upper()}] Connection error", error=e)
        
        return results
    
    def run_once(self, site_key: str = None):
        """즉시 실행 (테스트용)"""
        if site_key:
            return self.create_and_publish_post(site_key)
        else:
            results = {}
            for site in SITE_CONFIGS.keys():
                results[site] = self.create_and_publish_post(site)
            return results
    
    def start(self):
        """스케줄러 시작"""
        blog_logger.info("Starting Blog Automation Scheduler")
        
        # 연결 테스트
        connection_results = self.test_connection()
        failed_connections = [k for k, v in connection_results.items() if not v]
        
        if failed_connections:
            blog_logger.warning(f"Some connections failed: {failed_connections}")
        
        # 스케줄 설정
        self.setup_schedules()
        
        # 스케줄 정보 출력
        jobs = self.scheduler.get_jobs()
        blog_logger.info(f"Scheduled {len(jobs)} jobs:")
        for job in jobs:
            blog_logger.info(f"  - {job.id}: {job.next_run_time}")
        
        try:
            # 스케줄러 실행
            self.scheduler.start()
        except KeyboardInterrupt:
            blog_logger.info("Scheduler stopped by user")
        except Exception as e:
            blog_logger.error("Scheduler error", error=e)
        finally:
            self.scheduler.shutdown()
            blog_logger.info("Scheduler shutdown complete")
    
    def stop(self):
        """스케줄러 중지"""
        blog_logger.info("Stopping scheduler...")
        self.scheduler.shutdown()


if __name__ == "__main__":
    # CLI 실행
    import sys
    
    scheduler = BlogAutomationScheduler()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # 연결 테스트
            results = scheduler.test_connection()
            print(f"Connection test results: {results}")
        
        elif sys.argv[1] == "run":
            # 즉시 실행
            site = sys.argv[2] if len(sys.argv) > 2 else None
            results = scheduler.run_once(site)
            print(f"Execution results: {results}")
        
        elif sys.argv[1] == "schedule":
            # 스케줄러 시작
            scheduler.start()
    
    else:
        print("Usage: python scheduler.py [test|run|schedule] [site_key]")
        print("  test: Test all connections")
        print("  run [site]: Run once for site (or all sites)")
        print("  schedule: Start scheduler")