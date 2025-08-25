#!/usr/bin/env python3
"""
월간 계획표 자동 생성 시스템 실행 스크립트
Usage:
    python run_monthly_scheduler.py              # 자동 스케줄러 시작
    python run_monthly_scheduler.py --manual     # 수동으로 계획표 생성
    python run_monthly_scheduler.py --test       # 테스트 실행
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.monthly_scheduler import MonthlyScheduler
import logging

def main():
    """메인 실행 함수"""
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    scheduler = MonthlyScheduler()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--manual":
            print("=== 월간 계획표 수동 생성 ===")
            success = scheduler.manual_generate_current_month()
            if success:
                print("✅ 계획표 생성 완료!")
            else:
                print("❌ 계획표 생성 실패!")
                sys.exit(1)
                
        elif command == "--test":
            print("=== 테스트 모드 ===")
            print(f"오늘이 월 마지막 날인가? {scheduler.is_last_day_of_month()}")
            print("테스트 완료!")
            
        elif command == "--help":
            print(__doc__)
            
        else:
            print(f"알 수 없는 명령어: {command}")
            print("사용법: python run_monthly_scheduler.py [--manual|--test|--help]")
            sys.exit(1)
    
    else:
        # 자동 스케줄러 시작
        print("=== 월간 계획표 자동 생성 시스템 시작 ===")
        print("매월 마지막 날 23:00에 다음달 계획표를 자동 생성합니다.")
        print("Ctrl+C로 종료할 수 있습니다.")
        scheduler.run_forever()

if __name__ == "__main__":
    main()