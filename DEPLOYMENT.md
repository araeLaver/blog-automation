# Koyeb 배포 가이드

## 필수 환경변수 설정

Koyeb Dashboard > Service > Settings > Environment variables에서 다음 환경변수를 설정해야 합니다:

### PostgreSQL 데이터베이스 (필수)
```
PG_HOST=aws-0-ap-northeast-2.pooler.supabase.com
PG_PORT=5432
PG_DATABASE=postgres
PG_USER=postgres.lhqzjnpwuftaicjurqxq  # Supabase에서 확인
PG_PASSWORD=your_password_here          # Supabase에서 확인
PG_SCHEMA=unble
```

### AI API Keys (필수)
```
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
```

### WordPress 사이트 정보 (선택)
```
UNPRE_URL=https://unpre.co.kr
UNPRE_USERNAME=your_username
UNPRE_PASSWORD=your_app_password

UNTAB_URL=https://untab.co.kr
UNTAB_USERNAME=your_username
UNTAB_PASSWORD=your_app_password

SKEWESE_URL=https://skewese.com
SKEWESE_USERNAME=your_username
SKEWESE_PASSWORD=your_app_password
```

### Tistory API (선택)
```
TISTORY_APP_ID=your_app_id
TISTORY_SECRET_KEY=your_secret_key
TISTORY_ACCESS_TOKEN=your_access_token
TISTORY_BLOG_NAME=untab
```

### 이미지 API (선택)
```
PEXELS_API_KEY=your_key
UNSPLASH_ACCESS_KEY=your_key
```

## 시간대 설정

- 서버는 UTC 시간으로 작동하지만, 모든 스케줄링은 한국 시간(KST, UTC+9)으로 설정됩니다.
- 스케줄러는 `Asia/Seoul` 시간대를 사용합니다.
- 대시보드는 한국 시간으로 표시됩니다.

## 엔드포인트

- `/` - 메인 대시보드
- `/health` - 헬스체크
- `/api/status` - 시스템 상태
- `/api/system/time` - 시간 정보 (서버 시간과 한국 시간 비교)
- `/api/posts` - 포스트 목록
- `/api/stats` - 통계 정보
- `/api/trending` - 트렌딩 토픽

## Supabase 연결 정보 확인

1. [Supabase Dashboard](https://app.supabase.com) 접속
2. 프로젝트 선택
3. Settings > Database 
4. Connection string > URI 복사
5. 연결 문자열에서 다음 정보 추출:
   - Host: aws-0-ap-northeast-2.pooler.supabase.com
   - User: postgres.lhqzjnpwuftaicjurqxq
   - Password: 설정한 비밀번호

## 문제 해결

### DB 연결 실패
- PG_USER와 PG_PASSWORD가 올바르게 설정되었는지 확인
- Supabase 대시보드에서 연결 정보 재확인
- Pooler 모드 사용 중인지 확인 (Transaction 모드 권장)

### 시간 표시 문제
- `/api/system/time` 엔드포인트로 시간 차이 확인
- 모든 시간은 한국 시간(KST)으로 표시되어야 함

### 로그 확인
- Koyeb Dashboard > Service > Logs에서 실시간 로그 확인
- PostgreSQL 연결 로그 확인
- 에러 메시지 확인