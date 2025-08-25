#!/usr/bin/env python3
"""
매월 말일에 다음달 전체 계획표 자동 생성하는 독립 스크립트
- 매월 말일 23:00에 실행
- 다음달 1일~말일 전체 계획표 생성
"""

import subprocess
import sys
from datetime import datetime, date
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monthly_auto_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_last_day_of_month():
    """오늘이 월의 마지막 날인지 확인"""
    today = date.today()
    tomorrow = today.replace(day=today.day + 1) if today.day < 28 else None
    
    try:
        if tomorrow is None:
            # 28일 이후는 다음 날 계산해서 확인
            next_day = today.replace(month=today.month + 1, day=1) if today.month < 12 else today.replace(year=today.year + 1, month=1, day=1)
            return (next_day - today).days == 1
        else:
            return tomorrow.month != today.month
    except:
        # 다음 월로 넘어가는지 확인
        try:
            tomorrow = today.replace(day=today.day + 1)
            return False
        except ValueError:
            return True

def generate_next_month_full_schedule():
    """다음달 전체 계획표 생성"""
    
    try:
        today = date.today()
        
        # 다음달 계산
        if today.month == 12:
            next_year = today.year + 1
            next_month = 1
        else:
            next_year = today.year
            next_month = today.month + 1
        
        logger.info(f"다음달 전체 계획표 생성 시작: {next_year}년 {next_month}월")
        
        # create_full_monthly_schedule.py 스크립트 경로
        script_path = Path(__file__).parent / "create_single_month_schedule.py"
        
        # 단일 월 계획표 생성 스크립트 생성 (임시)
        create_single_month_script(script_path, next_year, next_month)
        
        # 스크립트 실행
        result = subprocess.run([
            sys.executable, 
            str(script_path)
        ], 
        capture_output=True, 
        text=True,
        input='y\n'  # 자동 승인
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {next_year}년 {next_month}월 전체 계획표 자동 생성 성공")
            logger.info(f"출력: {result.stdout}")
            return True
        else:
            logger.error(f"❌ 계획표 생성 실패: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"💥 계획표 생성 중 예외 발생: {e}")
        return False

def create_single_month_script(script_path, year, month):
    """특정 월만 생성하는 임시 스크립트 생성"""
    
    script_content = f'''#!/usr/bin/env python3
"""
{year}년 {month}월 전체 계획표 생성 (자동 생성)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from create_full_monthly_schedule import create_full_month_schedule, save_full_month_to_db

def main():
    print(f"=== {year}년 {month}월 전체 계획표 자동 생성 ===")
    
    # 계획표 생성
    schedule = create_full_month_schedule({year}, {month})
    print(f"{year}년 {month}월 계획 생성: {{len(schedule)}}개")
    
    # 데이터베이스 저장
    if save_full_month_to_db(schedule, {year}, {month}):
        print(f"✅ {year}년 {month}월 계획표 자동 생성 완료!")
        return True
    else:
        print(f"❌ {year}년 {month}월 계획표 생성 실패")
        return False

if __name__ == "__main__":
    main()
'''
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

def main():
    """메인 실행 함수"""
    
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        # 강제 실행
        logger.info("강제 실행 모드: 다음달 계획표 생성")
        success = generate_next_month_full_schedule()
        if success:
            logger.info("다음달 계획표 생성 성공!")
        else:
            logger.error("다음달 계획표 생성 실패!")
        return success
    
    # 오늘이 월 마지막 날인지 확인
    if is_last_day_of_month():
        logger.info("월의 마지막 날 감지 - 다음달 전체 계획표 자동 생성 시작")
        success = generate_next_month_full_schedule()
        
        if success:
            logger.info("🎉 다음달 전체 계획표 자동 생성 완료!")
        else:
            logger.error("💥 다음달 전체 계획표 생성 실패!")
        
        return success
    else:
        logger.info("오늘은 월의 마지막 날이 아님 - 계획표 생성 건너뜀")
        return True

if __name__ == "__main__":
    main()
'''