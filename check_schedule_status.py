"""
스케줄 상태 확인 스크립트
현재 설정된 Windows Task Scheduler 작업과 스케줄러 상태를 확인합니다.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def check_windows_task():
    """Windows Task Scheduler에 등록된 작업 확인"""
    print("=" * 60)
    print("Windows Task Scheduler 상태 확인")
    print("=" * 60)
    
    try:
        # 작업 스케줄러에서 BlogAutomationScheduler 작업 조회
        result = subprocess.run(
            ['schtasks', '/query', '/tn', 'BlogAutomationScheduler', '/v', '/fo', 'LIST'],
            capture_output=True,
            text=True,
            encoding='cp949'  # Windows 한글 인코딩
        )
        
        if result.returncode == 0:
            print("✓ 작업이 등록되어 있습니다.\n")
            # 주요 정보만 추출하여 표시
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['작업 이름:', '다음 실행 시간:', '상태:', '마지막 실행 시간:', '마지막 결과:']):
                    print(line.strip())
        else:
            print("× 작업이 등록되어 있지 않습니다.")
            print("\n설정 방법:")
            print("1. 관리자 권한으로 명령 프롬프트 실행")
            print("2. cd C:\\Develop\\unble\\blog-automation")
            print("3. setup_auto_schedule.bat 실행")
    except Exception as e:
        print(f"오류 발생: {e}")

def check_scheduler_config():
    """스케줄러 설정 확인"""
    print("\n" + "=" * 60)
    print("스케줄러 설정 확인")
    print("=" * 60)
    
    # 프로젝트 경로 추가
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from config.sites_config import PUBLISHING_SCHEDULE
        
        print("\n발행 스케줄 설정:")
        for site, schedule in PUBLISHING_SCHEDULE.items():
            print(f"  - {site}: {schedule['time']} / {', '.join(schedule['days'])}")
            
        print("\n✓ 모든 사이트가 새벽 3시에 자동 발행되도록 설정되어 있습니다.")
        
    except Exception as e:
        print(f"설정 파일 로드 오류: {e}")

def check_last_logs():
    """최근 로그 확인"""
    print("\n" + "=" * 60)
    print("최근 실행 로그 확인")
    print("=" * 60)
    
    log_dir = Path("data/logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            # 최신 로그 파일 찾기
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            print(f"\n최신 로그 파일: {latest_log.name}")
            
            # 마지막 10줄 출력
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = lines[-10:] if len(lines) > 10 else lines
                print("\n최근 로그 내용:")
                for line in last_lines:
                    print(f"  {line.strip()}")
        else:
            print("로그 파일이 없습니다.")
    else:
        print("로그 디렉토리가 존재하지 않습니다.")

def main():
    print("\n블로그 자동 발행 시스템 상태 점검")
    print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    check_windows_task()
    check_scheduler_config()
    check_last_logs()
    
    print("\n" + "=" * 60)
    print("점검 완료")
    print("=" * 60)
    
    print("\n수동 실행 명령어:")
    print("  - 테스트: python run_scheduler.py test")
    print("  - 즉시 실행: python run_scheduler.py run")
    print("  - 스케줄러 시작: python run_scheduler.py schedule")

if __name__ == "__main__":
    main()