"""
블로그 자동화 시스템 웹 대시보드
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# 데이터베이스 경로
DB_PATH = "./data/blog_content.db"
LOG_PATH = "./data/logs/performance.jsonl"


def get_db_connection():
    """데이터베이스 연결"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def dashboard():
    """메인 대시보드 페이지"""
    return render_template('dashboard.html')


@app.route('/api/stats')
def get_stats():
    """전체 통계 데이터"""
    try:
        from src.utils.database import ContentDatabase
        database = ContentDatabase()
        
        # 대시보드 통합 통계 사용
        stats = database.get_dashboard_stats()
        
        return jsonify({
            'total_posts': stats['posts']['total'],
            'today_posts': stats['posts']['today'],
            'site_stats': stats['posts']['by_site'],
            'file_stats': stats['files'],
            'revenue': stats['revenue'],
            'api_usage': stats['api_usage']
        })
        
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({
            'total_posts': 0,
            'today_posts': 0,
            'site_stats': {},
            'file_stats': {},
            'revenue': {'total_revenue': 0, 'total_views': 0},
            'api_usage': {}
        })


@app.route('/api/recent_posts')
def get_recent_posts():
    """최근 포스트 목록"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT site, title, category, url, published_date, status
        FROM content_history
        ORDER BY published_date DESC
        LIMIT 20
    """)
    
    posts = []
    for row in cursor.fetchall():
        posts.append({
            'site': row['site'],
            'title': row['title'],
            'category': row['category'],
            'url': row['url'],
            'published_date': row['published_date'],
            'status': row['status']
        })
    
    conn.close()
    return jsonify(posts)


@app.route('/api/schedule')
def get_schedule():
    """발행 일정"""
    from config.sites_config import PUBLISHING_SCHEDULE
    
    schedule_data = []
    for site, config in PUBLISHING_SCHEDULE.items():
        schedule_data.append({
            'site': site,
            'time': config['time'],
            'days': config['days']
        })
    
    return jsonify(schedule_data)


@app.route('/api/logs')
def get_logs():
    """최근 로그"""
    logs = []
    
    # 성능 로그 읽기
    if Path(LOG_PATH).exists():
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-50:]  # 최근 50개
            for line in lines:
                try:
                    log = json.loads(line.strip())
                    logs.append(log)
                except:
                    continue
    
    return jsonify(logs)


@app.route('/api/chart/daily')
def get_daily_chart():
    """일별 발행 차트 데이터"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DATE(published_date) as date, COUNT(*) as count
        FROM content_history
        WHERE published_date >= DATE('now', '-30 days')
        GROUP BY DATE(published_date)
        ORDER BY date
    """)
    
    data = {
        'labels': [],
        'data': []
    }
    
    for row in cursor.fetchall():
        data['labels'].append(row['date'])
        data['data'].append(row['count'])
    
    conn.close()
    return jsonify(data)


@app.route('/api/chart/site')
def get_site_chart():
    """사이트별 통계 차트"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT site, COUNT(*) as count
        FROM content_history
        GROUP BY site
    """)
    
    data = {
        'labels': [],
        'data': []
    }
    
    for row in cursor.fetchall():
        data['labels'].append(row['site'])
        data['data'].append(row['count'])
    
    conn.close()
    return jsonify(data)


@app.route('/api/content_files')
def get_content_files():
    """모든 콘텐츠 파일 목록 (WordPress + Tistory)"""
    try:
        from src.utils.database import ContentDatabase
        database = ContentDatabase()
        
        # 데이터베이스에서 파일 정보 가져오기
        wordpress_files = database.get_content_files(file_type="wordpress", limit=20)
        tistory_files = database.get_content_files(file_type="tistory", limit=20)
        
        return jsonify({
            'wordpress': wordpress_files,
            'tistory': tistory_files
        })
        
    except Exception as e:
        print(f"Content files error: {e}")
        return jsonify({'wordpress': [], 'tistory': []})


@app.route('/api/download_tistory/<filename>')
def download_tistory(filename):
    """Tistory HTML 파일 다운로드"""
    file_path = Path("./data/tistory_posts") / filename
    if file_path.exists():
        return send_file(str(file_path), as_attachment=True)
    return "File not found", 404


@app.route('/api/system_status')
def get_system_status():
    """시스템 상태 확인"""
    status = {
        'wordpress': {},
        'tistory': False,
        'ai_api': False,
        'database': False
    }
    
    # WordPress 연결 상태
    try:
        from src.publishers.wordpress_publisher import WordPressPublisher
        for site in ['unpre', 'untab', 'skewese']:
            try:
                publisher = WordPressPublisher(site)
                status['wordpress'][site] = publisher.test_connection()
            except:
                status['wordpress'][site] = False
    except:
        pass
    
    # 데이터베이스 상태
    try:
        conn = get_db_connection()
        conn.close()
        status['database'] = True
    except:
        status['database'] = False
    
    # AI API 상태 (환경변수 확인)
    status['ai_api'] = bool(os.getenv('ANTHROPIC_API_KEY'))
    
    return jsonify(status)


