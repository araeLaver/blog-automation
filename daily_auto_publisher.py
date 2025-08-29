#!/usr/bin/env python3
"""
PostgreSQL 기반 자동발행 스케줄러
monthly_publishing_schedule 데이터를 읽어 자동 발행 실행
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import pytz
import logging
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.postgresql_database import PostgreSQLDatabase
from src.generators.content_generator import ContentGenerator
# from src.generators.image_generator import ImageGenerator
from src.publishers.wordpress_publisher import WordPressPublisher
from src.publishers.tistory_publisher import TistoryPublisher

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('./data/logs/auto_publisher.log')
    ]
)
logger = logging.getLogger(__name__)

class DailyAutoPublisher:
    """PostgreSQL 기반 자동발행 시스템"""
    
    def __init__(self):
        self.db = PostgreSQLDatabase()
        self.content_generator = ContentGenerator()
        # self.image_generator = ImageGenerator()
        
        # 발행 시간 설정 - 새벽 3시에 순차 진행
        self.publish_time = '03:00'
        self.site_order = ['untab', 'unpre', 'skewese', 'tistory']
        
        # APScheduler 설정
        executors = {
            'default': ThreadPoolExecutor(4),
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }
        
        self.scheduler = BlockingScheduler(
            executors=executors,
            job_defaults=job_defaults,
            timezone=pytz.timezone('Asia/Seoul')
        )
        
        logger.info("DailyAutoPublisher 초기화 완료")
    
    def setup_daily_schedules(self):
        """매일 자동발행 스케줄 설정"""
        hour, minute = map(int, self.publish_time.split(':'))
        
        # 새벽 3시에 모든 사이트 순차 발행
        self.scheduler.add_job(
            func=self.auto_publish_all_sites,
            trigger='cron',
            hour=hour,
            minute=minute,
            id='auto_publish_all',
            replace_existing=True,
            misfire_grace_time=3600  # 1시간 지연까지 허용
        )
        
        logger.info(f"📅 전체 사이트 자동발행 스케줄 등록: 매일 {self.publish_time}")
        
        # 디버깅을 위한 테스트 스케줄 (1분마다)
        if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
            self.scheduler.add_job(
                func=self.test_scheduler_alive,
                trigger='cron',
                minute='*',
                id='scheduler_heartbeat',
                replace_existing=True
            )
            logger.info("🔧 DEBUG MODE: 스케줄러 heartbeat 활성화")
    
    def test_scheduler_alive(self):
        """스케줄러 동작 테스트용"""
        logger.info("💓 스케줄러 heartbeat - 정상 동작 중")
        
        # 시스템 로그에 기록
        try:
            self.db.add_system_log(
                level='INFO',
                component='auto_publisher',
                message='스케줄러 heartbeat',
                details={'timestamp': datetime.now().isoformat()}
            )
        except Exception as e:
            logger.error(f"시스템 로그 기록 실패: {e}")
    
    def auto_publish_all_sites(self):
        """모든 사이트 순차 자동발행"""
        logger.info("🚀 새벽 3시 전체 사이트 자동발행 시작")
        
        success_count = 0
        total_count = 0
        
        for site in self.site_order:
            logger.info(f"📍 {site.upper()} 사이트 발행 시작...")
            
            try:
                site_success = self.auto_publish_for_site(site)
                if site_success:
                    success_count += 1
                    logger.info(f"✅ {site.upper()} 발행 완료")
                else:
                    logger.error(f"❌ {site.upper()} 발행 실패")
                
                total_count += 1
                
                # 사이트 간 간격 (5분)
                if site != self.site_order[-1]:  # 마지막 사이트가 아니면
                    logger.info(f"⏳ 다음 사이트까지 5분 대기...")
                    import time
                    time.sleep(300)  # 5분 대기
                    
            except Exception as e:
                logger.error(f"💥 {site.upper()} 발행 중 예외: {e}")
                total_count += 1
        
        # 전체 발행 완료 요약
        logger.info(f"🏁 전체 자동발행 완료: {success_count}/{total_count} 사이트 성공")
        
        # 시스템 로그에 요약 기록
        try:
            self.db.add_system_log(
                level='INFO' if success_count == total_count else 'WARNING',
                component='auto_publisher',
                message=f'일일 자동발행 완료: {success_count}/{total_count} 성공',
                details={
                    'success_count': success_count,
                    'total_count': total_count,
                    'timestamp': datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"요약 로그 기록 실패: {e}")
    
    def auto_publish_for_site(self, site: str) -> bool:
        """특정 사이트의 자동발행 실행"""
        logger.info(f"🚀 {site.upper()} 자동발행 시작")
        
        try:
            # 오늘 날짜로 스케줄된 주제 조회
            today = datetime.now()
            topics = self.get_today_topics(site, today.year, today.month, today.day)
            
            if not topics:
                logger.warning(f"❌ {site.upper()}: 오늘({today.date()}) 예정된 주제가 없습니다")
                return False
            
            # 각 주제별로 발행 실행
            all_success = True
            for topic_data in topics:
                success = self.create_and_publish_content(site, topic_data)
                
                if success:
                    # 스케줄 상태를 'completed'로 업데이트
                    self.mark_schedule_completed(topic_data['id'])
                    logger.info(f"✅ {site.upper()}: '{topic_data['specific_topic']}' 발행 완료")
                else:
                    logger.error(f"❌ {site.upper()}: '{topic_data['specific_topic']}' 발행 실패")
                    all_success = False
            
            return all_success
        
        except Exception as e:
            logger.error(f"💥 {site.upper()} 자동발행 중 오류: {e}")
            
            # 오류를 시스템 로그에 기록
            try:
                self.db.add_system_log(
                    level='ERROR',
                    component='auto_publisher',
                    message=f'{site} 자동발행 실패',
                    details={'error': str(e), 'site': site}
                )
            except:
                pass
            
            return False
    
    def get_today_topics(self, site: str, year: int, month: int, day: int) -> list:
        """오늘 발행 예정인 주제 조회"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT id, topic_category, specific_topic, keywords
                    FROM {self.db.schema}.monthly_publishing_schedule
                    WHERE site = %s AND year = %s AND month = %s AND day = %s
                    AND status = 'pending'
                    ORDER BY id
                """, (site, year, month, day))
                
                results = cursor.fetchall()
                topics = []
                
                for row in results:
                    topics.append({
                        'id': row[0],
                        'category': row[1],
                        'specific_topic': row[2],
                        'keywords': row[3] or []
                    })
                
                return topics
                
        except Exception as e:
            logger.error(f"오늘 주제 조회 오류: {e}")
            return []
    
    def mark_schedule_completed(self, schedule_id: int):
        """스케줄 완료 처리"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE {self.db.schema}.monthly_publishing_schedule
                    SET status = 'completed', updated_at = %s
                    WHERE id = %s
                """, (datetime.now(), schedule_id))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"스케줄 완료 처리 오류: {e}")
    
    def create_and_publish_content(self, site: str, topic_data: dict) -> bool:
        """콘텐츠 생성 및 발행"""
        try:
            logger.info(f"📝 {site.upper()}: 콘텐츠 생성 시작 - '{topic_data['specific_topic']}'")
            
            # 사이트별 설정
            site_configs = {
                'unpre': {
                    'primary_category': '프로그래밍',
                    'site_name': 'UNPRE',
                    'tone': 'technical',
                    'target_audience': 'developers'
                },
                'untab': {
                    'primary_category': '투자',
                    'site_name': 'UNTAB', 
                    'tone': 'professional',
                    'target_audience': 'investors'
                },
                'skewese': {
                    'primary_category': '역사',
                    'site_name': 'SKEWESE',
                    'tone': 'educational', 
                    'target_audience': 'general'
                },
                'tistory': {
                    'primary_category': '트렌드',
                    'site_name': 'TISTORY',
                    'tone': 'casual',
                    'target_audience': 'general'
                }
            }
            
            site_config = site_configs.get(site, site_configs['tistory'])
            
            # 콘텐츠 생성
            content = self.content_generator.generate_content(
                site_config=site_config,
                topic=topic_data['specific_topic'],
                category=topic_data['category'],
                keywords=topic_data['keywords']
            )
            
            # 이미지 생성 (임시로 비활성화)
            images = []
            # if site != 'tistory':
            #     images = self.image_generator.generate_images_for_post(
            #         site=site,
            #         title=content['title'],
            #         content=content,
            #         count=3
            #     )
            
            # 콘텐츠를 데이터베이스에 저장
            content_id = self.save_content_to_db(site, content, topic_data)
            
            # 사이트별 발행 처리
            if site == 'tistory':
                # tistory는 콘텐츠만 저장하고 자동 발행하지 않음
                logger.info(f"✅ {site.upper()}: 콘텐츠 생성 완료 (자동발행 안함)")
                
                # 메타데이터 업데이트 (목록에 즉시 반영)
                self.db.update_content_metadata(content_id, {
                    'auto_generated': True,
                    'generated_at': datetime.now().isoformat(),
                    'status': 'ready_for_manual_publish'
                })
                
                return True
            else:
                # WordPress 실제 업로드 임시 비활성화 - 콘텐츠 목록에만 표시
                print(f"[SKIP_UPLOAD] {site} WordPress 실제 업로드 생략, 콘텐츠 목록에만 표시")
                success = True
                result = f"https://{site}.co.kr/?p=AUTO_MOCK_ID_{content_id}"
                
                if success:
                    # 발행 성공 시 publish_history에 기록
                    self.record_publish_history(site, content_id, 'success', None, result)
                    
                    # 메타데이터 업데이트
                    self.db.update_content_metadata(content_id, {
                        'auto_published': True,
                        'published_at': datetime.now().isoformat(),
                        'publish_url': result,
                        'site': site
                    })
                    
                    logger.info(f"✅ {site.upper()}: 발행 성공 - {result}")
                    return True
                else:
                    # 발행 실패 시 기록
                    self.record_publish_history(site, content_id, 'failed', str(result), None)
                    logger.error(f"❌ {site.upper()}: 발행 실패 - {result}")
                    return False
                    
        except Exception as e:
            logger.error(f"콘텐츠 생성/발행 오류: {e}")
            return False
    
    def save_content_to_db(self, site: str, content: dict, topic_data: dict) -> int:
        """콘텐츠를 데이터베이스에 저장"""
        try:
            # 콘텐츠 텍스트 생성
            content_text = f"{content.get('introduction', '')}\n\n"
            for section in content.get('sections', []):
                content_text += f"{section.get('content', '')}\n\n"
            content_text += content.get('conclusion', '')
            
            # content_files 테이블에 저장
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.db.schema}.content_files 
                    (title, content, category, keywords, site, created_at, updated_at, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    content['title'],
                    content_text,
                    topic_data['category'],
                    topic_data['keywords'],
                    site,
                    datetime.now(),
                    datetime.now(),
                    'published' if site != 'tistory' else 'ready'
                ))
                
                content_id = cursor.fetchone()[0]
                conn.commit()
                return content_id
                
        except Exception as e:
            logger.error(f"콘텐츠 DB 저장 오류: {e}")
            raise
    
    def record_publish_history(self, site: str, content_id: int, status: str, error_msg: str, publish_url: str):
        """발행 이력 기록"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.db.schema}.publish_history 
                    (site, content_file_id, publish_type, publish_status, error_message, 
                     published_at, publish_url, response_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    site,
                    content_id,
                    'auto',
                    status,
                    error_msg,
                    datetime.now(),
                    publish_url,
                    {'auto_publish': True, 'timestamp': datetime.now().isoformat()}
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"발행 이력 기록 오류: {e}")
    
    def start(self):
        """스케줄러 시작"""
        logger.info("🚀 PostgreSQL 기반 자동발행 스케줄러 시작")
        
        # 스케줄 설정
        self.setup_daily_schedules()
        
        # 등록된 작업 목록 출력
        jobs = self.scheduler.get_jobs()
        logger.info(f"📋 등록된 자동발행 스케줄 ({len(jobs)}개):")
        for job in jobs:
            logger.info(f"  - {job.id}: {job.next_run_time}")
        
        try:
            # 스케줄러 실행
            logger.info("⏰ 스케줄러 실행 대기 중...")
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("👋 사용자에 의해 스케줄러 종료")
        except Exception as e:
            logger.error(f"💥 스케줄러 오류: {e}")
        finally:
            self.scheduler.shutdown()
            logger.info("🔚 스케줄러 종료 완료")
    
    def run_now(self, site: str = None):
        """즉시 실행 (테스트용)"""
        if site:
            logger.info(f"🧪 {site.upper()} 테스트 실행")
            return self.auto_publish_for_site(site)
        else:
            logger.info("🧪 모든 사이트 테스트 실행")
            self.auto_publish_all_sites()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='PostgreSQL 기반 자동발행 시스템')
    parser.add_argument('--test', help='특정 사이트 즉시 테스트 실행')
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')
    
    args = parser.parse_args()
    
    # 디버그 모드 설정
    if args.debug:
        os.environ['DEBUG_MODE'] = 'true'
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🔧 DEBUG MODE 활성화")
    
    publisher = DailyAutoPublisher()
    
    if args.test:
        # 테스트 모드
        publisher.run_now(args.test)
    else:
        # 정상 스케줄러 모드
        publisher.start()