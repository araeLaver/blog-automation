"""
스케줄러 실행 래퍼 스크립트
프로젝트 경로를 sys.path에 추가하여 import 오류 해결
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 이제 scheduler를 실행
from src.scheduler import BlogAutomationScheduler

if __name__ == "__main__":
    scheduler = BlogAutomationScheduler()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # 연결 테스트
            results = scheduler.test_connection()
            print(f"Connection test results: {results}")
        
        elif sys.argv[1] == "run":
            # 즉시 실행
            site = sys.argv[2] if len(sys.argv) > 2 else None
            results = scheduler.run_once(site)
            print(f"Execution results: {results}")
        
        elif sys.argv[1] == "schedule":
            # 스케줄러 시작
            scheduler.start()
    
    else:
        # 기본: 스케줄러 시작
        print("자동 발행 스케줄러를 시작합니다...")
        print("새벽 3시에 자동으로 발행됩니다.")
        print("종료하려면 Ctrl+C를 누르세요.")
        scheduler.start()