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
from typing import Tuple
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
        # 매일 새벽 3시에 자동 발행 (월간 계획표 기반)
        schedule.every().day.at("03:00").do(self.daily_auto_publish)
        
        print("[AUTO_PUBLISHER] 자동 발행 스케줄 설정 완료")
        print("- 매일 새벽 3시: 월간 계획표 기반 자동 콘텐츠 생성 및 발행")
        print("- 월간 계획표: 매월 마지막 날 자동 생성")
    
    def daily_auto_publish(self):
        """일일 2개 카테고리 자동 발행 실행"""
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
                message=f"2개 카테고리 자동 발행 시작: {today}",
                details={
                    "date": str(today),
                    "start_time": start_time.isoformat(),
                    "day_of_week": today.weekday(),
                    "dual_category": True
                }
            )
        except Exception as db_error:
            print(f"[DUAL_PUBLISH] 데이터베이스 로그 오류: {db_error}")
        
        try:
            print(f"\n[DUAL_PUBLISH] {today} 2개 카테고리 자동 발행 시작 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            sites = ['unpre', 'untab', 'skewese', 'tistory']
            total_published = 0
            failed_sites = []
            
            # 각 사이트별로 2개 카테고리 발행
            for site in sites:
                site_start_time = datetime.now()
                
                try:
                    print(f"\n[DUAL_PUBLISH] {site.upper()} 2개 카테고리 발행 시작")
                    
                    # 2개 카테고리 주제 가져오기
                    primary_topic, secondary_topic = schedule_manager.get_today_dual_topics_for_manual(site)
                    
                    # Primary 카테고리 발행
                    print(f"  Primary [{primary_topic['category']}]: {primary_topic['topic'][:50]}...")
                    success_primary = self._execute_dual_category_publishing(site, primary_topic, "primary", db)
                    
                    if success_primary:
                        total_published += 1
                        print(f"  ✅ Primary 발행 완료")
                    else:
                        print(f"  ❌ Primary 발행 실패")
                    
                    # Secondary 카테고리 발행
                    print(f"  Secondary [{secondary_topic['category']}]: {secondary_topic['topic'][:50]}...")
                    success_secondary = self._execute_dual_category_publishing(site, secondary_topic, "secondary", db)
                    
                    if success_secondary:
                        total_published += 1
                        print(f"  ✅ Secondary 발행 완료")
                    else:
                        print(f"  ❌ Secondary 발행 실패")
                    
                    site_end_time = datetime.now()
                    site_duration = (site_end_time - site_start_time).total_seconds()
                    
                    # 사이트별 결과
                    if success_primary and success_secondary:
                        print(f"🎉 {site.upper()} 2개 카테고리 발행 완료 (소요: {site_duration:.1f}초)")
                        
                        if db:
                            db.add_system_log(
                                level="INFO",
                                component="auto_publisher",
                                message=f"{site} 2개 카테고리 발행 완료",
                                details={
                                    "site": site,
                                    "primary_topic": primary_topic['topic'],
                                    "secondary_topic": secondary_topic['topic'],
                                    "duration_seconds": site_duration,
                                    "posts_published": 2
                                },
                                site=site,
                                duration_ms=int(site_duration * 1000)
                            )
                    elif success_primary or success_secondary:
                        print(f"⚠️  {site.upper()} 부분 성공 (1/2) (소요: {site_duration:.1f}초)")
                        failed_sites.append(f"{site} (부분실패)")
                        
                        if db:
                            db.add_system_log(
                                level="WARNING",
                                component="auto_publisher",
                                message=f"{site} 2개 카테고리 부분 성공",
                                details={
                                    "site": site,
                                    "primary_success": success_primary,
                                    "secondary_success": success_secondary,
                                    "duration_seconds": site_duration,
                                    "posts_published": 1
                                },
                                site=site,
                                duration_ms=int(site_duration * 1000)
                            )
                    else:
                        print(f"💥 {site.upper()} 발행 실패 (소요: {site_duration:.1f}초)")
                        failed_sites.append(site)
                        
                        if db:
                            db.add_system_log(
                                level="ERROR",
                                component="auto_publisher",
                                message=f"{site} 2개 카테고리 발행 실패",
                                details={
                                    "site": site,
                                    "primary_topic": primary_topic.get('topic', ''),
                                    "secondary_topic": secondary_topic.get('topic', ''),
                                    "duration_seconds": site_duration,
                                    "posts_published": 0
                                },
                                site=site,
                                duration_ms=int(site_duration * 1000)
                            )
                    
                    # 사이트 간 간격 (서버 부하 방지)
                    time.sleep(60)  # 2개 포스팅이므로 더 긴 간격
                    
                except Exception as site_error:
                    site_end_time = datetime.now()
                    site_duration = (site_end_time - site_start_time).total_seconds()
                    
                    print(f"💥 {site.upper()} 오류: {site_error}")
                    failed_sites.append(site)
                    
                    if db:
                        import traceback
                        db.add_system_log(
                            level="ERROR",
                            component="auto_publisher",
                            message=f"{site} 2개 카테고리 발행 중 예외",
                            details={
                                "site": site,
                                "error": str(site_error),
                                "traceback": traceback.format_exc(),
                                "duration_seconds": site_duration
                            },
                            site=site,
                            duration_ms=int(site_duration * 1000)
                        )
            
            # 전체 결과 요약
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            print(f"\n" + "="*60)
            print(f"📊 2개 카테고리 자동 발행 완료 - {end_time.strftime('%H:%M:%S')}")
            print(f"   • 총 발행: {total_published}/8개")
            print(f"   • 성공률: {total_published/8*100:.1f}%")
            print(f"   • 소요시간: {total_duration/60:.1f}분")
            
            if failed_sites:
                print(f"   • 실패 사이트: {', '.join(failed_sites)}")
            else:
                print(f"   🎉 모든 사이트 발행 성공!")
            
            print("="*60)
            
            if db:
                db.add_system_log(
                    level="INFO",
                    component="auto_publisher",
                    message=f"2개 카테고리 자동 발행 완료: {total_published}/8개 성공",
                    details={
                        "date": str(today),
                        "total_posts_expected": 8,
                        "total_posts_published": total_published,
                        "success_rate": total_published/8*100,
                        "failed_sites": failed_sites,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "total_duration_minutes": total_duration/60,
                        "dual_category": True
                    },
                    duration_ms=int(total_duration * 1000)
                )
            
        except Exception as e:
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            error_msg = str(e)
            
            print(f"[DUAL_PUBLISH] 2개 카테고리 자동 발행 오류: {error_msg}")
            
            if db:
                import traceback
                db.add_system_log(
                    level="CRITICAL",
                    component="auto_publisher",
                    message="2개 카테고리 자동 발행 중 치명적 오류 발생",
                    details={
                        "date": str(today),
                        "error": error_msg,
                        "traceback": traceback.format_exc(),
                        "start_time": start_time.isoformat(),
                        "error_time": end_time.isoformat(),
                        "duration_seconds": total_duration,
                        "dual_category": True
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

    def _execute_dual_category_publishing(self, site: str, topic_info: dict, category_type: str, db) -> bool:
        """2개 카테고리 발행을 위한 단일 주제 발행"""
        try:
            content_start_time = datetime.now()
            
            print(f"    📝 [{category_type}] 콘텐츠 생성 중...")
            
            # 직접 콘텐츠 생성 함수 호출
            if site in ['unpre', 'untab', 'skewese']:
                # WordPress 사이트 콘텐츠 생성 및 발행
                success = self._generate_and_publish_wordpress_dual(site, topic_info, category_type, db)
                
            elif site == 'tistory':
                # Tistory 콘텐츠 생성
                success = self._generate_tistory_content_dual(site, topic_info, category_type, db)
            else:
                print(f"    ❌ {site} 지원하지 않는 사이트")
                return False
                
            content_end_time = datetime.now()
            duration = (content_end_time - content_start_time).total_seconds()
            
            if success:
                print(f"    ✅ [{category_type}] 발행 성공 (소요: {duration:.1f}초)")
                
                if db:
                    db.add_system_log(
                        level="INFO",
                        component="auto_publisher",
                        message=f"{site} {category_type} 카테고리 발행 성공",
                        details={
                            "site": site,
                            "category_type": category_type,
                            "topic": topic_info.get('topic', ''),
                            "category": topic_info.get('category', ''),
                            "duration_seconds": duration
                        },
                        site=site,
                        duration_ms=int(duration * 1000)
                    )
            else:
                print(f"    ❌ [{category_type}] 발행 실패 (소요: {duration:.1f}초)")
                
                if db:
                    db.add_system_log(
                        level="ERROR",
                        component="auto_publisher",
                        message=f"{site} {category_type} 카테고리 발행 실패",
                        details={
                            "site": site,
                            "category_type": category_type,
                            "topic": topic_info.get('topic', ''),
                            "category": topic_info.get('category', ''),
                            "duration_seconds": duration,
                            "error": "콘텐츠 생성 또는 발행 실패"
                        },
                        site=site,
                        duration_ms=int(duration * 1000)
                    )
                
            return success
            
        except Exception as e:
            content_end_time = datetime.now()
            duration = (content_end_time - content_start_time).total_seconds()
            
            print(f"    ❌ [{category_type}] 발행 중 오류: {str(e)} (소요: {duration:.1f}초)")
            
            if db:
                import traceback
                db.add_system_log(
                    level="ERROR",
                    component="auto_publisher",
                    message=f"{site} {category_type} 카테고리 발행 실행 중 예외",
                    details={
                        "site": site,
                        "category_type": category_type,
                        "topic": topic_info.get('topic', ''),
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                        "duration_seconds": duration
                    },
                    site=site,
                    duration_ms=int(duration * 1000)
                )
            return False

    def _generate_and_publish_wordpress_dual(self, site: str, topic_info: dict, category_type: str, db) -> bool:
        """2개 카테고리용 WordPress 콘텐츠 생성 및 실제 사이트 발행"""
        try:
            from ..generators.content_generator import ContentGenerator
            from ..generators.wordpress_content_exporter import WordPressContentExporter
            from ..publishers.wordpress_publisher import WordPressPublisher
            
            # 1. 콘텐츠 생성
            print(f"    🎯 {site} [{category_type}] AI 콘텐츠 생성 시작")
            
            generator = ContentGenerator()
            exporter = WordPressContentExporter()
            
            site_config = {
                'name': f"{site} - {category_type}",
                'categories': [topic_info.get('category', 'general')],
                'content_style': '전문적이고 신뢰할 수 있는 톤',
                'target_audience': '전문가 및 일반인',
                'keywords_focus': topic_info.get('keywords', [])
            }
            
            content = generator.generate_content(
                site_config=site_config,
                topic=topic_info['topic'],
                category=topic_info.get('category', 'general'),
                content_length=topic_info.get('length', 'medium')
            )
            
            print(f"    📄 {site} [{category_type}] 콘텐츠 생성 완료: {content.get('title', 'Unknown')}")
            
            # 2. 파일 저장 (카테고리별로 구분)
            filepath = exporter.export_content(site, content, category_suffix=category_type)
            print(f"    💾 {site} [{category_type}] 파일 저장 완료: {filepath}")
            
            # 3. 데이터베이스에 파일 정보 저장
            if db:
                from pathlib import Path
                file_path_obj = Path(filepath)
                file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
                content_text = content.get('introduction', '') + ' '.join([s.get('content', '') for s in content.get('sections', [])])
                word_count = len(content_text.replace(' ', ''))
                
                file_id = db.add_content_file(
                    site=site,
                    title=f"[{category_type.upper()}] {content['title']}",
                    file_path=filepath,
                    file_type="wordpress",
                    metadata={
                        'tags': content.get('tags', []),
                        'categories': [content.get('category', topic_info.get('category', 'general'))],
                        'word_count': word_count,
                        'file_size': file_size,
                        'auto_generated': True,
                        'dual_category': True,
                        'category_type': category_type
                    }
                )
                print(f"    💿 {site} [{category_type}] 데이터베이스 저장 완료 (ID: {file_id})")
                
            # 4. WordPress 사이트에 실제 발행
            print(f"    🚀 {site} [{category_type}] WordPress 사이트 발행 시작")
            
            publisher = WordPressPublisher(site)
            
            # 콘텐츠 데이터 준비
            content_data = {
                'title': f"[{topic_info.get('category', '')}] {content['title']}",
                'introduction': content.get('introduction', ''),
                'sections': content.get('sections', []),
                'conclusion': content.get('conclusion', ''),
                'meta_description': content.get('meta_description', ''),
                'categories': [content.get('category', topic_info.get('category', 'general'))],
                'tags': content.get('tags', [])
            }
            
            # WordPress에 실제 발행
            wp_success, wp_result = publisher.publish_post(content_data, images=[], draft=False)
            
            if wp_success:
                print(f"    🎉 {site} [{category_type}] WordPress 발행 성공: {wp_result}")
                
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
                        message=f"{site} [{category_type}] WordPress 발행 성공",
                        details={
                            "site": site,
                            "category_type": category_type,
                            "title": content['title'],
                            "wordpress_url": wp_result,
                            "file_id": file_id
                        },
                        site=site
                    )
                
                return True
            else:
                print(f"    ❌ {site} [{category_type}] WordPress 발행 실패: {wp_result}")
                
                if db:
                    db.add_system_log(
                        level="ERROR",
                        component="auto_publisher",
                        message=f"{site} [{category_type}] WordPress 발행 실패",
                        details={
                            "site": site,
                            "category_type": category_type,
                            "title": content['title'],
                            "error": str(wp_result)
                        },
                        site=site
                    )
                return False
                
        except Exception as e:
            print(f"    ❌ {site} [{category_type}] WordPress 발행 중 오류: {str(e)}")
            
            if db:
                import traceback
                db.add_system_log(
                    level="ERROR",
                    component="auto_publisher",
                    message=f"{site} [{category_type}] WordPress 발행 중 예외",
                    details={
                        "site": site,
                        "category_type": category_type,
                        "topic": topic_info.get('topic', ''),
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    },
                    site=site
                )
            return False

    def _generate_tistory_content_dual(self, site: str, topic_info: dict, category_type: str, db) -> bool:
        """2개 카테고리용 Tistory 콘텐츠 생성"""
        try:
            from ..generators.content_generator import ContentGenerator
            from ..generators.tistory_content_exporter import TistoryContentExporter
            
            print(f"    🎯 {site} [{category_type}] AI 콘텐츠 생성 시작")
            
            generator = ContentGenerator()
            exporter = TistoryContentExporter()
            
            site_config = {
                'name': f'Tistory 블로그 - {category_type}',
                'categories': [topic_info.get('category', 'general')],
                'content_style': '친근하고 실용적인 톤',
                'target_audience': '일반인',
                'keywords_focus': topic_info.get('keywords', [])
            }
            
            content = generator.generate_content(
                site_config=site_config,
                topic=topic_info['topic'],
                category=topic_info.get('category', 'general'),
                content_length=topic_info.get('length', 'medium')
            )
            
            print(f"    📄 {site} [{category_type}] 콘텐츠 생성 완료: {content.get('title', 'Unknown')}")
            
            # 파일 저장 (카테고리별로 구분)
            filepath = exporter.export_content(content, category_suffix=category_type)
            print(f"    💾 {site} [{category_type}] 파일 저장 완료: {filepath}")
            
            # 데이터베이스에 파일 정보 저장
            if db:
                content_text = content.get('introduction', '') + ' '.join([s.get('content', '') for s in content.get('sections', [])])
                word_count = len(content_text.replace(' ', ''))
                
                file_id = db.add_content_file(
                    site='tistory',
                    title=f"[{category_type.upper()}] {content['title']}",
                    file_path=filepath,
                    file_type="tistory",
                    metadata={
                        'tags': content.get('tags', []),
                        'categories': [content.get('category', topic_info.get('category', 'general'))],
                        'word_count': word_count,
                        'auto_generated': True,
                        'dual_category': True,
                        'category_type': category_type
                    }
                )
                print(f"    💿 {site} [{category_type}] 데이터베이스 저장 완료 (ID: {file_id})")
                
                db.add_system_log(
                    level="INFO",
                    component="auto_publisher",
                    message=f"{site} [{category_type}] Tistory 콘텐츠 생성 성공",
                    details={
                        "site": site,
                        "category_type": category_type,
                        "title": content['title'],
                        "file_id": file_id,
                        "filepath": filepath
                    },
                    site=site
                )
                
            return True
            
        except Exception as e:
            print(f"    ❌ {site} [{category_type}] Tistory 콘텐츠 생성 중 오류: {str(e)}")
            
            if db:
                import traceback
                db.add_system_log(
                    level="ERROR",
                    component="auto_publisher",
                    message=f"{site} [{category_type}] Tistory 콘텐츠 생성 중 예외",
                    details={
                        "site": site,
                        "category_type": category_type,
                        "topic": topic_info.get('topic', ''),
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