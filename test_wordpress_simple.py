"""
WordPress 간단 테스트 - API 연결 확인 및 테스트 포스트 발행
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Windows 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

def test_wordpress_connection():
    """WordPress 연결 테스트"""
    from src.publishers.wordpress_publisher import WordPressPublisher
    
    print("=" * 60)
    print("WordPress API 연결 테스트")
    print("=" * 60)
    
    sites = ["unpre", "untab", "skewese"]
    results = {}
    
    for site in sites:
        try:
            print(f"\n{site.upper()} 테스트 중...")
            publisher = WordPressPublisher(site)
            
            # 연결 테스트
            if publisher.test_connection():
                print(f"✓ {site}.co.kr 연결 성공!")
                
                # 최근 포스트 조회
                recent_posts = publisher.get_recent_posts(3)
                print(f"  최근 포스트 {len(recent_posts)}개:")
                for post in recent_posts:
                    print(f"    - {post['title'][:50]}...")
                
                results[site] = True
            else:
                print(f"✗ {site}.co.kr 연결 실패")
                results[site] = False
                
        except Exception as e:
            print(f"✗ {site}.co.kr 오류: {e}")
            results[site] = False
    
    print("\n" + "=" * 60)
    print("연결 테스트 결과:")
    for site, success in results.items():
        status = "성공" if success else "실패"
        print(f"  {site}: {status}")
    print("=" * 60)
    
    return results


def create_test_post(site: str = "unpre"):
    """테스트 포스트 생성"""
    from src.publishers.wordpress_publisher import WordPressPublisher
    
    print(f"\n{site.upper()}에 테스트 포스트 생성 중...")
    
    try:
        publisher = WordPressPublisher(site)
        
        # 테스트 콘텐츠
        test_content = {
            "title": "자동화 테스트 포스트 - 삭제 가능",
            "meta_description": "이것은 자동화 시스템 테스트용 포스트입니다.",
            "introduction": "이 포스트는 블로그 자동화 시스템의 테스트를 위해 생성되었습니다.",
            "sections": [
                {
                    "heading": "테스트 섹션 1",
                    "content": "WordPress REST API를 통한 자동 발행 테스트입니다."
                },
                {
                    "heading": "테스트 섹션 2",
                    "content": "카테고리, 태그, 이미지 등 모든 기능이 정상 작동하는지 확인합니다."
                }
            ],
            "conclusion": "테스트가 완료되었습니다. 이 포스트는 삭제하셔도 됩니다.",
            "tags": ["테스트", "자동화"],
            "categories": ["테스트"]
        }
        
        # 초안으로 발행
        success, result = publisher.publish_post(test_content, draft=True)
        
        if success:
            print(f"✓ 테스트 포스트 생성 성공!")
            print(f"  URL: {result}")
            print(f"  상태: 초안 (비공개)")
            print(f"  관리자 페이지에서 확인 가능")
        else:
            print(f"✗ 테스트 포스트 생성 실패: {result}")
        
        return success
        
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        return False


if __name__ == "__main__":
    # 1. 연결 테스트
    results = test_wordpress_connection()
    
    # 2. 모든 사이트가 연결되었으면 테스트 포스트 생성
    if all(results.values()):
        print("\n모든 사이트 연결 성공! 테스트 포스트를 생성하시겠습니까?")
        print("(초안으로 저장되므로 공개되지 않습니다)")
        
        choice = input("\n사이트 선택 (unpre/untab/skewese) 또는 엔터(건너뛰기): ").strip().lower()
        
        if choice in ["unpre", "untab", "skewese"]:
            create_test_post(choice)
    else:
        print("\n일부 사이트 연결 실패. .env 파일의 설정을 확인하세요.")