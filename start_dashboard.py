"""
웹 대시보드 시작 스크립트
"""

import os
import sys
import webbrowser
from pathlib import Path

# Windows 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

def start_dashboard():
    """웹 대시보드 시작"""
    print("Blog Automation Web Dashboard Starting...")
    print("=" * 60)
    
    # 필요한 디렉토리 생성
    dirs = ["data", "data/logs", "templates", "static"]
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Flask 앱 시작
    from src.web_dashboard import app
    
    print("Dashboard URL: http://localhost:8080")
    print("Features:")
    print("   - Real-time system status monitoring")
    print("   - Post publishing dashboard")
    print("   - Tistory content generation and download")
    print("   - Topic pool and performance analysis")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # 브라우저 자동 열기
    import threading
    import time
    
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:8080')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Flask 서버 시작
    app.run(debug=False, host='127.0.0.1', port=8080)


if __name__ == "__main__":
    try:
        start_dashboard()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    except Exception as e:
        print(f"Error occurred: {e}")
        input("Press Enter to exit...")