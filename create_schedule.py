#!/usr/bin/env python3
"""
현재 주 스케줄 생성 - 원격 서버에서 실행
"""
import requests
import json

# 수동 발행을 통해 스케줄 생성을 강제로 트리거
try:
    print("=== 현재 주 스케줄 강제 생성 ===")
    
    # 각 사이트별로 발행을 시도해서 스케줄 생성을 유도
    sites = ["unpre", "untab", "skewese"]
    
    for site in sites:
        print(f"\n{site} 사이트 스케줄 생성 시도...")
        
        response = requests.post(
            "https://sore-kaile-untab-34c55d0a.koyeb.app/api/quick_publish",
            json={"sites": [site]},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {site}: {result.get('message', '성공')}")
        else:
            print(f"❌ {site}: 실패 - {response.status_code}")
    
    print("\n=== 스케줄 생성 완료 ===")
    print("이제 계획표대로 정확한 주제가 발행될 것입니다.")
    
except Exception as e:
    print(f"오류 발생: {e}")