#!/usr/bin/env python3
"""
간단한 API 테스트
"""

import requests
import json

def test_api():
    """API 테스트"""
    
    base_url = "http://localhost:5000"
    
    print("=== 간단한 API 테스트 ===")
    
    # 1. 컨텐츠 생성
    print("1. 컨텐츠 생성 테스트...")
    
    payload = {
        'site': 'unpre',
        'topic': 'React Hook 최신 가이드',
        'category': 'programming',
        'content_length': 'medium'
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate_wordpress",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        print(f"응답 상태: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"[SUCCESS] 제목: {result.get('title')}")
            print(f"[SUCCESS] 파일 ID: {result.get('file_id')}")
            print(f"[SUCCESS] 파일 경로: {result.get('filepath')}")
            
            if result.get('file_id'):
                print("\n2. WordPress 발행 테스트...")
                
                publish_payload = {
                    'file_id': result.get('file_id'),
                    'site': 'unpre'
                }
                
                publish_response = requests.post(
                    f"{base_url}/api/publish_to_wordpress",
                    json=publish_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=60
                )
                
                publish_result = publish_response.json()
                
                if publish_result.get('success'):
                    print(f"[SUCCESS] WordPress 발행 성공!")
                    print(f"[SUCCESS] URL: {publish_result.get('url', '알 수 없음')}")
                else:
                    print(f"[FAIL] WordPress 발행 실패: {publish_result.get('error')}")
            else:
                print("[FAIL] file_id가 없어서 발행 테스트 생략")
        else:
            print(f"[FAIL] 컨텐츠 생성 실패: {result.get('error')}")
            
    except Exception as e:
        print(f"[ERROR] 테스트 오류: {e}")

if __name__ == "__main__":
    test_api()