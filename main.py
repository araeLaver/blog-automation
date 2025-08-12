"""
블로그 자동화 시스템 메인 실행 파일
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.scheduler import BlogAutomationScheduler
from src.generators.content_generator import ContentGenerator
from src.generators.image_generator import ImageGenerator
from src.publishers.wordpress_publisher import WordPressPublisher
from src.publishers.tistory_publisher import TistoryPublisher
from src.utils.database import ContentDatabase
from src.utils.logger import blog_logger, log_info, log_error
from config.sites_config import SITE_CONFIGS


class BlogAutomationManager:
    def __init__(self):
        """메인 매니저 초기화"""
        load_dotenv()
        
        self.scheduler = BlogAutomationScheduler()
        self.database = ContentDatabase()
        
        log_info("Blog Automation System initialized")
        
        # 환경변수 검증
        self._validate_environment()
    
    def _validate_environment(self):
        """필수 환경변수 검증"""
        required_vars = [
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY"
        ]
        
        # WordPress 사이트 설정
        for site in ["UNPRE", "UNTAB", "SKEWESE"]:
            required_vars.extend([
                f"{site}_URL",
                f"{site}_USERNAME", 
                f"{site}_PASSWORD"
            ])
        
        # Tistory 설정
        required_vars.extend([
            "TISTORY_APP_ID",
            "TISTORY_SECRET_KEY",
            "TISTORY_ACCESS_TOKEN"
        ])
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            log_error(f"Missing required environment variables: {missing_vars}")
            log_info("Please check your .env file")
            return False
        
        log_info("Environment validation passed")
        return True
    
    def setup_initial_data(self):
        """초기 데이터 설정"""
        log_info("Setting up initial topic data...")
        
        for site_key, config in SITE_CONFIGS.items():
            topics = []
            for topic in config["topics"]:
                for category in config["categories"]:
                    topics.append({
                        "topic": f"{topic} - {category}",
                        "category": category,
                        "priority": 5
                    })
            
            self.database.add_topics_bulk(site_key, topics)
            log_info(f"Added {len(topics)} topics for {site_key}")
        
        log_info("Initial data setup completed")
    
    def test_all_connections(self):
        """모든 API 연결 테스트"""
        log_info("Testing all API connections...")
        
        results = {}
        
        # WordPress 사이트들 테스트
        for site_key in ["unpre", "untab", "skewese"]:
            try:
                publisher = WordPressPublisher(site_key)
                results[site_key] = publisher.test_connection()
                
                if results[site_key]:
                    log_info(f"✅ {site_key.upper()} WordPress connection OK")
                else:
                    log_error(f"❌ {site_key.upper()} WordPress connection failed")
                    
            except Exception as e:
                results[site_key] = False
                log_error(f"❌ {site_key.upper()} WordPress connection error: {e}")
        
        # Tistory는 API 서비스 종료로 제외
        log_info("ℹ️  Tistory Open API는 2022년 서비스 종료됨 (제외)")
        
        # AI API 테스트
        try:
            generator = ContentGenerator()
            # 간단한 테스트 콘텐츠 생성
            test_content = generator.generate_content(
                site_config=SITE_CONFIGS["unpre"],
                topic="API 테스트",
                category="테스트"
            )
            results["ai_api"] = bool(test_content)
            log_info("✅ AI API connection OK")
            
        except Exception as e:
            results["ai_api"] = False
            log_error(f"❌ AI API connection error: {e}")
        
        # 결과 요약
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        log_info(f"Connection test results: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            log_info("🎉 All connections successful!")
        else:
            log_error("⚠️  Some connections failed. Check your configuration.")
        
        return results
    
    def create_sample_post(self, site_key: str):
        """샘플 포스트 생성 (테스트용)"""
        log_info(f"Creating sample post for {site_key}...")
        
        try:
            success = self.scheduler.create_and_publish_post(site_key)
            
            if success:
                log_info(f"✅ Sample post created successfully for {site_key}")
            else:
                log_error(f"❌ Failed to create sample post for {site_key}")
            
            return success
            
        except Exception as e:
            log_error(f"❌ Error creating sample post for {site_key}: {e}")
            return False
    
    def show_stats(self):
        """시스템 통계 표시"""
        log_info("=== Blog Automation Statistics ===")
        
        # 시스템 통계
        stats = blog_logger.get_stats()
        log_info(f"Posts Created: {stats['posts_created']}")
        log_info(f"Posts Published: {stats['posts_published']}")
        log_info(f"Images Generated: {stats['images_generated']}")
        log_info(f"API Calls: {stats['api_calls']}")
        log_info(f"Errors: {stats['errors']}")
        log_info(f"Uptime: {stats['uptime_hours']:.1f} hours")
        
        # 사이트별 최근 포스트
        for site_key in SITE_CONFIGS.keys():
            recent_posts = self.database.get_recent_posts(site_key, 5)
            log_info(f"\n[{site_key.upper()}] Recent Posts ({len(recent_posts)}):")
            for post in recent_posts:
                log_info(f"  - {post['title']} ({post['date']})")
    
    def run_scheduler(self):
        """스케줄러 실행"""
        log_info("Starting Blog Automation Scheduler...")
        log_info("Press Ctrl+C to stop")
        
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            log_info("Scheduler stopped by user")
        except Exception as e:
            log_error("Scheduler error", error=e)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Blog Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py test                    # Test all connections
  python main.py setup                   # Setup initial data
  python main.py post unpre              # Create sample post for unpre
  python main.py stats                   # Show system statistics
  python main.py schedule                # Start scheduler
        """
    )
    
    parser.add_argument(
        "command",
        choices=["test", "setup", "post", "stats", "schedule"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "site",
        nargs="?",
        choices=["unpre", "untab", "skewese"],
        help="Site key (required for 'post' command)"
    )
    
    args = parser.parse_args()
    
    # 매니저 초기화
    manager = BlogAutomationManager()
    
    # 명령어 실행
    if args.command == "test":
        manager.test_all_connections()
    
    elif args.command == "setup":
        manager.setup_initial_data()
    
    elif args.command == "post":
        if not args.site:
            log_error("Site key is required for 'post' command")
            parser.print_help()
            sys.exit(1)
        
        manager.create_sample_post(args.site)
    
    elif args.command == "stats":
        manager.show_stats()
    
    elif args.command == "schedule":
        manager.run_scheduler()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error("Fatal error in main", error=e)
        sys.exit(1)