# WordPress 자동 발행 설정 가이드

## 현재 상황
- 코드는 정상 작동
- WordPress REST API가 401 인증 오류 반환
- 해결책: WordPress 사이트 설정 변경 필요

## 해결 방법

### 1. WordPress 관리자 페이지 접속
각 사이트 관리자 페이지에 로그인:
- https://unpre.co.kr/wp-admin/
- https://untab.co.kr/wp-admin/  
- https://skewese.com/wp-admin/

### 2. Application Passwords 활성화

#### WordPress 5.6 이상인 경우:
1. WordPress 관리자 페이지 로그인
2. 왼쪽 메뉴에서 **사용자** > **프로필** 클릭
3. 페이지 맨 아래로 스크롤하여 **Application Passwords** 섹션 찾기
4. "새 Application Password 추가" 입력란에 "BlogAutomation" 입력
5. **새 Application Password 추가** 버튼 클릭
6. 생성된 패스워드 복사 (xxxx xxxx xxxx 형태)

#### Application Passwords 섹션이 없는 경우:
WordPress 버전이 낮거나 비활성화된 상태입니다.

**해결 방법 1**: 플러그인 설치
1. **플러그인** > **새로 추가**
2. 검색창에 "Application Passwords" 입력
3. WordPress 팀이 만든 공식 플러그인 설치 및 활성화
4. 다시 **사용자** > **프로필**에서 설정

**해결 방법 2**: functions.php 코드 추가
1. **외모** > **테마 편집기**
2. **functions.php** 선택
3. 파일 맨 아래에 다음 코드 추가:
```php
// Application Passwords 강제 활성화
add_filter('wp_is_application_passwords_available', '__return_true');
```
4. **파일 업데이트** 클릭

### 3. .env 파일 업데이트
생성된 Application Password로 .env 파일 업데이트:

```env
# 기존 비밀번호 대신 Application Password 사용
UNPRE_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
UNTAB_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
SKEWESE_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

### 4. 대안 해결책 (Application Passwords가 안되는 경우)

#### 방법 A: REST API 플러그인 설치
1. **플러그인** > **새로 추가**
2. "Application Passwords" 플러그인 설치/활성화

#### 방법 B: functions.php 추가
WordPress 테마의 functions.php에 다음 코드 추가:

```php
// REST API 인증 활성화
add_filter('rest_authentication_errors', function($result) {
    if (!empty($result)) {
        return $result;
    }
    if (!is_user_logged_in()) {
        return new WP_Error('rest_not_logged_in', 'You are not currently logged in.', array('status' => 401));
    }
    return $result;
});
```

#### 방법 C: 보안 플러그인 설정
Wordfence, iThemes Security 등 보안 플러그인에서:
1. **방화벽** 설정 이동
2. **REST API** 접근 허용
3. **IP 화이트리스트**에 서버 IP 추가

## 테스트 방법
설정 완료 후 다시 발행 테스트:

```bash
cd C:\Develop\unble\blog-automation
python src\web_dashboard_pg.py
```

대시보드에서 WordPress 콘텐츠 발행 버튼 클릭하여 확인.

## 예상 결과
- ✅ 발행 성공 시: "사이트에 성공적으로 발행되었습니다" 메시지와 URL 표시
- ❌ 여전히 실패 시: 위 3가지 방법 모두 적용 필요