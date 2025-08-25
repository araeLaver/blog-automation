#!/usr/bin/env python3
"""
2개 카테고리 발행 시스템 테스트 스크립트
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.utils.trending_topic_manager import TrendingTopicManager
from src.utils.schedule_manager import ScheduleManager

def test_trending_topic_manager():
    """트렌딩 주제 매니저 테스트"""
    print("=" * 60)
    print("트렌딩 주제 매니저 테스트")
    print("=" * 60)
    
    manager = TrendingTopicManager()
    
    # 오늘과 내일의 주제 확인
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    sites = ['unpre', 'untab', 'skewese', 'tistory']
    
    for date in [today, tomorrow]:
        print(f"\n📅 {date} ({['월','화','수','목','금','토','일'][date.weekday()]}요일)")
        print("-" * 50)
        
        for site in sites:
            try:
                primary, secondary = manager.get_daily_topics(site, date)
                print(f"{site.upper():8s}")
                print(f"  Primary  : {primary['topic'][:60]}...")
                print(f"           ({primary['category']})")
                print(f"  Secondary: {secondary['topic'][:60]}...")
                print(f"           ({secondary['category']})")
                print()
            except Exception as e:
                print(f"{site.upper():8s}: ERROR - {e}")

def test_dual_category_schedule():
    """2개 카테고리 스케줄 생성 테스트"""
    print("=" * 60)
    print("2개 카테고리 스케줄 생성 테스트")
    print("=" * 60)
    
    try:
        # 로컬에서는 DB 연결이 안되므로 API 방식으로 테스트
        import requests
        
        # 현재 주 2개 카테고리 스케줄 생성 API 호출
        api_url = "https://sore-kaile-untab-34c55d0a.koyeb.app/api/create_dual_category_schedule"
        
        response = requests.post(api_url, json={
            "week_start": "2025-08-25"
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API 호출 성공: {result.get('message', '')}")
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API 테스트 오류: {e}")

def test_topic_addition():
    """트렌디한 주제 추가 테스트"""
    print("=" * 60)
    print("트렌디한 주제 추가 테스트")
    print("=" * 60)
    
    manager = TrendingTopicManager()
    
    # 새로운 트렌디한 주제 추가
    new_topics = [
        {
            "site": "unpre",
            "category": "기술/디지털",
            "topic": "Claude 3.5 Sonnet vs GPT-4o 성능 비교",
            "keywords": ["Claude", "GPT-4o", "AI비교"]
        },
        {
            "site": "untab", 
            "category": "재정/투자",
            "topic": "2025년 금리 인하 전망과 부동산 시장",
            "keywords": ["금리인하", "부동산", "2025년"]
        },
        {
            "site": "skewese",
            "category": "건강/웰니스", 
            "topic": "겨울철 비타민D 부족 해결법",
            "keywords": ["비타민D", "겨울", "건강"]
        },
        {
            "site": "tistory",
            "category": "트렌드/이슈",
            "topic": "2024년 K-콘텐츠 해외 수출 성과 분석",
            "keywords": ["K콘텐츠", "수출", "한류"]
        }
    ]
    
    for topic_data in new_topics:
        success = manager.add_trending_topic(
            topic_data["site"],
            topic_data["category"], 
            topic_data["topic"],
            topic_data["keywords"]
        )
        
        if success:
            print(f"✅ {topic_data['site']} - {topic_data['category']}: 주제 추가 성공")
        else:
            print(f"❌ {topic_data['site']} - {topic_data['category']}: 주제 추가 실패")
    
    # 주제 데이터 저장
    manager.save_topics_to_file()
    print("\n💾 업데이트된 주제 데이터 파일로 저장 완료")

def show_daily_publishing_plan():
    """일일 발행 계획 시뮬레이션"""
    print("=" * 60)
    print("일일 발행 계획 시뮬레이션 (2개 카테고리)")
    print("=" * 60)
    
    manager = TrendingTopicManager()
    today = datetime.now().date()
    sites = ['unpre', 'untab', 'skewese', 'tistory']
    
    print(f"📅 {today} ({['월','화','수','목','금','토','일'][today.weekday()]}요일)")
    print(f"🚀 총 {len(sites) * 2}개 포스팅 예정 (사이트별 2개)")
    print("-" * 60)
    
    total_posts = 0
    for site in sites:
        primary, secondary = manager.get_daily_topics(site, today)
        
        print(f"\n🏷️  {site.upper()} ({site}.co.kr)")
        print(f"   1️⃣  [{primary['category']}]")
        print(f"      📝 {primary['topic']}")
        print(f"      🏷️  키워드: {', '.join(primary['keywords'][:3])}")
        
        print(f"   2️⃣  [{secondary['category']}]")
        print(f"      📝 {secondary['topic']}")
        print(f"      🏷️  키워드: {', '.join(secondary['keywords'][:3])}")
        
        total_posts += 2
    
    print(f"\n📊 총 발행 예정: {total_posts}개 포스팅")
    print(f"⏰ 예상 소요 시간: {total_posts * 15}분 (포스팅당 15분)")

if __name__ == "__main__":
    print("🚀 2개 카테고리 발행 시스템 종합 테스트")
    print("=" * 60)
    
    # 1. 트렌딩 주제 매니저 테스트
    test_trending_topic_manager()
    
    # 2. 일일 발행 계획 시뮬레이션
    show_daily_publishing_plan()
    
    # 3. 트렌디한 주제 추가 테스트
    test_topic_addition()
    
    # 4. 2개 카테고리 스케줄 생성 테스트
    test_dual_category_schedule()
    
    print("\n✅ 모든 테스트 완료!")
    print("💡 이제 사이트별로 하루 2개씩 총 8개 포스팅이 가능합니다!")