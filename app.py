"""
Koyeb 배포용 웹 서버 앱
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file, make_response
from flask_cors import CORS
from datetime import datetime, timedelta
import pytz
import json
import logging
from dotenv import load_dotenv

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

# 환경변수 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# 템플릿 캐싱 비활성화
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 전역 데이터베이스 인스턴스 (옵셔널)
database = None

def get_database():
    """데이터베이스 인스턴스 반환 (실패해도 None 반환)"""
    global database
    if database is None:
        try:
            from src.utils.postgresql_database import PostgreSQLDatabase
            database = PostgreSQLDatabase()
            if database.is_connected:
                logger.info("PostgreSQL 데이터베이스 연결 성공")
            else:
                database = None
        except Exception as e:
            logger.warning(f"PostgreSQL 연결 실패 (앱은 계속 실행): {e}")
            database = None
    return database

def get_mock_data():
    """DB 연결 실패 시 사용할 목업 데이터"""
    now = datetime.now(KST)
    return {
        'posts': [
            {
                'id': 1,
                'title': '샘플 포스트 1',
                'site': 'unpre',
                'category': '프로그래밍',
                'url': '#',
                'created_at': now.strftime('%Y-%m-%d %H:%M:%S'),
                'published': True
            },
            {
                'id': 2,
                'title': '샘플 포스트 2',
                'site': 'skewese',
                'category': '역사',
                'url': '#',
                'created_at': (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'published': True
            }
        ],
        'stats': {
            'total_posts': 2,
            'published': 2,
            'scheduled': 0,
            'today_posts': 1
        }
    }

@app.route('/')
def dashboard():
    """메인 대시보드 페이지"""
    response = make_response(render_template('dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/posts')
def get_posts():
    """발행된 포스트 목록 조회"""
    try:
        db = get_database()
        if db:
            site_filter = request.args.get('site', 'all')
            date_filter = request.args.get('date', '')
            
            posts = []
            for site in ['unpre', 'untab', 'skewese']:
                if site_filter == 'all' or site_filter == site:
                    site_posts = db.get_recent_posts(site, limit=10)
                    posts.extend(site_posts)
            
            # 날짜별 필터링
            if date_filter:
                filtered_posts = []
                for post in posts:
                    if post.get('created_at', '').startswith(date_filter):
                        filtered_posts.append(post)
                posts = filtered_posts
            
            # 시간순 정렬
            posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return jsonify({'status': 'success', 'posts': posts})
        else:
            # DB 연결 실패 시 목업 데이터 반환
            mock = get_mock_data()
            return jsonify({'status': 'success', 'posts': mock['posts']})
            
    except Exception as e:
        logger.error(f"포스트 조회 오류: {e}")
        mock = get_mock_data()
        return jsonify({'status': 'success', 'posts': mock['posts']})

@app.route('/api/stats')
def get_stats():
    """통계 정보 조회"""
    try:
        db = get_database()
        if db:
            # 각 사이트별 통계
            total_posts = 0
            published = 0
            scheduled = 0
            today_posts = 0
            
            today = datetime.now(KST).date()
            
            for site in ['unpre', 'untab', 'skewese']:
                posts = db.get_recent_posts(site, limit=100)
                total_posts += len(posts)
                
                for post in posts:
                    if post.get('published'):
                        published += 1
                    else:
                        scheduled += 1
                    
                    # 오늘 발행된 포스트
                    created_at = post.get('created_at', '')
                    if created_at.startswith(str(today)):
                        today_posts += 1
            
            stats = {
                'total_posts': total_posts,
                'published': published,
                'scheduled': scheduled,
                'today_posts': today_posts
            }
        else:
            # DB 연결 실패 시 목업 데이터 반환
            mock = get_mock_data()
            stats = mock['stats']
        
        return jsonify({'status': 'success', 'stats': stats})
        
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        mock = get_mock_data()
        return jsonify({'status': 'success', 'stats': mock['stats']})

@app.route('/api/trending')
def get_trending():
    """트렌딩 토픽 조회"""
    try:
        from src.utils.trending_topics import trending_manager
        
        # DB 연결 실패해도 기본 트렌드 반환
        current_trends = trending_manager.get_current_week_trends()
        
        return jsonify({
            'status': 'success',
            'trends': current_trends
        })
    except Exception as e:
        logger.error(f"트렌딩 조회 오류: {e}")
        return jsonify({
            'status': 'success',
            'trends': {
                'period': '기본 트렌드',
                'cross_trends': [],
                'site_trends': {}
            }
        })

@app.route('/api/system/time')
def get_system_time():
    """시스템 시간 조회 (한국 시간)"""
    kst_time = datetime.now(KST)
    return jsonify({
        'status': 'success',
        'time': kst_time.strftime('%Y-%m-%d %H:%M:%S'),
        'timezone': 'Asia/Seoul'
    })

@app.route('/health')
def health():
    """헬스체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'message': 'Blog automation system is running',
        'time': datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')
    }), 200

@app.route('/api/status')
def api_status():
    """시스템 상태 API"""
    db = get_database()
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'database': 'connected' if db and db.is_connected else 'disconnected',
        'features': {
            'content_generation': True,
            'wordpress_publishing': True,
            'tistory_publishing': True,
            'image_generation': True,
            'seo_optimization': True
        },
        'server_time': datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)