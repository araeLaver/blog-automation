"""
자동 월간 계획표 생성 시스템
- 매월 마지막 날에 다음달 계획표 자동 생성
- 스케줄러에서 호출하여 사용
"""

import schedule
import time
from datetime import datetime, timedelta
import subprocess
import sys
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonthlyScheduler:
    """월간 계획표 자동 생성 시스템"""
    
    def __init__(self):
        self.script_path = Path(__file__).parent.parent.parent / "create_monthly_schedule.py"
        self.setup_schedule()
    
    def setup_schedule(self):
        """스케줄 설정 - 매월 마지막 날 23:00에 실행"""
        schedule.every().day.at("23:00").do(self.check_and_generate_monthly)
        logger.info("월간 계획표 자동 생성 스케줄 설정 완료 - 매월 마지막 날 23:00")
    
    def is_last_day_of_month(self):
        """오늘이 월의 마지막 날인지 확인"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        return today.month != tomorrow.month
    
    def check_and_generate_monthly(self):
        """월 마지막 날 체크 후 다음달 계획표 생성"""
        if self.is_last_day_of_month():
            logger.info("월의 마지막 날 감지 - 다음달 계획표 생성 시작")
            self.generate_next_month_schedule()
        else:
            logger.debug("월의 마지막 날이 아님 - 계획표 생성 건너뜀")
    
    def generate_next_month_schedule(self):
        """다음달 계획표 생성 실행"""
        try:
            today = datetime.now()
            
            # 다음달 계산
            if today.month == 12:
                next_year = today.year + 1
                next_month = 1
            else:
                next_year = today.year
                next_month = today.month + 1
            
            logger.info(f"{next_year}년 {next_month}월 계획표 자동 생성 시작")
            
            # 스크립트 실행
            result = subprocess.run([
                sys.executable, 
                str(self.script_path)
            ], 
            capture_output=True, 
            text=True, 
            input='y\n'  # 데이터베이스 저장 승인
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {next_year}년 {next_month}월 계획표 생성 완료")
                logger.info(f"출력: {result.stdout}")
                
                # 성공 로그를 데이터베이스에도 기록
                self._log_to_database("SUCCESS", f"{next_year}년 {next_month}월 계획표 자동 생성 성공")
                
            else:
                logger.error(f"❌ 계획표 생성 실패: {result.stderr}")
                self._log_to_database("ERROR", f"계획표 생성 실패: {result.stderr}")
                
        except Exception as e:
            logger.error(f"💥 계획표 생성 중 예외 발생: {e}")
            self._log_to_database("ERROR", f"계획표 생성 예외: {str(e)}")
    
    def _log_to_database(self, level, message):
        """데이터베이스에 로그 기록"""
        try:
            from ..web_dashboard_pg import get_database
            db = get_database()
            db.add_system_log(
                level=level,
                component="monthly_scheduler",
                message=message,
                details={
                    "timestamp": datetime.now().isoformat(),
                    "type": "monthly_schedule_generation"
                }
            )
        except Exception as e:
            logger.error(f"데이터베이스 로그 기록 실패: {e}")
    
    def run_forever(self):
        """스케줄러 계속 실행"""
        logger.info("월간 계획표 자동 생성 시스템 시작")
        logger.info("매월 마지막 날 23:00에 다음달 계획표 자동 생성")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except KeyboardInterrupt:
                logger.info("월간 스케줄러 종료")
                break
            except Exception as e:
                logger.error(f"스케줄러 오류: {e}")
                time.sleep(300)  # 오류 시 5분 대기
    
    def manual_generate_current_month(self):
        """현재 월 계획표 수동 생성 (테스트용)"""
        logger.info("현재 월 계획표 수동 생성 시작")
        
        try:
            result = subprocess.run([
                sys.executable, 
                str(self.script_path)
            ], 
            capture_output=True, 
            text=True,
            input='y\n'
            )
            
            if result.returncode == 0:
                logger.info("✅ 현재 월 계획표 수동 생성 완료")
                print(result.stdout)
                return True
            else:
                logger.error(f"❌ 계획표 생성 실패: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"💥 수동 생성 중 예외 발생: {e}")
            return False

# 독립 실행용
if __name__ == "__main__":
    scheduler = MonthlyScheduler()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        # 수동 실행
        scheduler.manual_generate_current_month()
    else:
        # 자동 스케줄러 실행
        scheduler.run_forever()