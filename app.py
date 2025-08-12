"""
Koyeb 배포용 웹 서버 앱
"""

import os
from flask import Flask, jsonify, render_template_string

# Flask 앱 생성
app = Flask(__name__)

# 간단한 HTML 템플릿
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Blog Automation System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .status {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .success {
            color: #4CAF50;
            font-weight: bold;
        }
        .info {
            color: #666;
            margin: 10px 0;
        }
        .endpoints {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .endpoints h3 {
            margin-top: 0;
        }
        .endpoints ul {
            list-style-type: none;
            padding-left: 0;
        }
        .endpoints li {
            padding: 5px 0;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>🚀 Blog Automation System</h1>
    <div class="status">
        <p class="success">✅ System is running successfully!</p>
        <p class="info">This is a blog automation system that manages content generation and publishing.</p>
        <p class="info">Server Time: {{ current_time }}</p>
    </div>
    
    <div class="endpoints">
        <h3>Available Endpoints:</h3>
        <ul>
            <li>GET / - Home page (this page)</li>
            <li>GET /health - Health check endpoint</li>
            <li>GET /api/status - System status in JSON</li>
        </ul>
    </div>
    
    <div class="status">
        <h3>Features:</h3>
        <ul>
            <li>✨ Automated content generation using AI</li>
            <li>📝 Multi-platform publishing (WordPress, Tistory)</li>
            <li>🖼️ Automatic image generation</li>
            <li>📊 SEO optimization</li>
            <li>⏰ Scheduled posting</li>
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """홈페이지"""
    from datetime import datetime
    return render_template_string(HOME_TEMPLATE, current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/health')
def health():
    """헬스체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'message': 'Blog automation system is running'
    }), 200

@app.route('/api/status')
def api_status():
    """시스템 상태 API"""
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'features': {
            'content_generation': True,
            'wordpress_publishing': True,
            'tistory_publishing': True,
            'image_generation': True,
            'seo_optimization': True
        }
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)