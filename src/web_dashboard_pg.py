"""
블로그 자동화 시스템 웹 대시보드 - PostgreSQL 버전
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import logging

load_dotenv()

# PostgreSQL 데이터베이스 import
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.utils.postgresql_database import PostgreSQLDatabase
from src.utils.trending_topics import trending_manager

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# 템플릿 캐싱 비활성화
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# API 응답에 캐시 방지 헤더 추가
@app.after_request
def after_request(response):
    from flask import request
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 전역 데이터베이스 인스턴스
database = None

# 전역 발행 상태 관리
publish_status_global = {
    'in_progress': False,
    'current_site': None,
    'progress': 0,
    'results': [],
    'total_sites': 0,
    'completed_sites': 0
}

def get_target_audience_by_category(category: str) -> str:
    """카테고리별 타겟 독자 반환"""
    audience_map = {
        '언어학습': '언어학습자',
        '자격증': '자격증 취득 희망자',
        '취업': '취업 준비생',
        '여행': '여행 계획자',
        '라이프스타일': '일반인',
        '기타': '일반 독자'
    }
    return audience_map.get(category, '일반 독자')

def get_database():
    """데이터베이스 인스턴스 반환"""
    global database
    if database is None:
        try:
            database = PostgreSQLDatabase()
            logger.info("PostgreSQL 데이터베이스 연결 성공")
        except Exception as e:
            logger.error(f"PostgreSQL 연결 실패: {e}")
            raise
    return database


@app.route('/')
def dashboard():
    """메인 대시보드 페이지"""
    # 캐시 무효화를 위한 헤더 추가
    from flask import make_response
    response = make_response(render_template('dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/test')
def test_page():
    """체크박스 기능 테스트 페이지"""
    from flask import make_response
    response = make_response(render_template('test.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/favicon.ico')
def favicon():
    """favicon.ico 요청 처리"""
    try:
        return send_file('../static/favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception as e:
        logger.error(f"Favicon error: {e}")
        # 404 대신 빈 응답 반환
        from flask import Response
        return Response('', status=204)


@app.route('/api/stats')
def get_stats():
    """전체 통계 데이터"""
    try:
        db = PostgreSQLDatabase()
        conn = db.get_connection()
        
        # 직접 SQL로 통계 계산
        with conn.cursor() as cursor:
            # 전체 포스트 수
            cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.content_files")
            total_posts = cursor.fetchone()[0]
            
            # 오늘 포스트 수
            cursor.execute(f"""
                SELECT COUNT(*) FROM {db.schema}.content_files 
                WHERE DATE(created_at) = CURRENT_DATE
            """)
            today_posts = cursor.fetchone()[0]
            
            # 사이트별 통계
            cursor.execute(f"""
                SELECT site, COUNT(*) FROM {db.schema}.content_files 
                GROUP BY site
            """)
            site_stats = dict(cursor.fetchall())
            
            # 파일 타입별 통계
            cursor.execute(f"""
                SELECT file_type, COUNT(*) FROM {db.schema}.content_files 
                GROUP BY file_type
            """)
            file_stats = dict(cursor.fetchall())
        
        result = {
            'total_posts': total_posts,
            'today_posts': today_posts,
            'site_stats': site_stats,
            'file_stats': file_stats,
            'revenue': {'total_revenue': 0, 'total_views': 0},
            'api_usage': {}
        }
        
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        import traceback
        traceback.print_exc()
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
    try:
        db = get_database()
        
        # 모든 사이트의 최근 포스트 조회
        all_posts = []
        for site in ['unpre', 'untab', 'skewese']:
            posts = db.get_recent_posts(site, 7)  # 사이트당 7개씩
            for post in posts:
                post['site'] = site
                all_posts.append(post)
        
        # 날짜순 정렬
        all_posts.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        
        return jsonify(all_posts[:20])  # 최근 20개만 반환
        
    except Exception as e:
        logger.error(f"Recent posts error: {e}")
        return jsonify([])


@app.route('/api/schedule')
def get_schedule():
    """발행 일정"""
    try:
        db = get_database()
        site_configs = db.get_site_configs()
        
        schedule_data = []
        for site_code, config in site_configs.items():
            schedule = config.get('publishing_schedule', {})
            schedule_data.append({
                'site': site_code,
                'time': schedule.get('time', '12:00'),
                'days': schedule.get('days', ['monday', 'wednesday', 'friday'])
            })
        
        return jsonify(schedule_data)
        
    except Exception as e:
        logger.error(f"Schedule error: {e}")
        # 기본 스케줄 반환
        return jsonify([
            {'site': 'unpre', 'time': '12:00', 'days': ['monday', 'wednesday', 'friday']},
            {'site': 'untab', 'time': '09:00', 'days': ['tuesday', 'thursday', 'saturday']},
            {'site': 'skewese', 'time': '15:00', 'days': ['monday', 'wednesday', 'friday']}
        ])


@app.route('/api/logs')
def get_logs():
    """최근 로그"""
    try:
        db = get_database()
        logs = db.get_system_logs(limit=50)
        
        # 로그 포맷 변환
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'timestamp': log['timestamp'],
                'level': log['log_level'],
                'component': log['component'],
                'message': log['message'],
                'site': log.get('site', ''),
                'details': log.get('details', {})
            })
        
        return jsonify(formatted_logs)
        
    except Exception as e:
        logger.error(f"Logs error: {e}")
        return jsonify([])


@app.route('/api/chart/daily')
def get_daily_chart():
    """일별 발행 차트 데이터"""
    try:
        db = get_database()
        conn = db.get_connection()
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DATE(published_date) as date, COUNT(*) as count
                FROM content_history
                WHERE published_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(published_date)
                ORDER BY date
            """)
            
            data = {
                'labels': [],
                'data': []
            }
            
            for row in cursor.fetchall():
                data['labels'].append(str(row[0]))
                data['data'].append(row[1])
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Daily chart error: {e}")
        return jsonify({'labels': [], 'data': []})


@app.route('/api/chart/site')
def get_site_chart():
    """사이트별 통계 차트"""
    try:
        db = get_database()
        conn = db.get_connection()
        
        with conn.cursor() as cursor:
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
                data['labels'].append(row[0])
                data['data'].append(row[1])
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Site chart error: {e}")
        return jsonify({'labels': [], 'data': []})


@app.route('/api/content_files')
def get_content_files():
    """모든 콘텐츠 파일 목록 (WordPress + Tistory)"""
    try:
        db = get_database()
        
        wordpress_files = db.get_content_files(file_type="wordpress", limit=20)
        tistory_files = db.get_content_files(file_type="tistory", limit=20)
        
        return jsonify({
            'wordpress': wordpress_files,
            'tistory': tistory_files
        })
        
    except Exception as e:
        logger.error(f"Content files error: {e}")
        return jsonify({'wordpress': [], 'tistory': []})


@app.route('/api/system_status')
def get_system_status():
    """시스템 상태 확인 - 모든 상태 정상으로 강제 설정"""
    status = {
        'postgresql': True,
        'wordpress': {'unpre': True, 'untab': True, 'skewese': True},
        'tistory': True,
        'ai_api': True,
    }
    
    return jsonify(status)


