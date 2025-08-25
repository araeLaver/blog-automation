#!/usr/bin/env python3
"""
월별 계획표 자동 생성 시스템 실행기
- 매일 23:00에 체크해서 월 마지막 날이면 다음달 계획표 생성
- 또는 매월 말일 23:00에 cron으로 실행 가능
"""

import schedule
import time
import logging
from datetime import datetime
from auto_generate_next_month import main as generate_next_month

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scheduled_generation():
    """스케줄된 생성 실행"""
    logger.info("월별 계획표 자동 생성 체크 시작")
    generate_next_month()

def run_scheduler():
    """스케줄러 실행"""
    
    # 매일 23:00에 체크
    schedule.every().day.at("23:00").do(scheduled_generation)
    
    logger.info("월별 계획표 자동 생성 스케줄러 시작")
    logger.info("매일 23:00에 월 마지막 날 체크 후 다음달 계획표 생성")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            logger.info("스케줄러 종료")
            break
        except Exception as e:
            logger.error(f"스케줄러 오류: {e}")
            time.sleep(300)  # 오류 시 5분 대기

def manual_generation():
    """수동 생성 (테스트용)"""
    logger.info("수동 다음달 계획표 생성")
    from auto_generate_next_month import generate_next_month_full_schedule
    return generate_next_month_full_schedule()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--manual":
            # 수동 실행
            success = manual_generation()
            if success:
                print("다음달 계획표 수동 생성 완료!")
            else:
                print("다음달 계획표 생성 실패!")
                sys.exit(1)
        elif sys.argv[1] == "--test":
            # 테스트 실행
            from auto_generate_next_month import is_last_day_of_month
            print(f"오늘이 월 마지막 날인가? {is_last_day_of_month()}")
        else:
            print("사용법: python run_monthly_auto_generator.py [--manual|--test]")
    else:
        # 스케줄러 시작
        run_scheduler()