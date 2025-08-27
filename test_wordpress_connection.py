#!/usr/bin/env python3
"""
WordPress 연결 테스트 스크립트
각 사이트의 WordPress REST API 연결 상태를 확인합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 시스템 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.publishers.wordpress_publisher import WordPressPublisher
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wordpress_sites():
    """모든 WordPress 사이트 연결 테스트"""
    
    sites = ['unpre', 'untab', 'skewese']
    results = {}
    
    print("🔗 WordPress REST API 연결 테스트 시작...\n")
    
    for site in sites:
        print(f"📡 {site.upper()} 사이트 테스트 중...")
        
        try:
            publisher = WordPressPublisher(site)
            is_connected = publisher.test_connection()
            
            if is_connected:
                print(f"✅ {site.upper()}: 연결 성공!")
                results[site] = "성공"
            else:
                print(f"❌ {site.upper()}: 연결 실패!")
                results[site] = "실패"
                
        except Exception as e:
            print(f"❌ {site.upper()}: 오류 - {e}")
            results[site] = f"오류: {e}"
        
        print()
    
    # 결과 요약
    print("=" * 50)
    print("📊 WordPress 연결 테스트 결과 요약:")
    print("=" * 50)
    
    success_count = 0
    for site, result in results.items():
        status_icon = "✅" if result == "성공" else "❌"
        print(f"{status_icon} {site.upper()}: {result}")
        if result == "성공":
            success_count += 1
    
    print(f"\n📈 성공률: {success_count}/{len(sites)} ({int(success_count/len(sites)*100)}%)")
    
    if success_count == len(sites):
        print("\n🎉 모든 사이트 연결이 정상입니다!")
        print("이제 수동 발행 시 실제 WordPress 사이트로 업로드가 가능합니다.")
    else:
        print(f"\n⚠️  {len(sites) - success_count}개 사이트에 연결 문제가 있습니다.")
        print("WordPress 사이트 설정을 확인하세요:")
        print("1. WordPress REST API가 활성화되어 있는지 확인")
        print("2. Application Password가 올바르게 설정되어 있는지 확인")
        print("3. 사이트 URL이 올바른지 확인")
    
    return results

if __name__ == "__main__":
    test_results = test_wordpress_sites()
    
    # 연결 실패한 사이트가 있으면 종료 코드 1로 종료
    failed_sites = [site for site, result in test_results.items() if result != "성공"]
    if failed_sites:
        sys.exit(1)
    else:
        print("\n✅ 모든 테스트가 완료되었습니다.")
        sys.exit(0)