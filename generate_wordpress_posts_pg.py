"""
WordPress 콘텐츠 생성 및 파일 저장 스크립트 - PostgreSQL 버전
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Windows 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.generators.content_generator import ContentGenerator
from src.generators.image_generator import ImageGenerator
from src.generators.wordpress_content_exporter import WordPressContentExporter
from src.utils.postgresql_database import PostgreSQLDatabase
from dotenv import load_dotenv

load_dotenv()


def generate_wordpress_post(site: str, topic: str = None, save_file: bool = True):
    """WordPress용 포스트 생성 - PostgreSQL 버전"""
    
    print(f"🚀 {site.upper()} WordPress 콘텐츠 생성 시작... (PostgreSQL)")
    
    # 생성기 초기화
    content_generator = ContentGenerator()
    image_generator = ImageGenerator()
    exporter = WordPressContentExporter()
    database = PostgreSQLDatabase()
    
    try:
        # 사이트 설정 조회 (PostgreSQL에서)
        site_configs = database.get_site_configs()
        site_config = site_configs.get(site)
        
        if not site_config:
            # 기본 설정 사용
            default_configs = {
                'unpre': {
                    'name': 'unpre.co.kr',
                    'categories': ['개발', 'IT', '정보처리기사', '언어학습'],
                    'content_style': '전문적이고 실용적인',
                    'target_audience': '개발자, IT전문가'
                },
                'untab': {
                    'name': 'untab.co.kr',
                    'categories': ['부동산', '투자', '경제'],
                    'content_style': '신뢰감 있고 전문적인',
                    'target_audience': '부동산 투자자, 일반인'
                },
                'skewese': {
                    'name': 'skewese.com',
                    'categories': ['역사', '문화', '교육'],
                    'content_style': '교육적이고 흥미로운',
                    'target_audience': '역사 애호가, 학생'
                }
            }
            site_config = {'content_config': default_configs.get(site, default_configs['unpre'])}
        
        content_config = site_config.get('content_config', {})
        
        # content_config에 name 추가 (ContentGenerator에서 필요)
        if 'name' not in content_config:
            content_config['name'] = site_config.get('site_name', f'{site}.co.kr')
        
        # keywords_focus 추가
        if 'keywords_focus' not in content_config:
            content_config['keywords_focus'] = ['SEO', '최적화', '사용자 경험', '성능']
        
        # 1. 주제 선택 또는 자동 선택
        if not topic:
            topic_data = database.get_unused_topic(site)
            if topic_data:
                topic = topic_data["topic"]
                category = topic_data["category"]
                target_keywords = topic_data.get("target_keywords", [])
            else:
                # 기본 주제 사용
                import random
                topic = random.choice([
                    f"{site} 전문 콘텐츠 주제",
                    f"{site} 최신 트렌드 분석",
                    f"{site} 실무 가이드"
                ])
                category = content_config.get('categories', ['일반'])[0]
                target_keywords = []
        else:
            category = content_config.get('categories', ['일반'])[0]
            target_keywords = []
        
        print(f"📝 주제: {topic}")
        print(f"📂 카테고리: {category}")
        
        # 2. 기존 포스트 확인 (중복 방지)
        recent_posts = database.get_recent_posts(site, 10)
        existing_titles = [post["title"] for post in recent_posts]
        
        # 3. 콘텐츠 생성
        print("✍️ AI로 콘텐츠 생성 중...")
        content = content_generator.generate_content(
            site_config=content_config,
            topic=topic,
            category=category,
            existing_posts=existing_titles
        )
        
        # 4. 이미지 생성
        print("🎨 이미지 생성 중...")
        images = image_generator.generate_images_for_post(
            site=site,
            title=content["title"],
            content=content,
            count=3
        )
        
        # 5. 파일로 저장 (선택사항)
        filepath = None
        if save_file:
            print("💾 HTML 파일 생성 중...")
            filepath = exporter.export_content(site, content, images)
            
            # PostgreSQL에 파일 정보 저장
            file_size = Path(filepath).stat().st_size if Path(filepath).exists() else 0
            text_content = exporter._extract_text_content(content)
            
            metadata = {
                'word_count': len(text_content),
                'reading_time': exporter._calculate_reading_time(content),
                'tags': content.get('tags', []),
                'categories': content.get('categories', [content.get('category', '')]),
                'file_size': file_size,
                'content_hash': hash(text_content)
            }
            
            database.add_content_file(
                site=site,
                title=content["title"],
                file_path=filepath,
                file_type="wordpress",
                metadata=metadata
            )
            
            # 시스템 로그 추가
            database.add_system_log(
                level="INFO",
                component="content_generator",
                message=f"WordPress content file created for {site}",
                details={"topic": topic, "file_path": filepath},
                site=site
            )
        
        # 6. 콘텐츠 히스토리에 추가
        database.add_content(
            site=site,
            title=content["title"],
            category=category,
            keywords=content.get('keywords', []),
            content=exporter._extract_text_content(content),
            url=None,  # 아직 발행 전
            meta_description=content.get('meta_description', ''),
            tags=content.get('tags', []),
            word_count=len(exporter._extract_text_content(content)),
            reading_time=exporter._calculate_reading_time(content)
        )
        
        # 7. 결과 출력
        print("\\n" + "="*60)
        print("✅ WordPress 콘텐츠 생성 완료! (PostgreSQL)")
        print("="*60)
        print(f"🌐 사이트: {site}")
        print(f"📋 제목: {content['title']}")
        print(f"📂 카테고리: {category}")
        print(f"🏷️ 태그: {', '.join(content.get('tags', []))}")
        print(f"📊 단어 수: {len(exporter._extract_text_content(content))}자")
        print(f"⏱️ 예상 읽기 시간: {exporter._calculate_reading_time(content)}분")
        
        if filepath:
            print(f"📁 파일 위치: {filepath}")
            print("\\n사용 방법:")
            print("1. 위 HTML 파일을 브라우저에서 열기")
            print("2. 'WordPress용 복사' 버튼 클릭")
            print("3. WordPress 관리자 → 글 → 새 글 추가")
            print("4. HTML 모드로 전환 후 붙여넣기")
        
        print("="*60)
        
        return {
            'success': True,
            'content': content,
            'images': images,
            'filepath': filepath,
            'site': site
        }
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
        # 에러 로그 추가
        try:
            database.add_system_log(
                level="ERROR",
                component="content_generator",
                message=f"WordPress content generation failed for {site}",
                details={"error": str(e)},
                site=site
            )
        except:
            pass
        
        return {
            'success': False,
            'error': str(e),
            'site': site
        }


def generate_multiple_posts(sites: list = None, count: int = 1):
    """여러 사이트/포스트 일괄 생성"""
    if not sites:
        sites = ["unpre", "untab", "skewese"]
    
    print(f"📚 {len(sites)}개 사이트 × {count}개씩 총 {len(sites) * count}개 포스트 생성")
    print("="*60)
    
    results = []
    
    for site in sites:
        print(f"\\n🎯 {site.upper()} 사이트 처리 중...")
        
        for i in range(count):
            print(f"\\n[{i+1}/{count}] 포스트 생성 중...")
            
            result = generate_wordpress_post(site)
            results.append(result)
            
            # API 제한 방지를 위한 대기
            if i < count - 1:
                import time
                print("⏳ API 제한 방지를 위해 5초 대기...")
                time.sleep(5)
    
    # 결과 요약
    print("\\n" + "="*60)
    print("📊 생성 결과 요약")
    print("="*60)
    
    success_count = sum(1 for r in results if r['success'])
    error_count = len(results) - success_count
    
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {error_count}개")
    
    # 사이트별 요약
    site_summary = {}
    for result in results:
        site = result['site']
        if site not in site_summary:
            site_summary[site] = {'success': 0, 'error': 0}
        
        if result['success']:
            site_summary[site]['success'] += 1
        else:
            site_summary[site]['error'] += 1
    
    print("\\n사이트별 결과:")
    for site, stats in site_summary.items():
        print(f"  {site}: 성공 {stats['success']}개, 실패 {stats['error']}개")
    
    if error_count > 0:
        print("\\n❌ 실패한 작업:")
        for result in results:
            if not result['success']:
                print(f"  - {result['site']}: {result['error']}")
    
    return results


def preview_content(site: str, topic: str = None):
    """콘텐츠 미리보기 (파일 저장 없이)"""
    print(f"👀 {site.upper()} 콘텐츠 미리보기...")
    
    result = generate_wordpress_post(site, topic, save_file=False)
    
    if result['success']:
        content = result['content']
        
        print(f"\\n제목: {content['title']}")
        print(f"메타 설명: {content.get('meta_description', '')}")
        print(f"\\n서론:")
        print(f"  {content.get('introduction', '')[:100]}...")
        
        print(f"\\n본문 구조:")
        for i, section in enumerate(content.get('sections', [])[:3]):
            print(f"  {i+1}. {section['heading']}")
        
        print(f"\\n태그: {', '.join(content.get('tags', []))}")
    
    return result


def test_postgresql_connection():
    """PostgreSQL 연결 테스트"""
    print("🔗 PostgreSQL 연결 테스트...")
    
    try:
        database = PostgreSQLDatabase()
        stats = database.get_dashboard_stats()
        
        print("✅ PostgreSQL 연결 성공!")
        print(f"📊 총 포스트: {stats['posts']['total']}")
        print(f"📁 파일: {stats['files']}")
        print(f"💰 수익: {stats['revenue']['total_revenue']}")
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        print("💡 .env 파일의 PG_PASSWORD 설정을 확인하세요.")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WordPress 콘텐츠 생성기 - PostgreSQL")
    parser.add_argument("--site", choices=["unpre", "untab", "skewese"], help="대상 사이트")
    parser.add_argument("--topic", type=str, help="특정 주제 지정")
    parser.add_argument("--count", type=int, default=1, help="생성할 포스트 개수")
    parser.add_argument("--preview", action="store_true", help="미리보기만 (파일 저장 안함)")
    parser.add_argument("--all-sites", action="store_true", help="모든 사이트 대상")
    parser.add_argument("--test-db", action="store_true", help="데이터베이스 연결 테스트")
    
    args = parser.parse_args()
    
    try:
        if args.test_db:
            # 데이터베이스 연결 테스트
            test_postgresql_connection()
            
        elif args.preview:
            # 미리보기 모드
            site = args.site or "unpre"
            preview_content(site, args.topic)
            
        elif args.all_sites:
            # 모든 사이트 대상
            generate_multiple_posts(count=args.count)
            
        elif args.site:
            # 특정 사이트
            if args.count > 1:
                generate_multiple_posts([args.site], args.count)
            else:
                generate_wordpress_post(args.site, args.topic)
        
        else:
            # 인터랙티브 모드
            print("WordPress 콘텐츠 생성기 - PostgreSQL")
            print("="*30)
            print("0. 데이터베이스 연결 테스트")
            print("1. unpre (IT/개발)")
            print("2. untab (부동산)")  
            print("3. skewese (역사)")
            print("4. 모든 사이트")
            
            choice = input("\\n선택 (0-4): ").strip()
            
            if choice == "0":
                test_postgresql_connection()
            elif choice in ["1", "2", "3"]:
                site_map = {"1": "unpre", "2": "untab", "3": "skewese"}
                generate_wordpress_post(site_map[choice])
            elif choice == "4":
                generate_multiple_posts()
            else:
                print("잘못된 선택입니다.")
                
    except KeyboardInterrupt:
        print("\\n👋 작업을 중단합니다.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        print("💡 PostgreSQL 연결 설정을 확인하세요.")