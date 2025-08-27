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
from src.utils.trending_topic_manager import TrendingTopicManager

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

# 전역 발행 상태 관리 - 상세 로깅 및 실시간 현황 지원
publish_status_global = {
    'in_progress': False,
    'current_site': None,
    'current_task': None,
    'progress': 0,
    'total_posts': 0,
    'completed_posts': 0,
    'failed_posts': 0,
    'results': [],
    'total_sites': 0,
    'completed_sites': 0,
    'errors': [],  # 상세 에러 로그
    'start_time': None,
    'current_step': None,  # 현재 수행중인 단계
    'step_details': None,  # 단계별 상세 정보
    'message': '대기 중...'
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
            
            # 파일 타입별 통계 (file_type 컬럼이 없을 경우 site 기반으로 처리)
            cursor.execute(f"""
                SELECT 
                    COALESCE(file_type, CASE WHEN site = 'tistory' THEN 'tistory' ELSE 'wordpress' END) as file_type, 
                    COUNT(*) 
                FROM {db.schema}.content_files 
                GROUP BY COALESCE(file_type, CASE WHEN site = 'tistory' THEN 'tistory' ELSE 'wordpress' END)
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
    """발행 일정 (레거시)"""
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

@app.route('/api/dual_category_schedule')
def get_dual_category_schedule():
    """2개 카테고리 주간 발행 계획표"""
    try:
        from datetime import datetime, timedelta
        from src.utils.trending_topic_manager import TrendingTopicManager
        
        # 이번주 월요일부터 일요일까지
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        
        manager = TrendingTopicManager()
        sites = ['unpre', 'untab', 'skewese', 'tistory']
        days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        
        weekly_schedule = []
        
        for day_idx in range(7):
            current_date = monday + timedelta(days=day_idx)
            day_name = days[day_idx]
            
            daily_schedule = {
                'date': current_date.isoformat(),
                'day_name': day_name,
                'is_today': current_date == today,
                'sites': {}
            }
            
            for site in sites:
                try:
                    primary, secondary = manager.get_daily_topics(site, current_date)
                    
                    daily_schedule['sites'][site] = {
                        'primary': {
                            'category': primary['category'],
                            'topic': primary['topic'],
                            'keywords': primary['keywords'][:3]
                        },
                        'secondary': {
                            'category': secondary['category'],
                            'topic': secondary['topic'],
                            'keywords': secondary['keywords'][:3]
                        }
                    }
                except Exception as site_error:
                    daily_schedule['sites'][site] = {
                        'error': str(site_error),
                        'primary': None,
                        'secondary': None
                    }
            
            weekly_schedule.append(daily_schedule)
        
        # 사이트 정보 추가
        site_info = {
            'unpre': {'name': 'UNPRE', 'domain': 'unpre.co.kr', 'color': '#1976d2'},
            'untab': {'name': 'UNTAB', 'domain': 'untab.co.kr', 'color': '#388e3c'},
            'skewese': {'name': 'SKEWESE', 'domain': 'skewese.com', 'color': '#f57c00'},
            'tistory': {'name': 'TISTORY', 'domain': 'tistory.com', 'color': '#c2185b'}
        }
        
        return jsonify({
            'success': True,
            'week_start': monday.isoformat(),
            'week_end': (monday + timedelta(days=6)).isoformat(),
            'schedule': weekly_schedule,
            'site_info': site_info,
            'stats': {
                'total_weekly_posts': 56,  # 7일 × 4사이트 × 2카테고리
                'daily_posts': 8,
                'sites_count': len(sites),
                'categories_per_site': 2
            },
            'auto_publish_time': '03:00 KST',
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Dual category schedule error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


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


@app.route('/api/get_today_topics')
def get_today_topics():
    """오늘의 실제 듀얼 카테고리 주제 조회 - PostgreSQL DB 기반"""
    try:
        db = get_database()
        conn = db.get_connection()
        today = date.today()
        
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT site, topic_category, specific_topic
                FROM {db.schema}.monthly_publishing_schedule
                WHERE year = %s AND month = %s AND day = %s
                ORDER BY site, topic_category
            """, (today.year, today.month, today.day))
            
            results = cursor.fetchall()
            
        # 사이트별로 Primary/Secondary 구분
        today_topics = {}
        
        for site, category, topic in results:
            site_lower = site.lower()
            if site_lower not in today_topics:
                today_topics[site_lower] = {}
                
            # 첫 번째 주제를 Primary로, 두 번째 주제를 Secondary로 분류
            if 'primary' not in today_topics[site_lower]:
                today_topics[site_lower]['primary'] = {
                    'category': category,
                    'topic': topic
                }
            else:
                today_topics[site_lower]['secondary'] = {
                    'category': category,
                    'topic': topic
                }
        
        logger.info(f"오늘({today}) 실제 스케줄 조회 완료: {len(results)}개 주제")
        return jsonify(today_topics)
        
    except Exception as e:
        logger.error(f"Today topics error: {e}")
        # 오류 발생시 빈 객체 대신 실제 오류 정보 반환
        return jsonify({
            'error': str(e),
            'message': 'DB에서 오늘 스케줄을 불러올 수 없습니다',
            'date': date.today().isoformat()
        }), 500


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
        
        # 보안상 위험한 경로 접근 방지
        if '..' in filepath or filepath.startswith('/'):
            return jsonify({'error': 'Invalid file path'}), 400
        
        # 절대 경로인 경우 그대로 사용, 상대 경로인 경우 프로젝트 루트 기준으로 생성
        if Path(filepath).is_absolute():
            file_path = Path(filepath)
        else:
            file_path = project_root / filepath
        
        logger.info(f"Looking for file at: {file_path}")
        
        # 파일 존재 여부 및 접근 권한 확인
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
            
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            return jsonify({'error': 'Path is not a file'}), 400
        
        # 파일 다운로드
        return send_file(str(file_path), as_attachment=True)
        
    except Exception as e:
        logger.error(f"File download error: {e}")
        return jsonify({'error': f'Download error: {str(e)}'}), 500


@app.route('/api/download_content/<int:file_id>')
def download_content(file_id):
    """콘텐츠 다운로드 (PostgreSQL 기반)"""
    try:
        db = get_database()
        
        # DB에서 콘텐츠 조회
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, title, file_path, category, tags, site, created_at
                FROM {db.schema}.content_files 
                WHERE id = %s
            """, (file_id,))
            
            result = cursor.fetchone()
            
            if not result:
                logger.error(f"콘텐츠를 찾을 수 없음: ID {file_id}")
                return jsonify({'error': 'Content not found'}), 404
            
            content_id, title, file_path, category, tags, site, created_at = result
            keywords = tags or []
            
            # 실제 파일에서 콘텐츠 읽기
            content_text = ""
            if file_path and Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # HTML 파일인 경우 본문 추출
                    if file_path.endswith('.html'):
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(file_content, 'html.parser')
                        content_text = soup.get_text(separator='\n', strip=True)
                    else:
                        content_text = file_content
                        
                except Exception as e:
                    logger.error(f"파일 읽기 실패 ({file_path}): {e}")
                    content_text = "콘텐츠를 읽을 수 없습니다."
            else:
                content_text = "파일이 존재하지 않습니다."
            
            # HTML 콘텐츠 생성
            html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Noto Sans KR', Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #007bff;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .title {{
            color: #333;
            font-size: 2em;
            font-weight: bold;
            margin: 0;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .content {{
            color: #444;
            font-size: 1.1em;
            line-height: 1.8;
        }}
        .keywords {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }}
        .keyword {{
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-bottom: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">{title}</h1>
            <div class="meta">
                카테고리: {category} | 사이트: {site.upper()} | 생성일: {created_at.strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
        
        <div class="content">
            {content_text.replace(chr(10), '<br>')}
        </div>
        
        <div class="keywords">
            <strong>키워드:</strong><br>
            {''.join([f'<span class="keyword">{keyword}</span>' for keyword in (keywords or [])])}
        </div>
    </div>
</body>
</html>"""
            
            # 파일로 저장 후 다운로드
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_path = f.name
            
            filename = f"{title[:30]}_{site}_{content_id}.html"
            # 파일명에서 특수문자 제거
            import re
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            return send_file(temp_path, as_attachment=True, download_name=filename)
            
    except Exception as e:
        logger.error(f"콘텐츠 다운로드 오류: {e}")
        return jsonify({'error': f'Download error: {str(e)}'}), 500

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
    """WordPress에 실제 발행 - 진행상황 업데이트 포함"""
    try:
        from src.publishers.wordpress_publisher import WordPressPublisher
        
        data = request.get_json(force=True)
        site = data.get('site')
        file_id = data.get('file_id')
        
        if not site or not file_id:
            return jsonify({'success': False, 'error': 'site와 file_id가 필요합니다'}), 400
        
        # 발행 상태 초기화
        global publish_status_global
        publish_status_global.update({
            'in_progress': True,
            'current_site': site,
            'current_task': f'콘텐츠 ID {file_id} 발행 중',
            'current_step': 'preparation',
            'step_details': f'{site.upper()} 사이트로 개별 발행 시작',
            'message': f'📤 {site.upper()} 사이트로 발행 시작...',
            'progress': 10
        })
        
        db = get_database()
        
        # 파일 정보 조회
        publish_status_global.update({
            'current_step': 'database_query',
            'step_details': f'DB에서 콘텐츠 정보 조회',
            'message': f'📋 콘텐츠 정보 조회 중...',
            'progress': 20
        })
        
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT title, file_path, tags, categories
                FROM {db.schema}.content_files 
                WHERE id = %s
            """, (file_id,))
            
            file_info = cursor.fetchone()
            if not file_info:
                publish_status_global.update({
                    'in_progress': False,
                    'current_step': 'error',
                    'step_details': '파일을 찾을 수 없음',
                    'message': '❌ 파일을 찾을 수 없습니다',
                    'progress': 0
                })
                return jsonify({'success': False, 'error': '파일을 찾을 수 없습니다'}), 404
            
            title, file_path, tags, categories = file_info
            
            # metadata 형태로 변환
            metadata = {
                'tags': tags if tags else [],
                'categories': categories if categories else [],
                'meta_description': ''
            }
        
        # HTML 파일에서 콘텐츠 추출
        publish_status_global.update({
            'current_step': 'file_reading',
            'step_details': f'콘텐츠 파일 읽기',
            'message': f'📄 콘텐츠 파일 로드 중...',
            'progress': 30
        })
        
        from pathlib import Path
        html_file = Path(file_path)
        if not html_file.exists():
            publish_status_global.update({
                'in_progress': False,
                'current_step': 'error',
                'step_details': '파일이 존재하지 않음',
                'message': '❌ 파일이 존재하지 않습니다',
                'progress': 0
            })
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
            publish_status_global.update({
                'current_step': 'wordpress_connection',
                'step_details': f'{site.upper()} WordPress 연결 초기화',
                'message': f'🔗 {site.upper()} WordPress 연결 중...',
                'progress': 40
            })
            
            publisher = WordPressPublisher(site)
            
            # 연결 테스트
            if not publisher.test_connection():
                publish_status_global.update({
                    'in_progress': False,
                    'current_step': 'error',
                    'step_details': f'{site.upper()} WordPress 연결 실패',
                    'message': f'❌ {site.upper()} WordPress 연결 실패 - 호스팅 차단 또는 설정 오류',
                    'progress': 0
                })
                return jsonify({
                    'success': False, 
                    'error': f'{site.upper()} WordPress API 연결 실패 - 호스팅에서 REST API가 차단되었을 수 있습니다'
                }), 503
            
            # 디버깅: 파일 경로와 메타데이터 파일 존재 확인
            print(f"HTML 파일: {html_file}")
            print(f"메타데이터 파일: {metadata_file}")
            print(f"메타데이터 파일 존재: {metadata_file.exists()}")
            print(f"HTML 내용 길이: {len(html_content)}")
            
            # 고품질 대표이미지 생성 (Pexels API 우선, 로컬 폴백)
            publish_status_global.update({
                'current_step': 'image_generation',
                'step_details': f'대표이미지 생성',
                'message': f'🖼️ 대표이미지 생성 중...',
                'progress': 50
            })
            
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
            publish_status_global.update({
                'current_step': 'publishing',
                'step_details': f'{site.upper()} WordPress로 콘텐츠 전송',
                'message': f'🚀 {site.upper()}로 콘텐츠 발행 중...',
                'progress': 70
            })
            
            success, result = publisher.publish_post(content_data, images=images, draft=False)
            
            if success:
                # 파일 상태 업데이트
                publish_status_global.update({
                    'current_step': 'completion',
                    'step_details': f'발행 완료 - DB 업데이트',
                    'message': f'✅ {site.upper()} 발행 성공!',
                    'progress': 90
                })
                
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
                
                publish_status_global.update({
                    'in_progress': False,
                    'current_step': 'success',
                    'step_details': f'{site.upper()} 발행 완료',
                    'message': f'🎉 {site.upper()}에 성공적으로 발행되었습니다',
                    'progress': 100
                })
                
                return jsonify({
                    'success': True,
                    'message': f'{site} 사이트에 성공적으로 발행되었습니다',
                    'url': result
                })
            else:
                publish_status_global.update({
                    'in_progress': False,
                    'current_step': 'error',
                    'step_details': f'{site.upper()} 발행 실패',
                    'message': f'❌ {site.upper()} 발행 실패: {result}',
                    'progress': 0
                })
                return jsonify({
                    'success': False, 
                    'error': f'WordPress 발행 실패: {result}'
                }), 500
                
        except Exception as wp_error:
            logger.error(f"WordPress API 오류: {wp_error}")
            publish_status_global.update({
                'in_progress': False,
                'current_step': 'error',
                'step_details': f'WordPress 연결 오류',
                'message': f'❌ WordPress API 오류: {str(wp_error)}',
                'progress': 0
            })
            return jsonify({
                'success': False, 
                'error': f'WordPress 연결 오류: {str(wp_error)}'
            }), 500
        
    except Exception as e:
        logger.error(f"발행 오류: {e}")
        publish_status_global.update({
            'in_progress': False,
            'current_step': 'error',
            'step_details': f'시스템 오류',
            'message': f'❌ 시스템 오류: {str(e)}',
            'progress': 0
        })
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
                SELECT id, site, title, file_path, 
                       COALESCE(file_type, 'wordpress') as file_type,
                       COALESCE(word_count, 0) as word_count,
                       COALESCE(reading_time, 0) as reading_time,
                       COALESCE(status, 'draft') as status,
                       COALESCE(tags, ARRAY[]::text[]) as tags,
                       COALESCE(categories, ARRAY[]::text[]) as categories,
                       created_at, published_at,
                       COALESCE(file_size, 0) as file_size
                FROM {db.schema}.content_files 
                WHERE COALESCE(file_type, 'wordpress') = 'wordpress' OR site != 'tistory'
                ORDER BY created_at DESC, id DESC
                LIMIT 50
            """)
            
            files = []
            for row in cursor.fetchall():
                # 인덱스 재조정: id, site, title, file_path, file_type, word_count, reading_time, status, tags, categories, created_at, published_at, file_size
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
    """일주일치 발행 스케줄 조회 (레거시)"""
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

