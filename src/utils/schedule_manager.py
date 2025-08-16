"""
일주일치 자동 발행 스케줄 관리 모듈
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.web_dashboard_pg import get_database

class ScheduleManager:
    """발행 스케줄 관리 클래스"""
    
    def __init__(self):
        self.db = get_database()
        self._ensure_schedule_table()
        self._auto_initialize_schedules()
    
    def _ensure_schedule_table(self):
        """스케줄 테이블 생성 (없을 경우)"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS publishing_schedule (
                        id SERIAL PRIMARY KEY,
                        week_start_date DATE NOT NULL,
                        day_of_week INTEGER NOT NULL, -- 0=월요일, 6=일요일
                        site VARCHAR(20) NOT NULL,
                        topic_category VARCHAR(50) NOT NULL,
                        specific_topic TEXT NOT NULL,
                        keywords TEXT[], -- 키워드 배열
                        target_length VARCHAR(20) DEFAULT 'medium',
                        status VARCHAR(20) DEFAULT 'planned', -- planned, generated, published, failed
                        generated_content_id INTEGER,
                        published_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(week_start_date, day_of_week, site)
                    )
                """)
                conn.commit()
                print("[SCHEDULE] 발행 스케줄 테이블 준비 완료")
        except Exception as e:
            print(f"[SCHEDULE] 테이블 생성 오류: {e}")
    
    def _auto_initialize_schedules(self):
        """자동으로 이번 주, 다음 주 스케줄 생성"""
        try:
            today = datetime.now().date()
            
            # 이번 주 월요일 계산 (오늘이 포함된 주)
            current_week_start = today - timedelta(days=today.weekday())
            
            # 다음 주 월요일 계산
            next_week_start = current_week_start + timedelta(days=7)
            
            # 이번 주 스케줄 생성 (오늘 포함)
            if not self._week_schedule_exists(current_week_start):
                print(f"[AUTO_SCHEDULE] {current_week_start} 주 (이번주) 자동 스케줄 생성")
                self.create_weekly_schedule(current_week_start)
            
            # 다음 주 스케줄 생성
            if not self._week_schedule_exists(next_week_start):
                print(f"[AUTO_SCHEDULE] {next_week_start} 주 (다음주) 자동 스케줄 생성")
                self.create_weekly_schedule(next_week_start)
                
        except Exception as e:
            print(f"[AUTO_SCHEDULE] 자동 스케줄 초기화 오류: {e}")
    
    def _week_schedule_exists(self, week_start: datetime.date) -> bool:
        """해당 주에 스케줄이 존재하는지 확인"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM publishing_schedule 
                    WHERE week_start_date = %s
                """, (week_start,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"[SCHEDULE] 스케줄 존재 확인 오류: {e}")
            return False
    
    def create_weekly_schedule(self, start_date: datetime = None) -> bool:
        """일주일치 발행 스케줄 생성"""
        try:
            if start_date is None:
                # 다음 월요일부터 시작
                today = datetime.now().date()
                days_ahead = 0 - today.weekday()  # 0 = 월요일
                if days_ahead <= 0:  # 오늘이 월요일이거나 지났으면 다음 주
                    days_ahead += 7
                start_date = today + timedelta(days=days_ahead)
            
            # 4개 사이트 × 7일 = 28개 발행 계획
            sites = ['unpre', 'untab', 'skewese', 'tistory']
            
            # 주제 카테고리와 세부 주제들
            topic_plans = self._generate_topic_plans()
            
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                for day in range(7):  # 월요일(0) ~ 일요일(6)
                    current_date = start_date + timedelta(days=day)
                    
                    for site_idx, site in enumerate(sites):
                        # 각 사이트별로 다른 주제 할당
                        site_topics = self._get_site_topic_plans(site)
                        topic_idx = (day * 4 + site_idx) % len(site_topics)
                        topic_plan = site_topics[topic_idx]
                        
                        # 기존 계획 체크
                        cursor.execute("""
                            SELECT id FROM publishing_schedule 
                            WHERE week_start_date = %s AND day_of_week = %s AND site = %s
                        """, (start_date, day, site))
                        
                        if cursor.fetchone():
                            continue  # 이미 계획 있음
                        
                        # 중복 컨텐츠 검사
                        if self.check_duplicate_content(site, topic_plan['topic'], topic_plan['keywords']):
                            print(f"[SCHEDULE] {site} 중복 주제 제외: {topic_plan['topic']}")
                            # 다른 주제로 대체
                            for alt_idx in range(len(site_topics)):
                                alt_topic = site_topics[alt_idx]
                                if not self.check_duplicate_content(site, alt_topic['topic'], alt_topic['keywords']):
                                    topic_plan = alt_topic
                                    print(f"[SCHEDULE] {site} 대체 주제 선택: {topic_plan['topic']}")
                                    break
                        
                        # 새 계획 추가
                        cursor.execute("""
                            INSERT INTO publishing_schedule 
                            (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            start_date,
                            day,
                            site,
                            topic_plan['category'],
                            topic_plan['topic'],
                            topic_plan['keywords'],
                            topic_plan['length']
                        ))
                
                conn.commit()
                print(f"[SCHEDULE] {start_date} 주 발행 스케줄 생성 완료")
                return True
                
        except Exception as e:
            print(f"[SCHEDULE] 스케줄 생성 오류: {e}")
            return False
    
    def _get_site_topic_plans(self, site: str) -> List[Dict]:
        """사이트별 주제 계획 생성"""
        if site == 'unpre':
            # unpre.co.kr - 개발, IT, 개발 자격증 정보 (다양한 카테고리로 확장)
            return [
                # 프로그래밍 언어 & 기초
                {'category': 'programming', 'topic': 'Python 완벽 마스터 가이드', 'keywords': ['python', '기초', '문법'], 'length': 'long'},
                {'category': 'programming', 'topic': 'JavaScript 최신 트렌드와 ES2024', 'keywords': ['javascript', 'es2024', '모던'], 'length': 'long'},
                {'category': 'programming', 'topic': 'TypeScript 실전 활용법', 'keywords': ['typescript', '타입', '개발'], 'length': 'medium'},
                {'category': 'programming', 'topic': 'Go 언어 성능 최적화', 'keywords': ['golang', '성능', '백엔드'], 'length': 'medium'},
                {'category': 'programming', 'topic': 'Rust로 안전한 시스템 프로그래밍', 'keywords': ['rust', '시스템', '안전성'], 'length': 'long'},
                {'category': 'programming', 'topic': 'C++ 모던 프로그래밍 기법', 'keywords': ['cpp', '모던', '최적화'], 'length': 'long'},
                
                # 웹 개발 & 프레임워크
                {'category': 'web', 'topic': 'React 18 신기능 완전정복', 'keywords': ['react', '18', '신기능'], 'length': 'long'},
                {'category': 'web', 'topic': 'Vue.js 3 컴포지션 API 실전', 'keywords': ['vuejs', 'composition', 'api'], 'length': 'medium'},
                {'category': 'web', 'topic': 'Angular 최신 버전 마이그레이션', 'keywords': ['angular', '마이그레이션', '업그레이드'], 'length': 'medium'},
                {'category': 'web', 'topic': 'Next.js 풀스택 개발', 'keywords': ['nextjs', '풀스택', 'ssr'], 'length': 'long'},
                {'category': 'web', 'topic': 'Svelte Kit으로 빠른 웹앱 개발', 'keywords': ['svelte', 'kit', '성능'], 'length': 'medium'},
                {'category': 'web', 'topic': 'Nuxt.js 3로 Vue 앱 개발', 'keywords': ['nuxtjs', 'vue', 'ssr'], 'length': 'medium'},
                
                # 백엔드 & API
                {'category': 'backend', 'topic': 'Node.js 마이크로서비스 아키텍처', 'keywords': ['nodejs', '마이크로서비스', '아키텍처'], 'length': 'long'},
                {'category': 'backend', 'topic': 'FastAPI로 고성능 API 개발', 'keywords': ['fastapi', 'python', 'api'], 'length': 'medium'},
                {'category': 'backend', 'topic': 'Express.js vs Fastify 성능 비교', 'keywords': ['express', 'fastify', '성능'], 'length': 'medium'},
                {'category': 'backend', 'topic': 'GraphQL 스키마 설계 베스트 프랙티스', 'keywords': ['graphql', '스키마', '설계'], 'length': 'long'},
                {'category': 'backend', 'topic': 'gRPC 마이크로서비스 통신', 'keywords': ['grpc', '마이크로서비스', '통신'], 'length': 'medium'},
                {'category': 'backend', 'topic': 'Spring Boot 3 신기능 가이드', 'keywords': ['springboot', 'java', '신기능'], 'length': 'long'},
                
                # 데이터베이스 & 스토리지
                {'category': 'database', 'topic': 'PostgreSQL 고급 최적화 기법', 'keywords': ['postgresql', '최적화', '성능'], 'length': 'long'},
                {'category': 'database', 'topic': 'MongoDB 집계 파이프라인 활용', 'keywords': ['mongodb', '집계', '파이프라인'], 'length': 'medium'},
                {'category': 'database', 'topic': 'Redis 캐싱 전략과 패턴', 'keywords': ['redis', '캐싱', '전략'], 'length': 'medium'},
                {'category': 'database', 'topic': 'Elasticsearch 검색 엔진 구축', 'keywords': ['elasticsearch', '검색', '엔진'], 'length': 'long'},
                {'category': 'database', 'topic': 'Neo4j 그래프 데이터베이스', 'keywords': ['neo4j', '그래프', 'db'], 'length': 'medium'},
                
                # 클라우드 & DevOps
                {'category': 'cloud', 'topic': 'AWS Lambda 서버리스 아키텍처', 'keywords': ['aws', 'lambda', '서버리스'], 'length': 'long'},
                {'category': 'cloud', 'topic': 'Docker 컨테이너 최적화 전략', 'keywords': ['docker', '컨테이너', '최적화'], 'length': 'medium'},
                {'category': 'cloud', 'topic': 'Kubernetes 운영 가이드', 'keywords': ['kubernetes', '운영', 'k8s'], 'length': 'long'},
                {'category': 'cloud', 'topic': 'Terraform으로 IaC 구축', 'keywords': ['terraform', 'iac', '인프라'], 'length': 'medium'},
                {'category': 'cloud', 'topic': 'GitHub Actions CI/CD 파이프라인', 'keywords': ['github', 'actions', 'cicd'], 'length': 'long'},
                {'category': 'cloud', 'topic': 'Azure DevOps 완전 가이드', 'keywords': ['azure', 'devops', '파이프라인'], 'length': 'long'},
                
                # AI & 머신러닝
                {'category': 'ai', 'topic': 'ChatGPT API 실전 활용법', 'keywords': ['chatgpt', 'api', '활용'], 'length': 'medium'},
                {'category': 'ai', 'topic': 'TensorFlow 2 딥러닝 모델 개발', 'keywords': ['tensorflow', '딥러닝', '모델'], 'length': 'long'},
                {'category': 'ai', 'topic': 'PyTorch로 컴퓨터 비전 구현', 'keywords': ['pytorch', '컴퓨터비전', 'cv'], 'length': 'long'},
                {'category': 'ai', 'topic': 'LangChain으로 LLM 앱 개발', 'keywords': ['langchain', 'llm', '앱개발'], 'length': 'medium'},
                {'category': 'ai', 'topic': 'Vector Database 구축과 활용', 'keywords': ['vector', 'database', '임베딩'], 'length': 'medium'},
                
                # 모바일 개발
                {'category': 'mobile', 'topic': 'React Native 크로스플랫폼 개발', 'keywords': ['reactnative', '크로스플랫폼', '모바일'], 'length': 'long'},
                {'category': 'mobile', 'topic': 'Flutter 앱 개발 완전 가이드', 'keywords': ['flutter', '앱개발', 'dart'], 'length': 'long'},
                {'category': 'mobile', 'topic': 'Swift UI로 iOS 앱 개발', 'keywords': ['swiftui', 'ios', '앱개발'], 'length': 'medium'},
                {'category': 'mobile', 'topic': 'Kotlin으로 Android 앱 개발', 'keywords': ['kotlin', 'android', '앱개발'], 'length': 'medium'},
                
                # 보안 & 테스팅
                {'category': 'security', 'topic': '웹 애플리케이션 보안 가이드', 'keywords': ['웹보안', 'security', '취약점'], 'length': 'long'},
                {'category': 'security', 'topic': 'JWT 토큰 보안 베스트 프랙티스', 'keywords': ['jwt', '토큰', '보안'], 'length': 'medium'},
                {'category': 'testing', 'topic': 'Jest를 이용한 JavaScript 테스팅', 'keywords': ['jest', '테스팅', 'javascript'], 'length': 'medium'},
                {'category': 'testing', 'topic': 'Cypress E2E 테스트 자동화', 'keywords': ['cypress', 'e2e', '자동화'], 'length': 'medium'},
                
                # IT 자격증
                {'category': 'certification', 'topic': '정보처리기사 실기 완전정복', 'keywords': ['정보처리기사', '실기', '자격증'], 'length': 'long'},
                {'category': 'certification', 'topic': 'AWS SAA 자격증 합격 전략', 'keywords': ['aws', 'saa', '자격증'], 'length': 'long'},
                {'category': 'certification', 'topic': 'Google Cloud ACE 자격증 가이드', 'keywords': ['gcp', 'ace', '자격증'], 'length': 'medium'},
                {'category': 'certification', 'topic': 'Azure Fundamentals 자격증', 'keywords': ['azure', 'fundamentals', '자격증'], 'length': 'medium'},
                {'category': 'certification', 'topic': 'CISSP 보안 자격증 취득 가이드', 'keywords': ['cissp', '보안', '자격증'], 'length': 'long'},
                
                # 개발 도구 & 방법론
                {'category': 'tools', 'topic': 'Git 고급 워크플로우와 협업', 'keywords': ['git', '워크플로우', '협업'], 'length': 'medium'},
                {'category': 'tools', 'topic': 'VS Code 생산성 극대화 팁', 'keywords': ['vscode', '생산성', '팁'], 'length': 'medium'},
                {'category': 'tools', 'topic': 'IntelliJ IDEA 고급 활용법', 'keywords': ['intellij', 'idea', '활용법'], 'length': 'medium'},
                {'category': 'methodology', 'topic': '애자일 개발 방법론 실천', 'keywords': ['애자일', '개발방법론', '실천'], 'length': 'medium'},
                {'category': 'methodology', 'topic': 'DDD(도메인 주도 설계) 실전 적용', 'keywords': ['ddd', '도메인', '설계'], 'length': 'long'},
                
                # 성능 최적화 & 모니터링
                {'category': 'optimization', 'topic': '웹 성능 최적화 완전 가이드', 'keywords': ['웹성능', '최적화', '속도'], 'length': 'long'},
                {'category': 'monitoring', 'topic': 'Prometheus & Grafana 모니터링', 'keywords': ['prometheus', 'grafana', '모니터링'], 'length': 'medium'},
                {'category': 'monitoring', 'topic': 'ELK 스택으로 로그 분석', 'keywords': ['elk', '로그', '분석'], 'length': 'medium'},
            ]
        elif site == 'untab':
            # untab.co.kr - 부동산, 경매, 투자, 정책 정보 (다양한 카테고리로 확장)
            return [
                # 부동산 경매 전문
                {'category': 'auction', 'topic': '부동산 경매 입찰 전 완벽 체크리스트', 'keywords': ['부동산경매', '입찰', '체크포인트'], 'length': 'long'},
                {'category': 'auction', 'topic': '이주의 주목할만한 경매 물건 분석', 'keywords': ['경매물건', '투자정보', '분석'], 'length': 'medium'},
                {'category': 'auction', 'topic': '경매 권리분석 실무 가이드', 'keywords': ['권리분석', '실무', '경매'], 'length': 'long'},
                {'category': 'auction', 'topic': '공매와 경매의 차이점과 전략', 'keywords': ['공매', '경매', '투자전략'], 'length': 'medium'},
                {'category': 'auction', 'topic': '경매 낙찰 후 소유권 이전 절차', 'keywords': ['낙찰', '소유권이전', '절차'], 'length': 'medium'},
                {'category': 'auction', 'topic': '부동산 경매 현장 답사 포인트', 'keywords': ['경매답사', '현장', '포인트'], 'length': 'medium'},
                {'category': 'auction', 'topic': '경매 유찰 부동산 투자 전략', 'keywords': ['유찰', '투자전략', '경매'], 'length': 'medium'},
                {'category': 'auction', 'topic': '상업용 부동산 경매 투자 가이드', 'keywords': ['상업용', '부동산경매', '투자'], 'length': 'long'},
                
                # 부동산 투자 & 시장분석
                {'category': 'investment', 'topic': '2025년 부동산 시장 전망과 투자 전략', 'keywords': ['부동산시장', '2025년', '투자전략'], 'length': 'long'},
                {'category': 'investment', 'topic': '지역별 부동산 투자 수익률 분석', 'keywords': ['지역별', '투자수익률', '분석'], 'length': 'long'},
                {'category': 'investment', 'topic': '부동산 임대수익 극대화 방법', 'keywords': ['임대수익', '극대화', '방법'], 'length': 'medium'},
                {'category': 'investment', 'topic': '신축 vs 기존 부동산 투자 비교', 'keywords': ['신축', '기존', '투자비교'], 'length': 'medium'},
                {'category': 'investment', 'topic': '부동산 투자 시기 판단법', 'keywords': ['투자시기', '판단', '타이밍'], 'length': 'medium'},
                {'category': 'investment', 'topic': '리츠(REITs) 투자 완전 가이드', 'keywords': ['리츠', 'reits', '투자'], 'length': 'long'},
                {'category': 'investment', 'topic': '부동산 펀드 투자 전략', 'keywords': ['부동산펀드', '투자전략', '수익'], 'length': 'medium'},
                
                # 부동산 정책 & 제도
                {'category': 'policy', 'topic': '2025년 부동산 정책 변화 완전정리', 'keywords': ['부동산정책', '2025년', '변화'], 'length': 'long'},
                {'category': 'policy', 'topic': '기획재정부 부동산 관련 정책 분석', 'keywords': ['기획재정부', '정책분석', '부동산'], 'length': 'medium'},
                {'category': 'policy', 'topic': '주택공급 확대 정책과 시장 영향', 'keywords': ['주택공급', '정책', '시장영향'], 'length': 'medium'},
                {'category': 'policy', 'topic': '부동산 세제 개편 내용과 대응법', 'keywords': ['부동산세제', '개편', '대응법'], 'length': 'long'},
                {'category': 'policy', 'topic': '임대차보호법 개정 사항 정리', 'keywords': ['임대차보호법', '개정', '정리'], 'length': 'medium'},
                {'category': 'policy', 'topic': '주택담보대출 규제 변화와 대응', 'keywords': ['주택담보대출', '규제', '대응'], 'length': 'medium'},
                {'category': 'policy', 'topic': '재개발 재건축 정책 변화 분석', 'keywords': ['재개발', '재건축', '정책변화'], 'length': 'long'},
                
                # 부동산 법률 & 계약
                {'category': 'legal', 'topic': '부동산 계약 시 주의사항 완전정리', 'keywords': ['부동산계약', '주의사항', '정리'], 'length': 'long'},
                {'category': 'legal', 'topic': '전세보증금 반환보증보험 가이드', 'keywords': ['전세보증금', '반환보증보험', '가이드'], 'length': 'medium'},
                {'category': 'legal', 'topic': '부동산 중개수수료 계산과 절약법', 'keywords': ['중개수수료', '계산', '절약'], 'length': 'medium'},
                {'category': 'legal', 'topic': '부동산 등기 절차와 비용 정리', 'keywords': ['부동산등기', '절차', '비용'], 'length': 'medium'},
                {'category': 'legal', 'topic': '부동산 분쟁 해결 방법과 사례', 'keywords': ['부동산분쟁', '해결방법', '사례'], 'length': 'long'},
                
                # 부동산 금융 & 대출
                {'category': 'finance', 'topic': '주택담보대출 금리 비교와 선택법', 'keywords': ['주택담보대출', '금리비교', '선택법'], 'length': 'medium'},
                {'category': 'finance', 'topic': '부동산 투자를 위한 대출 활용법', 'keywords': ['부동산투자', '대출활용', '방법'], 'length': 'long'},
                {'category': 'finance', 'topic': '전세자금대출 완전 가이드', 'keywords': ['전세자금대출', '가이드', '조건'], 'length': 'medium'},
                {'category': 'finance', 'topic': 'DSR 규제와 대출한도 계산법', 'keywords': ['dsr', '규제', '대출한도'], 'length': 'medium'},
                {'category': 'finance', 'topic': '부동산 투자 수익률 계산 방법', 'keywords': ['투자수익률', '계산', '방법'], 'length': 'medium'},
                
                # 부동산 세금 & 절세
                {'category': 'tax', 'topic': '부동산 취득세 계산과 절세 방법', 'keywords': ['취득세', '계산', '절세'], 'length': 'medium'},
                {'category': 'tax', 'topic': '부동산 양도소득세 완전정리', 'keywords': ['양도소득세', '정리', '계산'], 'length': 'long'},
                {'category': 'tax', 'topic': '종합부동산세 대상과 절세 전략', 'keywords': ['종합부동산세', '절세전략', '대상'], 'length': 'long'},
                {'category': 'tax', 'topic': '부동산 임대소득세 신고 가이드', 'keywords': ['임대소득세', '신고', '가이드'], 'length': 'medium'},
                {'category': 'tax', 'topic': '1주택자 비과세 요건과 활용법', 'keywords': ['1주택자', '비과세', '요건'], 'length': 'medium'},
                
                # 지역별 부동산 분석
                {'category': 'regional', 'topic': '서울 강남 부동산 시장 분석', 'keywords': ['서울강남', '부동산시장', '분석'], 'length': 'long'},
                {'category': 'regional', 'topic': '경기도 신도시 개발 현황과 전망', 'keywords': ['경기도', '신도시', '개발현황'], 'length': 'long'},
                {'category': 'regional', 'topic': '부산 해운대 부동산 투자 가이드', 'keywords': ['부산해운대', '부동산투자', '가이드'], 'length': 'medium'},
                {'category': 'regional', 'topic': '대구 수성구 아파트 시장 동향', 'keywords': ['대구수성구', '아파트시장', '동향'], 'length': 'medium'},
                {'category': 'regional', 'topic': '인천 송도 국제도시 부동산 전망', 'keywords': ['인천송도', '국제도시', '부동산전망'], 'length': 'medium'},
                
                # 부동산 트렌드 & 미래
                {'category': 'trend', 'topic': '스마트홈 기술이 부동산에 미치는 영향', 'keywords': ['스마트홈', '기술', '부동산영향'], 'length': 'medium'},
                {'category': 'trend', 'topic': '친환경 건축과 그린 부동산 트렌드', 'keywords': ['친환경건축', '그린부동산', '트렌드'], 'length': 'medium'},
                {'category': 'trend', 'topic': '부동산 디지털 전환과 프롭테크', 'keywords': ['디지털전환', '프롭테크', '부동산'], 'length': 'long'},
                {'category': 'trend', 'topic': '코워킹 스페이스와 상업부동산 변화', 'keywords': ['코워킹', '상업부동산', '변화'], 'length': 'medium'},
                {'category': 'trend', 'topic': '고령화 사회와 실버타운 투자', 'keywords': ['고령화사회', '실버타운', '투자'], 'length': 'medium'},
            ]
        elif site == 'skewese':
            # skewese.com - 역사, 문화, 라이프스타일 (다양한 카테고리로 확장)
            return [
                # 한국사 - 고대
                {'category': 'koreanhistory', 'topic': '고구려 광개토대왕의 정복 활동과 업적', 'keywords': ['고구려', '광개토대왕', '정복'], 'length': 'long'},
                {'category': 'koreanhistory', 'topic': '백제 근초고왕 시대의 발전과 문화', 'keywords': ['백제', '근초고왕', '문화'], 'length': 'medium'},
                {'category': 'koreanhistory', 'topic': '신라 통일의 과정과 역사적 의미', 'keywords': ['신라', '통일', '의미'], 'length': 'long'},
                {'category': 'koreanhistory', 'topic': '가야 연맹의 철 문화와 발달', 'keywords': ['가야', '철문화', '발달'], 'length': 'medium'},
                
                # 한국사 - 중세/근세
                {'category': 'koreanhistory', 'topic': '고려 몽골 침입과 강화도 항쟁', 'keywords': ['고려', '몽골침입', '강화도'], 'length': 'long'},
                {'category': 'koreanhistory', 'topic': '조선 세종대왕의 문화 정치와 업적', 'keywords': ['조선', '세종대왕', '문화정치'], 'length': 'long'},
                {'category': 'koreanhistory', 'topic': '임진왜란과 이순신의 활약', 'keywords': ['임진왜란', '이순신', '활약'], 'length': 'long'},
                {'category': 'koreanhistory', 'topic': '정조의 개혁 정치와 화성 건설', 'keywords': ['정조', '개혁정치', '화성'], 'length': 'medium'},
                {'category': 'koreanhistory', 'topic': '흥선대원군의 개혁과 쇄국정책', 'keywords': ['흥선대원군', '개혁', '쇄국정책'], 'length': 'medium'},
                
                # 한국사 - 근현대
                {'category': 'koreanhistory', 'topic': '개항기 조선의 근대화 과정', 'keywords': ['개항기', '조선', '근대화'], 'length': 'long'},
                {'category': 'koreanhistory', 'topic': '일제강점기 독립운동의 전개', 'keywords': ['일제강점기', '독립운동', '전개'], 'length': 'long'},
                {'category': 'koreanhistory', 'topic': '3.1운동의 배경과 전개 과정', 'keywords': ['3.1운동', '배경', '전개'], 'length': 'long'},
                {'category': 'koreanhistory', 'topic': '한국전쟁의 원인과 영향', 'keywords': ['한국전쟁', '원인', '영향'], 'length': 'long'},
                {'category': 'koreanhistory', 'topic': '4.19혁명과 민주주의 발전', 'keywords': ['4.19혁명', '민주주의', '발전'], 'length': 'medium'},
                
                # 세계사 - 고대
                {'category': 'worldhistory', 'topic': '고대 이집트 문명과 파라오의 권력', 'keywords': ['고대이집트', '파라오', '권력'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '메소포타미아 문명과 함무라비 법전', 'keywords': ['메소포타미아', '함무라비', '법전'], 'length': 'medium'},
                {'category': 'worldhistory', 'topic': '고대 그리스 민주정치와 철학', 'keywords': ['고대그리스', '민주정치', '철학'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '로마 제국의 성장과 멸망', 'keywords': ['로마제국', '성장', '멸망'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '인더스 문명의 도시 계획과 문화', 'keywords': ['인더스문명', '도시계획', '문화'], 'length': 'medium'},
                
                # 세계사 - 중세/근세
                {'category': 'worldhistory', 'topic': '중세 유럽의 봉건제도와 기사문화', 'keywords': ['중세유럽', '봉건제도', '기사문화'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '십자군 전쟁의 배경과 결과', 'keywords': ['십자군', '전쟁', '결과'], 'length': 'medium'},
                {'category': 'worldhistory', 'topic': '르네상스 시대의 예술과 과학 혁명', 'keywords': ['르네상스', '예술', '과학혁명'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '몽골 제국의 확장과 실크로드', 'keywords': ['몽골제국', '확장', '실크로드'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '대항해시대와 신대륙 발견', 'keywords': ['대항해시대', '신대륙', '발견'], 'length': 'medium'},
                
                # 세계사 - 근현대
                {'category': 'worldhistory', 'topic': '프랑스 대혁명과 나폴레옹 시대', 'keywords': ['프랑스대혁명', '나폴레옹', '시대'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '산업혁명과 사회 변화', 'keywords': ['산업혁명', '사회변화', '영향'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '제1차 세계대전의 원인과 결과', 'keywords': ['1차대전', '원인', '결과'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '제2차 세계대전과 홀로코스트', 'keywords': ['2차대전', '홀로코스트', '역사'], 'length': 'long'},
                {'category': 'worldhistory', 'topic': '냉전 시대의 세계 질서', 'keywords': ['냉전', '세계질서', '대립'], 'length': 'medium'},
                
                # 전통 문화 & 예술
                {'category': 'culture', 'topic': '한국 전통 건축의 아름다움과 과학', 'keywords': ['전통건축', '아름다움', '과학'], 'length': 'medium'},
                {'category': 'culture', 'topic': '고려청자와 조선백자의 예술 세계', 'keywords': ['고려청자', '조선백자', '예술'], 'length': 'medium'},
                {'category': 'culture', 'topic': '한복의 변천사와 현대적 계승', 'keywords': ['한복', '변천사', '현대계승'], 'length': 'medium'},
                {'category': 'culture', 'topic': '궁중음식의 역사와 문화적 의미', 'keywords': ['궁중음식', '역사', '문화의미'], 'length': 'medium'},
                {'category': 'culture', 'topic': '한국 전통 음악의 특징과 발전', 'keywords': ['전통음악', '특징', '발전'], 'length': 'medium'},
                
                # 철학 & 사상
                {'category': 'philosophy', 'topic': '공자의 유교 사상과 현대적 의미', 'keywords': ['공자', '유교사상', '현대의미'], 'length': 'long'},
                {'category': 'philosophy', 'topic': '노자의 도교 철학과 무위자연', 'keywords': ['노자', '도교철학', '무위자연'], 'length': 'medium'},
                {'category': 'philosophy', 'topic': '플라톤의 이데아론과 동굴의 비유', 'keywords': ['플라톤', '이데아론', '동굴비유'], 'length': 'long'},
                {'category': 'philosophy', 'topic': '아리스토텔레스의 윤리학과 덕의 철학', 'keywords': ['아리스토텔레스', '윤리학', '덕철학'], 'length': 'medium'},
                {'category': 'philosophy', 'topic': '칸트의 도덕 철학과 정언명령', 'keywords': ['칸트', '도덕철학', '정언명령'], 'length': 'long'},
                
                # 현대 라이프스타일
                {'category': 'lifestyle', 'topic': '미니멀 라이프의 철학과 실천 방법', 'keywords': ['미니멀라이프', '철학', '실천'], 'length': 'medium'},
                {'category': 'lifestyle', 'topic': '북유럽 휘게 문화와 행복한 삶', 'keywords': ['북유럽', '휘게', '행복'], 'length': 'medium'},
                {'category': 'lifestyle', 'topic': '일본의 와비사비 미학과 불완전함의 아름다움', 'keywords': ['와비사비', '미학', '불완전함'], 'length': 'medium'},
                {'category': 'lifestyle', 'topic': '명상과 마음챙김의 과학적 효과', 'keywords': ['명상', '마음챙김', '과학효과'], 'length': 'medium'},
                {'category': 'lifestyle', 'topic': '디지털 디톡스와 정신 건강', 'keywords': ['디지털디톡스', '정신건강', '방법'], 'length': 'medium'},
                
                # 건강 & 웰니스
                {'category': 'health', 'topic': '면역력 강화를 위한 생활습관', 'keywords': ['면역력', '강화', '생활습관'], 'length': 'medium'},
                {'category': 'health', 'topic': '장수의 비밀과 블루존 사람들', 'keywords': ['장수', '비밀', '블루존'], 'length': 'medium'},
                {'category': 'health', 'topic': '스트레스 관리와 정신 건강 유지법', 'keywords': ['스트레스관리', '정신건강', '유지법'], 'length': 'medium'},
                {'category': 'health', 'topic': '숙면의 과학과 질 좋은 잠자리', 'keywords': ['숙면', '과학', '잠자리'], 'length': 'medium'},
                
                # 환경 & 지속가능성
                {'category': 'environment', 'topic': '제로웨이스트 생활의 시작과 실천', 'keywords': ['제로웨이스트', '생활', '실천'], 'length': 'medium'},
                {'category': 'environment', 'topic': '비건 라이프스타일과 지구 환경', 'keywords': ['비건', '라이프스타일', '환경'], 'length': 'medium'},
                {'category': 'environment', 'topic': '도시 농업과 지속 가능한 먹거리', 'keywords': ['도시농업', '지속가능', '먹거리'], 'length': 'medium'},
                {'category': 'environment', 'topic': '재활용과 업사이클링의 창조적 실천', 'keywords': ['재활용', '업사이클링', '창조'], 'length': 'medium'},
                
                # 여행 & 문화 체험
                {'category': 'travel', 'topic': '역사 유적지를 통해 보는 세계사', 'keywords': ['역사유적지', '세계사', '여행'], 'length': 'long'},
                {'category': 'travel', 'topic': '각국의 전통 축제와 문화적 의미', 'keywords': ['전통축제', '문화의미', '각국'], 'length': 'medium'},
                {'category': 'travel', 'topic': '슬로우 트래블과 지역 문화 체험', 'keywords': ['슬로우트래블', '지역문화', '체험'], 'length': 'medium'},
                {'category': 'travel', 'topic': '박물관과 미술관에서 만나는 역사', 'keywords': ['박물관', '미술관', '역사'], 'length': 'medium'},
            ]
        elif site == 'tistory':
            # tistory - 시사, 트렌드, 현대 이슈 (다양한 카테고리로 확장)
            return [
                # IT & 기술 트렌드
                {'category': 'tech', 'topic': '2025년 AI 기술 발전과 산업 혁신', 'keywords': ['AI기술', '2025년', '산업혁신'], 'length': 'long'},
                {'category': 'tech', 'topic': 'ChatGPT와 생성형 AI의 비즈니스 활용', 'keywords': ['chatgpt', '생성AI', '비즈니스'], 'length': 'long'},
                {'category': 'tech', 'topic': '메타버스 플랫폼의 현재와 미래 전망', 'keywords': ['메타버스', '플랫폼', '미래전망'], 'length': 'medium'},
                {'category': 'tech', 'topic': '블록체인 기술의 실용적 활용 사례', 'keywords': ['블록체인', '활용사례', '실용성'], 'length': 'medium'},
                {'category': 'tech', 'topic': '6G 통신 기술과 초연결 사회', 'keywords': ['6G통신', '초연결사회', '기술'], 'length': 'medium'},
                {'category': 'tech', 'topic': '양자컴퓨팅의 현실화와 파급효과', 'keywords': ['양자컴퓨팅', '현실화', '파급효과'], 'length': 'long'},
                {'category': 'tech', 'topic': '자율주행차 기술 발전과 교통 혁신', 'keywords': ['자율주행차', '기술발전', '교통혁신'], 'length': 'medium'},
                
                # 경제 & 금융 트렌드
                {'category': 'economy', 'topic': '글로벌 인플레이션과 경제 전망', 'keywords': ['글로벌인플레이션', '경제전망', '물가'], 'length': 'long'},
                {'category': 'economy', 'topic': '가상화폐 시장의 변화와 투자 전망', 'keywords': ['가상화폐', '시장변화', '투자전망'], 'length': 'medium'},
                {'category': 'economy', 'topic': 'ESG 경영과 지속가능한 투자', 'keywords': ['ESG경영', '지속가능투자', '기업'], 'length': 'long'},
                {'category': 'economy', 'topic': '중앙은행 디지털화폐(CBDC) 도입 현황', 'keywords': ['CBDC', '디지털화폐', '중앙은행'], 'length': 'medium'},
                {'category': 'economy', 'topic': '신흥국 경제 성장과 글로벌 영향', 'keywords': ['신흥국경제', '성장', '글로벌영향'], 'length': 'medium'},
                {'category': 'economy', 'topic': '스타트업 생태계와 벤처 투자 트렌드', 'keywords': ['스타트업', '생태계', '벤처투자'], 'length': 'long'},
                
                # 사회 이슈 & 정책
                {'category': 'society', 'topic': '고령화 사회와 미래 사회보장 제도', 'keywords': ['고령화사회', '사회보장', '제도'], 'length': 'long'},
                {'category': 'society', 'topic': '저출산 문제와 인구 정책 방향', 'keywords': ['저출산', '인구정책', '방향'], 'length': 'long'},
                {'category': 'society', 'topic': '원격근무 확산과 일하는 방식의 변화', 'keywords': ['원격근무', '확산', '일하는방식'], 'length': 'medium'},
                {'category': 'society', 'topic': '젠더 갈등과 성평등 사회 구축', 'keywords': ['젠더갈등', '성평등', '사회구축'], 'length': 'long'},
                {'category': 'society', 'topic': '청년 주거 문제와 정책 대안', 'keywords': ['청년주거', '문제', '정책대안'], 'length': 'medium'},
                {'category': 'society', 'topic': '다문화 사회와 사회 통합 방안', 'keywords': ['다문화사회', '사회통합', '방안'], 'length': 'medium'},
                
                # 환경 & 기후변화
                {'category': 'environment', 'topic': '탄소중립 실현을 위한 정책과 기술', 'keywords': ['탄소중립', '실현', '정책기술'], 'length': 'long'},
                {'category': 'environment', 'topic': '신재생 에너지 산업의 성장과 전망', 'keywords': ['신재생에너지', '산업성장', '전망'], 'length': 'long'},
                {'category': 'environment', 'topic': '플라스틱 오염과 순환 경제 구축', 'keywords': ['플라스틱오염', '순환경제', '구축'], 'length': 'medium'},
                {'category': 'environment', 'topic': '기후변화로 인한 자연재해 대응책', 'keywords': ['기후변화', '자연재해', '대응책'], 'length': 'medium'},
                {'category': 'environment', 'topic': '도시 열섬현상과 녹색 도시 계획', 'keywords': ['도시열섬', '녹색도시', '계획'], 'length': 'medium'},
                
                # 국제 정치 & 외교
                {'category': 'international', 'topic': '미중 갈등과 글로벌 질서 재편', 'keywords': ['미중갈등', '글로벌질서', '재편'], 'length': 'long'},
                {'category': 'international', 'topic': '러시아-우크라이나 전쟁의 국제적 영향', 'keywords': ['러우전쟁', '국제영향', '분석'], 'length': 'long'},
                {'category': 'international', 'topic': '북한 핵 문제와 한반도 평화 프로세스', 'keywords': ['북한핵', '한반도평화', '프로세스'], 'length': 'long'},
                {'category': 'international', 'topic': '인도-태평양 전략과 지역 안보', 'keywords': ['인도태평양', '전략', '지역안보'], 'length': 'medium'},
                {'category': 'international', 'topic': 'NATO 확장과 유럽 안보 체제', 'keywords': ['NATO확장', '유럽안보', '체제'], 'length': 'medium'},
                
                # 교육 & 미래 세대
                {'category': 'education', 'topic': '디지털 교육 혁신과 에듀테크', 'keywords': ['디지털교육', '혁신', '에듀테크'], 'length': 'medium'},
                {'category': 'education', 'topic': '온라인 학습의 미래와 교육 격차', 'keywords': ['온라인학습', '미래', '교육격차'], 'length': 'medium'},
                {'category': 'education', 'topic': 'MZ세대의 가치관과 사회 변화', 'keywords': ['MZ세대', '가치관', '사회변화'], 'length': 'medium'},
                {'category': 'education', 'topic': '평생 교육 시대와 리스킬링', 'keywords': ['평생교육', '시대', '리스킬링'], 'length': 'medium'},
                
                # 헬스케어 & 의료 혁신
                {'category': 'healthcare', 'topic': '개인 맞춤 의료와 정밀 의학', 'keywords': ['개인맞춤의료', '정밀의학', '혁신'], 'length': 'long'},
                {'category': 'healthcare', 'topic': '디지털 헬스케어와 원격 진료', 'keywords': ['디지털헬스케어', '원격진료', '의료'], 'length': 'medium'},
                {'category': 'healthcare', 'topic': '고령화와 치매 예방 연구 동향', 'keywords': ['고령화', '치매예방', '연구동향'], 'length': 'medium'},
                {'category': 'healthcare', 'topic': '팬데믹 이후 공중보건 체계 변화', 'keywords': ['팬데믹', '공중보건', '체계변화'], 'length': 'long'},
                
                # 문화 & 라이프스타일 트렌드
                {'category': 'lifestyle', 'topic': 'K-컬처의 글로벌 확산과 문화 산업', 'keywords': ['K컬처', '글로벌확산', '문화산업'], 'length': 'long'},
                {'category': 'lifestyle', 'topic': 'OTT 플랫폼과 콘텐츠 산업 변화', 'keywords': ['OTT플랫폼', '콘텐츠산업', '변화'], 'length': 'medium'},
                {'category': 'lifestyle', 'topic': '워라밸 문화와 일과 삶의 균형', 'keywords': ['워라밸', '문화', '일삶균형'], 'length': 'medium'},
                {'category': 'lifestyle', 'topic': '펫코노미 성장과 반려동물 문화', 'keywords': ['펫코노미', '성장', '반려동물'], 'length': 'medium'},
                {'category': 'lifestyle', 'topic': '비건 트렌드와 지속가능한 소비', 'keywords': ['비건트렌드', '지속가능소비', '라이프스타일'], 'length': 'medium'},
                
                # 미래 예측 & 전망
                {'category': 'future', 'topic': '2030년 미래 직업과 일자리 변화', 'keywords': ['2030년', '미래직업', '일자리변화'], 'length': 'long'},
                {'category': 'future', 'topic': '스마트시티 구축과 도시의 미래', 'keywords': ['스마트시티', '구축', '도시미래'], 'length': 'medium'},
                {'category': 'future', 'topic': '우주 산업의 발전과 상업화', 'keywords': ['우주산업', '발전', '상업화'], 'length': 'medium'},
                {'category': 'future', 'topic': '로봇과 인간의 공존 사회', 'keywords': ['로봇', '인간공존', '사회'], 'length': 'medium'},
                {'category': 'future', 'topic': '바이오 기술과 인간 수명 연장', 'keywords': ['바이오기술', '수명연장', '인간'], 'length': 'long'},
            ]
        else:
            # 기본 개발 주제 (fallback)
            return [
                {
                    'category': 'programming',
                    'topic': 'Python 기초 프로그래밍',
                    'keywords': ['python', '프로그래밍'],
                    'length': 'medium'
                }
            ]

    def _generate_topic_plans(self) -> List[Dict]:
        """사이트별 다양한 주제 계획 생성"""
        all_topics = []
        
        # 각 사이트별 주제 풀 생성
        unpre_topics = self._get_site_topic_plans('unpre')
        untab_topics = self._get_site_topic_plans('untab')
        skewese_topics = self._get_site_topic_plans('skewese')
        tistory_topics = self._get_site_topic_plans('tistory')
        
        # 28개 항목을 사이트별로 순환 배치 (4개 사이트 × 7일)
        for i in range(28):
            if i % 4 == 0:  # unpre
                topic_idx = (i // 4) % len(unpre_topics)
                all_topics.append(unpre_topics[topic_idx])
            elif i % 4 == 1:  # untab
                topic_idx = (i // 4) % len(untab_topics)
                all_topics.append(untab_topics[topic_idx])
            elif i % 4 == 2:  # skewese
                topic_idx = (i // 4) % len(skewese_topics)
                all_topics.append(skewese_topics[topic_idx])
            else:  # tistory
                topic_idx = (i // 4) % len(tistory_topics)
                all_topics.append(tistory_topics[topic_idx])
        
        return all_topics
    
    def get_weekly_schedule(self, start_date: datetime = None) -> Dict:
        """일주일치 스케줄 조회"""
        try:
            if start_date is None:
                # 이번 주 월요일
                today = datetime.now().date()
                days_ahead = 0 - today.weekday()
                start_date = today + timedelta(days=days_ahead)
            
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT day_of_week, site, topic_category, specific_topic, 
                           keywords, target_length, status, published_url
                    FROM publishing_schedule 
                    WHERE week_start_date = %s
                    ORDER BY day_of_week, site
                """, (start_date,))
                
                schedule = {}
                day_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
                
                for day in range(7):
                    schedule[day] = {
                        'day_name': day_names[day],
                        'date': start_date + timedelta(days=day),
                        'sites': {}
                    }
                
                for row in cursor.fetchall():
                    day_of_week, site, category, topic, keywords, length, status, url = row
                    
                    schedule[day_of_week]['sites'][site] = {
                        'category': category,
                        'topic': topic,
                        'keywords': keywords,
                        'length': length,
                        'status': status,
                        'url': url
                    }
                
                return {
                    'week_start': start_date,
                    'schedule': schedule
                }
                
        except Exception as e:
            print(f"[SCHEDULE] 스케줄 조회 오류: {e}")
            return {}
    
    def check_duplicate_content(self, site: str, topic: str, keywords: List[str]) -> bool:
        """발행된 컨텐츠와 중복 여부 확인"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                # 기존 발행된 컨텐츠에서 유사한 주제 검색
                cursor.execute("""
                    SELECT specific_topic, keywords FROM publishing_schedule 
                    WHERE site = %s AND status = 'published'
                """, (site,))
                
                published_content = cursor.fetchall()
                
                for pub_topic, pub_keywords in published_content:
                    # 주제 유사도 검사 (간단한 키워드 매칭)
                    if self._is_similar_content(topic, keywords, pub_topic, pub_keywords):
                        print(f"[DUPLICATE] {site} 중복 컨텐츠 발견: {topic} vs {pub_topic}")
                        return True
                
                return False
                
        except Exception as e:
            print(f"[DUPLICATE] 중복 검사 오류: {e}")
            return False
    
    def _is_similar_content(self, topic1: str, keywords1: List[str], 
                           topic2: str, keywords2: List[str]) -> bool:
        """두 컨텐츠의 유사도 검사"""
        try:
            # 키워드 교집합 확인 (50% 이상 겹치면 중복으로 판단)
            set1 = set([kw.lower().strip() for kw in keywords1] if keywords1 else [])
            set2 = set([kw.lower().strip() for kw in keywords2] if keywords2 else [])
            
            if len(set1) == 0 or len(set2) == 0:
                return False
                
            intersection = set1.intersection(set2)
            similarity = len(intersection) / min(len(set1), len(set2))
            
            return similarity >= 0.5
            
        except Exception as e:
            print(f"[SIMILARITY] 유사도 검사 오류: {e}")
            return False

    def update_schedule_status(self, week_start: datetime, day: int, site: str, 
                              status: str, content_id: int = None, url: str = None) -> bool:
        """스케줄 상태 업데이트"""
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                update_fields = ["status = %s", "updated_at = CURRENT_TIMESTAMP"]
                params = [status]
                
                if content_id:
                    update_fields.append("generated_content_id = %s")
                    params.append(content_id)
                
                if url:
                    update_fields.append("published_url = %s")
                    params.append(url)
                
                params.extend([week_start, day, site])
                
                cursor.execute(f"""
                    UPDATE publishing_schedule 
                    SET {', '.join(update_fields)}
                    WHERE week_start_date = %s AND day_of_week = %s AND site = %s
                """, params)
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"[SCHEDULE] 상태 업데이트 오류: {e}")
            return False

# 전역 인스턴스
schedule_manager = ScheduleManager()