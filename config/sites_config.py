"""
사이트별 설정 및 콘텐츠 전략
"""

SITE_CONFIGS = {
    "unpre": {
        "name": "unpre.co.kr",
        "platform": "wordpress", 
        "categories": ["개발", "IT", "정보처리기사", "언어학습"],  # 티스토리 주제 흡수
        "topics": [
            "Python 프로그래밍",
            "JavaScript 최신 트렌드",
            "React/Vue/Angular 비교",
            "백엔드 아키텍처",
            "데이터베이스 최적화",
            "클라우드 서비스 (AWS, GCP, Azure)",
            "정보처리기사 실기 팁",
            "코딩테스트 문제 해설",
            "개발자 취업 준비",
            "IT 업계 동향",
            "오픈소스 프로젝트 리뷰",
            "DevOps 자동화",
            "API 설계 패턴",
            "보안 best practices",
            "성능 최적화 기법",
            "토익 파트별 공략법",
            "토익 단어 외우기 팁",
            "JLPT N3/N2/N1 문법",
            "일본어 한자 학습법",
            "실전 영어 회화 표현",
            "여행 필수 영어",
            "일본 여행 회화",
            "비즈니스 영어 이메일"
        ],
        "keywords_focus": [
            "개발자 연봉",
            "코딩 부트캠프", 
            "프로그래밍 언어 순위",
            "IT 자격증",
            "개발자 로드맵",
            "토익 인강 추천",
            "JLPT 시험 일정",
            "영어 회화 학원"
        ],
        "content_style": "기술적이고 실용적인 톤, 코드 예제 포함",
        "target_audience": "주니어 개발자, IT 취준생, 어학 학습자",
        "monetization": ["애드센스", "IT 도서 제휴", "온라인 강의 제휴", "어학 교재 제휴"],
        "image_style": "코드 스니펫, 아키텍처 다이어그램, 인포그래픽, 문법 도표"
    },
    
    "untab": {
        "name": "untab.co.kr",
        "platform": "wordpress",
        "categories": ["부동산", "정책/제도", "경매/공매"],
        "topics": [
            "이번 주 경매 추천 물건",
            "경매 초보자 가이드",
            "부동산 세금 절세 전략",
            "정부 부동산 정책 분석",
            "지역별 부동산 시장 동향",
            "경매 낙찰 전략",
            "권리분석 방법",
            "임대수익률 계산법",
            "재개발/재건축 정보",
            "부동산 대출 비교",
            "공매 vs 경매 차이점",
            "부동산 투자 리스크 관리",
            "상업용 부동산 투자",
            "경매 실패 사례 분석",
            "부동산 법률 상식"
        ],
        "keywords_focus": [
            "경매 컨설팅",
            "부동산 투자 수익률",
            "아파트 시세",
            "경매 대출",
            "부동산 세금"
        ],
        "content_style": "전문적이고 신뢰감 있는 톤, 데이터와 통계 중심",
        "target_audience": "부동산 투자자, 경매 관심자",
        "monetization": ["애드센스", "부동산 컨설팅", "경매 교육 프로그램"],
        "image_style": "지도, 차트, 통계 그래프, 물건 사진"
    },
    
    "skewese": {
        "name": "skewese.com",
        "platform": "wordpress",
        "categories": ["세계사", "한국사", "라이프"],
        "topics": [
            "오늘의 역사",
            "역사 속 오늘",
            "한국사 주요 사건",
            "세계사 대사건",
            "역사 인물 탐구",
            "고대 문명 이야기",
            "전쟁과 평화",
            "역사적 발견과 발명",
            "조선시대 이야기",
            "근현대사 재조명",
            "역사 속 미스터리",
            "문화재 이야기",
            "역사 여행지 소개",
            "역사 드라마 vs 실제 역사",
            "세계 문화유산"
        ],
        "keywords_focus": [
            "한국사능력검정시험",
            "역사 교과서",
            "역사 도서 추천",
            "박물관 전시",
            "역사 여행"
        ],
        "content_style": "스토리텔링 중심, 흥미롭고 교육적인 톤",
        "target_audience": "역사 애호가, 학생, 교육자",
        "monetization": ["애드센스", "역사 도서 제휴", "문화 상품"],
        "image_style": "역사적 그림, 유물 사진, 지도, AI 생성 역사 장면"
    }
}

# SEO 최적화 설정
SEO_SETTINGS = {
    "title_length": {"min": 30, "max": 60},
    "meta_description_length": {"min": 120, "max": 160},
    "keyword_density": {"min": 0.01, "max": 0.03},
    "internal_links": {"min": 2, "max": 5},
    "external_links": {"min": 1, "max": 3},
    "heading_structure": {
        "h1": 1,
        "h2": {"min": 3, "max": 6},
        "h3": {"min": 2, "max": 8}
    }
}

# 발행 스케줄 (Tistory 제외)
PUBLISHING_SCHEDULE = {
    "unpre": {"time": "12:00", "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]},
    "untab": {"time": "09:00", "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]}, 
    "skewese": {"time": "15:00", "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]}
}