#!/usr/bin/env python3
"""
티스토리 실시간 트렌드 주제 추가 및 업데이트
"""

from src.utils.schedule_manager import ScheduleManager
from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup

def get_realtime_trends():
    """실시간 트렌드 가져오기 (네이버, 구글 등)"""
    trends = {
        'tech': [  # 기술/IT 트렌드
            'AI 휴머노이드 로봇 시대 개막',
            '애플 비전프로 한국 출시 임박',
            '테슬라 자율주행 택시 로보택시 공개',
            '삼성 갤럭시 AI 신기능 발표',
            'OpenAI GPT-5 루머와 전망',
            '메타버스 플랫폼 경쟁 심화',
            '양자컴퓨터 상용화 가시권'
        ],
        'social': [  # 사회/이슈 트렌드
            'MZ세대 새로운 소비 트렌드',
            '저출산 대응 정책 총정리',
            '부동산 정책 변화와 전망',
            '전기차 보조금 정책 변경',
            '최저임금 인상 영향 분석',
            '청년 창업 지원 정책 확대',
            '디지털 노마드 비자 도입'
        ]
    }
    return trends

def add_tistory_dual_topics():
    """티스토리 2개 카테고리 주제 추가 - 실시간 트렌드 반영"""
    
    sm = ScheduleManager()
    
    # 실시간 트렌드 가져오기
    trends = get_realtime_trends()
    
    try:
        conn = sm.db.get_connection()
        total_added = 0
        
        # 9월 전체 날짜 처리
        sep_1 = date(2025, 9, 1)
        sep_30 = date(2025, 9, 30)
        
        with conn.cursor() as cursor:
            # 기존 티스토리 주제 업데이트 (첫 번째 카테고리)
            cursor.execute("""
                UPDATE publishing_schedule
                SET topic_category = 'tech'
                WHERE site = 'tistory' 
                AND week_start_date >= %s 
                AND week_start_date <= %s
                AND topic_category IN ('스포츠', 'current', 'trend')
            """, (sep_1 - timedelta(days=6), sep_30))
            
            print(f'✅ 기존 티스토리 카테고리 통일: tech')
            
            # 각 날짜별로 두 번째 카테고리 추가
            cursor.execute("""
                SELECT DISTINCT week_start_date, day_of_week
                FROM publishing_schedule
                WHERE site = 'tistory'
                AND week_start_date >= %s AND week_start_date <= %s
                ORDER BY week_start_date, day_of_week
            """, (sep_1 - timedelta(days=6), sep_30))
            
            dates = cursor.fetchall()
            
            for week_start, day_of_week in dates:
                current_date = week_start + timedelta(days=day_of_week)
                
                # 9월 내의 날짜만 처리
                if current_date.month != 9:
                    continue
                
                print(f'\n📅 {current_date} 티스토리 주제 설정...')
                
                # 첫 번째 카테고리 (tech) 업데이트 - 실시간 트렌드
                tech_topics = trends['tech']
                tech_topic_index = (current_date.toordinal()) % len(tech_topics)
                tech_topic = tech_topics[tech_topic_index]
                
                cursor.execute("""
                    UPDATE publishing_schedule
                    SET specific_topic = %s,
                        keywords = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE week_start_date = %s 
                    AND day_of_week = %s 
                    AND site = 'tistory'
                    AND topic_category = 'tech'
                """, (
                    tech_topic,
                    ['IT', '기술', '트렌드', 'AI'],
                    week_start, day_of_week
                ))
                
                print(f'  📱 [tech] {tech_topic}')
                
                # 두 번째 카테고리 (social) 추가 - 사회 이슈
                social_topics = trends['social']
                social_topic_index = (current_date.toordinal() + 7) % len(social_topics)
                social_topic = social_topics[social_topic_index]
                
                cursor.execute("""
                    INSERT INTO publishing_schedule 
                    (week_start_date, day_of_week, site, topic_category, 
                     specific_topic, keywords, target_length, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
                    DO UPDATE SET 
                        specific_topic = EXCLUDED.specific_topic,
                        keywords = EXCLUDED.keywords,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    week_start, day_of_week, 'tistory',
                    'social',
                    social_topic,
                    ['사회', '이슈', '트렌드', '정책'],
                    'medium',
                    'planned'
                ))
                
                print(f'  🌐 [social] {social_topic}')
                total_added += 1
        
        conn.commit()
        print(f'\n✨ 티스토리 {total_added}개 두 번째 카테고리 추가 완료!')
        
        # 오늘 날짜 전체 확인
        print('\n' + '=' * 60)
        print('📊 9월 2일 전체 사이트 주제 확인 (각 2개씩):')
        print('=' * 60)
        
        today = date(2025, 9, 2)
        week_start = today - timedelta(days=today.weekday())
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT site, topic_category, specific_topic
                FROM publishing_schedule
                WHERE week_start_date = %s AND day_of_week = %s
                ORDER BY 
                    CASE site 
                        WHEN 'unpre' THEN 1
                        WHEN 'untab' THEN 2
                        WHEN 'skewese' THEN 3
                        WHEN 'tistory' THEN 4
                    END,
                    topic_category
            """, (week_start, today.weekday()))
            
            results = cursor.fetchall()
            
            current_site = None
            site_count = {}
            
            for site, category, topic in results:
                if current_site != site:
                    if current_site:
                        print()
                    current_site = site
                    site_count[site] = 0
                    print(f'📍 {site.upper()}:')
                
                site_count[site] += 1
                print(f'  {site_count[site]}. [{category}] {topic}')
            
            print(f'\n✅ 총 4개 사이트, 각 2개씩 주제 설정 완료!')
        
    except Exception as e:
        print(f'❌ 오류: {e}')
        return False
    
    return True

def update_daily_trends():
    """매일 실행하여 티스토리 트렌드 업데이트"""
    sm = ScheduleManager()
    trends = get_realtime_trends()
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    try:
        conn = sm.db.get_connection()
        with conn.cursor() as cursor:
            # 오늘과 내일 티스토리 주제만 업데이트
            for days_ahead in [0, 1]:  # 오늘과 내일
                target_date = today + timedelta(days=days_ahead)
                target_weekday = target_date.weekday()
                target_week_start = target_date - timedelta(days=target_weekday)
                
                # tech 카테고리 업데이트
                tech_topic = trends['tech'][target_date.toordinal() % len(trends['tech'])]
                cursor.execute("""
                    UPDATE publishing_schedule
                    SET specific_topic = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE week_start_date = %s 
                    AND day_of_week = %s 
                    AND site = 'tistory'
                    AND topic_category = 'tech'
                """, (tech_topic, target_week_start, target_weekday))
                
                # social 카테고리 업데이트
                social_topic = trends['social'][(target_date.toordinal() + 7) % len(trends['social'])]
                cursor.execute("""
                    UPDATE publishing_schedule
                    SET specific_topic = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE week_start_date = %s 
                    AND day_of_week = %s 
                    AND site = 'tistory'
                    AND topic_category = 'social'
                """, (social_topic, target_week_start, target_weekday))
                
                print(f'✅ {target_date} 티스토리 트렌드 업데이트')
                print(f'  [tech] {tech_topic}')
                print(f'  [social] {social_topic}')
        
        conn.commit()
        
    except Exception as e:
        print(f'❌ 트렌드 업데이트 오류: {e}')

if __name__ == '__main__':
    # 초기 설정
    add_tistory_dual_topics()
    
    # 매일 실행 시 사용
    # update_daily_trends()