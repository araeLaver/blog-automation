"""
Koyeb 배포용 웹 서버 앱
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from src.web_dashboard_pg import create_app

# 환경변수 로드
load_dotenv()

# Flask 앱 생성
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)