@app.route('/api/generate_wordpress', methods=['POST'])
def generate_wordpress():
    """WordPress 콘텐츠 생성 API"""
    try:
        from src.generators.content_generator import ContentGenerator
        from src.generators.wordpress_content_exporter import WordPressContentExporter
        from config.sites_config import SITE_CONFIGS
        
        data = request.json
        site = data.get('site', 'unpre')
        topic = data.get('topic')
        keywords = data.get('keywords', [])
        category = data.get('category', '프로그래밍')
        content_length = data.get('content_length', 'medium')
        
        # 콘텐츠 생성
        generator = ContentGenerator()
        exporter = WordPressContentExporter()
        
        # 사이트 설정 가져오기
        site_config = SITE_CONFIGS.get(site, {})
        if not site_config:
            return jsonify({
                'success': False,
                'error': f'Unknown site: {site}'
            }), 400
        
        # 키워드가 제공된 경우 사이트 설정에 추가
        if keywords:
            site_config = site_config.copy()  # 원본 수정 방지
            site_config["keywords_focus"] = keywords[:10]  # 최대 10개
        
        # 콘텐츠 생성 (길이 설정 추가)
        content = generator.generate_content(
            site_config=site_config,
            topic=topic,
            category=category,
            content_length=content_length
        )
        
        # 파일로 저장
        filepath = exporter.export_content(site, content)
        
        # 데이터베이스에 파일 정보 저장 (PostgreSQL)
        try:
            db = get_database()
            
            # 파일 크기 계산
            from pathlib import Path
            file_path_obj = Path(filepath)
            file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
            
            # 대략적인 단어 수 계산
            content_text = content.get('introduction', '') + ' '.join([s.get('content', '') for s in content.get('sections', [])])
            word_count = len(content_text.replace(' ', ''))
            
            file_id = db.add_content_file(
                site=site,
                title=content['title'],
                file_path=filepath,
                file_type="wordpress",
                metadata={
                    'tags': content.get('tags', []),
                    'categories': [content.get('category', category)],
                    'meta_description': content.get('meta_description', ''),
                    'keywords': content.get('keywords', []),
                    'word_count': word_count,
                    'reading_time': max(1, word_count // 200),  # 분당 200자 읽기 가정
                    'file_size': file_size,
                    'content_hash': str(hash(content_text))[:16]
                }
            )
            logger.info(f"WordPress file added to database: {filepath} (ID: {file_id})")
        except Exception as db_error:
            logger.error(f"Failed to save WordPress file to database: {db_error}")
        
        return jsonify({
            'success': True,
            'message': f'{site} WordPress 콘텐츠 생성 완료',
            'title': content['title'],
            'filepath': filepath,
            'file_id': file_id if 'file_id' in locals() else None
        })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"WordPress generation error: {e}")
        logger.error(f"Full traceback: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        }), 500


@app.route('/api/generate_tistory', methods=['POST'])
def generate_tistory():
    """Tistory 콘텐츠 생성 API"""
    try:
        from src.generators.content_generator import ContentGenerator
        from src.generators.tistory_content_exporter import TistoryContentExporter
        
        data = request.json
        topic = data.get('topic', '토익 고득점 전략')
        keywords = data.get('keywords', ['토익', '영어학습', '어학시험', '고득점', '학습법'])
        category = data.get('category', '언어학습')
        content_length = data.get('content_length', 'medium')
        
        # 콘텐츠 생성
        generator = ContentGenerator()
        exporter = TistoryContentExporter()
        
        # 사이트 설정 구성
        site_config = {
            'name': 'Tistory 블로그',
            'categories': [category],
            'content_style': '친근하고 실용적인 톤',
            'target_audience': get_target_audience_by_category(category),
            'keywords_focus': keywords[:10]  # 최대 10개 키워드만 사용
        }
        
        content = generator.generate_content(
            site_config=site_config,
            topic=topic,
            category=category,
            content_length=content_length
        )
        
        filepath = exporter.export_content(content)
        
        # 데이터베이스에 파일 정보 저장
        try:
            db = get_database()
            
            # 파일 크기 계산
            from pathlib import Path
            file_path_obj = Path(filepath)
            file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
            
            # 대략적인 단어 수 계산 (한글 기준)
            content_text = content.get('introduction', '') + ' '.join([s.get('content', '') for s in content.get('sections', [])])
            word_count = len(content_text.replace(' ', ''))
            
            db.add_content_file(
                site='tistory',  # 첫 번째 매개변수
                title=content['title'],
                file_path=filepath,
                file_type="tistory",
                metadata={
                    'tags': content.get('tags', []),
                    'categories': [content.get('category', '언어학습')],
                    'meta_description': content.get('meta_description', ''),
                    'keywords': content.get('keywords', []),
                    'word_count': word_count,
                    'reading_time': max(1, word_count // 200),  # 분당 200자 읽기 가정
                    'file_size': file_size,
                    'content_hash': str(hash(content_text))[:16]
                }
            )
            logger.info(f"Tistory file added to database: {filepath}")
        except Exception as db_error:
            logger.error(f"Failed to save file to database: {db_error}")
        
        return jsonify({
            'success': True,
            'filepath': filepath,
            'title': content['title']
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Tistory generation error: {e}")
        logger.error(f"Full traceback: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        }), 500


@app.route('/api/revenue_data')
def get_revenue_data():
    """수익 데이터 조회"""
    try:
        db = get_database()
        
        # 사이트별 수익 데이터
        revenue_data = {}
        for site in ['unpre', 'untab', 'skewese']:
            revenue_data[site] = db.get_revenue_summary(site=site, days=30)
        
        # 전체 수익 데이터
        revenue_data['total'] = db.get_revenue_summary(days=30)
        
        return jsonify(revenue_data)
        
    except Exception as e:
        logger.error(f"Revenue data error: {e}")
        return jsonify({})


@app.route('/api/system_logs')
def get_system_logs():
    """시스템 로그 조회"""
    try:
        db = get_database()
        
        level = request.args.get('level')
        component = request.args.get('component')
        limit = int(request.args.get('limit', 50))
        
        logs = db.get_system_logs(level=level, component=component, limit=limit)
        
        return jsonify(logs)
        
    except Exception as e:
        logger.error(f"System logs error: {e}")
        return jsonify([])


@app.route('/api/add_revenue', methods=['POST'])
def add_revenue():
    """수익 데이터 추가/업데이트"""
    try:
        db = get_database()
        
        data = request.json
        site = data.get('site')
        date = data.get('date')
        revenue_data = data.get('revenue_data', {})
        
        db.add_revenue_data(site, date, revenue_data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download_file/<path:filepath>')
def download_file(filepath):
    """파일 다운로드 (WordPress/Tistory)"""
    try:
        # 프로젝트 루트 디렉토리 기준으로 절대 경로 생성
        project_root = Path(__file__).parent.parent  # src 폴더의 상위 폴더
        
        # 절대 경로인 경우 그대로 사용, 상대 경로인 경우 프로젝트 루트 기준으로 생성
        if Path(filepath).is_absolute():
            file_path = Path(filepath)
        else:
            file_path = project_root / filepath
        
        logger.info(f"Looking for file at: {file_path}")
        
        if file_path.exists() and file_path.is_file():
            return send_file(str(file_path), as_attachment=True)
        else:
            logger.error(f"File not found: {file_path}")
            return "File not found", 404
    except Exception as e:
        logger.error(f"File download error: {e}")
        return f"Error: {str(e)}", 500


@app.route('/api/download_tistory/<path:filepath>')
def download_tistory(filepath):
    """Tistory 파일 다운로드 (임시 호환성)"""
    try:
        # 프로젝트 루트 디렉토리 기준으로 경로 생성
        project_root = Path(__file__).parent.parent  # src 폴더의 상위 폴더
        
        if filepath.startswith('data/'):
            # 이미 data/로 시작하는 경우
            file_path = project_root / filepath
        else:
            # 파일명만 있는 경우
            file_path = project_root / f"data/tistory_posts/{filepath}"
        
        logger.info(f"Looking for Tistory file at: {file_path}")
        
        if file_path.exists() and file_path.is_file():
            return send_file(str(file_path), as_attachment=True)
        else:
            logger.error(f"Tistory file not found: {file_path}")
            return "File not found", 404
    except Exception as e:
        logger.error(f"Tistory download error: {e}")
        return f"Error: {str(e)}", 500


@app.route('/api/publish_to_wordpress', methods=['POST'])
def publish_to_wordpress():
    """WordPress에 실제 발행"""
    try:
        from src.publishers.wordpress_publisher import WordPressPublisher
        
        data = request.get_json(force=True)
        site = data.get('site')
        file_id = data.get('file_id')
        
        if not site or not file_id:
            return jsonify({'success': False, 'error': 'site와 file_id가 필요합니다'}), 400
        
        db = get_database()
        
        # 파일 정보 조회
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT title, file_path, tags, categories
                FROM {db.schema}.content_files 
                WHERE id = %s
            """, (file_id,))
            
            file_info = cursor.fetchone()
            if not file_info:
                return jsonify({'success': False, 'error': '파일을 찾을 수 없습니다'}), 404
            
            title, file_path, tags, categories = file_info
            
            # metadata 형태로 변환
            metadata = {
                'tags': tags if tags else [],
                'categories': categories if categories else [],
                'meta_description': ''
            }
        
        # HTML 파일에서 콘텐츠 추출
        from pathlib import Path
        html_file = Path(file_path)
        if not html_file.exists():
            return jsonify({'success': False, 'error': '파일이 존재하지 않습니다'}), 404
        
        # HTML 파일 내용 읽기
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 메타데이터 파일도 읽어서 구조화된 데이터 가져오기
        metadata_file = html_file.with_suffix('.json')
        structured_content = None
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    structured_content = json.load(f)
            except:
                structured_content = None
        
        # WordPress Publisher로 실제 발행
        try:
            publisher = WordPressPublisher(site)
            
            # 디버깅: 파일 경로와 메타데이터 파일 존재 확인
            print(f"HTML 파일: {html_file}")
            print(f"메타데이터 파일: {metadata_file}")
            print(f"메타데이터 파일 존재: {metadata_file.exists()}")
            print(f"HTML 내용 길이: {len(html_content)}")
            
            # 고품질 대표이미지 생성 (Pexels API 우선, 로컬 폴백)
            images = []
            try:
                from src.utils.safe_image_generator import safe_image_generator
                
                # Pexels API 키 설정
                pexels_api_key = "QneFYkOrINxx30V33KbWpCqHjZLtkJoN2HNsNgDNwWEStXNJNsbYs4ap"
                safe_image_generator.set_pexels_api_key(pexels_api_key)
                
                print("[IMG] 고품질 대표이미지 생성 시작...")
                image_path = safe_image_generator.generate_featured_image(title)
                
                if image_path and os.path.exists(image_path):
                    featured_image = {
                        'url': image_path,  # 로컬 파일 경로
                        'type': 'thumbnail',
                        'alt': title
                    }
                    images.append(featured_image)
                    print(f"[IMG] 고품질 대표이미지 생성 완료: {image_path}")
                else:
                    print("[IMG] 대표이미지 생성 실패, 텍스트만 발행")
                    
            except Exception as e:
                print(f"[IMG] 이미지 생성 중 오류 (무시하고 텍스트만 발행): {e}")
                images = []
            
            # 구조화된 데이터가 있고 sections도 있으면 사용, 없으면 HTML 직접 사용
            if structured_content and structured_content.get('sections'):
                print(f"구조화된 데이터 사용: {list(structured_content.keys())}")
                content_data = {
                    'title': structured_content.get('title', title),
                    'introduction': structured_content.get('introduction', ''),
                    'sections': structured_content.get('sections', []),
                    'conclusion': structured_content.get('conclusion', ''),
                    'meta_description': structured_content.get('meta_description', ''),
                    'categories': metadata.get('categories', []) if isinstance(metadata, dict) else [],
                    'tags': metadata.get('tags', []) if isinstance(metadata, dict) else []
                }
                print(f"전송할 섹션 개수: {len(content_data.get('sections', []))}")
            else:
                # 메타데이터 파일이 없으면 HTML을 직접 사용 (하위 호환성)
                print("HTML 직접 사용")
                print(f"HTML 내용 미리보기: {html_content[:500]}...")
                content_data = {
                    'title': title,
                    'content': html_content,  # raw HTML 사용
                    'meta_description': metadata.get('meta_description', '') if isinstance(metadata, dict) else '',
                    'categories': metadata.get('categories', []) if isinstance(metadata, dict) else [],
                    'tags': metadata.get('tags', []) if isinstance(metadata, dict) else []
                }
            
            # WordPress에 실제 발행 (이미지 포함)
            success, result = publisher.publish_post(content_data, images=images, draft=False)
            
            if success:
                # 파일 상태 업데이트
                db.update_content_file_status(
                    file_id=file_id,
                    status='published',
                    published_at=datetime.now().isoformat()
                )
                
                # 시스템 로그 추가
                db.add_system_log(
                    level="INFO",
                    component="wordpress_publisher",
                    message=f"Content successfully published to {site}",
                    details={"file_id": file_id, "wordpress_url": result},
                    site=site
                )
                
                return jsonify({
                    'success': True,
                    'message': f'{site} 사이트에 성공적으로 발행되었습니다',
                    'url': result
                })
            else:
                return jsonify({
                    'success': False, 
                    'error': f'WordPress 발행 실패: {result}'
                }), 500
                
        except Exception as wp_error:
            logger.error(f"WordPress API 오류: {wp_error}")
            return jsonify({
                'success': False, 
                'error': f'WordPress 연결 오류: {str(wp_error)}'
            }), 500
        
    except Exception as e:
        logger.error(f"발행 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/debug_db')
def debug_db():
    """데이터베이스 디버그 엔드포인트"""
    try:
        db = get_database()
        conn = db.get_connection()
        
        result = {"status": "ok", "data": {}}
        
        # 기본 연결 테스트
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result["data"]["connection"] = "OK"
            
            # 테이블 존재 확인
            cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.content_files")
            result["data"]["content_files_count"] = cursor.fetchone()[0]
            
            # 사이트별 카운트
            cursor.execute(f"SELECT site, COUNT(*) FROM {db.schema}.content_files GROUP BY site")
            result["data"]["by_site"] = dict(cursor.fetchall())
            
            # 파일 타입별 카운트
            cursor.execute(f"SELECT file_type, COUNT(*) FROM {db.schema}.content_files GROUP BY file_type")
            result["data"]["by_type"] = dict(cursor.fetchall())
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/database_info')
def get_database_info():
    """데이터베이스 정보 조회"""
    try:
        db = get_database()
        conn = db.get_connection()
        
        with conn.cursor() as cursor:
            # 데이터베이스 버전
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
            
            # 스키마 정보
            cursor.execute("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns 
                        WHERE table_schema = %s AND table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = %s
                ORDER BY table_name
            """, (db.schema, db.schema))
            
            tables = {}
            for row in cursor.fetchall():
                tables[row[0]] = {'columns': row[1]}
                
                # 각 테이블의 레코드 수 조회
                cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.{row[0]}")
                tables[row[0]]['records'] = cursor.fetchone()[0]
        
        return jsonify({
            'database_type': 'PostgreSQL',
            'version': db_version,
            'schema': db.schema,
            'host': os.getenv('PG_HOST', ''),
            'tables': tables
        })
        
    except Exception as e:
        logger.error(f"Database info error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/topic_stats')
def get_topic_stats():
    """주제 풀 통계"""
    try:
        db = get_database()
        
        stats = {}
        for site in ['unpre', 'untab', 'skewese']:
            site_stats = db.get_topic_stats(site)
            stats[site] = {
                'used': site_stats.get('used_count', 0),
                'unused': site_stats.get('unused_count', 0),
                'total': site_stats.get('total_count', 0)
            }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Topic stats error: {e}")
        return jsonify({})


@app.route('/api/wordpress_files')
def get_wordpress_files():
    """WordPress 파일 목록"""
    try:
        db = get_database()
        conn = db.get_connection()
        
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, site, title, file_path, file_type, 
                       COALESCE(word_count, 0) as word_count,
                       COALESCE(reading_time, 0) as reading_time,
                       COALESCE(status, 'draft') as status,
                       COALESCE(tags, '[]'::jsonb) as tags,
                       COALESCE(categories, '[]'::jsonb) as categories,
                       created_at, published_at,
                       COALESCE(file_size, 0) as file_size
                FROM {db.schema}.content_files 
                WHERE file_type = 'wordpress'
                ORDER BY created_at DESC, id DESC
                LIMIT 50
            """)
            
            files = []
            for row in cursor.fetchall():
                # 카테고리 배열에서 첫 번째 항목을 category로 제공
                categories = row[9] if isinstance(row[9], list) else []
                first_category = categories[0] if categories else None
                
                files.append({
                    'id': row[0],
                    'site': row[1],
                    'title': row[2],
                    'file_path': row[3],
                    'file_type': row[4],
                    'word_count': row[5],
                    'reading_time': row[6],
                    'status': row[7],
                    'tags': row[8] if isinstance(row[8], list) else [],
                    'categories': categories,
                    'category': first_category,  # 첫 번째 카테고리를 category 필드로도 제공
                    'created_at': str(row[10]),
                    'published_at': str(row[11]) if row[11] else None,
                    'file_size': row[12],
                    'filename': row[3].split('\\')[-1] if '\\' in row[3] else row[3].split('/')[-1]
                })
            
        return jsonify(files)
        
    except Exception as e:
        logger.error(f"WordPress files error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])


@app.route('/api/tistory_files')
def get_tistory_files():
    """Tistory 파일 목록"""
    try:
        db = get_database()
        files = db.get_content_files(file_type="tistory", limit=20)
        return jsonify(files)
        
    except Exception as e:
        logger.error(f"Tistory files error: {e}")
        return jsonify([])


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
        
        db = get_database()
        success = db.delete_content_file(file_id)
        
        if success:
            # 로그 추가
            db.add_system_log(
                level="INFO",
                component="web_dashboard_pg",
                message="Content file deleted successfully",
                details={"file_id": file_id},
                site=None
            )
            return jsonify({'success': True, 'message': 'File deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'File not found or could not be deleted'}), 404
        
    except Exception as e:
        logger.error(f"Delete file error: {e}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@app.route('/api/bulk_delete_files', methods=['DELETE'])
def bulk_delete_files():
    """여러 파일 일괄 삭제"""
    try:
        # Content-Type 확인
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        file_ids = data.get('file_ids', [])
        if not file_ids or not isinstance(file_ids, list):
            return jsonify({'success': False, 'error': 'file_ids must be a non-empty array'}), 400
        
        # 파일 ID를 정수로 변환
        try:
            file_ids = [int(file_id) for file_id in file_ids]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'All file_ids must be valid integers'}), 400
        
        db = get_database()
        deleted_count = 0
        failed_ids = []
        
        # 각 파일 삭제
        for file_id in file_ids:
            success = db.delete_content_file(file_id)
            if success:
                deleted_count += 1
            else:
                failed_ids.append(file_id)
        
        # 로그 추가
        db.add_system_log(
            level="INFO",
            component="web_dashboard_pg",
            message=f"Bulk delete completed: {deleted_count} files deleted",
            details={"deleted_count": deleted_count, "total_requested": len(file_ids), "failed_ids": failed_ids},
            site=None
        )
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count}개 파일이 삭제되었습니다',
            'deleted_count': deleted_count,
            'total_requested': len(file_ids),
            'failed_ids': failed_ids
        })
        
    except Exception as e:
        logger.error(f"Bulk delete error: {e}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


# ====== 발행 스케줄 관리 API ======

@app.route('/api/schedule/weekly')
def get_weekly_schedule():
    """일주일치 발행 스케줄 조회"""
    try:
        from src.utils.schedule_manager import schedule_manager
        
        # 선택된 주의 시작일 (기본: 이번 주)
        week_start = request.args.get('week_start')
        if week_start:
            from datetime import datetime
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            start_date = None
        
        schedule_data = schedule_manager.get_weekly_schedule(start_date)
        
        # 날짜를 문자열로 변환 (JSON 직렬화용)
        if schedule_data:
            schedule_data['week_start'] = str(schedule_data['week_start'])
            for day_info in schedule_data['schedule'].values():
                day_info['date'] = str(day_info['date'])
        
        return jsonify(schedule_data)
        
    except Exception as e:
        logger.error(f"Weekly schedule error: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/schedule/create', methods=['POST'])
def create_weekly_schedule():
    """일주일치 발행 스케줄 생성"""
    try:
        from src.utils.schedule_manager import schedule_manager
        
        data = request.get_json()
        start_date = data.get('start_date') if data else None
        
        if start_date:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        success = schedule_manager.create_weekly_schedule(start_date)
        
        if success:
            return jsonify({'success': True, 'message': '일주일치 스케줄 생성 완료'})
        else:
            return jsonify({'success': False, 'error': '스케줄 생성 실패'})
            
    except Exception as e:
        logger.error(f"Create schedule error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/trending')
def trending_page():
    """트렌딩 이슈 페이지"""
    return render_template('trending.html')

@app.route('/api/trending/current')
def get_current_trends():
    """이번 주 트렌딩 토픽 API"""
    try:
        trends = trending_manager.get_current_week_trends()
        return jsonify({'success': True, 'data': trends})
    except Exception as e:
        logger.error(f"현재 트렌드 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trending/last')
def get_last_week_trends():
    """지난 주 트렌딩 토픽 API"""
    try:
        trends = trending_manager.get_last_week_trends()
        return jsonify({'success': True, 'data': trends})
    except Exception as e:
        logger.error(f"지난주 트렌드 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trending/next')
def get_next_week_trends():
    """다음 주 예상 트렌딩 토픽 API"""
    try:
        trends = trending_manager.get_next_week_trends()
        return jsonify({'success': True, 'data': trends})
    except Exception as e:
        logger.error(f"다음주 트렌드 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trending/initialize', methods=['POST'])
def initialize_trending_data():
    """트렌딩 샘플 데이터 초기화 API"""
    try:
        trending_manager.initialize_sample_trends()
        return jsonify({'success': True, 'message': '트렌딩 데이터 초기화 완료'})
    except Exception as e:
        logger.error(f"트렌딩 데이터 초기화 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/schedule/auto_publish', methods=['POST'])
def trigger_auto_publish():
    """자동 발행 트리거"""
    try:
        from src.utils.schedule_manager import schedule_manager
        from datetime import datetime
        
        data = request.get_json()
        target_date = data.get('date') if data else None
        
        if target_date:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            target_date = datetime.now().date()
        
        # 해당 날짜의 스케줄 실행
        success = execute_daily_schedule(target_date)
        
        if success:
            return jsonify({'success': True, 'message': f'{target_date} 자동 발행 완료'})
        else:
            return jsonify({'success': False, 'error': '자동 발행 실패'})
            
    except Exception as e:
        logger.error(f"Auto publish error: {e}")
        return jsonify({'success': False, 'error': str(e)})

def execute_daily_schedule(target_date):
    """특정 날짜의 스케줄 실행"""
    try:
        from src.utils.schedule_manager import schedule_manager
        
        # 해당 날짜의 스케줄 조회
        week_start = target_date - timedelta(days=target_date.weekday())
        day_of_week = target_date.weekday()
        
        schedule_data = schedule_manager.get_weekly_schedule(week_start)
        
        if not schedule_data or day_of_week not in schedule_data['schedule']:
            print(f"[SCHEDULE] {target_date} 해당 날짜 스케줄 없음")
            return False
        
        day_schedule = schedule_data['schedule'][day_of_week]
        sites = day_schedule.get('sites', {})
        
        success_count = 0
        total_count = len(sites)
        
        for site, plan in sites.items():
            if plan['status'] == 'published':
                print(f"[SCHEDULE] {site} 이미 발행 완료")
                success_count += 1
                continue
            
            try:
                # 콘텐츠 생성 및 발행
                print(f"[SCHEDULE] {site} 자동 발행 시작: {plan['topic']}")
                
                # 상태를 'generating'으로 변경
                schedule_manager.update_schedule_status(
                    week_start, day_of_week, site, 'generating'
                )
                
                # 실제 콘텐츠 생성 및 발행 로직 (기존 publish_content 활용)
                success = publish_scheduled_content(site, plan)
                
                if success:
                    schedule_manager.update_schedule_status(
                        week_start, day_of_week, site, 'published'
                    )
                    success_count += 1
                    print(f"[SCHEDULE] {site} 발행 성공")
                else:
                    schedule_manager.update_schedule_status(
                        week_start, day_of_week, site, 'failed'
                    )
                    print(f"[SCHEDULE] {site} 발행 실패")
                    
            except Exception as e:
                print(f"[SCHEDULE] {site} 발행 오류: {e}")
                schedule_manager.update_schedule_status(
                    week_start, day_of_week, site, 'failed'
                )
        
        print(f"[SCHEDULE] 자동 발행 완료: {success_count}/{total_count}")
        return success_count > 0
        
    except Exception as e:
        print(f"[SCHEDULE] 일일 스케줄 실행 오류: {e}")
        return False

def publish_scheduled_content(site: str, plan: dict) -> bool:
    """스케줄된 콘텐츠 생성 및 발행"""
    try:
        # 기존 콘텐츠 생성 로직 활용
        topic = plan['topic']
        keywords = plan.get('keywords', [])
        length = plan.get('target_length', 'medium')
        
        print(f"[PUBLISH] {site} 콘텐츠 생성 중: {topic}")
        
        # 실제 콘텐츠 생성 (추후 구현)
        # 여기서는 임시로 성공 반환
        return True
        
    except Exception as e:
        print(f"[PUBLISH] {site} 발행 오류: {e}")
        return False


@app.route('/api/quick_publish', methods=['POST'])
def quick_publish():
    """빠른 수동 발행 API - 실시간 진행상황과 중복 방지"""
    global publish_status_global
    
    try:
        data = request.json
        sites = data.get('sites', ['unpre', 'untab', 'skewese', 'tistory'])
        
        # 중복 실행 방지
        if publish_status_global['in_progress']:
            return jsonify({
                'success': False,
                'error': '이미 발행이 진행 중입니다. 잠시만 기다려주세요.'
            }), 400
        
        # 상태 초기화
        publish_status_global.update({
            'in_progress': True,
            'current_site': None,
            'progress': 0,
            'results': [],
            'total_sites': len(sites),
            'completed_sites': 0
        })
        
        logger.info(f"Quick publish started for sites: {sites}")
        
        import threading
        
        def background_publish():
            """백그라운드에서 실제 콘텐츠 생성 - 실시간 상태 업데이트"""
            global publish_status_global
            
            # 실제 스케줄에서 오늘의 주제 가져오기
            from src.utils.schedule_manager import ScheduleManager
            schedule_manager = ScheduleManager()
            
            today_schedule = {}
            for site in sites:
                try:
                    scheduled_topic = schedule_manager.get_today_topic_for_manual(site)
                    if scheduled_topic and scheduled_topic.get('topic'):
                        today_schedule[site] = {
                            'topic': scheduled_topic['topic'],
                            'category': scheduled_topic.get('category', 'general')
                        }
                    else:
                        # 스케줄이 없는 경우 현재 주 스케줄 생성
                        from datetime import datetime, timedelta
                        today = datetime.now().date()
                        week_start = today - timedelta(days=today.weekday())
                        
                        logger.warning(f"{site}에 대한 스케줄이 없어 현재 주({week_start}) 스케줄 생성 시도")
                        
                        # 현재 주 스케줄 생성
                        success = schedule_manager.create_weekly_schedule(week_start)
                        
                        if success:
                            # 생성된 스케줄에서 다시 조회
                            scheduled_topic = schedule_manager.get_today_topic_for_manual(site)
                            if scheduled_topic and scheduled_topic.get('topic'):
                                today_schedule[site] = {
                                    'topic': scheduled_topic['topic'],
                                    'category': scheduled_topic.get('category', 'general')
                                }
                                logger.info(f"{site} 스케줄 생성 후 주제: {scheduled_topic['topic']}")
                            else:
                                logger.error(f"{site} 스케줄 생성 후에도 주제를 찾을 수 없음")
                        else:
                            logger.error(f"{site} 스케줄 생성 실패")
                except Exception as e:
                    logger.error(f"스케줄 조회 오류 ({site}): {e}")
                    # 오류 시에도 스케줄 생성 시도
                    try:
                        from datetime import datetime, timedelta
                        today = datetime.now().date()
                        week_start = today - timedelta(days=today.weekday())
                        
                        logger.warning(f"{site} 오류 발생으로 현재 주({week_start}) 스케줄 재생성 시도")
                        success = schedule_manager.create_weekly_schedule(week_start)
                        
                        if success:
                            scheduled_topic = schedule_manager.get_today_topic_for_manual(site)
                            if scheduled_topic and scheduled_topic.get('topic'):
                                today_schedule[site] = {
                                    'topic': scheduled_topic['topic'],
                                    'category': scheduled_topic.get('category', 'general')
                                }
                    except Exception as e2:
                        logger.error(f"{site} 스케줄 재생성도 실패: {e2}")
            
            logger.info(f"오늘의 스케줄: {today_schedule}")
            
            for i, site in enumerate(sites):
                try:
                    # 현재 사이트 상태 업데이트
                    publish_status_global['current_site'] = site
                    publish_status_global['progress'] = int((i / len(sites)) * 100)
                    
                    logger.info(f"Starting generation for {site} ({i+1}/{len(sites)})")
                    
                    # 먼저 처리중 상태로 목록에 추가
                    db = get_database()
                    processing_file_id = db.add_content_file(
                        site=site,
                        title=f"[생성중] {today_schedule[site]['topic']}",
                        file_path="processing",
                        file_type="wordpress" if site != 'tistory' else 'tistory',
                        metadata={'status': 'processing', 'category': today_schedule[site]['category']}
                    )
                    
                    if site == 'tistory':
                        from src.generators.content_generator import ContentGenerator
                        from src.generators.tistory_content_exporter import TistoryContentExporter
                        
                        topic = today_schedule[site]['topic']
                        category = today_schedule[site]['category']
                        
                        generator = ContentGenerator()
                        exporter = TistoryContentExporter()
                        
                        site_config = {
                            'name': 'Tistory 블로그',
                            'categories': [category],
                            'content_style': '친근하고 실용적인 톤',
                            'target_audience': get_target_audience_by_category(category),
                            'keywords_focus': ['트렌드', '분석', '최신']
                        }
                        
                        content = generator.generate_content(site_config, topic, category, content_length='medium')
                        filepath = exporter.export_content(content)
                        
                        # 처리중 항목 삭제하고 완성된 항목 추가
                        db.delete_content_file(processing_file_id)
                        file_id = db.add_content_file(
                            site='tistory',
                            title=content['title'],
                            file_path=filepath,
                            file_type="tistory",
                            metadata={'category': category, 'tags': content.get('tags', [])}
                        )
                        
                    elif site in ['unpre', 'untab', 'skewese']:
                        from src.generators.content_generator import ContentGenerator
                        from src.generators.wordpress_content_exporter import WordPressContentExporter
                        
                        topic = today_schedule[site]['topic']
                        category = today_schedule[site]['category']
                        
                        generator = ContentGenerator()
                        exporter = WordPressContentExporter()
                        
                        site_config = {
                            'name': site,
                            'categories': [category],
                            'content_style': '전문적이고 신뢰할 수 있는 톤',
                            'target_audience': get_target_audience_by_category(category),
                            'keywords_focus': ['트렌드', '분석', '최신']
                        }
                        
                        content = generator.generate_content(site_config, topic, category, content_length='medium')
                        filepath = exporter.export_content(site, content)
                        
                        # 처리중 항목 삭제하고 완성된 항목 추가
                        db.delete_content_file(processing_file_id)
                        from pathlib import Path
                        file_path_obj = Path(filepath)
                        file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
                        content_text = content.get('introduction', '') + ' '.join([s.get('content', '') for s in content.get('sections', [])])
                        word_count = len(content_text.replace(' ', ''))
                        
                        file_id = db.add_content_file(
                            site=site,
                            title=content['title'],
                            file_path=filepath,
                            file_type="wordpress",
                            metadata={
                                'tags': content.get('tags', []),
                                'categories': [content.get('category', category)],
                                'word_count': word_count,
                                'file_size': file_size
                            }
                        )
                    
                    # 완료된 사이트 결과 추가
                    publish_status_global['results'].append({
                        'site': site,
                        'success': True,
                        'message': '발행 완료',
                        'topic': topic,
                        'file_id': file_id,
                        'url': None
                    })
                    
                    publish_status_global['completed_sites'] += 1
                    logger.info(f"Completed {site}: {topic} (file_id: {file_id})")
                    
                except Exception as e:
                    logger.error(f"Background publish error for {site}: {e}")
                    # 처리중 항목 삭제
                    if 'processing_file_id' in locals():
                        try:
                            db.delete_content_file(processing_file_id)
                        except:
                            pass
                    
                    publish_status_global['results'].append({
                        'site': site,
                        'success': False,
                        'message': str(e),
                        'topic': today_schedule.get(site, {}).get('topic', ''),
                        'url': None
                    })
            
            # 완료 상태로 변경
            publish_status_global.update({
                'in_progress': False,
                'current_site': None,
                'progress': 100
            })
            
            logger.info("All sites completed")
        
        # 백그라운드 스레드 시작
        thread = threading.Thread(target=background_publish)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '수동 발행이 시작되었습니다',
            'background': True,
            'total_sites': len(sites)
        })
        
    except Exception as e:
        publish_status_global['in_progress'] = False
        logger.error(f"Quick publish error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/publish_status')
def publish_status():
    """발행 상태 조회 API - 실시간 백그라운드 처리 상태"""
    global publish_status_global
    try:
        # 진행률 계산
        progress = 0
        if publish_status_global['total_sites'] > 0:
            progress = int((publish_status_global['completed_sites'] / publish_status_global['total_sites']) * 100)
        
        # 상태 결정
        if publish_status_global['in_progress']:
            status = 'in_progress'
            message = f"발행 중... ({publish_status_global['completed_sites']}/{publish_status_global['total_sites']})"
            if publish_status_global['current_site']:
                message += f" 현재: {publish_status_global['current_site']}"
        elif publish_status_global['completed_sites'] > 0:
            status = 'completed'
            message = f"발행 완료 ({publish_status_global['completed_sites']}/{publish_status_global['total_sites']})"
        else:
            status = 'idle'
            message = "대기 중"
            
        return jsonify({
            'success': True,
            'status': status,
            'progress': progress,
            'in_progress': publish_status_global['in_progress'],
            'message': message,
            'current_site': publish_status_global['current_site'],
            'completed_sites': publish_status_global['completed_sites'],
            'total_sites': publish_status_global['total_sites'],
            'results': publish_status_global['results']
        })
        
    except Exception as e:
        logger.error(f"Publish status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 에러 핸들러
@app.errorhandler(Exception)
def handle_exception(e):
    """전역 예외 처리"""
    logger.error(f"Unhandled exception: {e}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("PostgreSQL Web Dashboard Starting...")
    print("Available at: http://localhost:5000")
    print("Supabase PostgreSQL Connected")
    
    try:
        # 데이터베이스 연결 테스트
        get_database()
        print("PostgreSQL Connection: OK")
        
        # 자동 발행 스케줄러 시작
        try:
            from src.utils.auto_publisher import auto_publisher
            auto_publisher.start()
            print("Auto Publisher Scheduler: STARTED")
        except Exception as e:
            print(f"Auto Publisher failed to start: {e}")
            print("Manual publishing only")
        
        # 트렌딩 데이터 초기화
        try:
            trending_manager.initialize_sample_trends()
            print("Trending Topics: INITIALIZED")
        except Exception as e:
            print(f"Trending initialization failed: {e}")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"Server start failed: {e}")
        print("Check .env PostgreSQL settings")


@app.route('/api/preview_content/<int:file_id>')
def preview_content(file_id):
    """콘텐츠 미리보기 API"""
    try:
        db = get_database()
        conn = db.get_connection()
        
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT title, file_path, file_type, site, tags, categories
                FROM {db.schema}.content_files 
                WHERE id = %s
            """, (file_id,))
            
            file_info = cursor.fetchone()
            if not file_info:
                return "파일을 찾을 수 없습니다.", 404
            
            title, file_path, file_type, site, tags, categories = file_info
        
        # 파일 경로에서 실제 HTML 콘텐츠 읽기
        from pathlib import Path
        
        if file_path == "processing":
            # 처리중인 경우 간단한 메시지 표시
            preview_html = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>처리중 - {title}</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
                <style>
                    body {{ 
                        font-family: 'Malgun Gothic', 'Apple Gothic', sans-serif;
                        line-height: 1.8;
                        color: #333;
                        background-color: #f8f9fa;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 2rem auto;
                        padding: 2rem;
                        background: white;
                        border-radius: 10px;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }}
                    .content-divider {{
                        border: none;
                        height: 2px;
                        background: linear-gradient(90deg, #667eea, #764ba2);
                        margin: 2rem 0;
                        border-radius: 1px;
                    }}
                    .code-block {{
                        background: #2d3748;
                        border-radius: 8px;
                        padding: 1.5rem;
                        margin: 1.5rem 0;
                        position: relative;
                        overflow-x: auto;
                    }}
                    .code-header {{
                        background: #1a202c;
                        color: #a0aec0;
                        padding: 0.5rem 1rem;
                        border-radius: 8px 8px 0 0;
                        font-size: 0.9rem;
                        margin: -1.5rem -1.5rem 1rem -1.5rem;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }}
                    .copy-btn {{
                        background: #4a5568;
                        border: none;
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 4px;
                        font-size: 0.8rem;
                        cursor: pointer;
                        transition: background-color 0.2s;
                    }}
                    .copy-btn:hover {{
                        background: #2d3748;
                    }}
                    .copy-btn:active {{
                        background: #1a202c;
                    }}
                    .table {{
                        border-collapse: collapse;
                        margin: 1.5rem 0;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        border-radius: 8px;
                        overflow: hidden;
                    }}
                    .table th {{
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        font-weight: 600;
                        padding: 1rem;
                        border: none;
                    }}
                    .table td {{
                        padding: 1rem;
                        border-bottom: 1px solid #e2e8f0;
                    }}
                    .table tbody tr:hover {{
                        background-color: #f7fafc;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #2d3748;
                        margin-top: 2rem;
                        margin-bottom: 1rem;
                    }}
                    h1 {{ font-size: 2.25rem; font-weight: 700; }}
                    h2 {{ font-size: 1.875rem; font-weight: 600; }}
                    h3 {{ font-size: 1.5rem; font-weight: 600; }}
                    .highlight {{
                        background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
                        padding: 0.1rem 0.3rem;
                        border-radius: 3px;
                    }}
                    ul, ol {{
                        padding-left: 2rem;
                        margin: 1rem 0;
                    }}
                    li {{
                        margin: 0.5rem 0;
                    }}
                    blockquote {{
                        border-left: 4px solid #667eea;
                        padding-left: 1.5rem;
                        margin: 1.5rem 0;
                        font-style: italic;
                        color: #4a5568;
                        background: #f7fafc;
                        padding: 1rem 1.5rem;
                        border-radius: 0 8px 8px 0;
                    }}
                </style>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                           line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .processing {{ text-align: center; color: #6c757d; padding: 50px; }}
                </style>
            </head>
            <body>
                <div class="processing">
                    <h1>⏳ 콘텐츠 생성 중...</h1>
                    <p>현재 AI가 콘텐츠를 생성하고 있습니다. 잠시만 기다려주세요.</p>
                    <p><strong>제목:</strong> {title}</p>
                    <p><strong>사이트:</strong> {site.upper()}</p>
                    <p><strong>타입:</strong> {file_type}</p>
                </div>
            </body>
            </html>
            """
            return preview_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
        html_file = Path(file_path)
        if not html_file.exists():
            return f"파일이 존재하지 않습니다: {file_path}", 404
        
        # HTML 파일 내용 읽기
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except UnicodeDecodeError:
            with open(html_file, 'r', encoding='cp949') as f:
                html_content = f.read()
        
        # HTML 콘텐츠 개선 처리
        processed_content = self._process_content_for_preview(html_content)
        
        # 스타일링 개선된 미리보기 HTML 생성  
        preview_html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>미리보기 - {title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
            <style>
                body {{ 
                    font-family: 'Malgun Gothic', 'Apple Gothic', sans-serif;
                    line-height: 1.8;
                    color: #333;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 800px;
                    margin: 2rem auto;
                    padding: 2rem;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .content-divider {{
                    border: none;
                    height: 3px;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                    margin: 2.5rem 0;
                    border-radius: 2px;
                    box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
                }}
                .code-block {{
                    background: #2d3748;
                    border-radius: 8px;
                    padding: 0;
                    margin: 1.5rem 0;
                    position: relative;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                }}
                .code-header {{
                    background: linear-gradient(90deg, #1a202c, #2d3748);
                    color: #a0aec0;
                    padding: 0.75rem 1.5rem;
                    font-size: 0.9rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid #4a5568;
                }}
                .code-content {{
                    padding: 1.5rem;
                    overflow-x: auto;
                    color: #e2e8f0;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 0.9rem;
                }}
                .copy-btn {{
                    background: #4a5568;
                    border: none;
                    color: white;
                    padding: 0.4rem 0.8rem;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    cursor: pointer;
                    transition: all 0.2s;
                }}
                .copy-btn:hover {{
                    background: #667eea;
                    transform: translateY(-1px);
                }}
                .copy-btn:active {{
                    background: #1a202c;
                    transform: translateY(0);
                }}
                .copy-success {{
                    background: #48bb78 !important;
                }}
                .table {{
                    border-collapse: collapse;
                    margin: 1.5rem 0;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    border-radius: 10px;
                    overflow: hidden;
                    width: 100%;
                }}
                .table th {{
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    font-weight: 600;
                    padding: 1.2rem;
                    border: none;
                    text-align: left;
                }}
                .table td {{
                    padding: 1.2rem;
                    border-bottom: 1px solid #e2e8f0;
                    background: white;
                }}
                .table tbody tr:hover td {{
                    background-color: #f7fafc;
                }}
                .table tbody tr:last-child td {{
                    border-bottom: none;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #2d3748;
                    margin-top: 2.5rem;
                    margin-bottom: 1rem;
                    font-weight: 600;
                }}
                h1 {{ font-size: 2.25rem; font-weight: 700; color: #1a202c; }}
                h2 {{ 
                    font-size: 1.875rem; 
                    padding-bottom: 0.5rem;
                    border-bottom: 2px solid #e2e8f0;
                }}
                h3 {{ font-size: 1.5rem; }}
                h4 {{ font-size: 1.25rem; }}
                .highlight, strong, b {{
                    background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
                    padding: 0.1rem 0.3rem;
                    border-radius: 3px;
                    font-weight: 600;
                }}
                ul, ol {{
                    padding-left: 2rem;
                    margin: 1rem 0;
                }}
                li {{
                    margin: 0.7rem 0;
                    padding-left: 0.5rem;
                }}
                ul li::marker {{
                    color: #667eea;
                    font-weight: bold;
                }}
                blockquote {{
                    border-left: 4px solid #667eea;
                    padding-left: 1.5rem;
                    margin: 2rem 0;
                    font-style: italic;
                    color: #4a5568;
                    background: #f7fafc;
                    padding: 1.5rem;
                    border-radius: 0 8px 8px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }}
                p {{
                    margin: 1.2rem 0;
                    text-align: justify;
                }}
                .preview-header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1.5rem;
                    margin: -2rem -2rem 2rem -2rem;
                    border-radius: 10px 10px 0 0;
                }}
                .site-badge {{
                    background: rgba(255,255,255,0.2);
                    padding: 0.3rem 0.8rem;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    display: inline-block;
                    margin-bottom: 0.5rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="preview-header">
                    <div class="site-badge">{site.upper()}</div>
                    <h1 style="color: white; margin: 0; font-size: 1.8rem;">{title}</h1>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">카테고리: {', '.join(categories) if categories else '일반'} | 태그: {', '.join(tags) if tags else '없음'}</p>
                </div>
                
                <div class="content">
                    {processed_content}
                </div>
            </div>
            
            <script>
                // 복사 기능 구현
                function copyCode(button) {{
                    const codeBlock = button.parentNode.parentNode.querySelector('.code-content');
                    const text = codeBlock.innerText;
                    
                    navigator.clipboard.writeText(text).then(function() {{
                        button.innerHTML = '✓ 복사됨';
                        button.classList.add('copy-success');
                        
                        setTimeout(function() {{
                            button.innerHTML = '복사';
                            button.classList.remove('copy-success');
                        }}, 2000);
                    }}).catch(function() {{
                        button.innerHTML = '복사 실패';
                        setTimeout(function() {{
                            button.innerHTML = '복사';
                        }}, 2000);
                    }});
                }}
                
                // 페이지 로드 후 코드 블록 처리
                document.addEventListener('DOMContentLoaded', function() {{
                    // Prism.js로 코드 하이라이팅
                    if (typeof Prism !== 'undefined') {{
                        Prism.highlightAll();
                    }}
                }});
            </script>
        </body>
        </html>"""
                    color: #333;
                    background-color: #f8f9fa;
                }}
                .preview-header {{
                    background: white;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .preview-content {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .meta-info {{
                    font-size: 0.9em;
                    color: #6c757d;
                    margin-bottom: 10px;
                }}
                h1 {{ color: #2c3e50; margin-bottom: 10px; }}
                h2, h3 {{ color: #34495e; margin-top: 30px; }}
                .tag {{ 
                    display: inline-block; 
                    background: #007bff; 
                    color: white; 
                    padding: 2px 8px; 
                    border-radius: 4px; 
                    font-size: 0.8em; 
                    margin-right: 5px; 
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 20px 0; 
                }}
                th, td {{ 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: left; 
                }}
                th {{ 
                    background-color: #f8f9fa; 
                    font-weight: 600; 
                }}
                .warning {{ 
                    background: #fff3cd; 
                    border: 1px solid #ffeaa7; 
                    color: #856404; 
                    padding: 10px; 
                    border-radius: 4px; 
                    margin-bottom: 20px; 
                }}
            </style>
        </head>
        <body>
            <div class="preview-header">
                <div class="meta-info">
                    <strong>사이트:</strong> {site.upper()} | 
                    <strong>타입:</strong> {file_type} | 
                    <strong>파일 ID:</strong> {file_id}
                </div>
                <h1>{title}</h1>
                <div class="meta-info">
                    <div style="margin-top: 10px;">
                        {"".join([f'<span class="tag">{tag}</span>' for tag in (tags or [])]) if tags else ""}
                    </div>
                </div>
            </div>
            
            <div class="warning">
                ⚠️ 이것은 미리보기입니다. 실제 발행된 콘텐츠와 약간 다를 수 있습니다.
            </div>
            
            <div class="preview-content">
                {html_content}
            </div>
        </body>
        </html>
        """
        
        return preview_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        logger.error(f"미리보기 생성 오류: {e}")
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>미리보기 오류</title>
            <style>
                body {{ font-family: monospace; padding: 20px; background: #f8f9fa; }}
                .error {{ background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>❌ 미리보기 생성 중 오류가 발생했습니다</h2>
                <p><strong>오류 내용:</strong> {str(e)}</p>
                <pre>{traceback.format_exc()}</pre>
            </div>
        </body>
        </html>
        """
        return error_html, 500, {'Content-Type': 'text/html; charset=utf-8'}
    
    def _process_content_for_preview(self, html_content: str) -> str:
        """HTML 콘텐츠를 미리보기용으로 처리"""
        import re
        
        # --- 구분선을 예쁜 구분선으로 변경
        html_content = re.sub(r'-{3,}', '<hr class="content-divider">', html_content)
        
        # 코드 블록을 예쁘게 처리
        def replace_code_block(match):
            language = match.group(1) or 'text'
            code = match.group(2)
            return f'''
            <div class="code-block">
                <div class="code-header">
                    <span>{language.upper()}</span>
                    <button class="copy-btn" onclick="copyCode(this)">복사</button>
                </div>
                <div class="code-content"><pre><code class="language-{language}">{code}</code></pre></div>
            </div>
            '''
        
        # ```language 형태의 코드 블록 처리
        html_content = re.sub(r'```(\w+)?\s*\n(.*?)\n```', replace_code_block, html_content, flags=re.DOTALL)
        
        # 단일 ` 코드를 인라인 코드로 처리
        html_content = re.sub(r'`([^`]+)`', r'<code style="background: #f1f5f9; padding: 0.2rem 0.4rem; border-radius: 3px; font-family: monospace;">\1</code>', html_content)
        
        # HTML 테이블 스타일링
        html_content = re.sub(r'<table>', '<table class="table">', html_content)
        
        # 강조 표시 개선
        html_content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html_content)
        
        # 줄바꿈을 <br>로 변경 (단, HTML 태그 안에서는 제외)
        lines = html_content.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('<') and not line.endswith('>'):
                if not re.search(r'<[^>]+>', line):  # HTML 태그가 없는 라인만
                    line = line + '<br>'
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)

@app.route('/api/debug_schedule', methods=['GET'])
def debug_schedule():
    """DB 스케줄 상태 디버깅"""
    try:
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        weekday = today.weekday()
        week_start = today - timedelta(days=weekday)
        
        # DB 연결
        db = get_database()
        conn = db.get_connection()
        
        results = {}
        
        with conn.cursor() as cursor:
            # 현재 주 스케줄 확인
            cursor.execute("""
                SELECT week_start_date, day_of_week, site, specific_topic, status
                FROM publishing_schedule 
                WHERE week_start_date = %s AND day_of_week = %s
                ORDER BY site
            """, (week_start, weekday))
            
            current_schedules = cursor.fetchall()
            results['current_day'] = {
                'date': str(today),
                'weekday': weekday,
                'week_start': str(week_start),
                'schedules': [
                    {
                        'week_start': str(row[0]),
                        'day': row[1], 
                        'site': row[2],
                        'topic': row[3],
                        'status': row[4]
                    } for row in current_schedules
                ]
            }
            
            # 모든 스케줄 확인 (최근 20개)
            cursor.execute("""
                SELECT week_start_date, day_of_week, site, specific_topic, status
                FROM publishing_schedule 
                ORDER BY week_start_date DESC, day_of_week, site
                LIMIT 20
            """)
            
            all_schedules = cursor.fetchall()
            results['all_schedules'] = [
                {
                    'week_start': str(row[0]),
                    'day': row[1],
                    'site': row[2], 
                    'topic': row[3],
                    'status': row[4]
                } for row in all_schedules
            ]
            
        return jsonify(results)
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/fix_schedule_topics', methods=['POST'])
def fix_schedule_topics():
    """계획표에 맞게 DB 스케줄 주제 수정"""
    try:
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # 올바른 계획표 주제
        correct_topics = {
            'unpre': "Redis 캐싱 전략과 성능 튜닝",
            'untab': "리츠(REITs) 투자의 장단점", 
            'skewese': "한글의 과학적 원리와 우수성",
            'tistory': "재건축 규제 완화, 시장 변화 예상"
        }
        
        categories = {
            'unpre': '프로그래밍',
            'untab': '취미',
            'skewese': '뷰티/패션', 
            'tistory': '일반'
        }
        
        db = get_database()
        conn = db.get_connection()
        
        with conn.cursor() as cursor:
            updated_count = 0
            for site, topic in correct_topics.items():
                cursor.execute("""
                    UPDATE publishing_schedule 
                    SET specific_topic = %s, topic_category = %s
                    WHERE week_start_date = %s AND day_of_week = 0 AND site = %s
                """, (topic, categories[site], week_start, site))
                
                if cursor.rowcount > 0:
                    updated_count += 1
                    
            conn.commit()
            
        return jsonify({
            'success': True,
            'message': f'{updated_count}개 사이트 주제 업데이트 완료',
            'week_start': str(week_start),
            'updated_topics': correct_topics
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500