"""
자동 발행 스케줄러 v2 실행 래퍼 스크립트
새벽 3시 자동 발행 및 계획표 기반 주제 선택
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 새로운 자동 발행 스케줄러 v2 실행
from src.auto_publisher_v2 import AutoPublisherV2

if __name__ == "__main__":
    publisher = AutoPublisherV2()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # 즉시 테스트 실행
            print("테스트 실행: 모든 사이트 듀얼 카테고리 발행 시작...")
            publisher.daily_publish_all()
            print("테스트 완료")
        
        elif sys.argv[1] == "once":
            # 즉시 실행 (1회)
            print("즉시 실행: 모든 사이트 듀얼 카테고리 발행 시작...")
            publisher.daily_publish_all()
            print("발행 완료")
        
        elif sys.argv[1] == "schedule":
            # 스케줄러 시작 (새벽 3시 자동 실행)
            print("자동 발행 스케줄러 v2를 시작합니다...")
            print("매일 새벽 3시에 계획표 기반 자동 발행됩니다.")
            print("종료하려면 Ctrl+C를 누르세요.")
            publisher.start()
    
    else:
        # 기본: 스케줄러 시작
        print("🚀 자동 발행 스케줄러 v2를 시작합니다...")
        print("📅 매일 새벽 3시에 계획표 기반으로 모든 사이트에 자동 발행됩니다.")
        print("🎯 대상 사이트: UNPRE, UNTAB, SKEWESE, TISTORY (각 사이트당 2개씩 총 8개 콘텐츠)")
        print("🛑 종료하려면 Ctrl+C를 누르세요.")
        publisher.start()