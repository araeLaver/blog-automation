#!/usr/bin/env python3
"""
월별 계획표 확인 도구
"""

from src.utils.monthly_schedule_manager import monthly_schedule_manager
from datetime import date

def check_monthly_schedule():
    """월별 계획표 확인"""
    
    today = date.today()
    
    print(f"=== {today.year}년 {today.month}월 발행 계획표 확인 ===")
    
    # 이번 달 전체 스케줄 조회
    schedule = monthly_schedule_manager.get_month_schedule(today.year, today.month)
    
    if not schedule:
        print("스케줄이 없습니다.")
        return
    
    for day in sorted(schedule.keys()):
        if day < today.day:
            continue  # 지난 날짜는 건너뛰기
            
        day_date = date(today.year, today.month, day)
        day_names = ['월', '화', '수', '목', '금', '토', '일']
        weekday = day_date.weekday()
        
        print(f"\n날짜: {today.month:02d}/{day:02d}({day_names[weekday]}):")
        
        sites = schedule[day]
        for site in sorted(sites.keys()):
            topics = sites[site]
            print(f"  {site.upper()}:")
            for topic in topics:
                status_icon = "[완료]" if topic['status'] == 'published' else "[계획]"
                print(f"    {status_icon} [{topic['category']}] {topic['topic']}")
    
    # 오늘 주제 상세 확인
    print(f"\n=== 오늘({today.month:02d}/{today.day:02d}) 듀얼 카테고리 주제 ===")
    
    sites = ['unpre', 'untab', 'skewese', 'tistory']
    for site in sites:
        print(f"\n사이트 {site.upper()}:")
        primary, secondary = monthly_schedule_manager.get_today_dual_topics(site)
        
        if primary:
            print(f"  Primary: [{primary['category']}] {primary['topic']}")
            print(f"           Keywords: {', '.join(primary['keywords'])}")
        
        if secondary:
            print(f"  Secondary: [{secondary['category']}] {secondary['topic']}")
            print(f"             Keywords: {', '.join(secondary['keywords'])}")
        
        if not primary and not secondary:
            print("  주제가 설정되지 않았습니다.")

if __name__ == "__main__":
    check_monthly_schedule()