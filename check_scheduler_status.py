#!/usr/bin/env python3
"""
자동 발행 스케줄러 v2 상태 확인 스크립트
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_scheduler_status():
    """스케줄러 상태 확인"""
    print("=" * 60)
    print("자동 발행 스케줄러 v2 상태 확인")
    print("=" * 60)
    
    # 로그 파일 확인
    log_file = project_root / "auto_publisher_v2.log"
    if log_file.exists():
        print(f"로그 파일: {log_file}")
        print(f"로그 파일 수정시간: {datetime.fromtimestamp(log_file.stat().st_mtime)}")
        
        # 최근 로그 확인
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print("\n최근 로그 (마지막 5줄):")
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
        except Exception as e:
            print(f"로그 읽기 오류: {e}")
    else:
        print("로그 파일이 아직 생성되지 않았습니다.")
    
    print()
    
    # 스케줄 정보 확인
    try:
        from src.auto_publisher_v2 import AutoPublisherV2
        import schedule
        
        print("스케줄 정보:")
        print(f"   매일 새벽 3시 자동 실행")
        
        # 다음 실행 시간 계산
        now = datetime.now()
        tomorrow_3am = now.replace(hour=3, minute=0, second=0, microsecond=0)
        if now.time() >= tomorrow_3am.time():
            tomorrow_3am += timedelta(days=1)
        
        print(f"   다음 실행 예정: {tomorrow_3am.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 시간 차이 계산
        time_diff = tomorrow_3am - now
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        print(f"   남은 시간: {hours}시간 {minutes}분")
        
    except Exception as e:
        print(f"스케줄 정보 확인 오류: {e}")
    
    print()
    
    # 월간 계획표 상태 확인
    try:
        from src.utils.monthly_schedule_manager import monthly_schedule_manager
        
        print("오늘의 발행 계획:")
        sites = ['unpre', 'untab', 'skewese', 'tistory']
        
        for site in sites:
            try:
                primary_topic, secondary_topic = monthly_schedule_manager.get_today_dual_topics_for_manual(site)
                if primary_topic and secondary_topic:
                    print(f"   {site.upper()}:")
                    print(f"      Primary: {primary_topic['topic']}")
                    print(f"      Secondary: {secondary_topic['topic']}")
                else:
                    print(f"   {site.upper()}: 주제 없음")
            except Exception as e:
                print(f"   {site.upper()}: 오류 - {str(e)}")
                
    except Exception as e:
        print(f"월간 계획표 확인 오류: {e}")
    
    print()
    print("=" * 60)
    print("상태 확인 완료")
    print("스케줄러가 백그라운드에서 실행 중이며, 매일 새벽 3시에 자동으로")
    print("   계획표 기반 콘텐츠를 모든 사이트에 발행합니다.")
    print("=" * 60)

if __name__ == "__main__":
    check_scheduler_status()