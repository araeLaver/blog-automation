"""
자동 발행 스케줄러 v2 - 새벽 3시 자동 실행
매일 새벽 3시에 계획표에 따라 모든 사이트 콘텐츠 자동 생성 및 발행
"""

import os
import logging
import schedule
import time
from datetime import datetime, timezone, timedelta
from threading import Thread
import sys

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.monthly_schedule_manager import monthly_schedule_manager
from src.generators.content_generator import ContentGenerator
from src.generators.wordpress_content_exporter import WordPressContentExporter
from src.generators.tistory_content_exporter import TistoryContentExporter
from src.utils.postgresql_database import PostgreSQLDatabase
from src.utils.api_tracker import api_tracker
from src.publishers.wordpress_publisher import WordPressPublisher
import json

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/auto_publisher_v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_log(message):
    """CP949 호환성을 위한 안전한 로깅"""
    try:
        logger.info(message)
    except UnicodeEncodeError:
        # 이모지 변환
        safe_message = (message
                       .replace('📊', '[리포트]')
                       .replace('✅', '[성공]')
                       .replace('❌', '[실패]')
                       .replace('⏱️', '[시간]')
                       .replace('🕐', '[완료]')
                       .replace('💰', '[가격]')
                       .replace('📝', '[작성]')
                       .replace('🎯', '[타겟]'))
        logger.info(safe_message)