@app.route('/api/generate_tistory', methods=['POST'])
def generate_tistory():
    """Tistory 콘텐츠 생성 API"""
    try:
        from src.generators.content_generator import ContentGenerator
        from src.generators.tistory_content_exporter import TistoryContentExporter
        from src.utils.database import ContentDatabase
        from config.sites_config import SITE_CONFIGS
        from pathlib import Path
        import json
        
        data = request.json
        topic = data.get('topic', '토익 고득점 전략')
        
        # 콘텐츠 생성
        generator = ContentGenerator()
        exporter = TistoryContentExporter()
        database = ContentDatabase()
        
        site_config = SITE_CONFIGS["unpre"].copy()
        site_config["content_style"] = "친근하고 실용적인 톤"
        
        content = generator.generate_content(
            site_config=site_config,
            topic=topic,
            category="언어학습"
        )
        
        filepath = exporter.export_content(content)
        
        # 데이터베이스에 파일 등록
        if filepath and Path(filepath).exists():
            file_path = Path(filepath)
            
            # 파일 크기 계산
            file_size = file_path.stat().st_size
            
            # 텍스트 추출 및 읽기 시간 계산
            text_content = exporter._extract_text_content(content)
            word_count = len(text_content)
            reading_time = exporter._calculate_reading_time(content)
            
            # 데이터베이스에 등록
            database.add_content_file(
                site="tistory",
                title=content['title'],
                file_path=str(file_path),
                file_type="tistory",
                word_count=word_count,
                reading_time=reading_time,
                status="generated",
                tags=content.get('tags', []),
                categories=content.get('categories', []),
                file_size=file_size
            )
            
            # 시스템 로그 추가
            database.add_system_log(
                level="INFO",
                component="tistory_generator",
                message=f"Tistory content file created",
                details=f"Topic: {topic}, File: {filepath}",
                site="tistory"
            )
        
        return jsonify({
            'success': True,
            'filepath': filepath,
            'title': content['title']
        })
        
    except Exception as e:
        print(f"Tistory generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate_wordpress', methods=['POST'])
def generate_wordpress():
    """WordPress 콘텐츠 생성 API"""
    try:
        data = request.json
        site = data.get('site', 'unpre')
        topic = data.get('topic')
        
        # WordPress 콘텐츠 생성 스크립트 실행
        import subprocess
        import sys
        
        cmd = [sys.executable, 'generate_wordpress_posts.py', '--site', site]
        if topic:
            cmd.extend(['--topic', topic])
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', cwd='.')
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': f'{site} WordPress 콘텐츠 생성 완료',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or result.stdout
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/revenue_data')
def get_revenue_data():
    """수익 데이터 조회"""
    try:
        from src.utils.database import ContentDatabase
        database = ContentDatabase()
        
        # 사이트별 수익 데이터
        revenue_data = {}
        for site in ['unpre', 'untab', 'skewese']:
            revenue_data[site] = database.get_revenue_summary(site=site, days=30)
        
        # 전체 수익 데이터
        revenue_data['total'] = database.get_revenue_summary(days=30)
        
        return jsonify(revenue_data)
        
    except Exception as e:
        print(f"Revenue data error: {e}")
        return jsonify({})


@app.route('/api/system_logs')
def get_system_logs():
    """시스템 로그 조회"""
    try:
        from src.utils.database import ContentDatabase
        database = ContentDatabase()
        
        level = request.args.get('level')
        component = request.args.get('component')
        limit = int(request.args.get('limit', 50))
        
        logs = database.get_system_logs(level=level, component=component, limit=limit)
        
        return jsonify(logs)
        
    except Exception as e:
        print(f"System logs error: {e}")
        return jsonify([])


@app.route('/api/add_revenue', methods=['POST'])
def add_revenue():
    """수익 데이터 추가/업데이트"""
    try:
        from src.utils.database import ContentDatabase
        database = ContentDatabase()
        
        data = request.json
        site = data.get('site')
        date = data.get('date')
        revenue_data = data.get('revenue_data', {})
        
        database.add_revenue_data(site, date, revenue_data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download_file/<path:filepath>')
def download_file(filepath):
    """파일 다운로드 (WordPress/Tistory)"""
    try:
        file_path = Path(filepath)
        if file_path.exists() and file_path.is_file():
            return send_file(str(file_path), as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/api/tistory_files')
def get_tistory_files():
    """Tistory 파일 목록"""
    try:
        from src.utils.database import ContentDatabase
        database = ContentDatabase()
        
        files = database.get_content_files(file_type="tistory", limit=20)
        return jsonify(files)
        
    except Exception as e:
        print(f"Tistory files error: {e}")
        return jsonify([])


@app.route('/api/wordpress_files')
def get_wordpress_files():
    """WordPress 파일 목록"""
    try:
        from src.utils.database import ContentDatabase
        database = ContentDatabase()
        
        files = database.get_content_files(file_type="wordpress", limit=50)
        return jsonify(files)
        
    except Exception as e:
        print(f"WordPress files error: {e}")
        return jsonify([])


@app.route('/api/topic_stats')
def get_topic_stats():
    """주제 풀 통계"""
    try:
        from src.utils.database import ContentDatabase
        database = ContentDatabase()
        
        stats = {}
        for site in ['unpre', 'untab', 'skewese']:
            site_stats = database.get_topic_stats(site)
            stats[site] = {
                'used': site_stats.get('used_count', 0),
                'unused': site_stats.get('unused_count', 0),
                'total': site_stats.get('total_count', 0)
            }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"Topic stats error: {e}")
        return jsonify({})


@app.route('/api/publish_to_wordpress', methods=['POST'])
def publish_to_wordpress():
    """WordPress에 실제 발행"""
    try:
        data = request.json
        site = data.get('site')
        file_id = data.get('file_id')
        
        from src.utils.database import ContentDatabase
        from src.publishers.wordpress_publisher import WordPressPublisher
        import json
        
        database = ContentDatabase()
        
        # 파일 정보 가져오기
        file_info = database.get_content_file_by_id(file_id)
        if not file_info:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # HTML 파일 경로
        html_path = Path(file_info['file_path'])
        if not html_path.exists():
            return jsonify({'success': False, 'error': 'HTML file not found'}), 404
        
        # 메타데이터 파일 경로
        meta_path = html_path.with_suffix('.json')
        if not meta_path.exists():
            return jsonify({'success': False, 'error': 'Metadata file not found'}), 404
        
        # 콘텐츠와 메타데이터 읽기
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # WordPress Publisher 초기화
        try:
            publisher = WordPressPublisher(site)
        except ValueError as e:
            return jsonify({'success': False, 'error': f'WordPress configuration error: {str(e)}'}), 500
        
        # 연결 테스트
        if not publisher.test_connection():
            return jsonify({'success': False, 'error': 'Failed to connect to WordPress'}), 500
        
        # 콘텐츠 준비
        content = {
            'title': metadata.get('title', 'Untitled'),
            'content': html_content,
            'meta_description': metadata.get('description', ''),
            'categories': metadata.get('categories', []),
            'tags': metadata.get('tags', [])
        }
        
        # 이미지 처리 (썸네일이 있는 경우)
        images = []
        if metadata.get('thumbnail'):
            thumbnail_path = Path(metadata['thumbnail'])
            if thumbnail_path.exists():
                images.append({
                    'path': str(thumbnail_path),
                    'type': 'thumbnail',
                    'alt': metadata.get('title', '')
                })
        
        # WordPress에 발행
        success, result = publisher.publish_post(content, images=images, draft=False)
        
        if success:
            # 데이터베이스 상태 업데이트
            database.update_content_file_status(
                file_id=file_id,
                status='published',
                published_at=datetime.now().isoformat()
            )
            
            database.add_system_log(
                level="INFO",
                component="wordpress_publisher",
                message=f"Content successfully published to {site}",
                details=f"File ID: {file_id}, Post URL: {result}",
                site=site
            )
            
            return jsonify({'success': True, 'url': result, 'message': f'Successfully published to {site}'})
        else:
            database.add_system_log(
                level="ERROR",
                component="wordpress_publisher",
                message=f"Failed to publish to {site}",
                details=f"File ID: {file_id}, Error: {result}",
                site=site
            )
            
            return jsonify({'success': False, 'error': result}), 500
        
    except Exception as e:
        print(f"Publish to WordPress error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delete_file', methods=['DELETE'])
def delete_file():
    """파일 삭제"""
    try:
        # Content-Type 확인
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        file_id = data.get('file_id')
        if not file_id:
            return jsonify({'success': False, 'error': 'file_id is required'}), 400
        
        # 파일 ID를 정수로 변환
        try:
            file_id = int(file_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'file_id must be a valid integer'}), 400
        
        from src.utils.database import ContentDatabase
        database = ContentDatabase()
        
        success = database.delete_content_file(file_id)
        
        if success:
            # 로그 추가
            database.add_system_log(
                level="INFO",
                component="web_dashboard",
                message=f"Content file deleted successfully",
                details=f"File ID: {file_id}",
                site=None
            )
            return jsonify({'success': True, 'message': 'File deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'File not found or could not be deleted'}), 404
        
    except Exception as e:
        print(f"Delete file error: {e}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@app.route('/favicon.ico')
def favicon():
    """Favicon 서빙"""
    static_folder = Path(__file__).parent.parent / 'static'
    return send_from_directory(str(static_folder), 'favicon.ico')

@app.route('/sw.js')
def service_worker():
    """Service Worker 서빙"""
    static_folder = Path(__file__).parent.parent / 'static'
    return send_from_directory(str(static_folder), 'sw.js')


if __name__ == '__main__':
    print("Web Dashboard Starting...")
    print("Dashboard URL: http://localhost:8080")
    app.run(debug=True, host='127.0.0.1', port=8080)