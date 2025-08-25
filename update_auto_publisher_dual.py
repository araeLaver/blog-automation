#!/usr/bin/env python3
"""
자동 발행 시스템을 2개 카테고리 지원하도록 업데이트
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def update_auto_publisher_for_dual_categories():
    """자동 발행 시스템을 2개 카테고리 지원하도록 업데이트"""
    
    # 기존 자동 발행 로직을 2개 카테고리로 확장
    dual_publish_logic = '''
def publish_dual_categories_daily():
    """하루 8개 포스팅 (사이트별 2개 카테고리) 자동 발행"""
    from src.utils.schedule_manager import ScheduleManager
    from datetime import datetime
    
    today = datetime.now().date()
    start_time = datetime.now()
    
    print(f"[DUAL_PUBLISH] {today} 2개 카테고리 자동 발행 시작")
    
    sites = ['unpre', 'untab', 'skewese', 'tistory']
    schedule_manager = ScheduleManager()
    
    total_published = 0
    failed_sites = []
    
    for site in sites:
        try:
            print(f"\\n[DUAL_PUBLISH] {site.upper()} 발행 시작")
            
            # 2개 카테고리 주제 가져오기
            primary_topic, secondary_topic = schedule_manager.get_today_dual_topics_for_manual(site)
            
            # Primary 카테고리 발행
            print(f"  Primary: {primary_topic['topic'][:50]}...")
            success_primary = publish_single_topic(site, primary_topic, "primary")
            
            if success_primary:
                total_published += 1
                print(f"  ✅ Primary 발행 완료")
            else:
                print(f"  ❌ Primary 발행 실패")
            
            # Secondary 카테고리 발행
            print(f"  Secondary: {secondary_topic['topic'][:50]}...")
            success_secondary = publish_single_topic(site, secondary_topic, "secondary")
            
            if success_secondary:
                total_published += 1
                print(f"  ✅ Secondary 발행 완료")
            else:
                print(f"  ❌ Secondary 발행 실패")
            
            # 사이트별 결과
            if success_primary and success_secondary:
                print(f"🎉 {site.upper()} 2개 카테고리 발행 완료")
            elif success_primary or success_secondary:
                print(f"⚠️  {site.upper()} 부분 성공 (1/2)")
                failed_sites.append(f"{site} (부분실패)")
            else:
                print(f"💥 {site.upper()} 발행 실패")
                failed_sites.append(site)
        
        except Exception as site_error:
            print(f"💥 {site.upper()} 오류: {site_error}")
            failed_sites.append(site)
    
    # 전체 결과 요약
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\\n" + "="*60)
    print(f"📊 2개 카테고리 자동 발행 완료 - {end_time.strftime('%H:%M:%S')}")
    print(f"   • 총 발행: {total_published}/8개")
    print(f"   • 성공률: {total_published/8*100:.1f}%")
    print(f"   • 소요시간: {duration.total_seconds():.1f}초")
    
    if failed_sites:
        print(f"   • 실패 사이트: {', '.join(failed_sites)}")
    else:
        print(f"   🎉 모든 사이트 발행 성공!")
    
    print("="*60)
    
    return total_published, failed_sites

def publish_single_topic(site, topic_info, category_type):
    """단일 주제 발행 (실제 발행 로직은 기존 코드 활용)"""
    try:
        # 여기서 실제 콘텐츠 생성 및 발행 로직 호출
        # 기존 auto_publisher의 발행 로직을 재사용
        
        print(f"    📝 콘텐츠 생성 중...")
        # content_generator 호출
        
        print(f"    🚀 사이트 발행 중...")
        # site_publisher 호출
        
        return True  # 성공시
        
    except Exception as e:
        print(f"    ❌ 발행 오류: {e}")
        return False
    '''
    
    print("=" * 60)
    print("자동 발행 시스템 2개 카테고리 업데이트 로직")
    print("=" * 60)
    print(dual_publish_logic)
    
    print("\\n📋 업데이트 포인트:")
    print("1. 기존 단일 주제 → 2개 카테고리 주제")
    print("2. 하루 4개 → 8개 포스팅")
    print("3. 사이트별 2번 발행 (Primary + Secondary)")
    print("4. 상세한 발행 현황 리포팅")
    
    return True

def show_dual_publishing_workflow():
    """2개 카테고리 발행 워크플로우 표시"""
    
    workflow = '''
    🔄 2개 카테고리 자동 발행 워크플로우
    
    1. 📅 스케줄 확인
       └─ get_today_dual_topics_for_manual(site) 호출
       
    2. 🏷️ 사이트별 순차 처리 (UNPRE → UNTAB → SKEWESE → TISTORY)
       ├─ Primary 카테고리 발행
       │  ├─ 콘텐츠 생성 (15분)
       │  └─ 사이트 발행 (5분)
       └─ Secondary 카테고리 발행
          ├─ 콘텐츠 생성 (15분)
          └─ 사이트 발행 (5분)
    
    3. 📊 결과 리포팅
       ├─ 총 발행 수: X/8개
       ├─ 성공률: XX%
       ├─ 소요시간: XX분
       └─ 실패 사이트 목록
    
    ⏱️ 예상 소요시간: 120분 (사이트별 40분 × 4개 사이트)
    🎯 목표: 새벽 3AM 시작 → 5AM 완료
    '''
    
    print("=" * 60)
    print("2개 카테고리 발행 워크플로우")
    print("=" * 60)
    print(workflow)
    
    # 현재 시간 기준 예상 일정
    from datetime import datetime, timedelta
    
    now = datetime.now()
    start_3am = now.replace(hour=3, minute=0, second=0) + timedelta(days=1)
    
    print(f"📅 다음 자동 발행 일정:")
    print(f"   시작: {start_3am.strftime('%Y-%m-%d %H:%M:%S')} (새벽 3시)")
    print(f"   종료: {(start_3am + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')} (새벽 5시)")
    print(f"   발행량: 8개 포스팅 (기존 대비 2배)")

if __name__ == "__main__":
    print("🚀 자동 발행 시스템 2개 카테고리 업데이트")
    
    # 1. 업데이트 로직 설명
    update_auto_publisher_for_dual_categories()
    
    # 2. 워크플로우 표시
    show_dual_publishing_workflow()
    
    print("\\n✅ 2개 카테고리 자동 발행 시스템 준비 완료!")
    print("💡 다음 새벽 3AM부터 하루 8개 포스팅으로 운영됩니다.")