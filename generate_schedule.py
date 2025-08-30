"""
8-9월 전체 발행 계획표 생성 스크립트
"""

from src.utils.postgresql_database import PostgreSQLDatabase
from datetime import date, timedelta
import calendar

def generate_monthly_schedule():
    """8-9월 전체 계획표 생성"""
    
    # 사이트별 카테고리 순환 계획
    site_categories = {
        'skewese': {
            'primary': ['건강/웰니스', '요리/레시피', '여행/관광', '스포츠/운동'],
            'secondary': ['역사/문화', '과학/기술', '환경/지속가능성', '심리/자기계발']
        },
        'tistory': {
            'primary': ['엔터테인먼트', '게임/오락', '음악/공연', '영화/드라마'],
            'secondary': ['트렌드/이슈', '사회/정치', '경제/비즈니스', '미디어/콘텐츠']
        },
        'unpre': {
            'primary': ['교육/자기계발', '커리어/취업', '창업/부업', '리더십/관리'],
            'secondary': ['기술/디지털', '프로그래밍/개발', 'AI/머신러닝', '데이터/분석']
        },
        'untab': {
            'primary': ['라이프스타일', '패션/뷰티', '인테리어/디자인', '육아/가족'],
            'secondary': ['재정/투자', '부동산/자산', '보험/금융', '절약/소비']
        }
    }
    
    # 각 카테고리별 구체적 주제 풀
    topic_pool = {
        '건강/웰니스': ['영양소 균형 잡힌 식단 구성법', '효과적인 홈트레이닝 루틴', '스트레스 해소 명상법', '수면의 질 향상 가이드'],
        '요리/레시피': ['간편한 한 그릇 요리 레시피', '건강한 샐러드 바리에이션', '집에서 만드는 베이커리', '계절 재료 활용법'],
        '여행/관광': ['국내 힐링 여행지 추천', '해외 배낭여행 준비 가이드', '가족 여행 코스 기획', '혼자 여행의 매력'],
        '스포츠/운동': ['러닝 초보자 가이드', '홈짐 운동 기구 추천', '요가로 몸과 마음 건강', '수영 기초 테크닉'],
        
        '역사/문화': ['한국 불교 문화재의 가치', '조선시대 생활상 탐구', '전통 공예의 현대적 계승', '지역별 문화유산 답사'],
        '과학/기술': ['우주 탐사의 최신 동향', '친환경 에너지 기술', '의학 기술의 미래', '과학으로 보는 일상'],
        '환경/지속가능성': ['제로웨이스트 실천법', '친환경 소비 가이드', '기후변화 대응책', '도시농업의 가능성'],
        '심리/자기계발': ['감정 조절 심리학', '목표 설정과 달성 전략', '인간관계 심리 분석', '자존감 향상 방법'],
        
        '엔터테인먼트': ['OTT 플랫폼 전쟁 현황', 'K-팝 글로벌 트렌드', '웹툰 산업의 성장', '게임 스트리밍 문화'],
        '게임/오락': ['인디게임 숨은 명작들', 'e스포츠 산업 분석', '모바일 게임 트렌드', 'VR/AR 게임의 미래'],
        '음악/공연': ['인디 음악씬 주목 아티스트', '클래식 음악 입문 가이드', '뮤지컬 관람 포인트', '페스티벌 문화 트렌드'],
        '영화/드라마': ['넷플릭스 화제작 분석', '한국 영화의 세계 진출', 'OTT 오리지널 콘텐츠', '영화 제작 과정 탐구'],
        
        '트렌드/이슈': ['구독 경제 성장 동향', 'MZ세대 소비 패턴', '리모트 워크 문화', '메타버스 현실화'],
        '사회/정치': ['청년 정책 현황 분석', '지역 균형 발전 방안', '디지털 민주주의', '사회적 경제 모델'],
        '경제/비즈니스': ['스타트업 생태계 동향', '플랫폼 경제의 명암', '중소기업 지원 정책', '글로벌 공급망 변화'],
        '미디어/콘텐츠': ['1인 미디어 성공 전략', '콘텐츠 마케팅 노하우', '숏폼 콘텐츠 트렌드', '팟캐스트 제작 가이드'],
        
        '교육/자기계발': ['개발자를 위한 시간 관리법', '효과적인 학습법 연구', '온라인 교육 플랫폼 활용', '평생학습 로드맵'],
        '커리어/취업': ['IT 직군별 전망 분석', '면접 성공 전략', '이직 준비 체크리스트', '프리랜서 생존 가이드'],
        '창업/부업': ['온라인 쇼핑몰 창업 가이드', '부업으로 시작하는 비즈니스', '스타트업 투자 유치', '1인 기업 운영법'],
        '리더십/관리': ['팀 빌딩 전략', '원격 팀 관리법', '갈등 해결 스킬', '동기부여 기법'],
        
        '기술/디지털': ['DevOps 도구 활용 가이드', 'AI 도구 실무 적용법', '클라우드 서비스 비교', '사이버 보안 기초'],
        '프로그래밍/개발': ['파이썬 프로젝트 아이디어', '웹 개발 프레임워크 선택', '코딩 테스트 준비법', 'Git 고급 활용'],
        'AI/머신러닝': ['ChatGPT 활용 실무 가이드', '머신러닝 입문 로드맵', 'AI 윤리와 사회적 책임', '자연어 처리 응용'],
        '데이터/분석': ['데이터 시각화 도구 비교', 'SQL 쿼리 최적화', '빅데이터 분석 기법', 'A/B 테스트 설계'],
        
        '라이프스타일': ['취미 생활 추천 리스트', '미니멀 라이프 실천법', '도시에서 즐기는 여가', '홈카페 만들기'],
        '패션/뷰티': ['계절별 코디 가이드', '자연 화장품 트렌드', '지속가능한 패션', '헤어케어 루틴'],
        '인테리어/디자인': ['소형 공간 활용법', 'DIY 인테리어 아이디어', '식물 인테리어 가이드', '색채 심리와 공간'],
        '육아/가족': ['아이와 함께하는 놀이', '육아 스트레스 관리', '가족 소통 방법', '아이 창의력 키우기'],
        
        '재정/투자': ['펀드 투자 완전 분석', '주식 투자 기초 전략', '부동산 투자 가이드', '연금 계획 수립법'],
        '부동산/자산': ['내집마련 로드맵', '부동산 시장 분석', '임대투자 성공법', '재건축 재개발 가이드'],
        '보험/금융': ['생명보험 선택 가이드', '은행권 금융상품 비교', '신용관리 전략', '세무 절약 노하우'],
        '절약/소비': ['가계부 작성법', '똑똑한 쇼핑 전략', '에너지 절약 아이디어', '구독 서비스 관리법']
    }
    
    schedule = []
    
    # 8월 (31일) + 9월 (30일)
    for month in [8, 9]:
        days_in_month = 31 if month == 8 else 30
        
        for day in range(1, days_in_month + 1):
            for site in ['skewese', 'tistory', 'unpre', 'untab']:
                # 날짜 기반으로 카테고리 순환 (Primary)
                primary_idx = (day - 1) % len(site_categories[site]['primary'])
                primary_cat = site_categories[site]['primary'][primary_idx]
                
                # Secondary는 Primary와 다른 인덱스 사용
                secondary_idx = (day - 1) % len(site_categories[site]['secondary'])
                secondary_cat = site_categories[site]['secondary'][secondary_idx]
                
                # 주제 선택 (날짜 기반 순환)
                primary_topic_idx = (day - 1) % len(topic_pool[primary_cat])
                primary_topic = topic_pool[primary_cat][primary_topic_idx]
                
                secondary_topic_idx = (day - 1) % len(topic_pool[secondary_cat])
                secondary_topic = topic_pool[secondary_cat][secondary_topic_idx]
                
                # Primary 스케줄 추가
                schedule.append({
                    'year': 2025,
                    'month': month,
                    'day': day,
                    'site': site,
                    'category': primary_cat,
                    'topic': primary_topic
                })
                
                # Secondary 스케줄 추가
                schedule.append({
                    'year': 2025,
                    'month': month,
                    'day': day,
                    'site': site,
                    'category': secondary_cat,
                    'topic': secondary_topic
                })
    
    return schedule

