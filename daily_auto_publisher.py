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
        logging.FileHandler('./data/logs/auto_publisher.log', encoding='utf-8')
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
        
        logger.info(f"[SCHEDULE] 전체 사이트 자동발행 스케줄 등록: 매일 {self.publish_time}")
        
        # 디버깅을 위한 테스트 스케줄 (1분마다)
        if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
            self.scheduler.add_job(
                func=self.test_scheduler_alive,
                trigger='cron',
                minute='*',
                id='scheduler_heartbeat',
                replace_existing=True
            )
            logger.info("DEBUG MODE: 스케줄러 heartbeat 활성화")
    
    def test_scheduler_alive(self):
        """스케줄러 동작 테스트용"""
        logger.info("[HEARTBEAT] 스케줄러 heartbeat - 정상 동작 중")
        
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
        logger.info("[AUTO_PUBLISH] 새벽 3시 전체 사이트 자동발행 시작")
        
        success_count = 0
        total_count = 0
        
        for site in self.site_order:
            logger.info(f"[PUBLISH] {site.upper()} 사이트 발행 시작...")
            
            try:
                site_success = self.auto_publish_for_site(site)
                if site_success:
                    success_count += 1
                    logger.info(f"[SUCCESS] {site.upper()} 발행 완료")
                else:
                    logger.error(f"[FAILED] {site.upper()} 발행 실패")
                
                total_count += 1
                
                # 사이트 간 간격 (5분)
                if site != self.site_order[-1]:  # 마지막 사이트가 아니면
                    logger.info(f"[WAIT] 다음 사이트까지 5분 대기...")
                    import time
                    time.sleep(300)  # 5분 대기
                    
            except Exception as e:
                logger.error(f"[EXCEPTION] {site.upper()} 발행 중 예외: {e}")
                total_count += 1
        
        # 전체 발행 완료 요약
        logger.info(f"[COMPLETE] 전체 자동발행 완료: {success_count}/{total_count} 사이트 성공")
        
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
        logger.info(f"[AUTO_PUBLISH] {site.upper()} 자동발행 시작")

        try:
            # 한국 시간 기준 오늘 날짜로 스코줄된 주제 조회
            import pytz
            kst = pytz.timezone('Asia/Seoul')
            today = datetime.now(kst)
            topics = self.get_today_topics(site, today.year, today.month, today.day)

            if not topics:
                logger.warning(f"[NO_TOPIC] {site.upper()}: 오늘({today.date()}) 예정된 주제가 없습니다")
                # 주간계획이 없으면 자동 생성 시도
                self._check_and_create_weekly_plan(today)
                # 다시 조회
                topics = self.get_today_topics(site, today.year, today.month, today.day)
                if not topics:
                    logger.warning(f"[NO_TOPIC] {site.upper()}: 주간계획 생성 후에도 주제가 없음")
                    return False
            
            # 각 주제별로 발행 실행
            all_success = True
            for topic_data in topics:
                success = self.create_and_publish_content(site, topic_data)
                
                if success:
                    # 스케줄 상태를 'completed'로 업데이트 (월간계획인 경우에만)
                    if isinstance(topic_data.get('id'), int):  # 정수 ID면 월간계획
                        self.mark_schedule_completed(topic_data['id'])
                    logger.info(f"[SUCCESS] {site.upper()}: '{topic_data['specific_topic']}' 발행 완료")
                else:
                    logger.error(f"[FAILED] {site.upper()}: '{topic_data['specific_topic']}' 발행 실패")
                    all_success = False
            
            return all_success
        
        except Exception as e:
            logger.error(f"[ERROR] {site.upper()} 자동발행 중 오류: {e}")
            
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
        """오늘 발행 예정인 주제 조회 - 주간계획표 우선 사용"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                # 한국 시간 기준으로 조회
                import pytz
                import json
                from datetime import datetime, timedelta

                kst = pytz.timezone('Asia/Seoul')
                today = datetime(year, month, day)
                today_str = today.strftime('%Y-%m-%d')

                # 먼저 주간계획(weekly_plans)에서 조회
                weekday = today.weekday()
                week_start = today - timedelta(days=weekday)
                week_start_str = week_start.strftime('%Y-%m-%d')

                cursor.execute(f"""
                    SELECT plan_data
                    FROM {self.db.schema}.weekly_plans
                    WHERE week_start = %s
                """, (week_start_str,))

                result = cursor.fetchone()

                if result and result[0]:
                    # 주간계획이 존재하면 해당 계획 사용
                    plan_data = result[0]
                    topics = []

                    # 오늘 날짜와 사이트에 해당하는 계획 찾기
                    for plan in plan_data.get('plans', []):
                        if plan.get('date') == today_str and plan.get('site') == site:
                            # 주간계획의 형식을 기존 형식으로 변환
                            topics.append({
                                'id': hash(f"{site}_{today_str}_{plan.get('title')}"),  # 고유 ID 생성
                                'category': plan.get('category', 'profit_optimized'),
                                'specific_topic': plan.get('title'),
                                'keywords': plan.get('keywords', []),
                                'profit_score': plan.get('profit_score', 0),
                                'priority': plan.get('priority', 'medium')
                            })

                    if topics:
                        logger.info(f"[TOPICS] {site.upper()}: {today_str} 주간계획에서 {len(topics)}개 주제 조회")
                        return topics
                    else:
                        logger.info(f"[TOPICS] {site.upper()}: 주간계획에 오늘 주제가 없음, 월간계획 확인")

                # 주간계획이 없거나 오늘 주제가 없으면 기존 월간계획에서 조회 (폴백)
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

                if topics:
                    logger.info(f"[TOPICS] {site.upper()}: {year}-{month:02d}-{day:02d} 월간계획에서 {len(topics)}개 주제 조회")
                else:
                    logger.warning(f"[NO_TOPICS] {site.upper()}: {today_str} 발행할 주제가 없음")

                return topics

        except Exception as e:
            logger.error(f"오늘 주제 조회 오류: {e}")
            return []
    
    def mark_schedule_completed(self, schedule_id: int):
        """스케줄 완료 처리"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                # 한국 시간으로 업데이트
                import pytz
                kst = pytz.timezone('Asia/Seoul')
                now_kst = datetime.now(kst)

                cursor.execute(f"""
                    UPDATE {self.db.schema}.monthly_publishing_schedule
                    SET status = 'completed'
                    WHERE id = %s
                """, (schedule_id,))
                
                conn.commit()
                logger.info(f"[COMPLETED] 스케줄 ID {schedule_id} 완료 처리됨")
                
        except Exception as e:
            logger.error(f"스케줄 완료 처리 오류: {e}")
    
    def create_and_publish_content(self, site: str, topic_data: dict) -> bool:
        """콘텐츠 생성 및 발행"""
        try:
            logger.info(f"[CONTENT] {site.upper()}: 콘텐츠 생성 시작 - '{topic_data['specific_topic']}'")
            
            # 사이트별 설정
            site_configs = {
                'unpre': {
                    'primary_category': '프로그래밍',
                    'name': 'UNPRE',
                    'tone': 'technical',
                    'target_audience': 'developers',
                    'content_style': '기술적이고 실용적인 개발자 가이드'
                },
                'untab': {
                    'primary_category': '투자',
                    'name': 'UNTAB', 
                    'tone': 'professional',
                    'target_audience': 'investors',
                    'content_style': '전문적이고 신뢰할 수 있는 투자 정보'
                },
                'skewese': {
                    'primary_category': '역사',
                    'name': 'SKEWESE',
                    'tone': 'educational', 
                    'target_audience': 'general',
                    'content_style': '교육적이고 흥미로운 역사 이야기'
                },
                'tistory': {
                    'primary_category': '트렌드',
                    'name': 'TISTORY',
                    'tone': 'casual',
                    'target_audience': 'general',
                    'content_style': '친근하고 트렌디한 일상 정보'
                }
            }
            
            site_config = site_configs.get(site, site_configs['tistory'])
            
            # 콘텐츠 생성
            content = self.content_generator.generate_content(
                site_config=site_config,
                topic=topic_data['specific_topic'],
                category=topic_data['category']
            )
            
            # 유니코드 특수 문자 안전 처리
            content = self._sanitize_content_for_encoding(content)
            
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
                # tistory는 콘텐츠만 저장하고 자동 발행하지 않음 - 목록에 표시됨
                logger.info(f"[CONTENT_READY] {site.upper()}: 콘텐츠 생성 완료 (목록에 표시됨)")
                
                # 상태를 published로 설정하여 목록에 표시되도록 함
                conn = self.db.get_connection()
                with conn.cursor() as cursor:
                    # 한국 시간으로 업데이트
                    import pytz
                    kst = pytz.timezone('Asia/Seoul')
                    now_kst = datetime.now(kst)

                    cursor.execute(f"""
                        UPDATE {self.db.schema}.content_files
                        SET status = 'published', published_at = %s
                        WHERE id = %s
                    """, (now_kst, content_id))
                    conn.commit()
                
                # 메타데이터 업데이트 (목록에 즉시 반영)
                try:
                    # 한국 시간으로 메타데이터 업데이트
                    import pytz
                    kst = pytz.timezone('Asia/Seoul')
                    now_kst = datetime.now(kst)

                    self.db.update_content_metadata(content_id, {
                        'auto_generated': True,
                        'generated_at': now_kst.isoformat(),
                        'schedule_id': topic_data.get('id'),
                        'category': topic_data['category']
                    })
                except Exception as meta_error:
                    logger.warning(f"메타데이터 업데이트 실패: {meta_error}")
                
                return True
            else:
                # WordPress 실제 업로드 임시 비활성화 - 콘텐츠 목록에만 표시
                print(f"[SKIP_UPLOAD] {site} WordPress 실제 업로드 생략, 콘텐츠 목록에만 표시")
                success = True
                result = f"https://{site}.co.kr/?p=AUTO_MOCK_ID_{content_id}"
                
                if success:
                    # 발행 성공 시 publish_history에 기록
                    self.record_publish_history(site, content_id, 'success', None, result)
                    
                    # 한국 시간으로 메타데이터 업데이트
                    import pytz
                    kst = pytz.timezone('Asia/Seoul')
                    now_kst = datetime.now(kst)

                    self.db.update_content_metadata(content_id, {
                        'auto_published': True,
                        'published_at': now_kst.isoformat(),
                        'publish_url': result,
                        'site': site
                    })
                    
                    logger.info(f"[PUBLISHED] {site.upper()}: 발행 성공 - {result}")
                    return True
                else:
                    # 발행 실패 시 기록
                    self.record_publish_history(site, content_id, 'failed', str(result), None)
                    logger.error(f"[PUBLISH_FAILED] {site.upper()}: 발행 실패 - {result}")
                    return False
                    
        except Exception as e:
            logger.error(f"콘텐츠 생성/발행 오류: {e}")
            return False
    
    def save_content_to_db(self, site: str, content: dict, topic_data: dict) -> int:
        """콘텐츠를 데이터베이스에 저장 - 수동발행과 동일한 방식"""
        try:
            # 사이트별 exporter 사용하여 파일 생성
            if site == 'tistory':
                from src.generators.tistory_content_exporter import TistoryContentExporter
                exporter = TistoryContentExporter()
            else:
                from src.generators.wordpress_content_exporter import WordPressContentExporter
                exporter = WordPressContentExporter()
            
            # 콘텐츠 파일 생성
            filepath = exporter.export_content(site, content) if site != 'tistory' else exporter.export_content(content)
            
            # content_files 테이블에 저장 (수동발행과 동일한 구조)
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                # 한국 시간으로 저장
                import pytz
                kst = pytz.timezone('Asia/Seoul')
                now_kst = datetime.now(kst)

                # metadata를 JSON 문자열로 변환
                import json
                metadata_dict = {
                    'category': topic_data['category'],
                    'auto_generated': True,
                    'schedule_id': topic_data.get('id'),
                    'tags': content.get('tags', []),
                    'keywords': topic_data['keywords']
                }

                cursor.execute(f"""
                    INSERT INTO {self.db.schema}.content_files
                    (site, title, file_path, file_type, metadata, created_at, status)
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
                    RETURNING id
                """, (
                    site,
                    content['title'],
                    filepath,
                    'tistory' if site == 'tistory' else 'wordpress',
                    json.dumps(metadata_dict, ensure_ascii=False),
                    now_kst,
                    'published'  # 초기상태는 published로 설정
                ))
                
                content_id = cursor.fetchone()[0]
                conn.commit()
                
                logger.info(f"[SAVED] {site.upper()}: 콘텐츠 파일 저장 완료 - ID: {content_id}, Path: {filepath}")
                return content_id
                
        except Exception as e:
            logger.error(f"콘텐츠 DB 저장 오류: {e}")
            raise
    
    def record_publish_history(self, site: str, content_id: int, status: str, error_msg: str, publish_url: str):
        """발행 이력 기록"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                # 한국 시간으로 기록
                import pytz
                kst = pytz.timezone('Asia/Seoul')
                now_kst = datetime.now(kst)

                # response_data를 JSON 문자열로 변환
                import json
                response_dict = {'auto_publish': True, 'timestamp': now_kst.isoformat()}

                cursor.execute(f"""
                    INSERT INTO {self.db.schema}.publish_history
                    (site, content_file_id, publish_type, publish_status, error_message,
                     published_at, publish_url, response_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                """, (
                    site,
                    content_id,
                    'auto',
                    status,
                    error_msg,
                    now_kst,
                    publish_url,
                    json.dumps(response_dict, ensure_ascii=False)
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"발행 이력 기록 오류: {e}")
    
    def start(self):
        """스케줄러 시작"""
        logger.info("[START] PostgreSQL 기반 자동발행 스케줄러 시작")
        
        # 스케줄 설정
        self.setup_daily_schedules()
        
        # 등록된 작업 목록 출력
        jobs = self.scheduler.get_jobs()
        logger.info(f"[SCHEDULE] 등록된 자동발행 스케줄 ({len(jobs)}개):")
        for job in jobs:
            try:
                next_run = getattr(job, 'next_run_time', '스케줄러 시작 후 결정')
                logger.info(f"  - {job.id}: {next_run}")
            except Exception as e:
                logger.info(f"  - {job.id}: 스케줄 정보 확인 중 오류 ({e})")
        
        try:
            # 스케줄러 실행
            logger.info("[WAITING] 스케줄러 실행 대기 중...")
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("[EXIT] 사용자에 의해 스케줄러 종료")
        except Exception as e:
            logger.error(f"[ERROR] 스케줄러 오류: {e}")
        finally:
            self.scheduler.shutdown()
            logger.info("[END] 스케줄러 종료 완료")
    
    def run_now(self, site: str = None):
        """즉시 실행 (테스트용)"""
        if site:
            logger.info(f"[TEST] {site.upper()} 테스트 실행")
            return self.auto_publish_for_site(site)
        else:
            logger.info("[TEST] 모든 사이트 테스트 실행")
            self.auto_publish_all_sites()
    
    def _sanitize_content_for_encoding(self, content: dict) -> dict:
        """콘텐츠에서 인코딩 문제를 일으킬 수 있는 특수 문자 제거/변환"""
        import re
        
        def clean_text(text: str) -> str:
            if not isinstance(text, str):
                return text
            
            # 문제가 되는 유니코드 이모지 및 특수 문자를 안전한 텍스트로 변환
            replacements = {
                '⚠️': '[주의]',
                '✅': '[확인]',
                '❌': '[오류]',
                '⭐': '[중요]',
                '🔥': '[핫]',
                '💡': '[팁]',
                '📌': '[포인트]',
                '🚀': '[시작]',
                '⏰': '[시간]',
                '💰': '[가격]',
                '📈': '[상승]',
                '📉': '[하락]'
            }
            
            for emoji, replacement in replacements.items():
                text = text.replace(emoji, replacement)
            
            # 기타 특수 유니코드 문자 제거 (ASCII 범위 외, 한글 제외)
            text = re.sub(r'[^\x00-\x7F가-힣ㄱ-ㅎㅏ-ㅣ]', '', text)
            
            return text
        
        # 콘텐츠 딕셔너리의 모든 텍스트 필드 정리
        if isinstance(content, dict):
            cleaned_content = {}
            for key, value in content.items():
                if isinstance(value, str):
                    cleaned_content[key] = clean_text(value)
                elif isinstance(value, list):
                    cleaned_content[key] = [clean_text(item) if isinstance(item, str) else item for item in value]
                else:
                    cleaned_content[key] = value
            return cleaned_content

        return content

    def _check_and_create_weekly_plan(self, today):
        """주간계획이 없으면 자동 생성"""
        try:
            from datetime import timedelta
            weekday = today.weekday()
            week_start = today - timedelta(days=weekday)
            week_start_str = week_start.strftime('%Y-%m-%d')

            # 주간계획 존재 여부 확인
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT id FROM {self.db.schema}.weekly_plans
                    WHERE week_start = %s
                """, (week_start_str,))

                if not cursor.fetchone():
                    logger.info(f"[주간계획] 이번주({week_start_str}) 계획이 없어 자동 생성 시작")
                    # auto_weekly_planner 실행
                    from auto_weekly_planner import ProfitWeeklyPlanner
                    planner = ProfitWeeklyPlanner()
                    weekly_plan = planner.generate_weekly_plan(target_week='current')
                    if weekly_plan and weekly_plan.get('plans'):
                        planner.save_weekly_plan(weekly_plan)
                        logger.info(f"[주간계획] 이번주 계획 생성 완료: {len(weekly_plan['plans'])}개 항목")
                    else:
                        logger.error("[주간계획] 계획 생성 실패")

        except Exception as e:
            logger.error(f"[주간계획] 자동 생성 오류: {e}")

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