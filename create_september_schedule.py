#!/usr/bin/env python3
"""
9월 전체 계획표 생성 - 조회수 높은 주제 중심
"""

from src.utils.schedule_manager import ScheduleManager
from datetime import datetime, date, timedelta
import sys

def create_september_schedule():
    """9월 전체 스케줄 생성 - 조회수 높은 주제들"""
    
    sm = ScheduleManager()
    
    # 조회수 높은 주제들 정의
    high_traffic_topics = {
        'unpre': [
            # AI/ML - 매우 인기
            {'topic': 'ChatGPT API 활용한 자동화 시스템 구축', 'category': 'programming', 'keywords': ['ChatGPT', 'API', '자동화']},
            {'topic': 'Python으로 만드는 AI 챗봇 완전정복', 'category': 'programming', 'keywords': ['Python', 'AI', '챗봇']},
            {'topic': 'Stable Diffusion 이미지 생성 실전 가이드', 'category': 'programming', 'keywords': ['AI', '이미지생성', 'Stable Diffusion']},
            {'topic': 'LangChain으로 구현하는 RAG 시스템', 'category': 'programming', 'keywords': ['LangChain', 'RAG', 'AI']},
            
            # 웹개발 - 높은 조회수
            {'topic': 'Next.js 14 App Router 실전 활용법', 'category': 'programming', 'keywords': ['Next.js', 'React', '웹개발']},
            {'topic': 'TypeScript 5.0 고급 기능 마스터하기', 'category': 'programming', 'keywords': ['TypeScript', 'JavaScript', '타입스크립트']},
            {'topic': 'Vue.js 3 Composition API 완벽 가이드', 'category': 'programming', 'keywords': ['Vue.js', 'Composition API', '프론트엔드']},
            {'topic': 'React Query vs SWR 데이터 패칭 비교', 'category': 'programming', 'keywords': ['React', 'React Query', 'SWR']},
            
            # 백엔드/인프라 - 실무 중심
            {'topic': 'Docker Compose 멀티 컨테이너 관리', 'category': 'programming', 'keywords': ['Docker', '컨테이너', 'DevOps']},
            {'topic': 'AWS Lambda 서버리스 아키텍처 구축', 'category': 'programming', 'keywords': ['AWS', 'Lambda', '서버리스']},
            {'topic': 'Spring Boot 3.0 성능 최적화 기법', 'category': 'programming', 'keywords': ['Spring Boot', 'Java', '성능최적화']},
            {'topic': 'PostgreSQL 고급 쿼리 튜닝 가이드', 'category': 'programming', 'keywords': ['PostgreSQL', 'DB', '쿼리튜닝']},
            
            # 모바일/크로스플랫폼
            {'topic': 'Flutter 3.0으로 앱 개발 완전정복', 'category': 'programming', 'keywords': ['Flutter', '앱개발', '크로스플랫폼']},
            {'topic': 'React Native vs Flutter 성능 비교', 'category': 'programming', 'keywords': ['React Native', 'Flutter', '모바일']},
            
            # 데이터/분석
            {'topic': 'Python 데이터 분석 with Pandas 심화', 'category': 'programming', 'keywords': ['Python', 'Pandas', '데이터분석']},
            {'topic': '실시간 데이터 파이프라인 구축하기', 'category': 'programming', 'keywords': ['데이터파이프라인', '빅데이터', '실시간처리']},
        ],
        
        'untab': [
            # 부동산 투자 - 높은 관심사
            {'topic': '2025년 서울 아파트 시장 전망과 투자전략', 'category': 'investment', 'keywords': ['부동산', '아파트', '서울']},
            {'topic': '금리인하 시대 부동산 투자 타이밍', 'category': 'investment', 'keywords': ['금리', '부동산투자', '타이밍']},
            {'topic': '청약 당첨 확률 높이는 실전 노하우', 'category': 'investment', 'keywords': ['청약', '당첨전략', '신규분양']},
            {'topic': '갭투자 성공을 위한 매물 선별법', 'category': 'investment', 'keywords': ['갭투자', '매물선별', '투자수익']},
            
            # 주식/투자 - 인기 주제
            {'topic': 'AI 관련주 투자 전략과 유망 종목', 'category': 'investment', 'keywords': ['AI주식', '테마주', '투자전략']},
            {'topic': 'ETF로 시작하는 장기 투자 포트폴리오', 'category': 'investment', 'keywords': ['ETF', '장기투자', '포트폴리오']},
            {'topic': '배당주 투자로 월 100만원 만들기', 'category': 'investment', 'keywords': ['배당주', '배당투자', '월배당']},
            {'topic': '미국주식 세금 완벽 가이드 2025', 'category': 'investment', 'keywords': ['미국주식', '세금', '해외투자']},
            
            # 경제/금융 트렌드
            {'topic': '비트코인 ETF 승인 후 암호화폐 전망', 'category': 'investment', 'keywords': ['비트코인', 'ETF', '암호화폐']},
            {'topic': '인플레이션 대응 투자 자산 배분법', 'category': 'investment', 'keywords': ['인플레이션', '자산배분', '헷지']},
            {'topic': '달러 강세 시대 환율 투자 전략', 'category': 'investment', 'keywords': ['달러', '환율', '외환투자']},
            {'topic': '중국 경제 회복과 투자 기회 분석', 'category': 'investment', 'keywords': ['중국경제', '투자기회', '해외투자']},
            
            # 재테크 실무
            {'topic': '30대 맞춤 자산관리 로드맵', 'category': 'investment', 'keywords': ['30대', '자산관리', '재테크']},
            {'topic': '퇴직연금 활용한 절세 투자법', 'category': 'investment', 'keywords': ['퇴직연금', '절세', '연금투자']},
            {'topic': 'ISA 계좌 200% 활용하는 방법', 'category': 'investment', 'keywords': ['ISA', '세금우대', '투자계좌']},
            {'topic': '신용점수 올리는 확실한 방법들', 'category': 'investment', 'keywords': ['신용점수', '신용관리', '금융']},
        ],
        
        'skewese': [
            # 한국사 - 드라마/영화와 연계된 인기 주제
            {'topic': '조선왕조 궁중 암투의 진실과 허구', 'category': 'history', 'keywords': ['조선왕조', '궁중', '역사드라마']},
            {'topic': '임진왜란 7년 전쟁의 숨겨진 이야기', 'category': 'history', 'keywords': ['임진왜란', '이순신', '전쟁사']},
            {'topic': '세종대왕의 혁신 리더십과 한글 창제', 'category': 'history', 'keywords': ['세종대왕', '한글', '리더십']},
            {'topic': '고구려 광개토대왕의 정복 전쟁', 'category': 'history', 'keywords': ['고구려', '광개토대왕', '정복전쟁']},
            
            # 현대사 - 높은 관심
            {'topic': '6.25 전쟁의 전환점과 영웅들', 'category': 'history', 'keywords': ['6.25전쟁', '한국전쟁', '근현대사']},
            {'topic': '일제강점기 독립운동가들의 활약상', 'category': 'history', 'keywords': ['일제강점기', '독립운동', '항일투쟁']},
            {'topic': '4.19 혁명과 민주주의의 승리', 'category': 'history', 'keywords': ['4.19혁명', '민주주의', '학생운동']},
            {'topic': '88올림픽이 한국에 미친 영향', 'category': 'history', 'keywords': ['88올림픽', '경제발전', '국제화']},
            
            # 문화/전통 - 관광/체험 연계
            {'topic': '한국 전통 음식의 과학적 우수성', 'category': 'culture', 'keywords': ['전통음식', '한식', '발효음식']},
            {'topic': '한옥 건축의 친환경 설계 원리', 'category': 'culture', 'keywords': ['한옥', '전통건축', '친환경']},
            {'topic': '한국 전통 의학 한의학의 현대적 가치', 'category': 'culture', 'keywords': ['한의학', '전통의학', '자연치료']},
            {'topic': '태권도 세계화 성공 스토리', 'category': 'culture', 'keywords': ['태권도', '무술', '세계화']},
            
            # 인물사 - 스토리텔링 중심
            {'topic': '이순신 장군의 리더십과 전술', 'category': 'history', 'keywords': ['이순신', '리더십', '전술']},
            {'topic': '신사임당의 예술 세계와 교육철학', 'category': 'history', 'keywords': ['신사임당', '예술', '교육']},
            {'topic': '퇴계 이황의 성리학과 교육사상', 'category': 'history', 'keywords': ['퇴계', '성리학', '교육']},
            {'topic': '윤동주 시인의 삶과 저항정신', 'category': 'history', 'keywords': ['윤동주', '시인', '저항문학']},
        ]
    }
    
    try:
        conn = sm.db.get_connection()
        
        # 9월 전체 주 계산 (9월 1일이 포함된 주부터 9월 30일이 포함된 주까지)
        september_weeks = []
        
        # 9월 1일이 포함된 주의 월요일
        sep_1 = date(2025, 9, 1)
        first_monday = sep_1 - timedelta(days=sep_1.weekday())
        
        # 9월 30일이 포함된 주의 월요일
        sep_30 = date(2025, 9, 30)  
        last_monday = sep_30 - timedelta(days=sep_30.weekday())
        
        current_monday = first_monday
        while current_monday <= last_monday:
            september_weeks.append(current_monday)
            current_monday += timedelta(days=7)
        
        print(f'📅 생성할 주차: {len(september_weeks)}주')
        for week in september_weeks:
            print(f'  - {week} 주')
            
        total_inserted = 0
        
        with conn.cursor() as cursor:
            for week_start in september_weeks:
                print(f'\n📝 {week_start} 주 스케줄 생성 중...')
                
                for day in range(7):  # 월-일
                    current_date = week_start + timedelta(days=day)
                    day_names = ['월', '화', '수', '목', '금', '토', '일']
                    
                    print(f'  📆 {current_date} ({day_names[day]}요일)')
                    
                    for site in ['unpre', 'untab', 'skewese']:
                        # 각 사이트별로 순환하며 주제 선택
                        topics = high_traffic_topics[site]
                        topic_index = (current_date.toordinal() + hash(site)) % len(topics)
                        selected_topic = topics[topic_index]
                        
                        cursor.execute("""
                            INSERT INTO publishing_schedule 
                            (week_start_date, day_of_week, site, topic_category, specific_topic, 
                             keywords, target_length, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            week_start, day, site,
                            selected_topic['category'],
                            selected_topic['topic'],
                            selected_topic['keywords'],
                            'medium',
                            'planned'
                        ))
                        
                        total_inserted += 1
                        print(f'    📍 {site}: {selected_topic["topic"]}')
        
        conn.commit()
        print(f'\n✅ 9월 전체 스케줄 생성 완료: {total_inserted}개 항목')
        
    except Exception as e:
        print(f'❌ 스케줄 생성 오류: {e}')
        return False
    
    return True

if __name__ == '__main__':
    create_september_schedule()