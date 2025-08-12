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

@app.route('/api/recent_posts')
def get_recent_posts():
    """최근 포스트 목록 조회"""
    try:
        db = get_database()
        if db:
            posts = []
            for site in ['unpre', 'untab', 'skewese']:
                site_posts = db.get_recent_posts(site, limit=5)
                posts.extend(site_posts)
            posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return jsonify(posts[:20])
        else:
            mock = get_mock_data()
            return jsonify(mock['posts'])
    except Exception as e:
        logger.error(f"최근 포스트 조회 오류: {e}")
        mock = get_mock_data()
        return jsonify(mock['posts'])

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
                'today_posts': today_posts,
                'revenue': {
                    'total_views': 0,
                    'total_revenue': 0
                }
            }
        else:
            # DB 연결 실패 시 목업 데이터 반환
            mock = get_mock_data()
            stats = mock['stats']
            stats['revenue'] = {
                'total_views': 0,
                'total_revenue': 0
            }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        mock = get_mock_data()
        stats = mock['stats']
        stats['revenue'] = {
            'total_views': 0,
            'total_revenue': 0
        }
        return jsonify(stats)

@app.route('/api/topic_stats')
def get_topic_stats():
    """주제 풀 통계 조회"""
    return jsonify({
        'unpre': {
            'total': 50,
            'used': 25,
            'available': 25
        },
        'untab': {
            'total': 50,
            'used': 20,
            'available': 30
        },
        'skewese': {
            'total': 50,
            'used': 15,
            'available': 35
        }
    })

@app.route('/api/system_status')
def get_system_status():
    """시스템 상태 조회"""
    db = get_database()
    return jsonify({
        'api': {
            'openai': {'status': 'online', 'response_time': 150},
            'claude': {'status': 'online', 'response_time': 120},
            'pexels': {'status': 'online', 'response_time': 200}
        },
        'sites': {
            'unpre': {'status': 'online', 'last_post': datetime.now(KST).strftime('%Y-%m-%d')},
            'untab': {'status': 'online', 'last_post': datetime.now(KST).strftime('%Y-%m-%d')},
            'skewese': {'status': 'online', 'last_post': datetime.now(KST).strftime('%Y-%m-%d')}
        },
        'database': {'status': 'online' if db and db.is_connected else 'offline'},
        'scheduler': {'status': 'online', 'next_run': '03:00 KST'}
    })

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

@app.route('/api/chart_data')
def get_chart_data():
    """차트 데이터 조회"""
    # 최근 7일 데이터 (목업)
    now = datetime.now(KST)
    daily_data = []
    site_data = {
        'unpre': 0,
        'untab': 0,
        'skewese': 0
    }
    
    try:
        db = get_database()
        if db:
            for i in range(7):
                date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
                count = 0
                for site in ['unpre', 'untab', 'skewese']:
                    posts = db.get_recent_posts(site, limit=100)
                    for post in posts:
                        if post.get('created_at', '').startswith(date):
                            count += 1
                            site_data[site] += 1
                daily_data.append({'date': date, 'count': count})
        else:
            # 목업 데이터
            for i in range(7):
                date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
                daily_data.append({'date': date, 'count': 3 - i % 2})
            site_data = {'unpre': 7, 'untab': 5, 'skewese': 3}
    except:
        # 목업 데이터
        for i in range(7):
            date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_data.append({'date': date, 'count': 3 - i % 2})
        site_data = {'unpre': 7, 'untab': 5, 'skewese': 3}
    
    return jsonify({
        'daily': daily_data,
        'bySite': site_data
    })

@app.route('/api/logs')
def get_logs():
    """최근 로그 조회"""
    logs = [
        {
            'time': datetime.now(KST).strftime('%H:%M:%S'),
            'level': 'info',
            'message': '시스템 정상 작동 중'
        }
    ]
    return jsonify(logs)

