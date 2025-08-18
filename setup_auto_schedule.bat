@echo off
:: 블로그 자동 발행 스케줄러 설정 배치 파일

echo ===============================================
echo   블로그 자동 발행 스케줄러 설정
echo ===============================================
echo.

:: 프로젝트 경로 설정
set PROJECT_PATH=C:\Develop\unble\blog-automation
set PYTHON_PATH=python

:: Windows Task Scheduler 작업 생성
echo Windows 작업 스케줄러에 자동 실행 작업을 추가합니다...
echo.

:: 기존 작업이 있으면 삭제
schtasks /delete /tn "BlogAutomationScheduler" /f 2>nul

:: 매일 새벽 2시 50분에 스케줄러 실행 (3시 발행을 위해 10분 전에 시작)
schtasks /create ^
    /tn "BlogAutomationScheduler" ^
    /tr "\"%PYTHON_PATH%\" \"%PROJECT_PATH%\run_scheduler.py\" schedule" ^
    /sc daily ^
    /st 02:50 ^
    /rl highest ^
    /f

if %errorlevel% equ 0 (
    echo.
    echo ✓ 작업 스케줄러 등록 완료!
    echo.
    echo 설정 내용:
    echo - 작업 이름: BlogAutomationScheduler
    echo - 실행 시간: 매일 새벽 2시 50분
    echo - 실행 파일: %PROJECT_PATH%\src\scheduler.py
    echo.
    echo 참고: 스케줄러는 새벽 3시에 자동으로 블로그 게시물을 발행합니다.
) else (
    echo.
    echo × 작업 스케줄러 등록 실패!
    echo 관리자 권한으로 실행해주세요.
)

echo.
pause