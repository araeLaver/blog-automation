#!/usr/bin/env python3
"""
WordPress 실제 발행 테스트 스크립트
- 테스트 콘텐츠를 생성하여 실제 WordPress 사이트에 발행
- 전체 발행 프로세스의 각 단계별 성공/실패 확인
"""

import sys
from pathlib import Path

# 프로젝트 루트를 시스템 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.publishers.wordpress_publisher import WordPressPublisher
from src.generators.content_generator import ContentGenerator
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_content():
    """테스트용 콘텐츠 생성"""
    return {
        'title': '🧪 WordPress 발행 테스트 - 자동 생성 콘텐츠',
        'meta_description': 'WordPress REST API를 통한 자동 발행 기능을 테스트하는 글입니다.',
        'introduction': '이 글은 블로그 자동화 시스템의 WordPress 발행 기능을 테스트하기 위해 생성된 콘텐츠입니다.',
        'sections': [
            {
                'heading': '테스트 섹션 1 - 기본 기능 확인',
                'content': '''이 섹션에서는 WordPress REST API를 통한 기본적인 포스트 발행 기능을 테스트합니다.

**주요 테스트 항목:**
- 제목과 본문 내용 전송
- HTML 포맷팅 처리
- 메타데이터 설정

이 테스트가 성공하면 기본적인 발행 파이프라인이 정상 작동하는 것입니다.'''
            },
            {
                'heading': '테스트 섹션 2 - 고급 기능 확인', 
                'content': '''이 섹션에서는 고급 기능들을 테스트합니다.

**고급 기능 목록:**
- 카테고리 자동 생성 및 설정
- 태그 자동 생성 및 설정  
- 발행 상태 관리
- SEO 메타데이터 처리

모든 기능이 정상 작동하면 완전한 자동 발행 시스템이 구축된 것입니다.'''
            }
        ],
        'additional_content': '''테스트가 완료되었습니다. 이 포스트가 WordPress 사이트에 정상적으로 게시되었다면 자동 발행 시스템이 올바르게 작동하고 있는 것입니다.

🎉 **테스트 성공 조건:**
- 포스트가 WordPress 관리자에서 확인 가능
- 모든 섹션이 올바르게 포맷팅됨
- 카테고리와 태그가 자동으로 설정됨''',
        'tags': ['테스트', '자동발행', 'WordPress', 'REST API'],
        'categories': ['기술', '테스트'],
        'keywords': ['WordPress', '자동발행', 'REST API']
    }

def test_wordpress_publish(site_name):
    """특정 사이트에 테스트 발행"""
    
    print(f"\n🚀 {site_name.upper()} 사이트 실제 발행 테스트 시작...")
    
    try:
        # 1. WordPress Publisher 초기화
        print("1. 📡 WordPress Publisher 초기화...")
        publisher = WordPressPublisher(site_name)
        
        # 2. 연결 테스트
        print("2. 🔗 연결 테스트...")
        if not publisher.test_connection():
            print("   ❌ 연결 실패")
            return False
        
        # 3. 테스트 콘텐츠 생성
        print("3. 📝 테스트 콘텐츠 생성...")
        test_content = create_test_content()
        print(f"   ✅ 테스트 콘텐츠 준비됨 (제목: {test_content['title']})")
        
        # 4. 실제 발행 시도
        print("4. 🚀 실제 WordPress 사이트에 발행...")
        success, result = publisher.publish_post(test_content, draft=True)  # 초안으로 발행
        
        if success:
            print(f"   ✅ 발행 성공!")
            print(f"   🔗 WordPress URL: {result}")
            return True
        else:
            print(f"   ❌ 발행 실패: {result}")
            return False
            
    except Exception as e:
        print(f"   💥 테스트 중 예외 발생: {e}")
        import traceback
        print(f"   📄 상세 오류:\n{traceback.format_exc()}")
        return False

def main():
    """메인 테스트 함수"""
    
    print("🧪 WordPress 실제 발행 테스트를 시작합니다...")
    print("각 사이트에 테스트 포스트를 초안으로 발행하여 전체 파이프라인을 검증합니다.")
    
    sites = ['unpre', 'untab', 'skewese']
    results = {}
    
    for site in sites:
        results[site] = test_wordpress_publish(site)
        print()  # 사이트 간 구분을 위한 빈 줄
    
    # 결과 요약
    print("=" * 70)
    print("📊 WordPress 실제 발행 테스트 결과 요약")
    print("=" * 70)
    
    success_count = 0
    for site, success in results.items():
        status_icon = "✅" if success else "❌"
        status_text = "발행 성공" if success else "발행 실패"
        print(f"{status_icon} {site.upper()}: {status_text}")
        if success:
            success_count += 1
    
    print(f"\n📈 성공률: {success_count}/{len(sites)} ({int(success_count/len(sites)*100)}%)")
    
    if success_count == len(sites):
        print("\n🎉 모든 사이트 발행 테스트 성공!")
        print("실제 수동 발행 기능이 완전히 작동합니다!")
    elif success_count > 0:
        print(f"\n⚠️ {len(sites) - success_count}개 사이트에서 발행 실패")
        print("성공한 사이트는 정상 작동하지만, 실패한 사이트의 설정을 확인하세요.")
    else:
        print("\n❌ 모든 사이트에서 발행 실패")
        print("WordPress Publisher 코드나 설정에 문제가 있을 수 있습니다.")
    
    print(f"\n💡 참고: 테스트 포스트는 '초안' 상태로 발행되므로")
    print("WordPress 관리자 > 포스트에서 확인할 수 있습니다.")
    
    return results

if __name__ == "__main__":
    try:
        test_results = main()
        
        # 실패한 사이트가 있으면 종료 코드 1
        failed_sites = [site for site, success in test_results.items() if not success]
        if failed_sites:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 테스트 중 오류 발생: {e}")
        sys.exit(1)