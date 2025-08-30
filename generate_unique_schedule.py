"""
8-9월 중복 없는 고유 주제 생성 스크립트
- 61일간 각 사이트별 122개 고유 주제
- 현재 트렌드와 인기 검색어 반영
- 광고 수익 최적화를 위한 SEO 친화적 주제
"""

from src.utils.postgresql_database import PostgreSQLDatabase
from datetime import date, timedelta
import calendar

def generate_unique_monthly_schedule():
    """8-9월 중복 없는 고유 주제 생성"""
    
    # 2025년 8-9월 트렌드와 검색량 높은 주제들
    site_topics = {
        'skewese': {
            # 건강/웰니스 (31개)
            '건강/웰니스': [
                '2025년 최신 다이어트 트렌드 GLP-1 약물 완벽 가이드',
                '간헐적 단식 16:8 vs 5:2 효과 비교 분석',
                '혈당 스파이크 막는 식사 순서와 타이밍',
                '만성피로 증후군 자가진단과 극복법',
                '장 건강 개선을 위한 프로바이오틱스 선택 가이드',
                '수면 부채 해결하는 과학적 방법',
                '스마트워치로 관리하는 건강 데이터 활용법',
                '코로나 후유증 롱코비드 관리 전략',
                '비타민 D 결핍 증상과 보충제 선택법',
                '근감소증 예방 단백질 섭취 가이드',
                '갱년기 증상 완화 천연 요법',
                '디지털 디톡스 실천 방법',
                '면역력 높이는 슈퍼푸드 10가지',
                '스트레스성 탈모 예방과 치료',
                '체지방 감소를 위한 HIIT 운동법',
                '당뇨병 전단계 관리 방법',
                '우울증 자가 관리 인지행동치료',
                '알레르기성 비염 완화 생활습관',
                '역류성 식도염 식단 관리법',
                '편두통 유발 요인과 예방법',
                '고혈압 낮추는 DASH 식단',
                '불면증 극복 수면위생 개선법',
                '관절염 통증 완화 운동법',
                '눈 건강 지키는 블루라이트 차단법',
                '치매 예방 두뇌 운동법',
                '폐경기 호르몬 대체요법 장단점',
                '청소년 성장기 영양 관리',
                '임신 준비 엽산 섭취 가이드',
                '노화 방지 항산화제 활용법',
                '만성 변비 해결 식이섬유 섭취법',
                '금연 성공 전략과 니코틴 대체요법'
            ],
            # 요리/레시피 (31개)
            '요리/레시피': [
                '에어프라이어 시간별 온도 설정 완벽 가이드',
                '키토 다이어트 일주일 식단표',
                '혼밥족을 위한 1인분 레시피 모음',
                '다이어트 도시락 일주일 메뉴',
                '채식주의자를 위한 단백질 레시피',
                '글루텐프리 베이킹 레시피 모음',
                '인스타그램 인기 카페 메뉴 재현',
                '전자레인지 5분 요리 레시피',
                '저탄고지 다이어트 레시피 30선',
                '밀프렙 일주일 식단 준비법',
                '비건 디저트 만들기',
                '한국식 브런치 메뉴 레시피',
                '다이어트 야식 레시피 모음',
                '저염식 맛있게 만드는 비법',
                '당뇨 환자를 위한 저당 레시피',
                '아이 편식 고치는 요리법',
                '캠핑 요리 레시피 베스트 20',
                '제철 과일 활용 디저트',
                '발효 음식 만들기 가이드',
                '집에서 만드는 미슐랭 요리',
                '다이어트 김밥 레시피 5가지',
                '저칼로리 파스타 레시피',
                '홈베이킹 실패 없는 레시피',
                '여름 보양식 레시피 모음',
                '아침 식사 대용 스무디 레시피',
                '저비용 고효율 자취 요리',
                '명절 음식 칼로리 줄이는 법',
                '술안주 레시피 베스트 30',
                '다이어트 치킨 레시피',
                '집에서 만드는 수제 버거',
                '저탄수화물 피자 만들기'
            ],
            # 역사/문화 (30개)
            '역사/문화': [
                '조선왕조실록에 기록된 팬데믹 대응',
                'K-컬처 세계 진출 역사와 미래',
                '한국 전통 차 문화의 현대적 해석',
                '고려청자와 백자의 미학적 가치',
                '한글 창제 원리와 과학성',
                '독립운동가들의 숨겨진 이야기',
                '한국 전통 건축의 친환경 지혜',
                '김치의 역사와 세계화 과정',
                '한복의 변천사와 현대 패션',
                '전통 민속놀이의 교육적 가치',
                '사찰 음식의 철학과 레시피',
                '한국 무형문화재 전승 현황',
                '고구려 벽화가 전하는 메시지',
                '세종대왕의 리더십과 혁신',
                '한국전쟁이 남긴 유산',
                '전통 장 담그기 문화',
                '한옥마을 관광 명소 가이드',
                '한국 신화와 전설 이야기',
                '조선시대 여성들의 삶',
                '고려 불교문화의 정수',
                '대한제국 근대화 과정',
                '한국 전통음악의 세계',
                '민주화 운동의 역사적 의미',
                '한국 도자기 명품 감상법',
                '전통 혼례 문화와 현대 결혼식',
                '삼국시대 국제 교류사',
                '한국 전통 의학 한의학 이해',
                '왕실 문화와 궁중 요리',
                '한국 서원의 교육 철학',
                '근현대사 주요 사건 정리'
            ],
            # 과학/기술 (30개)
            '과학/기술': [
                '양자컴퓨터가 바꿀 미래 기술',
                '제임스웹 망원경이 발견한 우주',
                '상온 초전도체 연구 현황',
                '뇌-컴퓨터 인터페이스 기술',
                '유전자 편집 CRISPR 기술의 미래',
                '화성 탐사 최신 발견',
                '핵융합 발전 상용화 전망',
                '메타물질과 투명망토 기술',
                '바이오프린팅 장기 제작 기술',
                '나노기술이 만드는 신소재',
                '기후변화 대응 지구공학 기술',
                '우주 엘리베이터 실현 가능성',
                '인공광합성 에너지 생산',
                '뇌과학으로 보는 의식의 비밀',
                '암흑물질과 암흑에너지 탐구',
                '줄기세포 치료 최신 동향',
                '시간여행의 과학적 가능성',
                '블랙홀 연구 최신 성과',
                '노화 역전 기술 연구',
                '인공 자궁 기술 개발 현황',
                '텔로미어와 수명 연장 연구',
                '뇌 오가노이드 연구 윤리',
                '우주 쓰레기 청소 기술',
                '해수 담수화 신기술',
                '탄소 포집 저장 기술',
                '초음속 여객기 개발 현황',
                '우주 관광 산업 전망',
                '인공 육류 생산 기술',
                '드론 택시 상용화 시점',
                '6G 통신 기술 전망'
            ]
        },
        'tistory': {
            # 엔터테인먼트 (31개)
            '엔터테인먼트': [
                '넷플릭스 vs 디즈니플러스 2025년 대작 라인업',
                'K-드라마 글로벌 OTT 진출 전략',
                '아이돌 서바이벌 프로그램 성공 공식',
                'AI 가상 아이돌 시대 도래',
                '숏폼 드라마 제작 붐 분석',
                '웹툰 원작 드라마 흥행 법칙',
                'K-팝 4세대 아이돌 판도 분석',
                '유튜브 쇼츠 vs 틱톡 콘텐츠 전쟁',
                '한국 영화 천만 관객 돌파 비결',
                '버추얼 콘서트 기술과 수익 모델',
                'OTT 오리지널 예능 트렌드',
                '인플루언서 연예인 전환 사례',
                '팬덤 경제학과 굿즈 시장',
                '리얼리티 데이팅쇼 인기 비결',
                '음원 차트 조작 논란과 대응',
                '연예인 유튜브 채널 성공 전략',
                'K-콘텐츠 IP 비즈니스 모델',
                '글로벌 팬미팅 온라인 플랫폼',
                '드라마 PPL 마케팅 효과',
                '아이돌 멤버 솔로 데뷔 전략',
                '예능 프로그램 포맷 수출',
                '뮤지컬 스타 캐스팅 전략',
                '독립영화 OTT 플랫폼 진출',
                '버라이어티쇼 MC 라인업 분석',
                '콘서트 티켓팅 전쟁 생존법',
                '드라마 OST 마케팅 전략',
                '예능 유니버스 구축 사례',
                '아이돌 리부트 프로젝트',
                '한류 3.0 시대 특징',
                '연예 기획사 주가 분석',
                '팬 사인회 진화하는 형태'
            ],
            # 게임/오락 (31개)
            '게임/오락': [
                'GTA6 출시 전 알아야 할 모든 것',
                '모바일 게임 과금 시스템 분석',
                'e스포츠 선수 연봉 순위',
                '스팀덱 vs ROG Ally 성능 비교',
                'AI NPC가 바꾸는 게임의 미래',
                '블록체인 게임 P2E 수익 구조',
                '언리얼 엔진 5 차세대 그래픽',
                '게임 스트리머 수익 창출 방법',
                '인디게임 성공 마케팅 전략',
                'VR 게임 멀미 해결 방법',
                '게임 중독 자가진단과 치료',
                '레트로 게임 리마스터 열풍',
                '게임 패스 구독 서비스 비교',
                '배틀로얄 게임 메타 분석',
                '모바일 게임 티어 시스템',
                'MMORPG 직업 밸런스 패치',
                '게임 내 경제 시스템 설계',
                '프로게이머 은퇴 후 진로',
                '게임 개발자 연봉과 전망',
                '클라우드 게이밍 서비스 비교',
                '게임 음악 작곡가 되는 법',
                '트위치 vs 유튜브 게임 방송',
                '게임 QA 테스터 직업 소개',
                '메타버스 게임 플랫폼 비교',
                '게임 번역가 되는 방법',
                'NFT 게임 아이템 거래',
                '게임 기획자 포트폴리오',
                '게임 그래픽 최적화 팁',
                '게임 커뮤니티 관리 노하우',
                '게임 대회 상금 순위',
                '차세대 콘솔 구매 가이드'
            ],
            # 트렌드/이슈 (30개)
            '트렌드/이슈': [
                'MZ세대 신조어 사전 2025',
                '도파민 디톡스 챌린지 효과',
                '미니멀 라이프 실천 가이드',
                'MBTI별 직업 추천과 궁합',
                '챗GPT 활용 부업 아이디어',
                '숏폼 콘텐츠 중독 현상',
                '알파세대 교육 트렌드',
                '구독경제 피로감 해결책',
                '리셀 테크 투자 수익률',
                '무인 매장 창업 수익성',
                '펫코노미 시장 규모 전망',
                '워케이션 인기 지역 TOP10',
                '탄소중립 라이프스타일',
                '디지털 노마드 비자 국가',
                '공유경제 서비스 활용법',
                '그린워싱 구별하는 방법',
                '갓생 살기 프로젝트',
                'ESG 경영 우수 기업',
                '메타버스 부동산 투자',
                '크리에이터 이코노미 시장',
                '시니어 디지털 교육 필요성',
                '제로웨이스트 샵 창업',
                '비건 라이프스타일 입문',
                '디지털 치료제 시장 전망',
                '실버 서퍼 소비 트렌드',
                '홈코노미 관련 주식',
                '언택트 서비스 진화',
                '리테일 테크 혁신 사례',
                '소셜 커머스 2.0 시대',
                '하이퍼 퍼스널라이제이션'
            ],
            # 경제/비즈니스 (30개)
            '경제/비즈니스': [
                '2025년 유망 스타트업 TOP20',
                '부동산 PF 대출 위기 전망',
                '전기차 보조금 정책 변화',
                '금리 인하 시기 예측',
                '반도체 산업 전망과 투자',
                '유니콘 기업 IPO 일정',
                '가상자산 규제 법안 영향',
                '배터리 산업 투자 포인트',
                '인플레이션 대응 자산 배분',
                '연금개혁안 상세 분석',
                '청년 창업 지원금 총정리',
                '해외 직구 관세 계산법',
                '프랜차이즈 창업 순위',
                '주식 세금 절세 전략',
                'REITs 투자 수익률 분석',
                '달러 환율 전망과 대응',
                '신용등급 올리는 방법',
                '퇴직연금 운용 전략',
                '소상공인 대출 지원 정책',
                '경제 지표 읽는 법',
                'ETF 투자 포트폴리오',
                '부동산 양도세 계산법',
                '스타트업 투자 유치 전략',
                '온라인 쇼핑몰 세금 신고',
                '가업승계 절세 방법',
                '해외 주식 투자 세금',
                '신용카드 혜택 비교',
                '대출 갈아타기 시기',
                '펀드 수수료 비교 분석',
                '경제 뉴스 해석하는 법'
            ]
        },
        'unpre': {
            # 교육/자기계발 (31개)
            '교육/자기계발': [
                '개발자 로드맵 2025 완벽 가이드',
                '비전공자 코딩 부트캠프 후기',
                'IT 자격증 취득 우선순위',
                '퇴사 없이 이직 준비하는 법',
                '개발자 포트폴리오 만들기',
                '해외 취업 비자 준비 과정',
                '온라인 강의 플랫폼 비교',
                '독학으로 개발자 되기',
                '코딩테스트 합격 전략',
                '기술 면접 예상 질문 100선',
                '개발자 연봉 협상 노하우',
                '사이드 프로젝트 아이디어',
                '오픈소스 기여 시작하기',
                '개발자 커뮤니티 활용법',
                '테크 블로그 운영 전략',
                '해커톤 참가 준비 가이드',
                '개발자 영어 공부법',
                '리더십 스킬 향상 방법',
                '번아웃 극복 실천법',
                '효율적인 코드리뷰 방법',
                '애자일 방법론 실무 적용',
                '개발자 이력서 작성법',
                'LinkedIn 프로필 최적화',
                '멘토링 프로그램 활용법',
                '자기주도 학습 전략',
                '시간 관리 앱 활용법',
                '개발자 커리어 전환 사례',
                '원격근무 생산성 향상법',
                '기술 세미나 네트워킹',
                '개발자 건강 관리법',
                '창의력 향상 트레이닝'
            ],
            # 프로그래밍/개발 (31개)
            '프로그래밍/개발': [
                'React 19 새로운 기능 총정리',
                'Next.js 14 App Router 완벽 가이드',
                'TypeScript 5.0 신기능 활용법',
                'Python FastAPI vs Django 비교',
                'Rust 언어가 뜨는 이유',
                'Go 언어 동시성 프로그래밍',
                'Flutter 3.0 크로스플랫폼 개발',
                'Spring Boot 3.0 마이그레이션',
                'Node.js 20 LTS 성능 개선',
                'Docker Compose 실무 활용',
                'Kubernetes 오케스트레이션',
                'GraphQL vs REST API 선택',
                'WebAssembly 활용 사례',
                'Svelte 4.0 반응형 프로그래밍',
                'Tailwind CSS 디자인 시스템',
                'PostgreSQL 성능 튜닝',
                'Redis 캐싱 전략 구현',
                'MongoDB 샤딩 아키텍처',
                'Git 브랜치 전략 비교',
                'CI/CD 파이프라인 구축',
                'AWS Lambda 서버리스 개발',
                'Vue 3 Composition API',
                'Microservices 설계 패턴',
                'Clean Code 원칙 실천',
                'TDD 실무 적용 사례',
                'WebSocket 실시간 통신',
                'OAuth 2.0 인증 구현',
                'PWA 프로그레시브 웹앱',
                'Electron 데스크톱 앱 개발',
                'React Native 앱 최적화',
                'Webpack 5 번들링 최적화'
            ],
            # AI/머신러닝 (30개)
            'AI/머신러닝': [
                'ChatGPT API 활용 프로젝트',
                'Stable Diffusion 이미지 생성',
                'LangChain RAG 시스템 구축',
                'Fine-tuning LLM 모델 실습',
                'Vector Database 비교 분석',
                'Prompt Engineering 고급 기법',
                'AutoML 플랫폼 활용법',
                'TensorFlow vs PyTorch 2025',
                'Transformer 모델 이해하기',
                'Computer Vision 프로젝트',
                'NLP 감정 분석 구현',
                'Reinforcement Learning 입문',
                'MLOps 파이프라인 구축',
                'Edge AI 임베디드 시스템',
                'Generative AI 비즈니스 활용',
                'AI 윤리와 편향성 해결',
                'Hugging Face 모델 활용',
                'YOLO v8 객체 탐지',
                'Time Series 예측 모델',
                'GAN 이미지 생성 원리',
                'Federated Learning 개념',
                'XAI 설명가능한 AI',
                'Kaggle 대회 입상 전략',
                'AI 모델 경량화 기법',
                'Multi-modal AI 시스템',
                'Speech Recognition 구현',
                'Recommendation System 설계',
                'Anomaly Detection 알고리즘',
                'AI 모델 배포 전략',
                'Quantum ML 미래 전망'
            ],
            # 기술/디지털 (30개)
            '기술/디지털': [
                '클라우드 비용 최적화 전략',
                '제로 트러스트 보안 모델',
                'DevOps 자동화 도구 비교',
                '마이크로서비스 모니터링',
                'Infrastructure as Code 실습',
                'API Gateway 설계 패턴',
                'Service Mesh 아키텍처',
                'Observability 구축 가이드',
                'Chaos Engineering 실무',
                'Event-Driven Architecture',
                'CQRS 패턴 구현 사례',
                'Domain-Driven Design 실전',
                'Serverless 비용 절감 방법',
                'Container Security Best Practice',
                'Multi-Cloud 전략 수립',
                'SRE 문화 도입 사례',
                'Platform Engineering 트렌드',
                'GitOps 워크플로우 구축',
                'FinOps 클라우드 비용 관리',
                'DataOps 데이터 파이프라인',
                'Blue-Green 배포 전략',
                'Canary Release 구현',
                'Feature Toggle 활용법',
                'API Versioning 전략',
                'Database Migration 도구',
                'Message Queue 시스템 비교',
                'Load Balancing 알고리즘',
                'CDN 최적화 전략',
                'WAF 보안 설정 가이드',
                'Backup & Recovery 계획'
            ]
        },
        'untab': {
            # 라이프스타일 (31개)
            '라이프스타일': [
                '1인 가구 인테리어 꿀팁 모음',
                '미니멀리스트 옷장 정리법',
                '홈카페 감성 인테리어 가이드',
                '반려동물과 함께 사는 집꾸미기',
                '재택근무 공간 만들기',
                '수납의 달인 되는 방법',
                '북유럽 스타일 인테리어',
                '식물 인테리어 관리 가이드',
                '원룸 공간 활용 아이디어',
                '계절별 홈데코 팁',
                '향초와 디퓨저 활용법',
                '홈트레이닝 공간 만들기',
                '주방 정리 수납 아이디어',
                '욕실 인테리어 셀프 시공',
                '베란다 텃밭 가꾸기',
                '수면 환경 개선 인테리어',
                '아이방 꾸미기 아이디어',
                '서재 공간 만들기',
                '현관 인테리어 포인트',
                '조명으로 분위기 바꾸기',
                'DIY 가구 만들기 프로젝트',
                '벽지 셀프 시공 가이드',
                '타일 시공 DIY 방법',
                '페인트 칠하기 기초',
                '커튼과 블라인드 선택법',
                '러그와 카펫 관리법',
                '계절별 침구 관리',
                '주방 가전 배치 팁',
                '수납장 정리 노하우',
                '거실 레이아웃 아이디어',
                '홈파티 데코레이션'
            ],
            # 패션/뷰티 (31개)
            '패션/뷰티': [
                '2025 F/W 패션 트렌드 분석',
                '퍼스널컬러 자가진단법',
                '체형별 코디 스타일링',
                '명품 가방 관리 보관법',
                '비건 화장품 브랜드 추천',
                '홈케어 피부관리 루틴',
                '탈모 예방 두피 관리법',
                '네일아트 셀프 디자인',
                '속눈썹 연장 관리 팁',
                '다이어트 후 옷 정리법',
                '계절별 스킨케어 루틴',
                '퍼스널 쇼퍼 활용법',
                '빈티지 쇼핑 명소 가이드',
                '운동화 세탁 관리법',
                '액세서리 보관 정리법',
                '헤어 스타일링 도구 사용법',
                '메이크업 브러시 세척법',
                '향수 레이어링 기법',
                '파운데이션 선택 가이드',
                '아이브로우 그리기 팁',
                '립스틱 오래 유지하는 법',
                '클렌징 제품 선택법',
                '자외선 차단제 고르기',
                '각질 제거 주기와 방법',
                '수분크림 vs 로션 차이',
                '앰플과 세럼 사용법',
                '마스크팩 효과적 사용법',
                '눈가 주름 관리법',
                '모공 축소 관리 팁',
                '미백 관리 홈케어',
                '안티에이징 루틴 구성'
            ],
            # 재정/투자 (30개)
            '재정/투자': [
                '2030 자산 1억 만들기 로드맵',
                '월 100만원 저축 전략',
                '신용카드 포인트 활용법',
                '청약통장 당첨 전략',
                'ISA 계좌 활용 절세법',
                '비과세 혜택 상품 총정리',
                '적금 금리 비교 사이트',
                '대출 상환 전략 수립',
                '보험 리모델링 필요성',
                '연말정산 환급 늘리기',
                '부동산 취득세 절감법',
                '월세 세액공제 받는 법',
                '주식 초보자 입문 가이드',
                '배당주 투자 전략',
                'ETF 정기 투자법',
                '해외주식 세금 정리',
                '가상화폐 투자 기초',
                '금 투자 방법 비교',
                'P2P 투자 리스크 관리',
                '펀드 수익률 읽는 법',
                '퇴직금 운용 전략',
                '노후자금 계산기 활용',
                '상속세 증여세 절세',
                '부부 재테크 전략',
                '자녀 용돈 관리법',
                '가계부 작성 어플 추천',
                '고정비 줄이기 전략',
                '부채 관리 우선순위',
                '재무 목표 설정법',
                '투자 성향 테스트'
            ],
            # 부동산/자산 (30개)
            '부동산/자산': [
                '전세 vs 매매 손익분기점',
                '청년 전세대출 조건 비교',
                '신혼부부 특공 청약 전략',
                '재개발 재건축 투자 분석',
                '오피스텔 투자 수익률',
                '상가 임대 투자 가이드',
                '경매 입찰 초보 가이드',
                '부동산 세금 계산법',
                '전세보증보험 가입 방법',
                '집 구하기 체크리스트',
                '부동산 계약서 작성법',
                '등기부등본 읽는 법',
                '건축물대장 확인 사항',
                '아파트 관리비 절감법',
                '리모델링 비용 산정',
                '인테리어 견적 비교법',
                '이사 비용 절약 팁',
                '집들이 선물 추천',
                '주택담보대출 갈아타기',
                '부동산 중개수수료 계산',
                '매물 사진 촬영 팁',
                '공인중개사 선택 기준',
                '부동산 앱 활용법',
                '지역 개발 정보 찾기',
                '학군과 집값 상관관계',
                '역세권 투자 가치',
                '신도시 분양 정보',
                '토지 투자 기초 지식',
                '건물 투자 임대 수익',
                '해외 부동산 투자'
            ]
        }
    }
    
    # 날짜별 스케줄 생성
    schedule = []
    
    # 8월과 9월 처리
    for month in [8, 9]:
        days_in_month = 31 if month == 8 else 30
        
        for day in range(1, days_in_month + 1):
            # 각 사이트별로 처리
            for site in ['skewese', 'tistory', 'unpre', 'untab']:
                if site == 'skewese':
                    # Primary 카테고리 선택
                    if day <= 31:
                        primary_cat = '건강/웰니스'
                        primary_topic = site_topics[site][primary_cat][day - 1] if day <= len(site_topics[site][primary_cat]) else site_topics[site][primary_cat][0]
                    else:
                        primary_cat = '요리/레시피' 
                        primary_topic = site_topics[site][primary_cat][day - 32] if day - 32 < len(site_topics[site][primary_cat]) else site_topics[site][primary_cat][0]
                    
                    # Secondary 카테고리 선택
                    if day <= 30:
                        secondary_cat = '역사/문화'
                        secondary_topic = site_topics[site][secondary_cat][day - 1] if day <= len(site_topics[site][secondary_cat]) else site_topics[site][secondary_cat][0]
                    else:
                        secondary_cat = '과학/기술'
                        secondary_topic = site_topics[site][secondary_cat][day - 31] if day - 31 < len(site_topics[site][secondary_cat]) else site_topics[site][secondary_cat][0]
                        
                elif site == 'tistory':
                    if day <= 31:
                        primary_cat = '엔터테인먼트'
                        primary_topic = site_topics[site][primary_cat][day - 1] if day <= len(site_topics[site][primary_cat]) else site_topics[site][primary_cat][0]
                    else:
                        primary_cat = '게임/오락'
                        primary_topic = site_topics[site][primary_cat][day - 32] if day - 32 < len(site_topics[site][primary_cat]) else site_topics[site][primary_cat][0]
                    
                    if day <= 30:
                        secondary_cat = '트렌드/이슈'
                        secondary_topic = site_topics[site][secondary_cat][day - 1] if day <= len(site_topics[site][secondary_cat]) else site_topics[site][secondary_cat][0]
                    else:
                        secondary_cat = '경제/비즈니스'
                        secondary_topic = site_topics[site][secondary_cat][day - 31] if day - 31 < len(site_topics[site][secondary_cat]) else site_topics[site][secondary_cat][0]
                        
                elif site == 'unpre':
                    if day <= 31:
                        primary_cat = '교육/자기계발'
                        primary_topic = site_topics[site][primary_cat][day - 1] if day <= len(site_topics[site][primary_cat]) else site_topics[site][primary_cat][0]
                    else:
                        primary_cat = '프로그래밍/개발'
                        primary_topic = site_topics[site][primary_cat][day - 32] if day - 32 < len(site_topics[site][primary_cat]) else site_topics[site][primary_cat][0]
                    
                    if day <= 30:
                        secondary_cat = 'AI/머신러닝'
                        secondary_topic = site_topics[site][secondary_cat][day - 1] if day <= len(site_topics[site][secondary_cat]) else site_topics[site][secondary_cat][0]
                    else:
                        secondary_cat = '기술/디지털'
                        secondary_topic = site_topics[site][secondary_cat][day - 31] if day - 31 < len(site_topics[site][secondary_cat]) else site_topics[site][secondary_cat][0]
                        
                else:  # untab
                    if day <= 31:
                        primary_cat = '라이프스타일'
                        primary_topic = site_topics[site][primary_cat][day - 1] if day <= len(site_topics[site][primary_cat]) else site_topics[site][primary_cat][0]
                    else:
                        primary_cat = '패션/뷰티'
                        primary_topic = site_topics[site][primary_cat][day - 32] if day - 32 < len(site_topics[site][primary_cat]) else site_topics[site][primary_cat][0]
                    
                    if day <= 30:
                        secondary_cat = '재정/투자'
                        secondary_topic = site_topics[site][secondary_cat][day - 1] if day <= len(site_topics[site][secondary_cat]) else site_topics[site][secondary_cat][0]
                    else:
                        secondary_cat = '부동산/자산'
                        secondary_topic = site_topics[site][secondary_cat][day - 31] if day - 31 < len(site_topics[site][secondary_cat]) else site_topics[site][secondary_cat][0]
                
                # 8월과 9월 구분하여 주제 할당
                actual_day = day if month == 8 else day + 31
                
                # 스케줄에 추가
                schedule.append({
                    'year': 2025,
                    'month': month,
                    'day': day,
                    'site': site,
                    'category': primary_cat,
                    'topic': primary_topic
                })
                
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
        print("중복 없는 고유 주제로 스케줄 생성 중...")
        schedule = generate_unique_monthly_schedule()
        
        # 데이터베이스에 삽입
        print("데이터베이스 삽입 중...")
        inserted = 0
        for item in schedule:
            cursor.execute(f'''
                INSERT INTO {db.schema}.monthly_publishing_schedule 
                (year, month, day, site, topic_category, specific_topic, keywords, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (item['year'], item['month'], item['day'], item['site'], item['category'], item['topic'], [], 'pending'))
            inserted += 1
        
        conn.commit()
        print(f'[완료] 8-9월 고유 주제 스케줄 생성 완료: {inserted}개 항목')
        
        # 확인용 출력
        cursor.execute(f'''
            SELECT site, topic_category, specific_topic 
            FROM {db.schema}.monthly_publishing_schedule
            WHERE year = 2025 AND month = 8 AND day = 30
            ORDER BY site, topic_category
        ''')
        aug30_topics = cursor.fetchall()
        
        print('\n[8월 30일 주제 확인]')
        current_site = None
        for site, cat, topic in aug30_topics:
            if site != current_site:
                print(f'\n{site}:')
                current_site = site
            print(f'  - {cat}: {topic}')
        
        # 9월 1일 확인
        cursor.execute(f'''
            SELECT site, topic_category, specific_topic 
            FROM {db.schema}.monthly_publishing_schedule
            WHERE year = 2025 AND month = 9 AND day = 1
            ORDER BY site, topic_category
        ''')
        sep1_topics = cursor.fetchall()
        
        print('\n[9월 1일 주제 확인]')
        current_site = None
        for site, cat, topic in sep1_topics:
            if site != current_site:
                print(f'\n{site}:')
                current_site = site
            print(f'  - {cat}: {topic}')
            
    except Exception as e:
        print(f"[오류] 발생: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()