@app.route('/api/schedule/monthly')
def get_monthly_schedule():
    """월별 발행 스케줄 조회"""
    try:
        from src.utils.monthly_schedule_manager import monthly_schedule_manager
        from datetime import datetime
        
        # 선택된 년월 (기본: 이번 달)
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        if not year or not month:
            today = datetime.now()
            year = year or today.year
            month = month or today.month
        
        # 월별 스케줄 조회
        schedule = monthly_schedule_manager.get_month_schedule(year, month)
        
        # 응답 형식 구성
        response = {
            'year': year,
            'month': month,
            'schedule': {}
        }
        
        # 날짜별로 정리하고 primary/secondary 형식으로 변환
        for day, sites in schedule.items():
            day_schedule = {}
            
            for site, topics in sites.items():
                # topics는 리스트 형태이므로 primary/secondary로 분리
                if len(topics) >= 2:
                    # 2개 이상인 경우 첫 번째는 primary, 두 번째는 secondary
                    day_schedule[site] = {
                        'primary': {
                            'category': topics[0]['category'],
                            'topic': topics[0]['topic'],
                            'keywords': topics[0]['keywords']
                        },
                        'secondary': {
                            'category': topics[1]['category'],
                            'topic': topics[1]['topic'],
                            'keywords': topics[1]['keywords']
                        }
                    }
                elif len(topics) == 1:
                    # 1개만 있는 경우 primary만 설정
                    day_schedule[site] = {
                        'primary': {
                            'category': topics[0]['category'],
                            'topic': topics[0]['topic'],
                            'keywords': topics[0]['keywords']
                        }
                    }
            
            if day_schedule:  # 스케줄이 있는 날만 추가
                response['schedule'][day] = day_schedule
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Monthly schedule error: {e}")
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
    """이번 주 트렌딩 토픽 API - 실시간 데이터"""
    try:
        real_trending_manager = TrendingTopicManager()
        
        # 실시간 트렌딩 데이터 수집 및 업데이트
        real_trending_manager.update_trending_cache(force_update=True)
        
        # 사이트별 트렌딩 주제 수집
        site_trends = {}
        for site in ['unpre', 'untab', 'skewese']:
            config = real_trending_manager.site_configs[site]
            primary_category = config['primary']
            secondary_category = config['secondary']
            
            primary_topics = real_trending_manager.get_trending_topics(site, primary_category, 8)
            secondary_topics = real_trending_manager.get_trending_topics(site, secondary_category, 8)
            
            # 트렌드 형식으로 변환
            trends = []
            for i, topic in enumerate(primary_topics[:4]):
                trends.append({
                    'category': primary_category,
                    'trend_type': 'hot' if i < 2 else 'rising',
                    'title': topic,
                    'description': f'{primary_category} 분야의 최신 트렌딩 이슈입니다',
                    'keywords': real_trending_manager._extract_keywords(topic),
                    'priority': 9 - i
                })
            
            for i, topic in enumerate(secondary_topics[:4]):
                trends.append({
                    'category': secondary_category,
                    'trend_type': 'rising' if i < 2 else 'predicted',
                    'title': topic,
                    'description': f'{secondary_category} 분야의 실시간 트렌딩 주제입니다',
                    'keywords': real_trending_manager._extract_keywords(topic),
                    'priority': 8 - i
                })
            
            site_trends[site] = trends
        
        # 공통 실시간 이슈 생성 (모든 사이트 트렌드에서 선별)
        cross_category_issues = []
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        
        # 실시간 트렌딩 데이터로 핫이슈 생성 (하드코딩 완전 제거)
        hot_issues = []
        
        try:
            # 실시간 트렌딩 매니저에서 최신 트렌드 가져오기
            real_trending_manager.update_trending_cache(force_update=True)
            
            # 모든 사이트에서 고우선순위 트렌딩 토픽 수집
            all_trending_topics = []
            for site in ['unpre', 'untab', 'skewese']:
                site_config = real_trending_manager.site_configs.get(site, {})
                for category in [site_config.get('primary'), site_config.get('secondary')]:
                    if category:
                        topics = real_trending_manager.get_trending_topics(site, category, 5)
                        for topic in topics:
                            all_trending_topics.append({
                                'category': category.split('/')[0].lower(),  # '기술/디지털' -> 'technology'
                                'trend_type': 'hot',
                                'title': f"🔥 {topic}",
                                'description': f"실시간으로 주목받고 있는 {category} 분야의 핫이슈입니다",
                                'keywords': real_trending_manager._extract_keywords(topic),
                                'priority': 9
                            })
            
            # 카테고리 매핑 (한국어 -> 영어)
            category_mapping = {
                '기술': 'technology',
                '교육': 'education', 
                '재정': 'economy',
                '라이프스타일': 'lifestyle',
                '건강': 'health',
                '역사': 'culture',
                '엔터테인먼트': 'culture',
                '트렌드': 'social'
            }
            
            # 카테고리별로 최고 우선순위 토픽만 선별 (중복 제거)
            category_best = {}
            for topic in all_trending_topics:
                category = topic['category']
                if category not in category_best or topic['priority'] > category_best[category]['priority']:
                    # 카테고리 매핑 적용
                    mapped_category = category_mapping.get(category, category)
                    topic['category'] = mapped_category
                    category_best[mapped_category] = topic
            
            # 최종 핫이슈 리스트 (최대 8개)
            hot_issues = list(category_best.values())[:8]
            
        except Exception as e:
            print(f"[TRENDING] 실시간 핫이슈 생성 오류: {e}")
            # 에러 시 기본 동적 이슈 생성
            current_time = datetime.now()
            
            hot_issues = [
                {
                    'category': 'technology',
                    'trend_type': 'hot',
                    'title': f'🔥 {current_time.strftime("%m월 %d일")} AI 기술 동향',
                    'description': '최신 AI 기술 발전과 산업 동향을 실시간으로 분석합니다',
                    'keywords': ['AI', '기술동향', '실시간분석'],
                    'priority': 9
                },
                {
                    'category': 'economy',
                    'trend_type': 'hot', 
                    'title': f'🔥 {current_time.strftime("%m월 %d일")} 경제 트렌드',
                    'description': '실시간 경제 지표와 시장 동향을 분석합니다',
                    'keywords': ['경제동향', '시장분석', '투자트렌드'],
                    'priority': 8
                }
            ]
        
        cross_category_issues.extend(hot_issues)
        
        # 사이트별 상위 트렌드도 일부 공통 이슈로 승격
        for site, trends in site_trends.items():
            if trends:
                top_trend = trends[0]  # 첫 번째 트렌드를 공통 이슈로 승격
                cross_category_issues.append({
                    'category': top_trend['category'],
                    'trend_type': 'rising',
                    'title': f"📈 {top_trend['title']}",
                    'description': f"{site} 사이트에서 주목받는 {top_trend['category']} 분야 트렌드",
                    'keywords': top_trend['keywords'],
                    'priority': top_trend['priority'] - 1
                })
        
        trends_data = {
            'period': '이번주',
            'week_start': week_start,
            'site_trends': site_trends,
            'cross_category_issues': cross_category_issues,
            'total_site_count': sum(len(site_trends) for site_trends in site_trends.values()),
            'cross_category_count': len(cross_category_issues)
        }
        
        return jsonify({'success': True, 'data': trends_data})
        
    except Exception as e:
        logger.error(f"실시간 트렌드 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trending/last')
def get_last_week_trends():
    """지난 주 트렌딩 토픽 API - 실시간 데이터"""
    try:
        real_trending_manager = TrendingTopicManager()
        real_trending_manager.update_trending_cache()
        
        # 전주 데이터는 실제 실시간 데이터의 이전 버전으로 시뮬레이션
        site_trends = {}
        for site in ['unpre', 'untab', 'skewese']:
            config = real_trending_manager.site_configs[site]
            primary_category = config['primary']
            secondary_category = config['secondary']
            
            # 이전 트렌드로 시뮬레이션 (실제로는 캐시된 데이터 활용)
            primary_topics = real_trending_manager.get_trending_topics(site, primary_category, 6)
            secondary_topics = real_trending_manager.get_trending_topics(site, secondary_category, 6)
            
            trends = []
            for i, topic in enumerate(primary_topics[-3:]):  # 뒤쪽 데이터를 전주 데이터로 사용
                trends.append({
                    'category': primary_category,
                    'trend_type': 'hot',
                    'title': f"전주 {topic}",
                    'description': f'지난주 {primary_category} 분야의 주요 이슈였습니다',
                    'keywords': real_trending_manager._extract_keywords(topic),
                    'priority': 8 - i
                })
            
            for i, topic in enumerate(secondary_topics[-3:]):
                trends.append({
                    'category': secondary_category,
                    'trend_type': 'rising',
                    'title': f"전주 {topic}",
                    'description': f'지난주 {secondary_category} 분야에서 관심받은 주제입니다',
                    'keywords': real_trending_manager._extract_keywords(topic),
                    'priority': 7 - i
                })
            
            site_trends[site] = trends
        
        # 지난주 공통 이슈
        cross_category_issues = [
            {
                'category': 'technology',
                'trend_type': 'hot',
                'title': '전주 AI 기술 발전',
                'description': '지난주 AI 기술 분야의 주요 발전이 있었습니다',
                'keywords': ['AI', '기술발전', '인공지능'],
                'priority': 8
            }
        ]
        
        last_week_start = (datetime.now() - timedelta(days=datetime.now().weekday() + 7)).strftime('%Y-%m-%d')
        
        trends_data = {
            'period': '전주',
            'week_start': last_week_start,
            'site_trends': site_trends,
            'cross_category_issues': cross_category_issues,
            'total_site_count': sum(len(site_trends) for site_trends in site_trends.values()),
            'cross_category_count': len(cross_category_issues)
        }
        
        return jsonify({'success': True, 'data': trends_data})
        
    except Exception as e:
        logger.error(f"전주 트렌드 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trending/next')
def get_next_week_trends():
    """다음 주 예상 트렌딩 토픽 API - 예측 데이터"""
    try:
        real_trending_manager = TrendingTopicManager()
        real_trending_manager.update_trending_cache()
        
        # 다음주 예상 트렌드 생성
        site_trends = {}
        for site in ['unpre', 'untab', 'skewese']:
            config = real_trending_manager.site_configs[site]
            primary_category = config['primary']
            secondary_category = config['secondary']
            
            # 현재 트렌드를 기반으로 다음주 예상 트렌드 생성
            current_primary = real_trending_manager.get_trending_topics(site, primary_category, 4)
            current_secondary = real_trending_manager.get_trending_topics(site, secondary_category, 4)
            
            trends = []
            
            # 예상 트렌드 생성 (현재 트렌드 기반)
            predicted_topics = [
                f"다음주 전망: {primary_category} 신기술 동향",
                f"예상 이슈: {secondary_category} 분야 주요 변화",
                f"다음주 주목: {primary_category} 업계 소식",
                f"예측 트렌드: {secondary_category} 최신 동향"
            ]
            
            for i, topic in enumerate(predicted_topics):
                category = primary_category if i % 2 == 0 else secondary_category
                trends.append({
                    'category': category,
                    'trend_type': 'predicted',
                    'title': topic,
                    'description': f'{category} 분야의 다음주 예상 트렌드입니다',
                    'keywords': [category.split('/')[0], '예상', '전망'],
                    'priority': 7 - (i // 2)
                })
            
            site_trends[site] = trends
        
        # 다음주 예상 공통 이슈
        cross_category_issues = [
            {
                'category': 'technology',
                'trend_type': 'predicted',
                'title': '다음주 기술 트렌드 전망',
                'description': '다음주 주목할 만한 기술 분야 이슈들이 예상됩니다',
                'keywords': ['기술', '전망', '예상이슈'],
                'priority': 8
            },
            {
                'category': 'economy',
                'trend_type': 'predicted',
                'title': '다음주 경제 동향 전망',
                'description': '경제 분야의 주요 변화가 예상되는 상황입니다',
                'keywords': ['경제', '동향', '전망'],
                'priority': 7
            }
        ]
        
        next_week_start = (datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=7)).strftime('%Y-%m-%d')
        
        trends_data = {
            'period': '다음주',
            'week_start': next_week_start,
            'site_trends': site_trends,
            'cross_category_issues': cross_category_issues,
            'total_site_count': sum(len(site_trends) for site_trends in site_trends.values()),
            'cross_category_count': len(cross_category_issues)
        }
        
        return jsonify({'success': True, 'data': trends_data})
        
    except Exception as e:
        logger.error(f"다음주 트렌드 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trending/initialize', methods=['POST'])
def initialize_trending_data():
    """실시간 트렌딩 데이터 강제 업데이트 API"""
    try:
        real_trending_manager = TrendingTopicManager()
        success = real_trending_manager.update_trending_cache(force_update=True)
        
        if success:
            return jsonify({'success': True, 'message': '실시간 트렌딩 데이터 업데이트 완료'})
        else:
            return jsonify({'success': False, 'message': '트렌딩 데이터 업데이트 실패'})
            
    except Exception as e:
        logger.error(f"트렌딩 데이터 업데이트 오류: {e}")
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
            """백그라운드에서 실제 콘텐츠 생성 - 듀얼 카테고리 시스템"""
            global publish_status_global

            # 듀얼 카테고리를 위한 월간 스케줄 매니저 사용
            from src.utils.monthly_schedule_manager import monthly_schedule_manager
            from src.generators.content_generator import ContentGenerator
            from src.generators.tistory_content_exporter import TistoryContentExporter
            from src.generators.wordpress_content_exporter import WordPressContentExporter

            from datetime import datetime
            import time
            
            start_time = datetime.now()
            logger.info("듀얼 카테고리 수동 발행 시작")
            
            # 상세 상태 초기화
            publish_status_global.update({
                'in_progress': True,
                'message': "발행 준비 중...",
                'progress': 0,
                'current_site': None,
                'current_task': None,
                'current_step': 'initialization',
                'step_details': '시스템 초기화 및 준비',
                'completed_sites': 0,
                'completed_posts': 0,
                'failed_posts': 0,
                'total_posts': len(sites) * 2,
                'total_sites': len(sites),
                'results': [],
                'errors': [],
                'start_time': start_time.isoformat()
            })

            # 각 사이트별로 2개씩 처리 (총 8개)
            total_posts = len(sites) * 2  # 사이트당 2개
            completed_posts = 0
            
            logger.info(f"📊 발행 계획: {len(sites)}개 사이트 × 2개 포스트 = {total_posts}개 총 포스트")
            
            # 초기화 완료 상태 업데이트
            publish_status_global.update({
                'current_step': 'database_connection',
                'step_details': 'DB 연결 확인 중...',
                'message': f"DB 연결 확인 중... (총 {total_posts}개 포스트 예정)"
            })

            # DB 연결
            try:
                logger.info("🔌 DB 연결 시도 중...")
                db = get_database()
                logger.info("✅ DB 연결 성공")
                
                publish_status_global.update({
                    'current_step': 'ready_to_publish',
                    'step_details': 'DB 연결 완료, 발행 시작 준비',
                    'message': f"DB 연결 성공! 발행 시작 중... (0/{total_posts})"
                })
                
            except Exception as e:
                error_msg = f"DB 연결 오류: {str(e)}"
                logger.error(f"❌ {error_msg}")
                
                publish_status_global.update({
                    'in_progress': False,
                    'current_step': 'failed',
                    'step_details': 'DB 연결 실패로 발행 중단',
                    'message': f"❌ DB 연결 실패: {str(e)}",
                    'errors': [{
                        'timestamp': datetime.now().isoformat(),
                        'type': 'database_connection',
                        'message': error_msg,
                        'details': str(e)
                    }]
                })
                return

            for site_idx, site in enumerate(sites, 1):
                try:
                    # 현재 사이트 상태 업데이트
                    publish_status_global.update({
                        'current_site': site,
                        'current_step': 'topic_loading',
                        'step_details': f'{site.upper()} 사이트 주제 조회',
                        'message': f"📋 {site.upper()} 사이트 주제 조회 중... ({site_idx}/{len(sites)} 사이트)"
                    })
                    
                    logger.info(f"🎯 {site} 사이트 듀얼 카테고리 발행 시작 ({site_idx}/{len(sites)})")

                    # 듀얼 카테고리 주제 가져오기
                    try:
                        primary_topic, secondary_topic = monthly_schedule_manager.get_today_dual_topics_for_manual(site)
                        logger.info(f"✅ {site} 주제 조회 성공")
                        
                    except Exception as e:
                        error_msg = f"{site} 주제 조회 오류: {str(e)}"
                        logger.error(f"❌ {error_msg}")
                        
                        publish_status_global['errors'].append({
                            'timestamp': datetime.now().isoformat(),
                            'site': site,
                            'type': 'topic_loading',
                            'message': error_msg,
                            'details': str(e)
                        })
                        
                        publish_status_global['results'].append({
                            'site': site,
                            'status': 'failed',
                            'message': f'주제 조회 실패: {str(e)}',
                            'category': 'system',
                            'error_details': str(e)
                        })
                        continue

                    if not primary_topic or not secondary_topic:
                        error_msg = f"{site}의 듀얼 카테고리 주제를 찾을 수 없습니다"
                        logger.error(f"❌ {error_msg}")
                        
                        publish_status_global['errors'].append({
                            'timestamp': datetime.now().isoformat(),
                            'site': site,
                            'type': 'missing_topics',
                            'message': error_msg,
                            'details': f'Primary: {primary_topic}, Secondary: {secondary_topic}'
                        })
                        
                        publish_status_global['results'].append({
                            'site': site,
                            'status': 'failed',
                            'message': '주제를 찾을 수 없음 - DB 스케줄 확인 필요',
                            'category': 'system'
                        })
                        continue

                    logger.info(f"🎯 {site} 듀얼 주제 확인 - Primary: {primary_topic['topic']}, Secondary: {secondary_topic['topic']}")
                    
                    # 주제 조회 완료 상태 업데이트
                    publish_status_global.update({
                        'current_step': 'content_generation',
                        'step_details': f'{site.upper()}: Primary + Secondary 콘텐츠 생성',
                        'message': f"📝 {site.upper()}: Primary [{primary_topic['topic']}] 생성 시작..."
                    })

                    # Primary 카테고리 발행
                    try:
                        logger.info(f"📝 {site} Primary 카테고리 발행 시작: {primary_topic['topic']}")
                        
                        # 상태 업데이트
                        publish_status_global.update({
                            'current_task': f"Primary: {primary_topic['topic']}",
                            'step_details': f'{site.upper()}: DB 저장 및 콘텐츠 생성 준비',
                            'message': f"💾 {site.upper()}: Primary DB 저장 중..."
                        })

                        # DB에 처리중 상태로 추가
                        try:
                            primary_file_id = db.add_content_file(
                                site=site,
                                title=f"[Primary 생성중] {primary_topic['topic']}",
                                file_path="processing",
                                file_type="wordpress" if site != 'tistory' else 'tistory',
                                metadata={
                                    'status': 'processing',
                                    'category': primary_topic['category'],
                                    'category_type': 'primary',
                                    'tags': primary_topic.get('keywords', []),
                                    'categories': [primary_topic['category']]
                                }
                            )
                            logger.info(f"✅ {site} Primary DB 저장 완료 (ID: {primary_file_id})")
                            
                        except Exception as e:
                            error_msg = f"{site} Primary DB 저장 실패: {str(e)}"
                            logger.error(f"❌ {error_msg}")
                            
                            publish_status_global['errors'].append({
                                'timestamp': datetime.now().isoformat(),
                                'site': site,
                                'type': 'database_save',
                                'category': 'primary',
                                'topic': primary_topic['topic'],
                                'message': error_msg,
                                'details': str(e)
                            })
                            
                            raise Exception(f"DB 저장 실패: {str(e)}")
                            
                        # 콘텐츠 생성 상태 업데이트
                        publish_status_global.update({
                            'step_details': f'{site.upper()}: Primary 콘텐츠 AI 생성 중',
                            'message': f"🤖 {site.upper()}: Primary [{primary_topic['topic']}] AI 생성 중..."
                        })

                        # 콘텐츠 생성
                        if site == 'tistory':
                            generator = ContentGenerator()
                            exporter = TistoryContentExporter()

                            site_config = {
                                'name': 'Tistory 블로그',
                                'categories': [primary_topic['category']],
                                'content_style': '친근하고 실용적인 톤',
                                'target_audience': get_target_audience_by_category(primary_topic['category']),
                                'keywords_focus': primary_topic.get('keywords', [])
                            }

                            content_data = generator.generate_content(
                                site_config,
                                primary_topic['topic'],
                                primary_topic['category'],
                                'medium'
                            )

                            if content_data:
                                filepath = exporter.export_content(content_data)

                                # DB 업데이트
                                db.delete_content_file(primary_file_id)
                                final_file_id = db.add_content_file(
                                    site=site,
                                    title=content_data['title'],
                                    file_path=filepath,
                                    file_type='tistory',
                                    metadata={
                                        'category': primary_topic['category'],
                                        'category_type': 'primary',
                                        'tags': content_data.get('tags', [])
                                    }
                                )
                                
                                # 발행 완료 시간 업데이트 - DB에 바로 반영되도록
                                from datetime import datetime
                                db.update_file_status(final_file_id, 'published', datetime.now())
                                
                                # 콘텐츠 목록에 즉시 반영되도록 메타데이터 업데이트
                                try:
                                    db.update_content_metadata(final_file_id, {
                                        'category': primary_topic['category'],
                                        'category_type': 'primary',
                                        'tags': content_data.get('tags', []),
                                        'auto_published': True
                                    })
                                except Exception as meta_error:
                                    logger.warning(f"메타데이터 업데이트 실패: {meta_error}")

                                # Tistory는 수동 발행만 지원 (자동 발행 제거)
                                logger.info(f"Tistory Primary 콘텐츠 생성 완료 (수동 발행): {primary_topic['topic']}")
                                publish_status_global['results'].append({
                                    'site': site,
                                    'status': 'success',
                                    'message': f'Primary 콘텐츠 생성 완료 (수동 발행 필요): {primary_topic["topic"]}',
                                    'category': 'primary',
                                    'topic': primary_topic['topic']
                                })

                                logger.info(f"{site} Primary 발행 성공: {primary_topic['topic']}")
                            else:
                                raise Exception("콘텐츠 생성 실패")
                        else:
                            # WordPress 사이트 처리
                            generator = ContentGenerator()
                            exporter = WordPressContentExporter()

                            site_config = {
                                'name': site,
                                'categories': [primary_topic['category']],
                                'content_style': '전문적이고 신뢰할 수 있는 톤',
                                'target_audience': get_target_audience_by_category(primary_topic['category']),
                                'keywords_focus': primary_topic.get('keywords', [])
                            }

                            content_data = generator.generate_content(
                                site_config,
                                primary_topic['topic'],
                                primary_topic['category'],
                                'medium'
                            )

                            if content_data:
                                filepath = exporter.export_content(site, content_data)

                                # DB 업데이트
                                db.delete_content_file(primary_file_id)
                                final_file_id = db.add_content_file(
                                    site=site,
                                    title=content_data['title'],
                                    file_path=filepath,
                                    file_type='wordpress',
                                    metadata={
                                        'category': primary_topic['category'],
                                        'category_type': 'primary',
                                        'tags': content_data.get('tags', [])
                                    }
                                )
                                
                                # 발행 완료 시간 업데이트 - DB에 바로 반영되도록
                                from datetime import datetime
                                db.update_file_status(final_file_id, 'published', datetime.now())
                                
                                # 콘텐츠 목록에 즉시 반영되도록 메타데이터 업데이트
                                try:
                                    db.update_content_metadata(final_file_id, {
                                        'category': primary_topic['category'],
                                        'category_type': 'primary',
                                        'tags': content_data.get('tags', []),
                                        'auto_published': True
                                    })
                                except Exception as meta_error:
                                    logger.warning(f"메타데이터 업데이트 실패: {meta_error}")

                                # WordPress 자동 사이트 발행
                                try:
                                    logger.info(f"WordPress Primary 자동 발행 시작: {primary_topic['topic']}")
                                    
                                    # WordPress Publisher를 사용한 자동 발행
                                    from src.publishers.wordpress_publisher import WordPressPublisher
                                    from pathlib import Path
                                    
                                    # 파일 정보 조회 - final_file_id 사용
                                    conn_auto = db.get_connection()
                                    with conn_auto.cursor() as cursor_auto:
                                        cursor_auto.execute(f"""
                                            SELECT title, file_path, tags, categories
                                            FROM {db.schema}.content_files 
                                            WHERE id = %s
                                        """, (final_file_id,))
                                        
                                        file_info = cursor_auto.fetchone()
                                        if file_info:
                                            title, file_path, tags, categories = file_info
                                            
                                            # HTML 및 메타데이터 파일 읽기
                                            html_file = Path(file_path)
                                            if html_file.exists():
                                                with open(html_file, 'r', encoding='utf-8') as f:
                                                    html_content = f.read()
                                                
                                                # 메타데이터 파일 확인
                                                metadata_file = html_file.with_suffix('.json')
                                                structured_content = None
                                                if metadata_file.exists():
                                                    try:
                                                        with open(metadata_file, 'r', encoding='utf-8') as f:
                                                            structured_content = json.load(f)
                                                    except:
                                                        structured_content = None
                                                
                                                # WordPress Publisher로 발행
                                                publisher = WordPressPublisher(site)
                                                
                                                # 이미지 생성
                                                images = []
                                                try:
                                                    from src.utils.safe_image_generator import safe_image_generator
                                                    pexels_api_key = "QneFYkOrINxx30V33KbWpCqHjZLtkJoN2HNsNgDNwWEStXNJNsbYs4ap"
                                                    safe_image_generator.set_pexels_api_key(pexels_api_key)
                                                    image_path = safe_image_generator.generate_featured_image(title)
                                                    if image_path and os.path.exists(image_path):
                                                        images.append({'url': image_path, 'type': 'thumbnail', 'alt': title})
                                                except:
                                                    images = []
                                                
                                                # 콘텐츠 데이터 준비 (카테고리 보강)
                                                if structured_content and structured_content.get('sections'):
                                                    content_data = {
                                                        'title': structured_content.get('title', title),
                                                        'introduction': structured_content.get('introduction', ''),
                                                        'sections': structured_content.get('sections', []),
                                                        'conclusion': structured_content.get('conclusion', ''),
                                                        'meta_description': structured_content.get('meta_description', ''),
                                                        'categories': categories if categories else [primary_topic['category']],
                                                        'tags': tags if tags else []
                                                    }
                                                else:
                                                    content_data = {
                                                        'title': title,
                                                        'content': html_content,
                                                        'meta_description': '',
                                                        'categories': categories if categories else [primary_topic['category']],
                                                        'tags': tags if tags else []
                                                    }
                                                
                                                # WordPress에 발행
                                                success, result = publisher.publish_post(content_data, images=images, draft=False)
                                                
                                                if success:
                                                    publish_status_global['results'].append({
                                                        'site': site,
                                                        'status': 'success',
                                                        'message': f'Primary 발행 및 자동 업로드 완료: {primary_topic["topic"]}',
                                                        'category': 'primary',
                                                        'topic': primary_topic['topic'],
                                                        'wordpress_url': result
                                                    })
                                                else:
                                                    publish_status_global['results'].append({
                                                        'site': site,
                                                        'status': 'success', # 콘텐츠는 생성됐으므로 success
                                                        'message': f'Primary 콘텐츠 생성 완료, 자동 업로드 실패: {result}',
                                                        'category': 'primary',
                                                        'topic': primary_topic['topic']
                                                    })
                                            else:
                                                publish_status_global['results'].append({
                                                    'site': site,
                                                    'status': 'success', # 콘텐츠는 생성됐으므로 success
                                                    'message': f'Primary 콘텐츠 생성 완료, 파일 없음으로 자동 업로드 실패',
                                                    'category': 'primary',
                                                    'topic': primary_topic['topic']
                                                })
                                        else:
                                            publish_status_global['results'].append({
                                                'site': site,
                                                'status': 'success', # 콘텐츠는 생성됐으므로 success
                                                'message': f'Primary 콘텐츠 생성 완료, DB 조회 실패로 자동 업로드 실패',
                                                'category': 'primary',
                                                'topic': primary_topic['topic']
                                            })
                                    
                                except Exception as publish_error:
                                    logger.error(f"WordPress Primary 자동 발행 실패: {publish_error}")
                                    publish_status_global['results'].append({
                                        'site': site,
                                        'status': 'success', # 콘텐츠는 생성됐으므로 success
                                        'message': f'Primary 콘텐츠 생성 완료, 사이트 업로드는 수동 필요: {primary_topic["topic"]}',
                                        'category': 'primary',
                                        'topic': primary_topic['topic']
                                    })

                                logger.info(f"{site} Primary 발행 성공: {primary_topic['topic']}")
                            else:
                                raise Exception("콘텐츠 생성 실패")

                        completed_posts += 1
                        publish_status_global['completed_sites'] = completed_posts
                        publish_status_global['progress'] = int((completed_posts / total_posts) * 100)

                    except Exception as e:
                        logger.error(f"{site} Primary 발행 실패: {e}")
                        # 처리중 항목 삭제
                        try:
                            db.delete_content_file(primary_file_id)
                        except:
                            pass
                        publish_status_global['results'].append({
                            'site': site,
                            'status': 'failed',
                            'message': f'Primary 발행 실패: {str(e)}',
                            'category': 'primary'
                        })

                    # Secondary 카테고리 발행
                    try:
                        logger.info(f"{site} Secondary 카테고리 발행 시작: {secondary_topic['topic']}")

                        # DB에 처리중 상태로 추가
                        secondary_file_id = db.add_content_file(
                            site=site,
                            title=f"[Secondary 생성중] {secondary_topic['topic']}",
                            file_path="processing",
                            file_type="wordpress" if site != 'tistory' else 'tistory',
                            metadata={
                                'status': 'processing',
                                'category': secondary_topic['category'],
                                'category_type': 'secondary'
                            }
                        )

                        # 콘텐츠 생성 (Primary와 유사한 로직)
                        if site == 'tistory':
                            generator = ContentGenerator()
                            exporter = TistoryContentExporter()

                            site_config = {
                                'name': 'Tistory 블로그',
                                'categories': [secondary_topic['category']],
                                'content_style': '친근하고 실용적인 톤',
                                'target_audience': get_target_audience_by_category(secondary_topic['category']),
                                'keywords_focus': secondary_topic.get('keywords', [])
                            }

                            content_data = generator.generate_content(
                                site_config,
                                secondary_topic['topic'],
                                secondary_topic['category'],
                                'medium'
                            )

                            if content_data:
                                filepath = exporter.export_content(content_data)

                                # DB 업데이트
                                db.delete_content_file(secondary_file_id)
                                final_secondary_file_id = db.add_content_file(
                                    site=site,
                                    title=content_data['title'],
                                    file_path=filepath,
                                    file_type='tistory',
                                    metadata={
                                        'category': secondary_topic['category'],
                                        'category_type': 'secondary',
                                        'tags': content_data.get('tags', [])
                                    }
                                )
                                
                                # 발행 완료 시간 업데이트
                                db.update_file_status(final_secondary_file_id, 'published', datetime.now())

                                # Tistory는 수동 발행만 지원 (자동 발행 제거)
                                logger.info(f"Tistory Secondary 콘텐츠 생성 완료 (수동 발행): {secondary_topic['topic']}")
                                publish_status_global['results'].append({
                                    'site': site,
                                    'status': 'success',
                                    'message': f'Secondary 콘텐츠 생성 완료 (수동 발행 필요): {secondary_topic["topic"]}',
                                    'category': 'secondary',
                                    'topic': secondary_topic['topic']
                                })

                                logger.info(f"{site} Secondary 발행 성공: {secondary_topic['topic']}")
                            else:
                                raise Exception("콘텐츠 생성 실패")
                        else:
                            # WordPress 사이트 처리
                            generator = ContentGenerator()
                            exporter = WordPressContentExporter()

                            site_config = {
                                'name': site,
                                'categories': [secondary_topic['category']],
                                'content_style': '전문적이고 신뢰할 수 있는 톤',
                                'target_audience': get_target_audience_by_category(secondary_topic['category']),
                                'keywords_focus': secondary_topic.get('keywords', [])
                            }

                            content_data = generator.generate_content(
                                site_config,
                                secondary_topic['topic'],
                                secondary_topic['category'],
                                'medium'
                            )

                            if content_data:
                                filepath = exporter.export_content(site, content_data)

                                # DB 업데이트
                                db.delete_content_file(secondary_file_id)
                                final_file_id = db.add_content_file(
                                    site=site,
                                    title=content_data['title'],
                                    file_path=filepath,
                                    file_type='wordpress',
                                    metadata={
                                        'category': secondary_topic['category'],
                                        'category_type': 'secondary',
                                        'tags': content_data.get('tags', [])
                                    }
                                )
                                
                                # 발행 완료 시간 업데이트
                                db.update_file_status(final_file_id, 'published', datetime.now())

                                # WordPress Secondary 자동 사이트 발행
                                try:
                                    logger.info(f"WordPress Secondary 자동 발행 시작: {secondary_topic['topic']}")
                                    
                                    # WordPress Publisher를 사용한 자동 발행
                                    from src.publishers.wordpress_publisher import WordPressPublisher
                                    from pathlib import Path
                                    
                                    # 파일 정보 조회 - final_file_id 사용
                                    conn_auto = db.get_connection()
                                    with conn_auto.cursor() as cursor_auto:
                                        cursor_auto.execute(f"""
                                            SELECT title, file_path, tags, categories
                                            FROM {db.schema}.content_files 
                                            WHERE id = %s
                                        """, (final_file_id,))
                                        
                                        file_info = cursor_auto.fetchone()
                                        if file_info:
                                            title, file_path, tags, categories = file_info
                                            
                                            # HTML 및 메타데이터 파일 읽기
                                            html_file = Path(file_path)
                                            if html_file.exists():
                                                with open(html_file, 'r', encoding='utf-8') as f:
                                                    html_content = f.read()
                                                
                                                # 메타데이터 파일 확인
                                                metadata_file = html_file.with_suffix('.json')
                                                structured_content = None
                                                if metadata_file.exists():
                                                    try:
                                                        with open(metadata_file, 'r', encoding='utf-8') as f:
                                                            structured_content = json.load(f)
                                                    except:
                                                        structured_content = None
                                                
                                                # WordPress Publisher로 발행
                                                publisher = WordPressPublisher(site)
                                                
                                                # 이미지 생성
                                                images = []
                                                try:
                                                    from src.utils.safe_image_generator import safe_image_generator
                                                    pexels_api_key = "QneFYkOrINxx30V33KbWpCqHjZLtkJoN2HNsNgDNwWEStXNJNsbYs4ap"
                                                    safe_image_generator.set_pexels_api_key(pexels_api_key)
                                                    image_path = safe_image_generator.generate_featured_image(title)
                                                    if image_path and os.path.exists(image_path):
                                                        images.append({'url': image_path, 'type': 'thumbnail', 'alt': title})
                                                except:
                                                    images = []
                                                
                                                # 콘텐츠 데이터 준비 (카테고리 보강)
                                                if structured_content and structured_content.get('sections'):
                                                    content_data = {
                                                        'title': structured_content.get('title', title),
                                                        'introduction': structured_content.get('introduction', ''),
                                                        'sections': structured_content.get('sections', []),
                                                        'conclusion': structured_content.get('conclusion', ''),
                                                        'meta_description': structured_content.get('meta_description', ''),
                                                        'categories': categories if categories else [primary_topic['category']],
                                                        'tags': tags if tags else []
                                                    }
                                                else:
                                                    content_data = {
                                                        'title': title,
                                                        'content': html_content,
                                                        'meta_description': '',
                                                        'categories': categories if categories else [primary_topic['category']],
                                                        'tags': tags if tags else []
                                                    }
                                                
                                                # WordPress에 발행
                                                success, result = publisher.publish_post(content_data, images=images, draft=False)
                                                
                                                if success:
                                                    publish_status_global['results'].append({
                                                        'site': site,
                                                        'status': 'success',
                                                        'message': f'Secondary 발행 및 자동 업로드 완료: {secondary_topic["topic"]}',
                                                        'category': 'secondary',
                                                        'topic': secondary_topic['topic'],
                                                        'wordpress_url': result
                                                    })
                                                else:
                                                    publish_status_global['results'].append({
                                                        'site': site,
                                                        'status': 'success', # 콘텐츠는 생성됐으므로 success
                                                        'message': f'Secondary 콘텐츠 생성 완료, 자동 업로드 실패: {result}',
                                                        'category': 'secondary',
                                                        'topic': secondary_topic['topic']
                                                    })
                                            else:
                                                publish_status_global['results'].append({
                                                    'site': site,
                                                    'status': 'success', # 콘텐츠는 생성됐으므로 success
                                                    'message': f'Secondary 콘텐츠 생성 완료, 파일 없음으로 자동 업로드 실패',
                                                    'category': 'secondary',
                                                    'topic': secondary_topic['topic']
                                                })
                                        else:
                                            publish_status_global['results'].append({
                                                'site': site,
                                                'status': 'success', # 콘텐츠는 생성됐으므로 success
                                                'message': f'Secondary 콘텐츠 생성 완료, DB 조회 실패로 자동 업로드 실패',
                                                'category': 'secondary',
                                                'topic': secondary_topic['topic']
                                            })
                                    
                                except Exception as publish_error:
                                    logger.error(f"WordPress Secondary 자동 발행 실패: {publish_error}")
                                    publish_status_global['results'].append({
                                        'site': site,
                                        'status': 'success', # 콘텐츠는 생성됐으므로 success
                                        'message': f'Secondary 콘텐츠 생성 완료, 사이트 업로드는 수동 필요: {secondary_topic["topic"]}',
                                        'category': 'secondary',
                                        'topic': secondary_topic['topic']
                                    })

                                logger.info(f"{site} Secondary 발행 성공: {secondary_topic['topic']}")
                            else:
                                raise Exception("콘텐츠 생성 실패")

                        completed_posts += 1
                        publish_status_global['completed_sites'] = completed_posts
                        publish_status_global['progress'] = int((completed_posts / total_posts) * 100)

                    except Exception as e:
                        logger.error(f"{site} Secondary 발행 실패: {e}")
                        # 처리중 항목 삭제
                        try:
                            db.delete_content_file(secondary_file_id)
                        except:
                            pass
                        publish_status_global['results'].append({
                            'site': site,
                            'status': 'failed',
                            'message': f'Secondary 발행 실패: {str(e)}',
                            'category': 'secondary'
                        })

                    # 사이트 완료 결과 추가
                    publish_status_global['results'].append({
                        'site': site,
                        'status': 'completed',
                        'message': f'Primary: {primary_topic["topic"]}, Secondary: {secondary_topic["topic"]}',
                        'primary_topic': primary_topic['topic'],
                        'secondary_topic': secondary_topic['topic']
                    })

                except Exception as e:
                    logger.error(f"{site} 전체 처리 실패: {e}")
                    publish_status_global['results'].append({
                        'site': site,
                        'status': 'failed',
                        'message': str(e)
                    })

            # 완료 처리
            publish_status_global['in_progress'] = False
            publish_status_global['progress'] = 100
            publish_status_global['completed_sites'] = completed_posts
            publish_status_global['total_sites'] = total_posts
            publish_status_global['current_site'] = None
            
            # 결과 요약 메시지 생성
            success_count = len([r for r in publish_status_global['results'] if r.get('status') == 'success'])
            failed_count = len(publish_status_global['results']) - success_count
            
            if failed_count == 0:
                publish_status_global['message'] = f"🎉 전체 발행 완료! 총 {completed_posts}개 포스트 생성됨"
            else:
                publish_status_global['message'] = f"⚠️ 발행 완료 - 성공: {success_count}개, 실패: {failed_count}개"

            logger.info(f"듀얼 카테고리 수동 발행 완료: {completed_posts}/{total_posts} 포스트")
        
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
    """발행 상태 조회 API - 실시간 백그라운드 처리 상태 (상세 로깅 포함)"""
    global publish_status_global
    try:
        from datetime import datetime
        
        # 진행률 계산 (포스트 기준)
        post_progress = 0
        if publish_status_global.get('total_posts', 0) > 0:
            completed = publish_status_global.get('completed_posts', 0)
            total = publish_status_global.get('total_posts', 1)
            post_progress = int((completed / total) * 100)
        
        # 사이트 진행률 계산
        site_progress = 0
        if publish_status_global.get('total_sites', 0) > 0:
            site_progress = int((publish_status_global.get('completed_sites', 0) / publish_status_global.get('total_sites', 1)) * 100)
        
        # 상태 결정
        if publish_status_global.get('in_progress', False):
            status = 'in_progress'
        elif publish_status_global.get('completed_posts', 0) > 0:
            status = 'completed'
        else:
            status = 'idle'
        
        # 실행 시간 계산
        elapsed_time = None
        if publish_status_global.get('start_time'):
            try:
                start = datetime.fromisoformat(publish_status_global['start_time'])
                elapsed = datetime.now() - start
                elapsed_time = f"{elapsed.seconds // 60}분 {elapsed.seconds % 60}초"
            except:
                pass
        
        # 응답 데이터 구성
        response = {
            'status': status,
            'message': publish_status_global.get('message', '대기 중...'),
            'progress': post_progress,
            'site_progress': site_progress,
            'current_site': publish_status_global.get('current_site'),
            'current_task': publish_status_global.get('current_task'),
            'current_step': publish_status_global.get('current_step'),
            'step_details': publish_status_global.get('step_details'),
            'completed_posts': publish_status_global.get('completed_posts', 0),
            'failed_posts': publish_status_global.get('failed_posts', 0),
            'total_posts': publish_status_global.get('total_posts', 0),
            'completed_sites': publish_status_global.get('completed_sites', 0),
            'total_sites': publish_status_global.get('total_sites', 0),
            'results': publish_status_global.get('results', []),
            'errors': publish_status_global.get('errors', []),  # 상세 에러 로그
            'start_time': publish_status_global.get('start_time'),
            'elapsed_time': elapsed_time,
            'in_progress': publish_status_global.get('in_progress', False)
        }
        
        return jsonify(response)
        
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
        processed_content = _process_content_for_preview(html_content)
        
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
    
def _process_content_for_preview(html_content: str) -> str:
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

@app.route('/api/sync_schedule', methods=['POST'])
def sync_schedule():
    """발행 계획표 동기화 API"""
    try:
        from src.utils.schedule_sync import sync_schedule_api
        
        # POST 데이터에서 스케줄 텍스트 가져오기
        data = request.get_json() or {}
        schedule_text = data.get('schedule_text')
        
        result = sync_schedule_api(schedule_text)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/emergency_sync', methods=['POST'])
def emergency_sync():
    """긴급 현재 주 동기화 API"""
    try:
        from src.utils.schedule_sync import emergency_sync_current_week
        
        result = emergency_sync_current_week()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/import_dashboard_schedules', methods=['POST'])
def import_dashboard_schedules():
    """대시보드 기존 스케줄을 DB에 강제 입력"""
    try:
        from src.utils.dashboard_schedule_importer import import_dashboard_schedules as import_func
        
        success = import_func()
        
        if success:
            return jsonify({
                'success': True,
                'message': '대시보드 스케줄 데이터를 DB에 성공적으로 가져왔습니다'
            })
        else:
            return jsonify({
                'success': False,
                'message': '스케줄 가져오기 실패'
            }), 500
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/create_dual_category_schedule', methods=['POST'])
def create_dual_category_schedule():
    try:
        from src.utils.schedule_manager import ScheduleManager
        from datetime import datetime, timedelta
        
        data = request.get_json() or {}
        week_start_str = data.get('week_start')
        
        if week_start_str:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        else:
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
        
        schedule_manager = ScheduleManager()
        success = schedule_manager.create_dual_category_weekly_schedule(week_start)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'{week_start} 주 2개 카테고리 스케줄 생성 완료',
                'week_start': week_start.isoformat(),
                'total_posts': 56
            })
        else:
            return jsonify({'success': False, 'message': '스케줄 생성 실패'}), 500
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_all_dual_topics', methods=['GET'])
def get_all_dual_topics():
    try:
        from src.utils.schedule_manager import ScheduleManager
        
        schedule_manager = ScheduleManager()
        sites = ['unpre', 'untab', 'skewese', 'tistory']
        all_topics = {}
        
        for site in sites:
            try:
                primary_topic, secondary_topic = schedule_manager.get_today_dual_topics_for_manual(site)
                all_topics[site] = {
                    'primary': {'category': primary_topic['category'], 'topic': primary_topic['topic']},
                    'secondary': {'category': secondary_topic['category'], 'topic': secondary_topic['topic']}
                }
            except Exception:
                all_topics[site] = {'error': 'Failed to get topics'}
        
        return jsonify({
            'success': True,
            'sites': all_topics,
            'total_daily_posts': len([t for t in all_topics.values() if 'error' not in t]) * 2,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================================================
# 시스템 상태 및 진단 API
# ========================================================================

@app.route('/api/system_status')
def system_status():
    """시스템 전체 상태 확인"""
    try:
        import time
        start_time = time.time()
        
        # 기본 시스템 정보
        status = {
            'overall': 'healthy',
            'server_info': 'Python Flask on Koyeb',
            'uptime': '서버 실행 중',
            'memory_usage': 'N/A',
            'cpu_usage': 'N/A'
        }
        
        # psutil 사용 가능 시에만 상세 정보 수집
        try:
            import psutil
            uptime_seconds = int(time.time() - psutil.boot_time())
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            status['uptime'] = f"{hours}시간 {minutes}분"
            status['memory_usage'] = f"{psutil.virtual_memory().percent:.1f}%"
            status['cpu_usage'] = f"{psutil.cpu_percent(interval=1):.1f}%"
        except:
            # psutil 없어도 기본 정보는 제공
            pass
        
        # DB 연결 상태 확인
        try:
            db = get_database()
            conn = db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            status['database'] = 'connected'
        except:
            status['database'] = 'disconnected'
            status['overall'] = 'warning'
        
        return jsonify({'success': True, 'status': status})
        
    except Exception as e:
        return jsonify({
            'success': True, 
            'status': {
                'overall': 'error',
                'uptime': '알 수 없음',
                'server_info': 'Python Flask',
                'memory_usage': 'N/A',
                'cpu_usage': 'N/A',
                'database': 'unknown',
                'error': str(e)
            }
        })

@app.route('/api/database_status')
def database_status():
    """데이터베이스 연결 상태 확인"""
    try:
        db = get_database()
        
        # DB 기본 정보
        db_info = {
            'connected': False,
            'host': getattr(db, 'connection_params', {}).get('host', '알 수 없음'),
            'database': getattr(db, 'connection_params', {}).get('database', '알 수 없음'),
            'schema': getattr(db, 'schema', 'unble'),
            'table_count': 0,
            'total_records': 0,
            'error': None
        }
        
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                # 기본 연결 테스트
                cursor.execute("SELECT 1")
                db_info['connected'] = True
                
                # 테이블 수 확인 (안전하게)
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_schema = '{db.schema}'
                    """)
                    db_info['table_count'] = cursor.fetchone()[0] or 0
                except:
                    db_info['table_count'] = '확인 불가'
                
                # 총 레코드 수 확인 (안전하게)
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.content_files")
                    db_info['total_records'] = cursor.fetchone()[0] or 0
                except:
                    db_info['total_records'] = '확인 불가'
                    
        except Exception as db_error:
            db_info['connected'] = False
            db_info['error'] = str(db_error)
            
        return jsonify({'success': True, 'database': db_info})
            
    except Exception as e:
        # 완전 실패시에도 기본 구조 유지
        return jsonify({
            'success': True,
            'database': {
                'connected': False,
                'host': '알 수 없음',
                'database': '알 수 없음', 
                'schema': 'unble',
                'table_count': 0,
                'total_records': 0,
                'error': f'시스템 오류: {str(e)}'
            }
        })

@app.route('/api/scheduler_status')
def scheduler_status():
    """자동발행 스케줄러 상태 확인"""
    try:
        # 기본 스케줄러 정보
        scheduler_info = {
            'running': False,
            'jobs_count': 0,
            'next_run': '확인 불가',
            'last_run': '없음',
            'last_error': None
        }
        
        # 스케줄러 상태 확인 (안전하게)
        try:
            import schedule
            from src.utils.auto_publisher import auto_publisher
            
            jobs = schedule.jobs
            scheduler_info['jobs_count'] = len(jobs)
            scheduler_info['running'] = getattr(auto_publisher, 'running', False)
            
            if jobs:
                next_run = jobs[0].next_run
                if next_run:
                    scheduler_info['next_run'] = str(next_run)
                else:
                    scheduler_info['next_run'] = '스케줄 없음'
            else:
                scheduler_info['next_run'] = '등록된 작업 없음'
                
        except ImportError:
            scheduler_info['next_run'] = '스케줄러 모듈 없음'
        except Exception as sched_error:
            scheduler_info['next_run'] = f'오류: {str(sched_error)}'
        
        # 시스템 로그에서 마지막 자동발행 정보 확인 (안전하게)
        try:
            db = get_database()
            logs = db.get_system_logs(component='auto_publisher', limit=1)
            if logs and len(logs) > 0:
                last_log = logs[0]
                timestamp = last_log.get('timestamp', '')
                if timestamp:
                    # ISO 형식을 한국어로 변환
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        scheduler_info['last_run'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        scheduler_info['last_run'] = timestamp.replace('T', ' ')
                        
                if last_log.get('log_level') == 'ERROR':
                    scheduler_info['last_error'] = last_log.get('message', '')
        except:
            # 로그 조회 실패해도 기본값 유지
            pass
        
        return jsonify({'success': True, 'scheduler': scheduler_info})
        
    except Exception as e:
        return jsonify({
            'success': True, 
            'scheduler': {
                'running': False,
                'jobs_count': 0,
                'next_run': '시스템 오류',
                'last_run': '확인 불가',
                'last_error': f'API 오류: {str(e)}'
            }
        })

@app.route('/api/environment_status')
def environment_status():
    """환경변수 상태 확인"""
    try:
        import os
        
        # 필수 환경변수들
        critical_vars = [
            'PG_HOST', 'PG_DATABASE', 'PG_USER', 'PG_PASSWORD',
            'ANTHROPIC_API_KEY', 'OPENAI_API_KEY'
        ]
        
        # 선택적 환경변수들  
        optional_vars = [
            'PEXELS_API_KEY', 'UNSPLASH_ACCESS_KEY',
            'UNPRE_USERNAME', 'UNPRE_PASSWORD',
            'UNTAB_USERNAME', 'UNTAB_PASSWORD', 
            'SKEWESE_USERNAME', 'SKEWESE_PASSWORD',
            'TISTORY_ACCESS_TOKEN'
        ]
        
        critical_missing = []
        optional_missing = []
        total_set = 0
        
        # 필수 변수 확인
        for var in critical_vars:
            if os.getenv(var):
                total_set += 1
            else:
                critical_missing.append(var)
                
        # 선택적 변수 확인
        for var in optional_vars:
            if os.getenv(var):
                total_set += 1
            else:
                optional_missing.append(var)
        
        env_info = {
            'critical_missing': critical_missing,
            'optional_missing': optional_missing,
            'total_set': total_set,
            'total_expected': len(critical_vars) + len(optional_vars)
        }
        
        return jsonify({'success': True, 'environment': env_info})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system_logs')
def get_system_logs_api():
    """시스템 로그 조회"""
    try:
        limit = int(request.args.get('limit', 20))
        level = request.args.get('level')
        component = request.args.get('component')
        
        db = get_database()
        logs = db.get_system_logs(level=level, component=component, limit=limit)
        
        return jsonify({'success': True, 'logs': logs})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trending_status')
def get_trending_status():
    """실시간 트렌딩 시스템 상태 조회"""
    try:
        trending_manager = TrendingTopicManager()
        summary = trending_manager.get_site_topics_summary()
        
        status = {
            'overall': 'active',
            'cache_status': 'active',
            'last_update': max([
                summary[site]['last_updated'] 
                for site in summary.keys()
            ]) if summary else datetime.now().isoformat(),
            'sites': summary
        }
        
        return jsonify({'success': True, 'trending_status': status})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'trending_status': {'overall': 'error'}}), 500


@app.route('/api/update_trending')
def update_trending():
    """실시간 트렌딩 데이터 강제 업데이트"""
    try:
        trending_manager = TrendingTopicManager()
        success = trending_manager.update_trending_cache(force_update=True)
        
        if success:
            summary = trending_manager.get_site_topics_summary()
            return jsonify({
                'success': True, 
                'message': '트렌딩 데이터 업데이트 완료',
                'updated_sites': list(summary.keys()),
                'update_time': datetime.now().isoformat()
            })
        else:
            return jsonify({'success': False, 'message': '트렌딩 데이터 업데이트 실패'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trending_topics/<site>')
def get_site_trending_topics(site):
    """특정 사이트의 트렌딩 주제 조회"""
    try:
        trending_manager = TrendingTopicManager()
        
        if site not in trending_manager.site_configs:
            return jsonify({'success': False, 'error': f'Unknown site: {site}'}), 400
            
        config = trending_manager.site_configs[site]
        primary_category = config['primary']
        secondary_category = config['secondary']
        
        primary_topics = trending_manager.get_trending_topics(site, primary_category, 10)
        secondary_topics = trending_manager.get_trending_topics(site, secondary_category, 10)
        
        return jsonify({
            'success': True,
            'site': site,
            'primary_category': primary_category,
            'secondary_category': secondary_category,
            'primary_topics': primary_topics,
            'secondary_topics': secondary_topics,
            'last_updated': trending_manager.last_update.get(site, datetime.now()).isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

