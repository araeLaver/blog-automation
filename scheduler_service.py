#!/usr/bin/env python3
"""
Koyeb 서버용 스케줄러 서비스
- APScheduler를 사용해 새벽 3시 자동발행
- 웹 서버와 함께 백그라운드에서 실행
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging
import threading
import time
from dotenv import load_dotenv

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.postgresql_database import PostgreSQLDatabase
from src.utils.monthly_schedule_manager import MonthlyScheduleManager
from src.generators.content_generator import ContentGenerator
from src.publishers.wordpress_publisher import WordPressPublisher
from src.publishers.tistory_publisher import TistoryPublisher

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('./data/logs/scheduler.log')
    ]
)
logger = logging.getLogger(__name__)

class BlogAutoPublisher:
    """백그라운드 자동발행 서비스"""
    
    def __init__(self):
        self.db = PostgreSQLDatabase()
        self.schedule_manager = MonthlyScheduleManager()
        self.content_generator = ContentGenerator()
        self.scheduler = BackgroundScheduler(timezone=pytz.UTC)
        
        # 발행기 초기화
        self.publishers = {
            'unpre': WordPressPublisher('unpre'),
            'untab': WordPressPublisher('untab'),
            'skewese': WordPressPublisher('skewese'),
            'tistory': TistoryPublisher()
        }
        
        self.sites = ['unpre', 'untab', 'skewese', 'tistory']
        
    def auto_publish_all_sites(self):
        """모든 사이트 자동발행 실행"""
        logger.info("🚀 전체 사이트 자동발행 시작")
        
        success_count = 0
        total_posts = 0
        
        for site in self.sites:
            try:
                logger.info(f"📝 {site.upper()} 사이트 발행 시작")
                
                # 오늘의 듀얼 주제 가져오기
                primary, secondary = self.schedule_manager.get_today_dual_topics(site)
                
                if not primary:
                    logger.warning(f"❌ {site}: 오늘 발행할 주제가 없습니다")
                    continue
                
                # 각 주제별로 콘텐츠 생성 및 발행
                topics = [primary]
                if secondary:
                    topics.append(secondary)
                
                for topic_data in topics:
                    try:
                        total_posts += 1
                        
                        topic = topic_data['topic']
                        category = topic_data['category']
                        keywords = topic_data.get('keywords', [])
                        
                        logger.info(f"  📖 주제: {topic} ({category})")
                        
                        # 콘텐츠 생성
                        content_data = self.content_generator.generate_blog_content(
                            topic=topic,
                            category=category,
                            target_audience='일반 독자',
                            keywords=keywords,
                            content_length='medium'
                        )
                        
                        if not content_data:
                            logger.error(f"  ❌ 콘텐츠 생성 실패: {topic}")
                            continue
                        
                        # 발행 실행
                        publisher = self.publishers[site]
                        result = publisher.publish_post(
                            title=content_data['title'],
                            content=content_data['content'],
                            category=category,
                            tags=keywords[:5],  # 최대 5개
                            featured_image_url=None
                        )
                        
                        if result.get('success'):
                            success_count += 1
                            logger.info(f"  ✅ 발행 성공: {topic}")
                            
                            # DB에 발행 기록 저장
                            self.db.save_published_post(
                                site=site,
                                title=content_data['title'],
                                content=content_data['content'],
                                category=category,
                                post_url=result.get('url', ''),
                                post_id=result.get('post_id', ''),
                                status='published'
                            )
                        else:
                            logger.error(f"  ❌ 발행 실패: {topic} - {result.get('error')}")
                        
                        # 발행 간격 (3초)
                        time.sleep(3)
                        
                    except Exception as e:
                        logger.error(f"  ❌ 포스트 처리 오류: {topic} - {e}")
                        continue
                
                logger.info(f"✅ {site.upper()} 사이트 발행 완료")
                
            except Exception as e:
                logger.error(f"❌ {site.upper()} 사이트 발행 오류: {e}")
                continue
        
        logger.info(f"🎉 전체 자동발행 완료: {success_count}/{total_posts} 포스트 성공")
        return success_count, total_posts
    
    def start_scheduler(self):
        """스케줄러 시작"""
        try:
            # UTC 기준 새벽 3시 (한국시간 12시) → 실제 한국시간 새벽 3시는 UTC 18시
            # 한국시간 새벽 3시 = UTC 18시 (전날)
            self.scheduler.add_job(
                func=self.auto_publish_all_sites,
                trigger=CronTrigger(hour=18, minute=0, timezone=pytz.UTC),  # UTC 18:00 = KST 03:00
                id='daily_auto_publish',
                name='전체 사이트 자동발행',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("📅 자동발행 스케줄러 시작됨: 매일 새벽 3시 (KST)")
            logger.info("📋 등록된 작업:")
            for job in self.scheduler.get_jobs():
                logger.info(f"  - {job.id}: {job.next_run_time}")
                
        except Exception as e:
            logger.error(f"❌ 스케줄러 시작 실패: {e}")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⏹️ 자동발행 스케줄러 중지됨")

# 글로벌 인스턴스
auto_publisher = None

def init_scheduler():
    """스케줄러 초기화"""
    global auto_publisher
    
    try:
        if auto_publisher is None:
            auto_publisher = BlogAutoPublisher()
            auto_publisher.start_scheduler()
            logger.info("✅ 백그라운드 자동발행 서비스 초기화 완료")
        return auto_publisher
    except Exception as e:
        logger.error(f"❌ 스케줄러 초기화 실패: {e}")
        return None

def get_scheduler_status():
    """스케줄러 상태 조회"""
    global auto_publisher
    
    if not auto_publisher or not auto_publisher.scheduler.running:
        return {
            'running': False,
            'jobs': [],
            'next_run': None
        }
    
    jobs = []
    next_run = None
    
    for job in auto_publisher.scheduler.get_jobs():
        job_info = {
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None
        }
        jobs.append(job_info)
        
        if not next_run or (job.next_run_time and job.next_run_time < next_run):
            next_run = job.next_run_time
    
    return {
        'running': True,
        'jobs': jobs,
        'next_run': next_run.isoformat() if next_run else None
    }

if __name__ == '__main__':
    # 직접 실행 시 스케줄러 시작
    publisher = init_scheduler()
    
    if publisher:
        try:
            logger.info("🔄 스케줄러 실행 중... (Ctrl+C로 종료)")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("⏹️ 사용자 요청으로 스케줄러 종료")
            publisher.stop_scheduler()
        except Exception as e:
            logger.error(f"❌ 스케줄러 실행 오류: {e}")
            if publisher:
                publisher.stop_scheduler()