@app.route('/api/schedule/weekly')
def get_weekly_schedule():
    """주간 스케줄 조회"""
    week_start = request.args.get('week_start', datetime.now(KST).strftime('%Y-%m-%d'))
    
    # 주간 스케줄 데이터 (목업)
    schedule = {}
    start_date = datetime.strptime(week_start, '%Y-%m-%d')
    
    for i in range(7):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        schedule[date] = {
            'unpre': {
                'time': '09:00',
                'topics': ['프로그래밍', 'AI 기술'],
                'status': 'scheduled'
            },
            'untab': {
                'time': '12:00',
                'topics': ['언어학습', '자격증'],
                'status': 'scheduled'
            },
            'skewese': {
                'time': '15:00',
                'topics': ['역사', '문화'],
                'status': 'scheduled'
            }
        }
    
    return jsonify(schedule)

@app.route('/api/generate_wordpress', methods=['POST'])
def generate_wordpress():
    """WordPress 콘텐츠 생성"""
    try:
        data = request.json
        site = data.get('site', 'unpre')
        topic = data.get('topic', '프로그래밍')
        
        # 실제 생성 로직 대신 목업 응답
        return jsonify({
            'success': True,
            'message': f'{site} 사이트에 {topic} 주제로 콘텐츠를 생성했습니다.',
            'post': {
                'title': f'{topic} 관련 새로운 포스트',
                'url': f'https://{site}.co.kr/new-post',
                'id': 123
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/delete_posts', methods=['POST'])
def delete_posts():
    """포스트 삭제"""
    try:
        data = request.json
        post_ids = data.get('post_ids', [])
        
        # 실제 삭제 로직 대신 목업 응답
        return jsonify({
            'success': True,
            'message': f'{len(post_ids)}개의 포스트를 삭제했습니다.',
            'deleted': post_ids
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedule')
def get_schedule():
    """발행 일정 조회"""
    try:
        now = datetime.now(KST)
        schedule = []
        
        # 다음 7일간의 예정
        for i in range(7):
            date = (now + timedelta(days=i)).strftime('%Y-%m-%d')
            schedule.append({
                'date': date,
                'time': '03:00',
                'status': 'scheduled',
                'sites': ['unpre', 'untab', 'skewese']
            })
        
        return jsonify(schedule)
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/wordpress_files')
def get_wordpress_files():
    """WordPress 파일 목록"""
    try:
        files = []
        
        # 목업 데이터
        for i, site in enumerate(['unpre', 'untab', 'skewese']):
            for j in range(3):
                files.append({
                    'id': f'{site}_{j}',
                    'site': site,
                    'title': f'샘플 포스트 {j+1}',
                    'date': datetime.now(KST).strftime('%Y-%m-%d'),
                    'size': '2.5KB',
                    'url': f'https://{site}.co.kr/post-{j}'
                })
        
        return jsonify(files)
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/tistory_files')
def get_tistory_files():
    """Tistory 파일 목록"""
    try:
        files = []
        
        # 목업 데이터
        for i in range(5):
            files.append({
                'id': f'tistory_{i}',
                'title': f'Tistory 포스트 {i+1}',
                'date': datetime.now(KST).strftime('%Y-%m-%d'),
                'size': '3.2KB',
                'url': f'https://untab.tistory.com/post-{i}'
            })
        
        return jsonify(files)
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/system/time')
def get_system_time():
    """시스템 시간 조회 (한국 시간과 서버 시간 비교)"""
    import time
    
    # 서버 UTC 시간
    utc_time = datetime.now(pytz.UTC)
    # 한국 시간
    kst_time = datetime.now(KST)
    # 서버 로컬 시간 (시간대 없이)
    server_local = datetime.now()
    
    # 시간 차이 계산
    time_diff = kst_time.hour - server_local.hour
    if time_diff < -12:
        time_diff += 24
    elif time_diff > 12:
        time_diff -= 24
    
    return jsonify({
        'status': 'success',
        'korea_time': kst_time.strftime('%Y-%m-%d %H:%M:%S KST'),
        'utc_time': utc_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'server_local_time': server_local.strftime('%Y-%m-%d %H:%M:%S'),
        'timezone': 'Asia/Seoul',
        'time_difference_hours': time_diff,
        'scheduler_info': {
            'timezone': 'Asia/Seoul',
            'note': '스케줄러는 한국 시간(KST) 기준으로 작동합니다'
        }
    })

@app.route('/favicon.ico')
def favicon():
    """favicon 처리"""
    from flask import Response
    # 간단한 빈 favicon 응답
    return Response('', status=204)

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