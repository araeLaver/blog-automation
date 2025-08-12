#!/usr/bin/env python3
"""
웹 API를 통한 직접 발행 테스트
"""

import requests
import json
import time

def test_api_generation_and_publishing():
    """API를 통한 컨텐츠 생성 및 발행 테스트"""
    
    base_url = "http://localhost:5000"
    
    # 테스트 케이스
    test_cases = [
        {
            'site': 'unpre',
            'topic': 'React 18 새로운 기능과 사용법',
            'category': 'programming',
            'content_length': 'medium'
        },
        {
            'site': 'untab', 
            'topic': '2025년 부동산 경매 투자 전략',
            'category': 'realestate',
            'content_length': 'medium'
        },
        {
            'site': 'skewese',
            'topic': '고대 이집트 문명의 놀라운 발견들',
            'category': 'worldhistory', 
            'content_length': 'medium'
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        site = test_case['site']
        print(f"\n=== {site.upper()} 사이트 API 테스트 ===")
        print(f"주제: {test_case['topic']}")
        
        try:
            # 1. 컨텐츠 생성
            print("1. 컨텐츠 생성 API 호출...")
            generate_payload = {
                'site': site,
                'topic': test_case['topic'],
                'category': test_case['category'],
                'content_length': test_case['content_length']
            }
            
            response = requests.post(
                f"{base_url}/api/generate_wordpress",
                json=generate_payload,
                headers={'Content-Type': 'application/json'},
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"[FAIL] 컨텐츠 생성 실패: {response.status_code}")
                print(f"응답: {response.text}")
                results[site] = False
                continue
            
            generate_result = response.json()
            if not generate_result.get('success'):
                print(f"[FAIL] 컨텐츠 생성 실패: {generate_result.get('error')}")
                results[site] = False
                continue
            
            file_path = generate_result.get('file_path') or generate_result.get('filepath')
            title = generate_result.get('title', '제목 없음')
            file_id = generate_result.get('file_id')
            
            print(f"[OK] 컨텐츠 생성 성공: {title}")
            print(f"[OK] 파일 경로: {file_path}")
            print(f"[OK] 파일 ID: {file_id}")
            
            # 2. WordPress 발행 (파일 ID 사용)
            print("2. WordPress 발행 API 호출...")
            
            if not file_id:
                print("[FAIL] 파일 ID가 없습니다")
                results[site] = False
                continue
            
            publish_payload = {
                'file_id': file_id,
                'site': site
            }
            
            response = requests.post(
                f"{base_url}/api/publish_to_wordpress",
                json=publish_payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"[FAIL] WordPress 발행 실패: {response.status_code}")
                print(f"응답: {response.text}")
                results[site] = False
                continue
            
            publish_result = response.json()
            
            if not publish_result.get('success'):
                print(f"[FAIL] WordPress 발행 실패: {publish_result.get('error')}")
                results[site] = False
                continue
            
            url = publish_result.get('url', '알 수 없음')
            print(f"[SUCCESS] WordPress 발행 성공!")
            print(f"[URL] {url}")
            
            results[site] = True
            
        except Exception as e:
            print(f"[ERROR] {site} API 테스트 오류: {e}")
            results[site] = False
        
        # 사이트 간 간격
        time.sleep(3)
    
    # 최종 결과
    print("\n" + "="*60)
    print("=== API 테스트 최종 결과 ===")
    
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    for site, success in results.items():
        status = "[OK] 성공" if success else "[FAIL] 실패"
        print(f"{site.upper()}: {status}")
    
    print(f"\n전체 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("[SUCCESS] 모든 사이트 API 테스트 성공!")
        return True
    else:
        print("[WARN] 일부 사이트에서 문제 발생")
        return False

if __name__ == "__main__":
    test_api_generation_and_publishing()