def main():
    """메인 실행 함수"""
    
    # 데이터베이스 연결
    db = PostgreSQLDatabase()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # 기존 8-9월 데이터 삭제
        print("기존 8-9월 스케줄 삭제 중...")
        cursor.execute(f'''
            DELETE FROM {db.schema}.monthly_publishing_schedule 
            WHERE year = 2025 AND month IN (8, 9)
        ''')
        
        # 새 스케줄 생성
        print("새 스케줄 생성 중...")
        schedule = generate_monthly_schedule()
        
        # 데이터베이스에 삽입
        print("데이터베이스 삽입 중...")
        for item in schedule:
            cursor.execute(f'''
                INSERT INTO {db.schema}.monthly_publishing_schedule 
                (year, month, day, site, topic_category, specific_topic, keywords, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (item['year'], item['month'], item['day'], item['site'], item['category'], item['topic'], [], 'pending'))
        
        conn.commit()
        print(f'[완료] 8-9월 전체 스케줄 생성 완료: {len(schedule)}개 항목')
        
        # 확인용 오늘 주제 출력
        cursor.execute(f'''
            SELECT site, topic_category, specific_topic 
            FROM {db.schema}.monthly_publishing_schedule
            WHERE year = 2025 AND month = 8 AND day = 30
            ORDER BY site, topic_category
        ''')
        today_topics = cursor.fetchall()
        
        print('\n[8월 30일 주제 확인]')
        current_site = None
        for site, cat, topic in today_topics:
            if site != current_site:
                print(f'\n{site}:')
                current_site = site
            print(f'  - {cat}: {topic}')
        
        # 9월 1일도 확인
        cursor.execute(f'''
            SELECT site, topic_category, specific_topic 
            FROM {db.schema}.monthly_publishing_schedule
            WHERE year = 2025 AND month = 9 AND day = 1
            ORDER BY site, topic_category
        ''')
        sep_topics = cursor.fetchall()
        
        print('\n[9월 1일 주제 확인]')
        current_site = None
        for site, cat, topic in sep_topics:
            if site != current_site:
                print(f'\n{site}:')
                current_site = site
            print(f'  - {cat}: {topic}')
            
    except Exception as e:
        print(f"[오류] 오류 발생: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()