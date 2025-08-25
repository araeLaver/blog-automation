#!/usr/bin/env python3
"""
2개 카테고리 발행 계획표 생성 스크립트
각 사이트별로 2개 카테고리씩 하루 총 8개 포스팅 계획
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.utils.trending_topic_manager import TrendingTopicManager

def create_weekly_dual_category_schedule():
    """주간 2개 카테고리 발행 계획표 생성"""
    manager = TrendingTopicManager()
    
    # 이번주 월요일부터 일요일까지
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    
    sites = ['unpre', 'untab', 'skewese', 'tistory']
    days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    
    print("=" * 80)
    print("📅 2개 카테고리 주간 발행 계획표")
    print(f"🗓️  {monday} 주 ({monday} ~ {monday + timedelta(days=6)})")
    print(f"🚀 일일 총 8개 포스팅 (사이트별 2개 × 4개 사이트)")
    print("=" * 80)
    
    # SQL 생성을 위한 데이터 수집
    sql_statements = []
    
    for day_idx in range(7):  # 월요일(0) ~ 일요일(6)
        current_date = monday + timedelta(days=day_idx)
        day_name = days[day_idx]
        
        print(f"\n📆 {current_date} ({day_name})")
        print("─" * 60)
        
        daily_posts = 0
        for site in sites:
            primary, secondary = manager.get_daily_topics(site, current_date)
            
            # 사이트 헤더
            print(f"\n🏷️  {site.upper()} ({site}.co.kr)")
            
            # Primary 카테고리
            print(f"   1️⃣  [{primary['category']}]")
            print(f"      📝 {primary['topic']}")
            print(f"      🏷️  키워드: {', '.join(primary['keywords'][:4])}")
            
            # Secondary 카테고리  
            print(f"   2️⃣  [{secondary['category']}]")
            print(f"      📝 {secondary['topic']}")
            print(f"      🏷️  키워드: {', '.join(secondary['keywords'][:4])}")
            
            daily_posts += 2
            
            # SQL 문 생성
            for topic_data in [primary, secondary]:
                sql = f"""INSERT INTO publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status) VALUES ('{monday}', {day_idx}, '{site}', '{topic_data['category']}', '{topic_data['topic'].replace("'", "''")}', ARRAY[{', '.join([f"'{kw}'" for kw in topic_data['keywords'][:5]])}], '{topic_data['length']}', 'planned') ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;"""
                sql_statements.append(sql)
        
        print(f"\n   📊 {day_name} 총 발행: {daily_posts}개")
    
    # 주간 요약
    weekly_total = len(sites) * 7 * 2
    print(f"\n" + "=" * 80)
    print(f"📈 주간 발행 요약")
    print(f"   • 총 발행 포스팅: {weekly_total}개")
    print(f"   • 사이트별 주간 발행: {7 * 2}개 (카테고리별 7개)")
    print(f"   • 예상 주간 소요 시간: {weekly_total * 15}분 ({weekly_total * 15 // 60}시간 {weekly_total * 15 % 60}분)")
    print(f"   • 일평균 발행: {weekly_total // 7}개")
    
    # 카테고리별 통계
    print(f"\n📋 사이트별 카테고리 분석")
    for site in sites:
        site_config = manager.base_topics[site]
        print(f"   🏷️ {site.upper()}")
        print(f"      Primary: {site_config['primary']} ({len(site_config['topics'][site_config['primary']])}개 주제)")
        print(f"      Secondary: {site_config['secondary']} ({len(site_config['topics'][site_config['secondary']])}개 주제)")
    
    # SQL 파일 저장
    sql_file_path = Path(__file__).parent / "dual_category_schedule.sql"
    with open(sql_file_path, 'w', encoding='utf-8') as f:
        f.write(f"-- 2개 카테고리 주간 발행 계획표\n")
        f.write(f"-- 생성일시: {datetime.now().isoformat()}\n")
        f.write(f"-- 대상 주: {monday} ~ {monday + timedelta(days=6)}\n")
        f.write(f"-- 총 {weekly_total}개 포스팅 (사이트별 2개 카테고리)\n\n")
        
        for sql in sql_statements:
            f.write(sql + '\n')
    
    print(f"\n💾 SQL 스크립트 저장: {sql_file_path}")
    print("=" * 80)
    
    return sql_statements

def create_monthly_trend_topics():
    """월간 트렌드 주제 예시 생성"""
    print("\n" + "=" * 80)
    print("📈 월간 트렌드 주제 추가 예시 (동적 업데이트용)")
    print("=" * 80)
    
    monthly_trends = {
        "unpre": {
            "프로그래밍/개발": [
                "2025년 개발자 트렌드: Rust vs Go 성능 비교",
                "Next.js 15 새로운 기능과 마이그레이션 가이드",
                "AI 코딩 도구 GitHub Copilot vs Cursor 실전 비교"
            ],
            "기술/디지털": [
                "Apple Vision Pro 2세대 출시 전망과 개발자 기회",
                "2025년 웹 표준 업데이트: CSS4, HTML6 미리보기",
                "개발자를 위한 ChatGPT-4o 고급 활용법"
            ]
        },
        "untab": {
            "재정/투자": [
                "2025년 부동산 시장 전망: 금리 변동 대응 전략",
                "비트코인 ETF 승인 후 암호화폐 투자 전략",
                "인플레이션 헤지 투자: 금, 부동산, 주식 포트폴리오"
            ],
            "라이프스타일": [
                "2025년 인테리어 트렌드: 미니멀 vs 맥시멀리즘",
                "제로웨이스트 라이프스타일 실천 가이드",
                "MZ세대 여행 트렌드: 워케이션과 디지털 노마드"
            ]
        },
        "skewese": {
            "역사/문화": [
                "2025년 문화재 복원 기술: AI와 3D 프린팅 활용",
                "한국사 속 여성 리더십: 신사임당부터 윤희순까지",
                "조선 왕실 문화와 현대 궁중 요리의 재해석"
            ],
            "건강/웰니스": [
                "2025년 헬스케어 트렌드: 개인 맞춤형 영양학",
                "겨울철 면역력 강화를 위한 한방 건강법",
                "디지털 디톡스와 멘탈 헬스 관리법"
            ]
        },
        "tistory": {
            "트렌드/이슈": [
                "2025년 AI 일자리 전망: 사라질 직업 vs 새로 생길 직업",
                "MZ세대 정치 참여 증가와 선거 판도 변화",
                "K-컬처 4.0: 웹툰, 게임, 음악의 글로벌 진출"
            ],
            "교육/엔터테인먼트": [
                "2025년 온라인 교육 플랫폼 비교: 클래스101 vs 탈잉",
                "넷플릭스 한국 오리지널 콘텐츠 성공 공식 분석",
                "메타버스 교육의 현실: VR 클래스룸 체험기"
            ]
        }
    }
    
    manager = TrendingTopicManager()
    
    for site, categories in monthly_trends.items():
        print(f"\n🏷️ {site.upper()} 월간 트렌드 주제")
        print("─" * 50)
        
        for category, topics in categories.items():
            print(f"\n📂 [{category}]")
            for i, topic in enumerate(topics, 1):
                print(f"   {i}. {topic}")
                
                # 실제로 주제 추가 (옵션)
                # manager.add_trending_topic(site, category, topic)
    
    print(f"\n💡 이 주제들을 trending_topic_manager.add_trending_topic()으로 동적 추가 가능")
    print("=" * 80)

if __name__ == "__main__":
    print("🚀 2개 카테고리 발행 계획표 생성")
    
    # 1. 주간 발행 계획표 생성
    create_weekly_dual_category_schedule()
    
    # 2. 월간 트렌드 주제 예시
    create_monthly_trend_topics()
    
    print("\n✅ 2개 카테고리 발행 계획 수립 완료!")
    print("📝 이제 하루 8개 포스팅으로 콘텐츠 생산량이 2배 증가합니다!")
    print("🎯 각 사이트의 전문성을 유지하면서도 다양한 콘텐츠 제공 가능!")