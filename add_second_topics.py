#!/usr/bin/env python3
"""
사이트별 두 번째 카테고리 주제 추가
"""

from src.utils.schedule_manager import ScheduleManager
from datetime import date, timedelta

def add_second_category_topics():
    """각 사이트별로 두 번째 카테고리 주제 추가"""
    
    sm = ScheduleManager()
    
    # 두 번째 카테고리별 조회수 높은 주제들
    second_topics = {
        'unpre': {
            'category': 'ai',  # AI/ML 카테고리
            'topics': [
                'OpenAI GPT-4 API 고급 활용 기법',
                'Midjourney vs DALL-E 3 이미지 생성 비교',
                'LLM 파인튜닝 완벽 가이드',
                'Claude API로 만드는 스마트 어시스턴트',
                'Gemini Pro 활용한 멀티모달 AI 구현',
                'Llama 2 로컬 AI 모델 활용법',
                'AI 에이전트 시스템 구축하기'
            ]
        },
        'untab': {
            'category': 'crypto',  # 암호화폐 카테고리
            'topics': [
                '비트코인 반감기 이후 투자 전략',
                '이더리움 스테이킹 수익률 극대화',
                '알트코인 시즌 대비 포트폴리오 구성',
                'DeFi 프로토콜 활용한 패시브 인컴',
                'NFT 투자 리스크와 기회 분석',
                '암호화폐 세금 절세 전략 2025',
                'Web3 프로젝트 투자 가이드'
            ]
        },
        'skewese': {
            'category': 'culture',  # 문화/전통 카테고리
            'topics': [
                'K-POP이 세계를 정복한 비결',
                '한류 드라마의 글로벌 성공 전략',
                'K-푸드 세계화 현황과 미래',
                '한복의 현대적 재해석과 패션',
                '전통 차 문화의 현대적 가치',
                '한국 전통 예술의 디지털 융합',
                '템플스테이와 힐링 관광 트렌드'
            ]
        }
    }
    
    try:
        conn = sm.db.get_connection()
        total_added = 0
        
        # 9월 전체 주차 가져오기
        sep_1 = date(2025, 9, 1)
        sep_30 = date(2025, 9, 30)
        
        with conn.cursor() as cursor:
            # 각 날짜별로 두 번째 카테고리 추가
            cursor.execute("""
                SELECT DISTINCT week_start_date, day_of_week
                FROM publishing_schedule
                WHERE week_start_date >= %s AND week_start_date <= %s
                ORDER BY week_start_date, day_of_week
            """, (sep_1 - timedelta(days=6), sep_30))
            
            dates = cursor.fetchall()
            
            for week_start, day_of_week in dates:
                current_date = week_start + timedelta(days=day_of_week)
                
                # 9월 내의 날짜만 처리
                if current_date.month != 9:
                    continue
                    
                print(f'\n📅 {current_date} 처리 중...')
                
                for site in ['unpre', 'untab', 'skewese']:
                    second_cat = second_topics[site]
                    topics_list = second_cat['topics']
                    
                    # 날짜 기반으로 주제 선택
                    topic_index = (current_date.toordinal() + hash(site) * 2) % len(topics_list)
                    selected_topic = topics_list[topic_index]
                    
                    # 키워드 생성
                    if site == 'unpre':
                        keywords = ['AI', 'GPT', '자동화', '머신러닝']
                    elif site == 'untab':
                        keywords = ['암호화폐', '비트코인', '투자', '블록체인']
                    else:  # skewese
                        keywords = ['K-문화', '한류', '전통', '글로벌']
                    
                    # 두 번째 카테고리 삽입
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
                        week_start, day_of_week, site,
                        second_cat['category'],
                        selected_topic,
                        keywords,
                        'medium',
                        'planned'
                    ))
                    
                    total_added += 1
                    print(f'  ✅ {site} ({second_cat["category"]}): {selected_topic}')
        
        conn.commit()
        print(f'\n✨ 총 {total_added}개 두 번째 카테고리 주제 추가 완료!')
        
        # 검증 - 오늘 날짜 확인
        print('\n📊 오늘(9월 2일) 주제 확인:')
        today = date(2025, 9, 2)
        week_start = today - timedelta(days=today.weekday())
        
        cursor.execute("""
            SELECT site, topic_category, specific_topic
            FROM publishing_schedule
            WHERE week_start_date = %s AND day_of_week = %s
            ORDER BY site, topic_category
        """, (week_start, today.weekday()))
        
        current_site = None
        for site, category, topic in cursor.fetchall():
            if current_site != site:
                print(f'\n{site}:')
                current_site = site
            print(f'  [{category}] {topic}')
        
    except Exception as e:
        print(f'❌ 오류: {e}')
        return False
    
    return True

if __name__ == '__main__':
    add_second_category_topics()