# 🤖 Blog Automation System

고품질 블로그 콘텐츠 자동 생성 및 발행 시스템입니다. AI를 활용하여 4개 사이트에 맞춤형 콘텐츠를 자동으로 생성하고 발행합니다.

## 📋 지원 사이트

- **unpre.co.kr** - IT/개발 전문 블로그 (WordPress)
- **untab.co.kr** - 부동산/경매 정보 블로그 (WordPress)  
- **skewese.com** - 역사/문화 블로그 (WordPress)
- **untab.tistory.com** - 언어학습 블로그 (Tistory)

## ✨ 주요 기능

### 🧠 AI 기반 콘텐츠 생성
- Claude 3.5 Sonnet & GPT-4 지원
- 사이트별 맞춤형 콘텐츠 생성
- SEO 최적화된 제목, 메타설명, 태그
- 중복 콘텐츠 자동 감지 및 방지

### 🎨 자동 이미지 생성
- 썸네일, 차트, 코드 스니펫 이미지 생성
- DALL-E 3 AI 이미지 생성
- 무료 스톡 이미지 자동 수집 (Unsplash, Pexels)
- 사이트별 브랜딩 적용

### 📈 스마트 발행 시스템
- WordPress REST API 완전 지원
- Tistory Open API 연동
- 자동 카테고리/태그 관리
- 예약 발행 및 초안 저장

### ⏰ 자동 스케줄러
- 사이트별 맞춤형 발행 일정
- 실패시 자동 재시도
- 일일/주간 리포트 생성
- 성능 모니터링

### 📊 데이터 관리
- SQLite 기반 콘텐츠 히스토리
- 성능 지표 추적
- 중복 방지 시스템
- 주제 풀 자동 관리

## 🚀 설치 및 설정

### 1. 프로젝트 클론
```bash
git clone <repository_url>
cd blog-automation
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env.example`을 복사하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

필수 환경변수 설정:
```env
# AI API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# WordPress 사이트들
UNPRE_URL=https://unpre.co.kr
UNPRE_USERNAME=your_username
UNPRE_PASSWORD=your_app_password

# Tistory
TISTORY_APP_ID=your_app_id
TISTORY_SECRET_KEY=your_secret_key
TISTORY_ACCESS_TOKEN=your_access_token

# 이미지 API (선택사항)
UNSPLASH_ACCESS_KEY=your_unsplash_key
PEXELS_API_KEY=your_pexels_key
```

### 4. WordPress 앱 패스워드 생성
각 WordPress 사이트에서:
1. 관리자 → 사용자 → 프로필
2. 애플리케이션 패스워드 생성
3. 생성된 패스워드를 `.env`에 설정

### 5. Tistory API 설정
1. [Tistory Open API](https://www.tistory.com/guide/api/manage/register) 앱 등록
2. 인증 후 액세스 토큰 획득
3. `.env`에 설정

## 💻 사용법

### 기본 명령어

```bash
# 연결 테스트
python main.py test

# 초기 데이터 설정
python main.py setup

# 샘플 포스트 생성
python main.py post unpre

# 시스템 통계 조회
python main.py stats

# 스케줄러 실행 (메인 기능)
python main.py schedule
```

### 개별 테스트

```bash
# 데이터베이스 테스트
python -m pytest tests/test_database.py -v

# WordPress 발행자 테스트
python -m pytest tests/test_wordpress_publisher.py -v

# 콘텐츠 생성기 테스트
python -m pytest tests/test_content_generator.py -v

# 전체 테스트
python -m pytest tests/ -v --cov=src
```

## 📁 프로젝트 구조

```
blog-automation/
├── config/                 # 사이트별 설정
│   └── sites_config.py     
├── src/
│   ├── generators/         # 콘텐츠/이미지 생성
│   │   ├── content_generator.py
│   │   └── image_generator.py
│   ├── publishers/         # 플랫폼별 발행
│   │   ├── wordpress_publisher.py
│   │   └── tistory_publisher.py
│   ├── utils/             # 유틸리티
│   │   ├── database.py
│   │   └── logger.py
│   └── scheduler.py       # 스케줄러
├── tests/                 # 테스트 코드
├── data/                  # 데이터 저장소
│   ├── content/          # 생성된 콘텐츠
│   ├── images/           # 생성된 이미지
│   └── logs/             # 로그 파일
├── templates/            # 템플릿
├── main.py              # 메인 실행 파일
└── requirements.txt     # 의존성
```

## 🔧 고급 설정

### 사이트별 콘텐츠 전략 수정
`config/sites_config.py`에서 각 사이트의:
- 주제 목록
- 키워드 전략  
- 콘텐츠 스타일
- 발행 일정 조정

### 커스텀 이미지 생성
`src/generators/image_generator.py`에서:
- 사이트별 브랜딩 색상
- 썸네일 템플릿
- 차트 스타일 수정

### 스케줄 조정
`config/sites_config.py`의 `PUBLISHING_SCHEDULE`에서:
- 발행 시간 변경
- 발행 요일 설정
- 사이트별 개별 일정

## 📊 모니터링

### 로그 확인
```bash
# 실시간 로그
tail -f data/logs/automation.log

# 에러 로그
tail -f data/logs/errors.log

# 성과 로그 (JSON)
cat data/logs/performance.jsonl | jq
```

### 일일 리포트
매일 23:50에 자동 생성되는 리포트:
```bash
cat data/logs/daily_report_2024-01-15.json
```

## 🚨 트러블슈팅

### 일반적인 문제들

**1. WordPress 인증 실패**
```bash
# 앱 패스워드 재생성 후 .env 파일 확인
python main.py test
```

**2. Tistory 토큰 만료**
```python
# Python 실행 후
from src.publishers.tistory_publisher import TistoryPublisher
publisher = TistoryPublisher()
# 출력된 URL로 재인증 후 토큰 업데이트
```

**3. AI API 할당량 초과**
- API 사용량 확인
- 백업 API로 자동 전환됨

**4. 이미지 생성 실패**
- 무료 스톡 이미지로 대체됨
- 이미지 API 키 확인

### 로그 레벨 조정
```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 🔒 보안 고려사항

- API 키는 절대 커밋하지 마세요
- WordPress 앱 패스워드 사용 (일반 패스워드 X)
- 로그 파일 권한 설정
- 정기적인 토큰 갱신

## 🛠️ 개발 참여

### 개발 환경 설정
```bash
# 개발용 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt

# pre-commit 훅 설정
pre-commit install
```

### 테스트 실행
```bash
# 전체 테스트
python -m pytest

# 커버리지 포함
python -m pytest --cov=src --cov-report=html
```

## 📄 라이센스

MIT License

## 🤝 지원

문제가 발생하면 이슈를 등록하거나 다음을 확인하세요:

1. 환경변수 설정 확인
2. API 연결 테스트 실행
3. 로그 파일 확인
4. 테스트 코드 실행

---

**⚡ 자동화로 블로그 운영의 새로운 차원을 경험하세요!**# Koyeb 배포 강제 트리거 Tue Sep  2 16:08:10 KST 2025
