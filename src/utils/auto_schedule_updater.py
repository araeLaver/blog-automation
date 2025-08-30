"""
매월 자동 스케줄 업데이트 시스템
- 매달 말일 자동으로 다음 달 스케줄 생성
- 중복 없는 고유 주제로 구성
- SEO 친화적 트렌드 반영 주제
"""

import os
from datetime import datetime, date, timedelta, time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.utils.postgresql_database import PostgreSQLDatabase
import logging
import calendar

logger = logging.getLogger(__name__)

class AutoScheduleUpdater:
    def __init__(self):
        self.db = PostgreSQLDatabase()
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
    def generate_next_month_topics(self, year, month):
        """다음 달 고유 주제 생성"""
        
        # 월별 기본 주제 풀 (트렌드 반영)
        base_topics = {
            'skewese': {
                '건강/웰니스': [
                    '{month}월 시작하는 다이어트 플랜',
                    '{month}월 제철 건강식품 가이드',
                    '가을철 면역력 강화 방법',
                    '겨울철 비타민D 부족 해결법',
                    '봄철 알레르기 예방법',
                    '여름철 수분 보충 전략',
                    '스트레스 관리 {month}월 실천법',
                    '{month}월 운동 루틴 추천',
                    '계절별 수면 패턴 조절',
                    '{month}월 건강검진 체크리스트',
                    '날씨 변화와 건강 관리',
                    '{month}월 추천 홈트레이닝',
                    '계절성 우울증 극복법',
                    '{month}월 다이어트 음식 추천',
                    '환절기 감기 예방법',
                    '{month}월 피부 관리 루틴',
                    '체중 감량 {month}월 목표 설정',
                    '혈압 관리 계절별 팁',
                    '{month}월 금연 도전 가이드',
                    '관절 건강 {month}월 운동법',
                    '소화기 건강 {month}월 식단',
                    '{month}월 스트레칭 루틴',
                    '눈 건강 {month}월 관리법',
                    '두뇌 건강 {month}월 훈련',
                    '{month}월 여성 건강 체크',
                    '남성 건강 {month}월 가이드',
                    '청소년 성장 {month}월 영양',
                    '시니어 건강 {month}월 운동',
                    '{month}월 건강한 간식 추천',
                    '정신건강 {month}월 자가진단',
                    '{month}월 웰니스 트렌드'
                ],
                '요리/레시피': [
                    '{month}월 제철 요리 레시피',
                    '가을 보양식 만들기',
                    '겨울 따뜻한 수프 레시피',
                    '봄나물 활용 요리',
                    '여름 시원한 음료 만들기',
                    '{month}월 다이어트 요리',
                    '명절 음식 만들기',
                    '{month}월 간편 도시락',
                    '계절별 샐러드 레시피',
                    '{month}월 홈베이킹 추천',
                    '환절기 보양 음식',
                    '{month}월 김치 담그기',
                    '계절 과일 디저트',
                    '{month}월 야식 레시피',
                    '건강한 {month}월 간식',
                    '파티 음식 {month}월 추천',
                    '{month}월 술안주 레시피',
                    '아이 반찬 {month}월 메뉴',
                    '노인 건강식 {month}월',
                    '당뇨 환자 {month}월 식단',
                    '비건 요리 {month}월 추천',
                    '{month}월 발효식품 만들기',
                    '계절별 차 우리기',
                    '{month}월 해독 주스',
                    '면역력 증진 {month}월 요리',
                    '소화 돕는 {month}월 음식',
                    '{month}월 단백질 요리',
                    '칼슘 보충 {month}월 식단',
                    '철분 부족 {month}월 요리',
                    '{month}월 에너지 충전 음식',
                    '숙취 해소 {month}월 요리'
                ],
                '역사/문화': [
                    '{month}월 역사 속 오늘',
                    '한국사 {month}월 주요 사건',
                    '세계사 {month}월 기념일',
                    '전통 문화 {month}월 행사',
                    '{month}월 문화재 답사',
                    '박물관 {month}월 특별전',
                    '{month}월 역사 인물 조명',
                    '고궁 투어 {month}월 추천',
                    '전통 음식 {month}월 유래',
                    '{month}월 민속놀이 체험',
                    '한복 {month}월 코디 추천',
                    '서원 답사 {month}월 코스',
                    '{month}월 전통 차 문화',
                    '궁중 문화 {month}월 탐구',
                    '불교 문화 {month}월 이해',
                    '{month}월 유교 사상 학습',
                    '민화 {month}월 감상법',
                    '전통 공예 {month}월 체험',
                    '{month}월 고전 문학 읽기',
                    '사찰 음식 {month}월 철학',
                    '한옥 건축 {month}월 이해',
                    '{month}월 전통 의상 역사',
                    '고려 시대 {month}월 생활',
                    '조선 시대 {month}월 문화',
                    '{month}월 근현대사 정리',
                    '독립운동 {month}월 재조명',
                    '일제강점기 {month}월 저항',
                    '{month}월 민주화 운동사',
                    '한국전쟁 {month}월 기록',
                    '{month}월 경제 발전사',
                    '문화유산 {month}월 보호'
                ]
            },
            'tistory': {
                '엔터테인먼트': [
                    '{month}월 드라마 신작 라인업',
                    'K-팝 {month}월 컴백 소식',
                    '영화 {month}월 개봉작 정리',
                    '{month}월 예능 신규 편성',
                    'OTT {month}월 화제작',
                    '{month}월 아이돌 활동 정리',
                    '연예계 {month}월 이슈 정리',
                    '{month}월 콘서트 일정',
                    '드라마 OST {month}월 차트',
                    '{month}월 예능 포맷 분석',
                    '웹툰 드라마화 {month}월',
                    '{month}월 팬미팅 일정',
                    '뮤직뱅크 {month}월 1위',
                    '{month}월 연기상 후보',
                    '버라이어티 {month}월 순위',
                    '{month}월 신인 아이돌',
                    '톱스타 {month}월 근황',
                    '{month}월 엔터 주가 동향',
                    '한류 {month}월 해외 반응',
                    '{month}월 음반 판매 순위',
                    'MV {month}월 조회수 순위',
                    '{month}월 팬덤 이슈 정리',
                    '연예인 {month}월 광고 계약',
                    '{month}월 예능인 순위',
                    '드라마 {month}월 시청률',
                    '{month}월 연예 뉴스 정리',
                    '가수 {month}월 활동 계획',
                    '{month}월 배우 캐스팅',
                    '예능 {month}월 게스트 라인업',
                    '{month}월 연예계 루머 정리',
                    'K-콘텐츠 {month}월 수출'
                ],
                '게임/오락': [
                    '{month}월 게임 신작 출시',
                    'PC방 {month}월 순위 게임',
                    '모바일 게임 {month}월 순위',
                    '{month}월 e스포츠 대회',
                    '게임 업데이트 {month}월',
                    '{month}월 게임 할인 정보',
                    '스팀 {month}월 무료 게임',
                    '{month}월 콘솔 게임 추천',
                    'VR 게임 {month}월 신작',
                    '{month}월 인디게임 추천',
                    '게임 스트리머 {month}월 순위',
                    '{month}월 게임 패치 노트',
                    'MMORPG {month}월 이벤트',
                    '{month}월 배틀로얄 메타',
                    '게임 쿠폰 {month}월 정리',
                    '{month}월 게임 공략 모음',
                    'FPS 게임 {month}월 팁',
                    '{month}월 RPG 게임 추천',
                    '시뮬레이션 {month}월 신작',
                    '{month}월 캐주얼 게임',
                    '게임 기어 {month}월 추천',
                    '{month}월 게이밍 마우스',
                    '게이밍 키보드 {month}월',
                    '{month}월 모니터 추천',
                    '그래픽카드 {month}월 가격',
                    '{month}월 게임 노트북',
                    '게임 의자 {month}월 추천',
                    '{month}월 헤드셋 리뷰',
                    '게임 컨트롤러 {month}월',
                    '{month}월 게임룸 꾸미기',
                    '게임 중독 {month}월 대책'
                ]
            },
            'unpre': {
                '교육/자기계발': [
                    '{month}월 학습 목표 설정',
                    '취업 준비 {month}월 일정',
                    '{month}월 자격증 시험 일정',
                    '온라인 강의 {month}월 추천',
                    '{month}월 독서 목록 추천',
                    '어학 공부 {month}월 계획',
                    '{month}월 면접 준비 가이드',
                    '이력서 {month}월 업데이트',
                    '{month}월 포트폴리오 정리',
                    '네트워킹 {month}월 이벤트',
                    '{month}월 세미나 참석 목록',
                    '커리어 {month}월 목표 설정',
                    '{month}월 승진 전략 수립',
                    '부업 시작 {month}월 가이드',
                    '{month}월 창업 아이디어',
                    '투자 공부 {month}월 시작',
                    '{month}월 재테크 계획',
                    '건강 관리 {month}월 루틴',
                    '{month}월 운동 계획 세우기',
                    '인간관계 {month}월 개선',
                    '{month}월 소통 스킬 향상',
                    '리더십 {month}월 훈련',
                    '{month}월 발표 스킬 연습',
                    '협상 기술 {month}월 학습',
                    '{month}월 시간 관리 개선',
                    '스트레스 {month}월 관리법',
                    '{month}월 번아웃 예방',
                    '워라밸 {month}월 개선',
                    '{month}월 취미 활동 시작',
                    '자기계발 {month}월 도서',
                    '{month}월 멘토링 활용법'
                ],
                '기술/디지털': [
                    '{month}월 기술 트렌드 정리',
                    'AI 기술 {month}월 동향',
                    '{month}월 프로그래밍 언어',
                    '클라우드 {month}월 업데이트',
                    '{month}월 보안 이슈 정리',
                    '데이터베이스 {month}월 최적화',
                    '{month}월 개발 도구 추천',
                    'DevOps {month}월 실무 팁',
                    '{month}월 API 개발 가이드',
                    '마이크로서비스 {month}월',
                    '{month}월 컨테이너 기술',
                    '서버리스 {month}월 활용',
                    '{month}월 모바일 앱 개발',
                    '웹 개발 {month}월 트렌드',
                    '{month}월 프론트엔드 기술',
                    '백엔드 {month}월 아키텍처',
                    '{month}월 데이터 분석 도구',
                    '머신러닝 {month}월 프로젝트',
                    '{month}월 블록체인 개발',
                    'IoT 기술 {month}월 응용',
                    '{month}월 사이버보안 동향',
                    '네트워크 {month}월 관리',
                    '{month}월 시스템 최적화',
                    '성능 튜닝 {month}월 가이드',
                    '{month}월 모니터링 도구',
                    '테스트 {month}월 자동화',
                    '{month}월 CI/CD 파이프라인',
                    '코드 리뷰 {month}월 베스트',
                    '{month}월 오픈소스 기여',
                    '기술 문서 {month}월 작성',
                    '{month}월 개발자 도구'
                ]
            },
            'untab': {
                '라이프스타일': [
                    '{month}월 인테리어 트렌드',
                    '계절별 홈데코 {month}월',
                    '{month}월 수납 정리 팁',
                    '미니멀 라이프 {month}월',
                    '{month}월 홈가드닝 시작',
                    '반려동물 {month}월 관리',
                    '{month}월 홈카페 만들기',
                    'DIY 프로젝트 {month}월',
                    '{month}월 셀프 인테리어',
                    '가구 배치 {month}월 팁',
                    '{month}월 조명 활용법',
                    '향초 {month}월 추천',
                    '{month}월 공기정화 식물',
                    '베란다 {month}월 꾸미기',
                    '{month}월 현관 인테리어',
                    '주방 정리 {month}월 아이디어',
                    '{month}월 욕실 인테리어',
                    '침실 {month}월 꾸미기',
                    '서재 공간 {month}월 만들기',
                    '{month}월 아이방 인테리어',
                    '원룸 {month}월 활용 팁',
                    '{month}월 색상 매칭 가이드',
                    '계절별 {month}월 침구',
                    '{month}월 커튼 선택법',
                    '러그 {month}월 코디 팁',
                    '{month}월 월페이퍼 추천',
                    '액자 {month}월 배치 팁',
                    '{month}월 소품 활용법',
                    '청소 {month}월 꿀팁',
                    '{month}월 정리수납 도구',
                    '라이프해킹 {month}월 모음'
                ],
                '재정/투자': [
                    '{month}월 가계부 정리',
                    '저축 목표 {month}월 설정',
                    '{month}월 투자 포트폴리오',
                    '적금 {month}월 추천 상품',
                    '{month}월 펀드 수익률',
                    '주식 {month}월 추천 종목',
                    '{month}월 부동산 시장 전망',
                    '연금 {month}월 가입 상품',
                    '{month}월 보험 리모델링',
                    '대출 {month}월 금리 비교',
                    '{month}월 신용카드 혜택',
                    '세금 절약 {month}월 팁',
                    '{month}월 연말정산 준비',
                    '투자 {month}월 세금 정리',
                    '{month}월 청약 통장 관리',
                    'ISA {month}월 활용법',
                    '{month}월 펀드 갈아타기',
                    '배당주 {month}월 추천',
                    '{month}월 ETF 포트폴리오',
                    '달러 투자 {month}월 전략',
                    '{month}월 금 투자 타이밍',
                    '가상화폐 {month}월 전망',
                    '{month}월 P2P 투자 현황',
                    '채권 {month}월 투자 가이드',
                    '{month}월 리츠 투자 전략',
                    '해외 주식 {month}월 추천',
                    '{month}월 중국 주식 전망',
                    '일본 주식 {month}월 분석',
                    '{month}월 신흥국 투자',
                    '원자재 {month}월 투자',
                    '{month}월 투자 계획 수립'
                ]
            }
        }
        
        # 해당 월의 일수 계산
        days_in_month = calendar.monthrange(year, month)[1]
        
        # 월 이름 매핑
        month_names = {
            1: '1월', 2: '2월', 3: '3월', 4: '4월', 5: '5월', 6: '6월',
            7: '7월', 8: '8월', 9: '9월', 10: '10월', 11: '11월', 12: '12월'
        }
        month_str = month_names[month]
        
        schedule = []
        
        for day in range(1, days_in_month + 1):
            for site in ['skewese', 'tistory', 'unpre', 'untab']:
                # 사이트별 카테고리 2개 선택
                site_topics = base_topics[site]
                categories = list(site_topics.keys())
                
                primary_cat = categories[0]
                secondary_cat = categories[1] if len(categories) > 1 else categories[0]
                
                # 주제 선택 (일자 기반 순환)
                primary_topics = site_topics[primary_cat]
                secondary_topics = site_topics[secondary_cat]
                
                primary_idx = (day - 1) % len(primary_topics)
                secondary_idx = (day - 1) % len(secondary_topics)
                
                primary_topic = primary_topics[primary_idx].format(month=month_str)
                secondary_topic = secondary_topics[secondary_idx].format(month=month_str)
                
                # 스케줄에 추가
                schedule.append({
                    'year': year,
                    'month': month,
                    'day': day,
                    'site': site,
                    'category': primary_cat,
                    'topic': primary_topic
                })
                
                schedule.append({
                    'year': year,
                    'month': month,
                    'day': day,
                    'site': site,
                    'category': secondary_cat,
                    'topic': secondary_topic
                })
        
        return schedule
    
    def update_next_month_schedule(self):
        """다음 달 스케줄 자동 업데이트"""
        try:
            now = datetime.now()
            
            # 다음 달 계산
            if now.month == 12:
                next_year = now.year + 1
                next_month = 1
            else:
                next_year = now.year
                next_month = now.month + 1
            
            logger.info(f"[AUTO_SCHEDULE] {next_year}년 {next_month}월 스케줄 자동 생성 시작")
            
            # DB 연결
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 기존 다음 달 데이터 확인
            cursor.execute(f'''
                SELECT COUNT(*) FROM {self.db.schema}.monthly_publishing_schedule
                WHERE year = %s AND month = %s
            ''', (next_year, next_month))
            
            existing_count = cursor.fetchone()[0]
            
            if existing_count > 0:
                logger.info(f"[AUTO_SCHEDULE] {next_year}년 {next_month}월 스케줄이 이미 존재함 ({existing_count}개)")
                cursor.close()
                conn.close()
                return
            
            # 새 스케줄 생성
            schedule = self.generate_next_month_topics(next_year, next_month)
            
            # 데이터베이스에 삽입
            inserted = 0
            for item in schedule:
                cursor.execute(f'''
                    INSERT INTO {self.db.schema}.monthly_publishing_schedule 
                    (year, month, day, site, topic_category, specific_topic, keywords, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (item['year'], item['month'], item['day'], item['site'], item['category'], item['topic'], [], 'pending'))
                inserted += 1
            
            conn.commit()
            logger.info(f"[AUTO_SCHEDULE] {next_year}년 {next_month}월 스케줄 생성 완료: {inserted}개")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"[AUTO_SCHEDULE] 스케줄 자동 업데이트 오류: {e}")
            if conn:
                conn.rollback()
    
    def start_scheduler(self):
        """스케줄러 시작"""
        if self.is_running:
            return
        
        try:
            # 매월 28일 오후 11시에 다음 달 스케줄 생성
            self.scheduler.add_job(
                func=self.update_next_month_schedule,
                trigger=CronTrigger(day=28, hour=23, minute=0),
                id='monthly_schedule_update',
                name='Monthly Schedule Auto Update',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("[AUTO_SCHEDULE] 월간 스케줄 자동 업데이트 스케줄러 시작됨")
            
        except Exception as e:
            logger.error(f"[AUTO_SCHEDULE] 스케줄러 시작 오류: {e}")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("[AUTO_SCHEDULE] 월간 스케줄 자동 업데이트 스케줄러 중지됨")
    
    def get_scheduler_status(self):
        """스케줄러 상태 조회"""
        if not self.is_running:
            return {"status": "stopped", "next_run": None}
        
        try:
            job = self.scheduler.get_job('monthly_schedule_update')
            if job:
                return {
                    "status": "running",
                    "next_run": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None
                }
            else:
                return {"status": "error", "message": "Job not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# 전역 인스턴스
auto_schedule_updater = AutoScheduleUpdater()