class AutoPublisherV2:
    def __init__(self):
        """자동 발행 스케줄러 초기화"""
        self.sites = ['unpre', 'untab', 'skewese', 'tistory']
        self.running = True
        
        # WordPress 설정 로드
        try:
            with open('config/wordpress_sites.json', 'r', encoding='utf-8') as f:
                self.wp_config = json.load(f)
            logger.info("✅ WordPress 설정 로드 완료")
        except Exception as e:
            logger.error(f"❌ WordPress 설정 로드 실패: {e}")
            self.wp_config = {}
        
        logger.info("✅ 자동 발행 스케줄러 v2 초기화 완료")
    
    def daily_publish_all(self):
        """매일 새벽 3시 모든 사이트 자동 발행 (듀얼 카테고리)"""
        KST = timezone(timedelta(hours=9))
        start_time = datetime.now(KST)
        
        logger.info("=" * 50)
        logger.info(f"🚀 자동 발행 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S KST')}")
        logger.info(f"📋 대상 사이트: {', '.join(self.sites)}")
        logger.info("=" * 50)
        
        success_count = 0
        fail_count = 0
        wp_success_count = 0  # WordPress 업로드 성공 카운트
        total_posts = len(self.sites) * 2  # 사이트당 2개 (Primary + Secondary)
        
        try:
            # DB 연결
            db = PostgreSQLDatabase()
            logger.info("✅ DB 연결 성공")
            
            # 각 사이트별 발행
            for site_idx, site in enumerate(self.sites, 1):
                logger.info(f"\n{'='*30}")
                logger.info(f"🎯 [{site_idx}/{len(self.sites)}] {site.upper()} 사이트 발행 시작")
                
                try:
                    # 오늘의 듀얼 카테고리 주제 가져오기
                    primary_topic, secondary_topic = monthly_schedule_manager.get_today_dual_topics_for_manual(site)
                    
                    if not primary_topic or not secondary_topic:
                        logger.error(f"❌ {site}: 오늘의 주제를 찾을 수 없음")
                        fail_count += 2
                        continue
                    
                    logger.info(f"📚 Primary: {primary_topic['topic']} ({primary_topic['category']})")
                    logger.info(f"📚 Secondary: {secondary_topic['topic']} ({secondary_topic['category']})")
                    
                    # Primary 카테고리 발행
                    primary_success, primary_wp_success = self._publish_content(db, site, primary_topic, 'primary')
                    if primary_success:
                        success_count += 1
                        if primary_wp_success:
                            wp_success_count += 1
                    else:
                        fail_count += 1
                    
                    # Secondary 카테고리 발행
                    secondary_success, secondary_wp_success = self._publish_content(db, site, secondary_topic, 'secondary')
                    if secondary_success:
                        success_count += 1
                        if secondary_wp_success:
                            wp_success_count += 1
                    else:
                        fail_count += 1
                    
                    logger.info(f"✅ {site.upper()} 완료: 진행률 {((site_idx * 2) / total_posts * 100):.0f}%")
                    
                except Exception as e:
                    logger.error(f"❌ {site} 발행 실패: {str(e)}")
                    fail_count += 2
            
            # 발행 완료 리포트
            end_time = datetime.now(KST)
            elapsed = end_time - start_time
            
            logger.info("\n" + "=" * 50)
            logger.info("📊 자동 발행 완료 리포트")
            logger.info(f"✅ 성공: {success_count}/{total_posts} 건")
            logger.info(f"❌ 실패: {fail_count}/{total_posts} 건")
            logger.info(f"🌐 WordPress 업로드 성공: {wp_success_count}/{success_count} 건")
            logger.info(f"⏱️  소요시간: {elapsed.seconds//60}분 {elapsed.seconds%60}초")
            logger.info(f"🕐 완료시간: {end_time.strftime('%Y-%m-%d %H:%M:%S KST')}")
            
            # API 사용량 리포트
            today_usage = api_tracker.get_today_usage()
            safe_log(f"💰 오늘 API 비용: ${today_usage['total_cost_usd']:.4f} USD")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"❌ 자동 발행 중 심각한 오류: {str(e)}")
    
    def _publish_content(self, db, site: str, topic_data: dict, category_type: str) -> tuple[bool, bool]:
        """개별 콘텐츠 생성 및 발행"""
        try:
            logger.info(f"  📝 {category_type.upper()}: {topic_data['topic']} 생성 시작...")
            
            # 콘텐츠 생성
            generator = ContentGenerator()
            
            if site == 'tistory':
                exporter = TistoryContentExporter()
                site_config = {
                    'name': 'Tistory 블로그',
                    'categories': [topic_data['category']],
                    'content_style': '친근하고 실용적인 톤',
                    'target_audience': self._get_target_audience(topic_data['category']),
                    'keywords_focus': topic_data.get('keywords', [])
                }
            else:
                exporter = WordPressContentExporter()
                site_config = {
                    'name': site.upper(),
                    'categories': [topic_data['category']],
                    'content_style': '전문적이고 신뢰할 수 있는 톤',
                    'target_audience': self._get_target_audience(topic_data['category']),
                    'keywords_focus': topic_data.get('keywords', [])
                }
            
            # 콘텐츠 생성 (API 추적 포함)
            content_data = generator.generate_content(
                site_config,
                topic_data['topic'],
                topic_data['category'],
                None,  # existing_posts
                'medium',  # content_length
                site  # site_key for API tracking
            )
            
            if not content_data:
                logger.error(f"  ❌ 콘텐츠 생성 실패")
                return False
            
            # 파일로 내보내기
            if site == 'tistory':
                filepath = exporter.export_content(content_data)
            else:
                filepath = exporter.export_content(site, content_data)
            
            # DB에 저장
            file_id = db.add_content_file(
                site=site,
                title=content_data['title'],
                file_path=filepath,
                file_type='tistory' if site == 'tistory' else 'wordpress',
                metadata={
                    'category': topic_data['category'],
                    'category_type': category_type,
                    'tags': content_data.get('tags', []),
                    'auto_published': True,
                    'published_at': datetime.now(timezone(timedelta(hours=9))).isoformat()
                }
            )
            
            # WordPress 업로드 (WordPress 사이트인 경우)
            wp_upload_success = False
            if site in ['unpre', 'untab', 'skewese'] and site in self.wp_config:
                try:
                    logger.info(f"  🌐 WordPress 업로드 시작: {site.upper()}")
                    
                    # WordPress 콘텐츠 형식으로 변환
                    wp_content = {
                        'title': content_data['title'],
                        'content': content_data['content'],
                        'excerpt': content_data.get('meta_description', '')[:160],
                        'status': 'publish',
                        'categories': [],  # 기본값, 필요시 카테고리 ID 매핑
                        'tags': []  # 기본값, 필요시 태그 처리
                    }
                    
                    # WordPress Publisher 초기화 및 업로드
                    publisher = WordPressPublisher(self.wp_config[site])
                    upload_result = publisher.publish_post(wp_content)
                    
                    if upload_result and upload_result.get('success'):
                        wp_upload_success = True
                        wp_url = upload_result.get('url', '')
                        logger.info(f"  ✅ WordPress 업로드 성공: {wp_url}")
                        
                        # DB 메타데이터에 WordPress URL 추가
                        db.cursor.execute("""
                            UPDATE unble.content_files 
                            SET metadata = metadata || %s::jsonb 
                            WHERE id = %s
                        """, [json.dumps({'wordpress_url': wp_url, 'wordpress_post_id': upload_result.get('post_id')}), file_id])
                        db.connection.commit()
                    else:
                        error_msg = upload_result.get('error', 'Unknown error') if upload_result else 'No response'
                        logger.error(f"  ❌ WordPress 업로드 실패: {error_msg}")
                        
                except Exception as wp_error:
                    logger.error(f"  ❌ WordPress 업로드 오류: {str(wp_error)}")
            
            # 발행 상태 업데이트 (WordPress 업로드 결과 반영)
            status_msg = 'published_with_wp' if wp_upload_success else 'published'
            db.update_file_status(file_id, status_msg, datetime.now())
            
            success_indicator = "🌐✅" if wp_upload_success else "✅"
            logger.info(f"  {success_indicator} {category_type.upper()} 완료: {content_data['title'][:50]}...")
            return True, wp_upload_success
            
        except Exception as e:
            logger.error(f"  ❌ {category_type} 발행 오류: {str(e)}")
            return False, False
    
    def _get_target_audience(self, category: str) -> str:
        """카테고리별 타겟 오디언스 반환"""
        audiences = {
            '테크': 'IT 전문가, 개발자, 테크 얼리어답터',
            '라이프': '20-40대 직장인, 자기계발에 관심있는 사람들',
            '비즈니스': '창업가, 비즈니스 리더, 마케터',
            '건강': '건강관리에 관심있는 모든 연령층',
            '여행': '여행을 좋아하는 2030세대',
            '음식': '요리와 맛집에 관심있는 사람들',
            '문화': '문화예술에 관심있는 교양있는 독자층',
            '교육': '학부모, 교육자, 평생학습에 관심있는 사람들',
            '스포츠': '스포츠 팬, 운동을 즐기는 사람들',
            '엔터테인먼트': '대중문화를 즐기는 젊은 세대'
        }
        return audiences.get(category, '다양한 관심사를 가진 독자들')
    
    def start(self):
        """스케줄러 시작"""
        logger.info("🔄 자동 발행 스케줄러 v2 시작...")
        
        # 매일 새벽 3시에 실행
        schedule.every().day.at("03:00").do(self.daily_publish_all)
        
        # 시작 시 다음 실행 시간 표시
        next_run = schedule.next_run()
        if next_run:
            logger.info(f"⏰ 다음 자동 발행: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 테스트용: 즉시 실행 (주석 해제하면 바로 실행)
        # self.daily_publish_all()
        
        # 스케줄 실행 루프
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except KeyboardInterrupt:
                logger.info("🛑 사용자에 의해 스케줄러 중지")
                self.running = False
                break
            except Exception as e:
                logger.error(f"스케줄 실행 오류: {str(e)}")
                time.sleep(60)
    
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        logger.info("🛑 자동 발행 스케줄러 v2 중지됨")


def main():
    """메인 함수"""
    publisher = AutoPublisherV2()
    
    try:
        # 백그라운드 스레드로 실행
        thread = Thread(target=publisher.start, daemon=True)
        thread.start()
        
        logger.info("✅ 자동 발행 스케줄러 v2가 백그라운드에서 실행 중...")
        logger.info("종료하려면 Ctrl+C를 누르세요.")
        
        # 메인 스레드 유지
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        publisher.stop()
        logger.info("프로그램 종료")


if __name__ == "__main__":
    main()