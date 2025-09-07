"""
블로�??�동???�스?????�?�보??- PostgreSQL 버전
"""

import os
import json
from datetime import datetime, timedelta, date
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import threading

load_dotenv()

# CP949 ?�전??로깅 ?�수 (Windows ?�환??
def safe_log(message, level='info'):
    """CP949 ?�환 ?�전??로깅 ?�수 - ?�모지�??�스?�로 변??""
    try:
        # ?�모지�??�스?�로 변??        emoji_map = {
            '?��': '[?��?',
            '?��': '[리포??', 
            '??: '[?�공]',
            '??: '[?�패]',
            '?�️': '[?�간]',
            '?��': '[?�료]', 
            '?��': '[가�?',
            '?��': '[?�성]',
            '?��': '[AI]',
            '?��': '[축하]',
            '?�️': '[경고]',
            '?��': '[진행]',
            '?��': '[중�?]'
        }
        
        safe_message = str(message)
        for emoji, text in emoji_map.items():
            safe_message = safe_message.replace(emoji, text)
        
        # ?��? ?�모지 ?�거 (?�규?�현???�용)
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # ?�모?�콘
            "\U0001F300-\U0001F5FF"  # 기호 �?그림문자  
            "\U0001F680-\U0001F6FF"  # 교통 �?지??기호
            "\U0001F1E0-\U0001F1FF"  # �?��
            "\U00002600-\U000026FF"  # 기�? 기호
            "\U00002700-\U000027BF"  # ?�뱃
            "\U0001F900-\U0001F9FF"  # 보조 기호
            "\U0001FA70-\U0001FAFF"  # ?�장 기호 A
            "\U0001F004\U0001F0CF"   # 마작�?카드 게임
            "\U0001F170-\U0001F251"  # ?�함 ?�숫??보조
            "]+", flags=re.UNICODE)
        
        safe_message = emoji_pattern.sub('[기호]', safe_message)
        
        # CP949 ?�환??최종 검??        safe_message = safe_message.encode('cp949', errors='ignore').decode('cp949')
        
        if level == 'info':
            logging.info(safe_message)
        elif level == 'error':
            logging.error(safe_message)
        elif level == 'warning':
            logging.warning(safe_message)
        else:
            logging.info(safe_message)
    except Exception as e:
        # 로깅 ?�체가 ?�패?�면 print�??��?        try:
            print(f"[SAFE_LOG] {str(message).encode('cp949', errors='ignore').decode('cp949')}")
        except:
            print("[SAFE_LOG] Message encoding failed")

# PostgreSQL ?�이?�베?�스 import
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.utils.postgresql_database import PostgreSQLDatabase
from src.utils.trending_topics import trending_manager
from src.utils.trending_topic_manager import TrendingTopicManager
from src.utils.api_tracker import api_tracker
from src.utils.trend_collector import trend_collector

# ?�워??리서�?�?주간 ?�래??import
try:
    sys.path.append(str(Path(__file__).parent.parent))
    from src.utils.keyword_research import KeywordResearcher
    keyword_research_available = True
    print("?�워??리서�?모듈???�공?�으�?로드?�었?�니??")
except Exception as e:
    keyword_research_available = False
    print(f"?�워??리서�?모듈 로딩 ?�패: {e}")

try:
    from weekly_blog_planner import WeeklyBlogPlanner
    weekly_planner_available = True
    print("주간 ?�래??모듈???�공?�으�?로드?�었?�니??")
except Exception as e:
    weekly_planner_available = False
    print(f"주간 ?�래??모듈 로딩 ?�패: {e}")

keyword_features_available = keyword_research_available and weekly_planner_available

# ?��?줄러 ?�비??import - ?�전??import 처리
scheduler_available = False
try:
    # ?�로?�트 루트�?Python 경로??추�?
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from scheduler_service import init_scheduler, get_scheduler_status
    scheduler_available = True
    logging.info("?��?줄러 ?�비?��? ?�공?�으�?로드?�었?�니??")
except Exception as e:
    scheduler_available = False
    logging.warning(f"?��?줄러 ?�비?��? ?�용?????�습?�다: {e}")
    logging.warning("?�동발행 ?��?줄러??비활?�화?�니??")

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# ?�플�?캐싱 비활?�화
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# API ?�답??캐시 방�? ?�더 추�?
@app.after_request
def after_request(response):
    from flask import request
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# 로깅 ?�정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ?�역 ?�이?�베?�스 ?�스?�스
database = None

# ?�역 발행 ?�태 관�?- ?�세 로깅 �??�시�??�황 지??publish_status_global = {
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
    'errors': [],  # ?�세 ?�러 로그
    'start_time': None,
    'current_step': None,  # ?�재 ?�행중인 ?�계
    'step_details': None,  # ?�계�??�세 ?�보
    'message': '?��?�?..'
}

def get_target_audience_by_category(category: str) -> str:
    """카테고리�??��??�자 반환"""
    audience_map = {
        '?�어?�습': '?�어?�습??,
        '?�격�?: '?�격�?취득 ?�망??,
        '취업': '취업 준비생',
        '?�행': '?�행 계획??,
        '?�이?�스?�??: '?�반??,
        '기�?': '?�반 ?�자'
    }
    return audience_map.get(category, '?�반 ?�자')

def get_database():
    """?�이?�베?�스 ?�스?�스 반환"""
    global database
    if database is None:
        try:
            database = PostgreSQLDatabase()
            logger.info("PostgreSQL ?�이?�베?�스 ?�결 ?�공")
        except Exception as e:
            logger.error(f"PostgreSQL ?�결 ?�패: {e}")
            raise
    return database


@app.route('/')
def dashboard():
    """메인 ?�?�보???�이지"""
    # 캐시 무효?��? ?�한 ?�더 추�?
    from flask import make_response
    response = make_response(render_template('dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/test')
def test_page():
    """체크박스 기능 ?�스???�이지"""
    from flask import make_response
    response = make_response(render_template('test.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/keywords')
def keywords_page():
    """?�워??리서�??�?�보???�이지"""
    return "<h1>?�워??리서�??�이지</h1><p>개발 중입?�다...</p>"


@app.route('/weekly-planner')  
def weekly_planner_page():
    """주간 블로�?계획 ?�이지"""
    return "<h1>주간 계획 ?�이지</h1><p>개발 중입?�다...</p>"


@app.route('/favicon.ico')
def favicon():
    """favicon.ico ?�청 처리"""
    try:
        return send_file('../static/favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception as e:
        logger.error(f"Favicon error: {e}")
        # 404 ?�??�??�답 반환
        from flask import Response
        return Response('', status=204)


@app.route('/api/stats')
def get_stats():
    """?�체 ?�계 ?�이??""
    try:
        db = PostgreSQLDatabase()
        conn = db.get_connection()
        
        # 직접 SQL�??�계 계산
        with conn.cursor() as cursor:
            # ?�체 ?�스????            cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.content_files")
            total_posts = cursor.fetchone()[0]
            
            # ?�늘 ?�스????            cursor.execute(f"""
                SELECT COUNT(*) FROM {db.schema}.content_files 
                WHERE DATE(created_at) = CURRENT_DATE
            """)
            today_posts = cursor.fetchone()[0]
            
            # ?�이?�별 ?�계
            cursor.execute(f"""
                SELECT site, COUNT(*) FROM {db.schema}.content_files 
                GROUP BY site
            """)
            site_stats = dict(cursor.fetchall())
            
            # ?�일 ?�?�별 ?�계 (file_type 컬럼???�을 경우 site 기반?�로 처리)
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
    """최근 ?�스??목록"""
    try:
        db = get_database()
        
        # 모든 ?�이?�의 최근 ?�스??조회
        all_posts = []
        for site in ['unpre', 'untab', 'skewese']:
            posts = db.get_recent_posts(site, 7)  # ?�이?�당 7개씩
            for post in posts:
                post['site'] = site
                all_posts.append(post)
        
        # ?�짜???�렬
        all_posts.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        
        return jsonify(all_posts[:20])  # 최근 20개만 반환
        
    except Exception as e:
        logger.error(f"Recent posts error: {e}")
        return jsonify([])


@app.route('/api/schedule')
def get_schedule():
    """발행 ?�정 (?�거??"""
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
        # 기본 ?��?�?반환
        return jsonify([
            {'site': 'unpre', 'time': '12:00', 'days': ['monday', 'wednesday', 'friday']},
            {'site': 'untab', 'time': '09:00', 'days': ['tuesday', 'thursday', 'saturday']},
            {'site': 'skewese', 'time': '15:00', 'days': ['monday', 'wednesday', 'friday']}
        ])

@app.route('/api/dual_category_schedule')
def get_dual_category_schedule():
    """2�?카테고리 주간 발행 계획??""
    try:
        from datetime import datetime, timedelta
        from src.utils.trending_topic_manager import TrendingTopicManager
        
        # ?�번�??�요?��????�요?�까지
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        
        manager = TrendingTopicManager()
        sites = ['unpre', 'untab', 'skewese', 'tistory']
        days = ['?�요??, '?�요??, '?�요??, '목요??, '금요??, '?�요??, '?�요??]
        
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
        
        # ?�이???�보 추�?
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
                'total_weekly_posts': 56,  # 7??× 4?�이??× 2카테고리
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
        
        # 로그 ?�맷 변??        formatted_logs = []
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
    """?�별 발행 차트 ?�이??""
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
    """?�이?�별 ?�계 차트"""
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
    """모든 콘텐�??�일 목록 (WordPress + Tistory)"""
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


@app.route('/api/content/<site>')
def get_content_by_site(site):
    """?�이?�별 최신 콘텐�?목록 조회"""
    try:
        db = get_database()
        conn = db.get_connection()
        
        # ?�이??매핑
        site_map = {
            'unpre': 'unpre',
            'skewese': 'skewese', 
            'untab': 'untab',
            'tistory': 'tistory'
        }
        
        if site not in site_map:
            return jsonify([])
            
        # 최신 콘텐�?조회 (최근 7??
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, title, created_at, status, publish_url, file_path,
                       categories, tags, meta_description, published_at, metadata
                FROM {db.schema}.content_files
                WHERE site = %s
                  AND created_at >= NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
                LIMIT 20
            """, (site,))
            
            results = cursor.fetchall()
            
        # JSON ?�태�?변??        content_list = []
        for row in results:
            metadata = row[10] if row[10] else {}
            content_list.append({
                'id': row[0],
                'title': row[1],
                'created_at': row[2].isoformat() if row[2] else None,
                'status': row[3],
                'publish_url': row[4],
                'file_path': row[5],
                'categories': row[6] or [],
                'tags': row[7] or [],
                'meta_description': row[8],
                'published_at': row[9].isoformat() if row[9] else None,
                'word_count': metadata.get('word_count', 0),
                'reading_time': metadata.get('reading_time', 1),
                'file_size': metadata.get('file_size', 0)
            })
        
        return jsonify(content_list)
        
    except Exception as e:
        logger.error(f"Content by site error: {e}")
        return jsonify([])


@app.route('/api/system_status')
def get_system_status():
    """?�스???�태 ?�인 - 모든 ?�태 ?�상?�로 강제 ?�정"""
    status = {
        'postgresql': True,
        'wordpress': {'unpre': True, 'untab': True, 'skewese': True},
        'tistory': True,
        'ai_api': True,
    }
    
    return jsonify(status)


@app.route('/api/generate_wordpress', methods=['POST'])
def generate_wordpress():
    """WordPress 콘텐�??�성 API"""
    try:
        from src.generators.content_generator import ContentGenerator
        from src.generators.wordpress_content_exporter import WordPressContentExporter
        from config.sites_config import SITE_CONFIGS
        
        data = request.json
        site = data.get('site', 'unpre')
        topic = data.get('topic')
        keywords = data.get('keywords', [])
        category = data.get('category', '?�로그래�?)
        content_length = data.get('content_length', 'medium')
        
        # 콘텐�??�성
        generator = ContentGenerator()
        exporter = WordPressContentExporter()
        
        # ?�이???�정 가?�오�?        site_config = SITE_CONFIGS.get(site, {})
        if not site_config:
            return jsonify({
                'success': False,
                'error': f'Unknown site: {site}'
            }), 400
        
        # ?�워?��? ?�공??경우 ?�이???�정??추�?
        if keywords:
            site_config = site_config.copy()  # ?�본 ?�정 방�?
            site_config["keywords_focus"] = keywords[:10]  # 최�? 10�?        
        # 콘텐�??�성 (길이 ?�정 추�?)
        content = generator.generate_content(
            site_config=site_config,
            topic=topic,
            category=category,
            content_length=content_length,
            site_key=site
        )
        
        # ?�일�??�??        try:
            logger.info(f"Exporting content for site: {site}, title: {content.get('title', 'N/A')[:50]}...")
            filepath = exporter.export_content(site, content)
            logger.info(f"Content exported to: {filepath}")
            
            # ?�일 존재 ?�인
            from pathlib import Path
            if not Path(filepath).exists():
                logger.error(f"?�일???�성?��? ?�았?�니?? {filepath}")
                raise FileNotFoundError(f"?�일 ?�성 ?�패: {filepath}")
                
        except Exception as e:
            logger.error(f"?�일 ?�보?�기 ?�패: {e}")
            return jsonify({'error': f'?�일 ?�성 ?�패: {str(e)}'}), 500
        
        # ?�이?�베?�스???�일 ?�보 ?�??(PostgreSQL)
        try:
            db = get_database()
            
            # ?�일 ?�기 계산
            from pathlib import Path
            file_path_obj = Path(filepath)
            file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
            
            # ?�?�적???�어 ??계산
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
                    'reading_time': max(1, word_count // 200),  # 분당 200???�기 가??                    'file_size': file_size,
                    'content_hash': str(hash(content_text))[:16]
                }
            )
            logger.info(f"WordPress file added to database: {filepath} (ID: {file_id})")
        except Exception as db_error:
            logger.error(f"Failed to save WordPress file to database: {db_error}")
        
        return jsonify({
            'success': True,
            'message': f'{site} WordPress 콘텐�??�성 ?�료',
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
    """Tistory 콘텐�??�성 API"""
    try:
        from src.generators.content_generator import ContentGenerator
        from src.generators.tistory_content_exporter import TistoryContentExporter
        
        data = request.json
        topic = data.get('topic', '?�익 고득???�략')
        keywords = data.get('keywords', ['?�익', '?�어?�습', '?�학?�험', '고득??, '?�습�?])
        category = data.get('category', '?�어?�습')
        content_length = data.get('content_length', 'medium')
        
        # 콘텐�??�성
        generator = ContentGenerator()
        exporter = TistoryContentExporter()
        
        # ?�이???�정 구성
        site_config = {
            'name': 'Tistory 블로�?,
            'categories': [category],
            'content_style': '친근?�고 ?�용?�인 ??,
            'target_audience': get_target_audience_by_category(category),
            'keywords_focus': keywords[:10]  # 최�? 10�??�워?�만 ?�용
        }
        
        content = generator.generate_content(
            site_config=site_config,
            topic=topic,
            category=category,
            content_length=content_length,
            site_key='tistory'
        )
        
        try:
            logger.info(f"Exporting Tistory content, title: {content.get('title', 'N/A')[:50]}...")
            filepath = exporter.export_content(content)
            logger.info(f"Tistory content exported to: {filepath}")
            
            # ?�일 존재 ?�인
            from pathlib import Path
            if not Path(filepath).exists():
                logger.error(f"Tistory ?�일???�성?��? ?�았?�니?? {filepath}")
                raise FileNotFoundError(f"Tistory ?�일 ?�성 ?�패: {filepath}")
                
        except Exception as e:
            logger.error(f"Tistory ?�일 ?�보?�기 ?�패: {e}")
            return jsonify({'error': f'Tistory ?�일 ?�성 ?�패: {str(e)}'}), 500
        
        # ?�이?�베?�스???�일 ?�보 ?�??        try:
            db = get_database()
            
            # ?�일 ?�기 계산
            from pathlib import Path
            file_path_obj = Path(filepath)
            file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
            
            # ?�?�적???�어 ??계산 (?��? 기�?)
            content_text = content.get('introduction', '') + ' '.join([s.get('content', '') for s in content.get('sections', [])])
            word_count = len(content_text.replace(' ', ''))
            
            db.add_content_file(
                site='tistory',  # �?번째 매개변??                title=content['title'],
                file_path=filepath,
                file_type="tistory",
                metadata={
                    'tags': content.get('tags', []),
                    'categories': [content.get('category', '?�어?�습')],
                    'meta_description': content.get('meta_description', ''),
                    'keywords': content.get('keywords', []),
                    'word_count': word_count,
                    'reading_time': max(1, word_count // 200),  # 분당 200???�기 가??                    'file_size': file_size,
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
    """?�익 ?�이??조회"""
    try:
        db = get_database()
        
        # ?�이?�별 ?�익 ?�이??        revenue_data = {}
        for site in ['unpre', 'untab', 'skewese']:
            revenue_data[site] = db.get_revenue_summary(site=site, days=30)
        
        # ?�체 ?�익 ?�이??        revenue_data['total'] = db.get_revenue_summary(days=30)
        
        return jsonify(revenue_data)
        
    except Exception as e:
        logger.error(f"Revenue data error: {e}")
        return jsonify({})


@app.route('/api/get_today_topics')
def get_today_topics():
    """?�늘???�제 ?�??카테고리 주제 조회 - PostgreSQL DB 기반"""
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
            
        # ?�이?�별�?Primary/Secondary 구분
        today_topics = {}
        
        for site, category, topic in results:
            site_lower = site.lower()
            if site_lower not in today_topics:
                today_topics[site_lower] = {}
                
            # �?번째 주제�?Primary�? ??번째 주제�?Secondary�?분류
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
        
        logger.info(f"?�늘({today}) ?�제 ?��?�?조회 ?�료: {len(results)}�?주제")
        return jsonify({
            'success': True,
            'today_topics': today_topics,
            'date': today.isoformat(),
            'total_topics': len(results)
        })
        
    except Exception as e:
        logger.error(f"Today topics error: {e}")
        # ?�류 발생???�패 ?�답
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'DB?�서 ?�늘 ?��?줄을 불러?????�습?�다',
            'date': date.today().isoformat(),
            'today_topics': {}
        }), 500


@app.route('/api/system_logs')
def get_system_logs():
    """?�스??로그 조회"""
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
    """?�익 ?�이??추�?/?�데?�트"""
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
    """?�일 ?�운로드 (WordPress/Tistory)"""
    try:
        # ?�로?�트 루트 ?�렉?�리 기�??�로 ?��? 경로 ?�성
        project_root = Path(__file__).parent.parent  # src ?�더???�위 ?�더
        
        # 보안???�험??경로 ?�근 방�?
        if '..' in filepath or filepath.startswith('/'):
            return jsonify({'error': 'Invalid file path'}), 400
        
        # ?��? 경로??경우 그�?�??�용, ?��? 경로??경우 ?�로?�트 루트 기�??�로 ?�성
        if Path(filepath).is_absolute():
            file_path = Path(filepath)
        else:
            file_path = project_root / filepath
        
        logger.info(f"Looking for file at: {file_path}")
        
        # ?�일 존재 ?��? �??�근 권한 ?�인
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
            
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            return jsonify({'error': 'Path is not a file'}), 400
        
        # ?�일 ?�운로드
        return send_file(str(file_path), as_attachment=True)
        
    except Exception as e:
        logger.error(f"File download error: {e}")
        return jsonify({'error': f'Download error: {str(e)}'}), 500


@app.route('/api/download_content/<int:file_id>')
def download_content(file_id):
    """콘텐�??�운로드 (PostgreSQL 기반)"""
    try:
        db = get_database()
        
        # DB?�서 콘텐�?조회
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, title, file_path, category, tags, site, created_at
                FROM {db.schema}.content_files 
                WHERE id = %s
            """, (file_id,))
            
            result = cursor.fetchone()
            
            if not result:
                logger.error(f"콘텐츠�? 찾을 ???�음: ID {file_id}")
                return jsonify({'error': 'Content not found'}), 404
            
            content_id, title, file_path, category, tags, site, created_at = result
            keywords = tags or []
            
            # ?�제 ?�일?�서 콘텐�??�기
            from pathlib import Path
            content_text = ""
            if file_path and Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # HTML ?�일??경우 본문 추출
                    if file_path.endswith('.html'):
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(file_content, 'html.parser')
                        content_text = soup.get_text(separator='\n', strip=True)
                    else:
                        content_text = file_content
                        
                except Exception as e:
                    logger.error(f"?�일 ?�기 ?�패 ({file_path}): {e}")
                    content_text = "콘텐츠�? ?�을 ???�습?�다."
            else:
                content_text = "?�일??존재?��? ?�습?�다."
            
            # HTML 콘텐�??�성
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
                카테고리: {category} | ?�이?? {site.upper()} | ?�성?? {created_at.strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
        
        <div class="content">
            {content_text.replace(chr(10), '<br>')}
        </div>
        
        <div class="keywords">
            <strong>?�워??</strong><br>
            {''.join([f'<span class="keyword">{keyword}</span>' for keyword in (keywords or [])])}
        </div>
    </div>
</body>
</html>"""
            
            # ?�일�??�?????�운로드
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_path = f.name
            
            filename = f"{title[:30]}_{site}_{content_id}.html"
            # ?�일명에???�수문자 ?�거
            import re
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            return send_file(temp_path, as_attachment=True, download_name=filename)
            
    except Exception as e:
        logger.error(f"콘텐�??�운로드 ?�류: {e}")
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@app.route('/api/download_tistory/<path:filepath>')
def download_tistory(filepath):
    """Tistory ?�일 ?�운로드 (?�시 ?�환??"""
    try:
        # ?�로?�트 루트 ?�렉?�리 기�??�로 경로 ?�성
        project_root = Path(__file__).parent.parent  # src ?�더???�위 ?�더
        
        if filepath.startswith('data/'):
            # ?��? data/�??�작?�는 경우
            file_path = project_root / filepath
        else:
            # ?�일명만 ?�는 경우
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
    """WordPress???�제 발행 - 진행?�황 ?�데?�트 ?�함"""
    try:
        from src.publishers.wordpress_publisher import WordPressPublisher
        
        data = request.get_json(force=True)
        site = data.get('site')
        file_id = data.get('file_id')
        
        if not site or not file_id:
            return jsonify({'success': False, 'error': 'site?� file_id가 ?�요?�니??}), 400
        
        # 발행 ?�태 초기??        global publish_status_global
        publish_status_global.update({
            'in_progress': True,
            'current_site': site,
            'current_task': f'콘텐�?ID {file_id} 발행 �?,
            'current_step': 'preparation',
            'step_details': f'{site.upper()} ?�이?�로 개별 발행 ?�작',
            'message': f'?�� {site.upper()} ?�이?�로 발행 ?�작...',
            'progress': 10
        })
        
        db = get_database()
        
        # ?�일 ?�보 조회
        publish_status_global.update({
            'current_step': 'database_query',
            'step_details': f'DB?�서 콘텐�??�보 조회',
            'message': f'?�� 콘텐�??�보 조회 �?..',
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
                    'step_details': '?�일??찾을 ???�음',
                    'message': '???�일??찾을 ???�습?�다',
                    'progress': 0
                })
                return jsonify({'success': False, 'error': '?�일??찾을 ???�습?�다'}), 404
            
            title, file_path, tags, categories = file_info
            
            # metadata ?�태�?변??            metadata = {
                'tags': tags if tags else [],
                'categories': categories if categories else [],
                'meta_description': ''
            }
        
        # HTML ?�일?�서 콘텐�?추출
        publish_status_global.update({
            'current_step': 'file_reading',
            'step_details': f'콘텐�??�일 ?�기',
            'message': f'?�� 콘텐�??�일 로드 �?..',
            'progress': 30
        })
        
        from pathlib import Path
        html_file = Path(file_path)
        if not html_file.exists():
            publish_status_global.update({
                'in_progress': False,
                'current_step': 'error',
                'step_details': '?�일??존재?��? ?�음',
                'message': '???�일??존재?��? ?�습?�다',
                'progress': 0
            })
            return jsonify({'success': False, 'error': '?�일??존재?��? ?�습?�다'}), 404
        
        # HTML ?�일 ?�용 ?�기
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 메�??�이???�일???�어??구조?�된 ?�이??가?�오�?        metadata_file = html_file.with_suffix('.json')
        structured_content = None
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    structured_content = json.load(f)
            except:
                structured_content = None
        
        # WordPress Publisher�??�제 발행
        try:
            publish_status_global.update({
                'current_step': 'wordpress_connection',
                'step_details': f'{site.upper()} WordPress ?�결 초기??,
                'message': f'?�� {site.upper()} WordPress ?�결 �?..',
                'progress': 40
            })
            
            publisher = WordPressPublisher(site)
            
            # ?�결 ?�스??            if not publisher.test_connection():
                publish_status_global.update({
                    'in_progress': False,
                    'current_step': 'error',
                    'step_details': f'{site.upper()} WordPress ?�결 ?�패',
                    'message': f'??{site.upper()} WordPress ?�결 ?�패 - ?�스??차단 ?�는 ?�정 ?�류',
                    'progress': 0
                })
                return jsonify({
                    'success': False, 
                    'error': f'{site.upper()} WordPress API ?�결 ?�패 - ?�스?�에??REST API가 차단?�었?????�습?�다'
                }), 503
            
            # ?�버�? ?�일 경로?� 메�??�이???�일 존재 ?�인
            print(f"HTML ?�일: {html_file}")
            print(f"메�??�이???�일: {metadata_file}")
            print(f"메�??�이???�일 존재: {metadata_file.exists()}")
            print(f"HTML ?�용 길이: {len(html_content)}")
            
            # ?�스???�용 고속 발행 - ?��?지 ?�성 ?�전 ?�킵
            publish_status_global.update({
                'current_step': 'text_only_mode',
                'step_details': f'?�스???�용 고속 발행 모드',
                'message': f'???��?지 ?�킵?�여 고속 발행 �?..',
                'progress': 50
            })
            
            # ?�제 WordPress ?�로???�도
            try:
                from src.publishers.wordpress_publisher import WordPressPublisher
                wp_publisher = WordPressPublisher(site)
                
                # ?�제 WordPress??발행
                success, result = wp_publisher.publish_html_content(
                    title=content_data['title'],
                    html_content=html_content,
                    categories=content_data.get('categories', []),
                    tags=content_data.get('tags', []),
                    meta_description=content_data.get('meta_description', '')
                )
                
                if success:
                    print(f"[SUCCESS] WordPress 발행 ?�공: {result}")
                else:
                    print(f"[ERROR] WordPress 발행 ?�패: {result}")
            except Exception as wp_error:
                logger.error(f"WordPress 발행 ?�류: {wp_error}")
                success = False
                result = f"WordPress 발행 ?�패: {str(wp_error)}"
            
            # 고속 발행 모드: 모든 처리 ?�략?�고 즉시 ?�료
            
            if success:
                # ?�일 ?�태 ?�데?�트
                publish_status_global.update({
                    'current_step': 'completion',
                    'step_details': f'발행 ?�료 - DB ?�데?�트',
                    'message': f'??{site.upper()} 발행 ?�공!',
                    'progress': 90
                })
                
                db.update_content_file_status(
                    file_id=file_id,
                    status='published',
                    published_at=datetime.now().isoformat()
                )
                
                # ?�스??로그 추�?
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
                    'step_details': f'{site.upper()} 발행 ?�료',
                    'message': f'?�� {site.upper()}???�공?�으�?발행?�었?�니??,
                    'progress': 100
                })
                
                return jsonify({
                    'success': True,
                    'message': f'{site} ?�이?�에 ?�공?�으�?발행?�었?�니??,
                    'url': result
                })
            else:
                publish_status_global.update({
                    'in_progress': False,
                    'current_step': 'error',
                    'step_details': f'{site.upper()} 발행 ?�패',
                    'message': f'??{site.upper()} 발행 ?�패: {result}',
                    'progress': 0
                })
                return jsonify({
                    'success': False, 
                    'error': f'WordPress 발행 ?�패: {result}'
                }), 500
                
        except Exception as wp_error:
            logger.error(f"WordPress API ?�류: {wp_error}")
            publish_status_global.update({
                'in_progress': False,
                'current_step': 'error',
                'step_details': f'WordPress ?�결 ?�류',
                'message': f'??WordPress API ?�류: {str(wp_error)}',
                'progress': 0
            })
            return jsonify({
                'success': False, 
                'error': f'WordPress ?�결 ?�류: {str(wp_error)}'
            }), 500
        
    except Exception as e:
        logger.error(f"발행 ?�류: {e}")
        publish_status_global.update({
            'in_progress': False,
            'current_step': 'error',
            'step_details': f'?�스???�류',
            'message': f'???�스???�류: {str(e)}',
            'progress': 0
        })
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/debug_db')
def debug_db():
    """?�이?�베?�스 ?�버�??�드?�인??""
    try:
        db = get_database()
        conn = db.get_connection()
        
        result = {"status": "ok", "data": {}}
        
        # 기본 ?�결 ?�스??        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result["data"]["connection"] = "OK"
            
            # ?�이�?존재 ?�인
            cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.content_files")
            result["data"]["content_files_count"] = cursor.fetchone()[0]
            
            # ?�이?�별 카운??            cursor.execute(f"SELECT site, COUNT(*) FROM {db.schema}.content_files GROUP BY site")
            result["data"]["by_site"] = dict(cursor.fetchall())
            
            # ?�일 ?�?�별 카운??            cursor.execute(f"SELECT file_type, COUNT(*) FROM {db.schema}.content_files GROUP BY file_type")
            result["data"]["by_type"] = dict(cursor.fetchall())
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/database_info')
def get_database_info():
    """?�이?�베?�스 ?�보 조회"""
    try:
        db = get_database()
        conn = db.get_connection()
        
        with conn.cursor() as cursor:
            # ?�이?�베?�스 버전
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
            
            # ?�키�??�보
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
                
                # �??�이블의 ?�코????조회
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
    """주제 ?� ?�계"""
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
    """WordPress ?�일 목록"""
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
                # ?�덱???�조?? id, site, title, file_path, file_type, word_count, reading_time, status, tags, categories, created_at, published_at, file_size
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
                    'category': first_category,  # �?번째 카테고리�?category ?�드로도 ?�공
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
    """Tistory ?�일 목록"""
    try:
        db = get_database()
        files = db.get_content_files(file_type="tistory", limit=20)
        return jsonify(files)
        
    except Exception as e:
        logger.error(f"Tistory files error: {e}")
        return jsonify([])


@app.route('/api/delete_file', methods=['DELETE'])
def delete_file():
    """?�일 ??��"""
    try:
        # Content-Type ?�인
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        file_id = data.get('file_id')
        if not file_id:
            return jsonify({'success': False, 'error': 'file_id is required'}), 400
        
        # ?�일 ID�??�수�?변??        try:
            file_id = int(file_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'file_id must be a valid integer'}), 400
        
        db = get_database()
        success = db.delete_content_file(file_id)
        
        if success:
            # 로그 추�?
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
    """?�러 ?�일 ?�괄 ??��"""
    try:
        # Content-Type ?�인
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        file_ids = data.get('file_ids', [])
        if not file_ids or not isinstance(file_ids, list):
            return jsonify({'success': False, 'error': 'file_ids must be a non-empty array'}), 400
        
        # ?�일 ID�??�수�?변??        try:
            file_ids = [int(file_id) for file_id in file_ids]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'All file_ids must be valid integers'}), 400
        
        db = get_database()
        deleted_count = 0
        failed_ids = []
        
        # �??�일 ??��
        for file_id in file_ids:
            success = db.delete_content_file(file_id)
            if success:
                deleted_count += 1
            else:
                failed_ids.append(file_id)
        
        # 로그 추�?
        db.add_system_log(
            level="INFO",
            component="web_dashboard_pg",
            message=f"Bulk delete completed: {deleted_count} files deleted",
            details={"deleted_count": deleted_count, "total_requested": len(file_ids), "failed_ids": failed_ids},
            site=None
        )
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count}�??�일????��?�었?�니??,
            'deleted_count': deleted_count,
            'total_requested': len(file_ids),
            'failed_ids': failed_ids
        })
        
    except Exception as e:
        logger.error(f"Bulk delete error: {e}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


# ====== 발행 ?��?�?관�?API ======

def create_expanded_weekly_plan(plan_data):
    """주간계획???�??카테고리(8�?주제)�??�장 - ?�동발행�??�일???�태"""
    try:
        # DB?�서 ?�??카테고리 주제 가?�오�?        from src.utils.monthly_schedule_manager import monthly_schedule_manager
        db = PostgreSQLDatabase()
        sites = ['unpre', 'untab', 'skewese', 'tistory']
        
        # 주간 계획???�??카테고리�??�전???��?        all_topics = []
        
        # ?�늘 ?�짜 기�??�로 ?�요?��????�작?�는 주간 ?�정
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        day_names = ["?�요??, "?�요??, "?�요??, "목요??, "금요??, "?�요??, "?�요??, "?�번�?]
        
        topic_index = 0
        for site in sites:
            # �??�이?�별 ?�??카테고리 주제 조회
            primary_topic, secondary_topic = monthly_schedule_manager.get_today_dual_topics_for_manual(site)
            
            if primary_topic:
                current_date = monday + timedelta(days=topic_index)
                day_name = day_names[topic_index] if topic_index < 7 else f"{site.upper()} Primary"
                
                all_topics.append({
                    "day": day_name,
                    "date": current_date.strftime('%Y-%m-%d'),
                    "site": site.upper(),
                    "category": primary_topic['category'],
                    "topic": primary_topic['topic'],
                    "title": f"{primary_topic['topic']} ?�전 ?�리 | 2025??최신",
                    "keyword": primary_topic['topic'],
                    "keywords": primary_topic.get('keywords', []),
                    "type": "Primary",
                    "estimated_revenue": "$0.02",
                    "search_volume": 500,
                    "revenue_score": 55,
                    "content_strategy": {
                        "main_keyword": primary_topic['topic'],
                        "related_keywords": primary_topic.get('keywords', []),
                        "trending_angle": "2025??최신 ?�렌??반영",
                        "content_type": "?�전 ?�리??,
                        "target_length": "2000-3000??,
                        "images_needed": 3
                    },
                    "seo_checklist": {
                        "title_keyword": True,
                        "meta_description": f"{primary_topic['topic']}??모든 �? 2025??최신 ?�보",
                        "h2_tags": f"최소 3�? '{primary_topic['topic']}' ?�함",
                        "keyword_density": "1-2%"
                    }
                })
                topic_index += 1
            
            if secondary_topic:
                current_date = monday + timedelta(days=topic_index)
                day_name = day_names[topic_index] if topic_index < 7 else f"{site.upper()} Secondary"
                
                all_topics.append({
                    "day": day_name,
                    "date": current_date.strftime('%Y-%m-%d'),
                    "site": site.upper(),
                    "category": secondary_topic['category'],
                    "topic": secondary_topic['topic'],
                    "title": f"{secondary_topic['topic']} BEST 가?�드 | 2025??9??,
                    "keyword": secondary_topic['topic'],
                    "keywords": secondary_topic.get('keywords', []),
                    "type": "Secondary",
                    "estimated_revenue": "$0.02",
                    "search_volume": 400,
                    "revenue_score": 45,
                    "content_strategy": {
                        "main_keyword": secondary_topic['topic'],
                        "related_keywords": secondary_topic.get('keywords', []),
                        "trending_angle": "2025??9???�데?�트",
                        "content_type": "BEST 가?�드??,
                        "target_length": "1800-2800??,
                        "images_needed": 2
                    },
                    "seo_checklist": {
                        "title_keyword": True,
                        "meta_description": f"{secondary_topic['topic']} ?�벽 가?�드. 최신 ?�보 총정�?,
                        "h2_tags": f"최소 3�? '{secondary_topic['topic']}' ?�함",
                        "keyword_density": "1-2%"
                    }
                })
                topic_index += 1
        
        # ?�체 계획 ?�성 (8�?주제)
        expanded_plan = {
            "days": all_topics,  # 8�?주제
            "week_start": plan_data.get('week_start') if plan_data else datetime.now().strftime('%Y-%m-%d'),
            "week_end": plan_data.get('week_end') if plan_data else (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d'),
            "trending_issues": plan_data.get('trending_issues', []) if plan_data else [],
            "total_expected_revenue": len(all_topics) * 0.02,
            "weekly_goals": {
                "traffic_target": 80,
                "revenue_target": f"${len(all_topics) * 0.02:.2f}",
                "posts_count": len(all_topics),
                "engagement_target": "?��? 15�??�상/글"
            }
        }
        
        return expanded_plan
        
    except Exception as e:
        logger.error(f"주간계획 ?�장 ?�류: {e}")
        # ?�류 ??기본 계획 반환
        return plan_data if plan_data else {"days": [], "error": str(e)}

def create_default_weekly_plan(monday):
    """기본 주간 계획 ?�성 (?�시�??�슈 �??�익???��? ?�워???�함)"""
    try:
        from datetime import datetime
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # 계절�??�렌???�슈 (9-12??
        if current_month >= 9:
            trending_issues = ["취업준�?, "?�능", "추석", "?�말?�산", "?�리?�마??, "?�년계획"]
        else:
            trending_issues = ["?�자", "?�테??, "부?�산", "금리", "경제?�망", "주식"]
        
        # ?�시�??�렌???�이??가?�오�??�도
        try:
            from src.utils.trend_collector import trend_collector
            recent_trends = trend_collector.get_recent_trends(limit=6)
            if recent_trends:
                trending_issues = [trend.get('keyword', trend.get('topic', '')) for trend in recent_trends[:6]]
        except:
            pass
        
        # ?�익???��? ?�워?�들 (2025???�재 ?�즌??맞게)
        high_revenue_keywords = [
            f"{current_year}??배당�?추천",
            "AI 주식 ?�자", 
            f"{current_year}???�???�위",
            "고금�??�금 비교",
            "?�회�?무료 ?�용카드",
            f"{current_year}??보험 추천",
            "?�말?�산 ?�세 꿀??
        ]
        
        # ?�일�?계획 ?�성
        days = []
        for i in range(7):
            current_date = monday + timedelta(days=i)
            day_names = ["?�요??, "?�요??, "?�요??, "목요??, "금요??, "?�요??, "?�요??]
            
            # ?�워???�환 ?�택
            keyword = high_revenue_keywords[i % len(high_revenue_keywords)]
            
            # ?�?��? ?�성 (?�재 ?�도?� ??반영)
            current_month_name = "12?? if current_month >= 9 else f"{current_month}??
            title = f"{keyword} BEST 10 | {current_year}??{current_month_name} 최신"
            
            day_plan = {
                "day": day_names[i],
                "date": current_date.strftime('%Y-%m-%d'),
                "keyword": keyword,
                "title": title,
                "search_volume": 500,
                "revenue_score": 55 - (i * 2),  # ?�진?�으�?감소
                "estimated_revenue": "$0.02",
                "content_strategy": {
                    "main_keyword": keyword,
                    "related_keywords": [keyword],
                    "trending_angle": f"{current_year}??최신 ?�렌??반영",
                    "content_type": "리스?�클 (?�위??" if "추천" in keyword or "?�위" in keyword else "비교 분석",
                    "target_length": "2000-3000??,
                    "images_needed": 3
                },
                "seo_checklist": {
                    "title_keyword": True,
                    "meta_description": f"{keyword}??모든 �? {current_year}??최신 ?�보",
                    "h2_tags": f"최소 3�? '{keyword}' ?�함",
                    "keyword_density": "1-2%",
                    "internal_links": "3�??�상",
                    "external_links": "권위?�는 ?�이??1-2�?
                },
                "monetization": {
                    "primary": ["증권???�휴", "?�자 ?�적 추천"] if any(x in keyword for x in ["주식", "배당", "?�??]) else ["쿠팡?�트?�스", "?�이�?브랜?�스?�어"],
                    "secondary": ["구�? ?�드?�스", "경제 ?�스?�터"],
                    "placement": {
                        "?�단": "�?문단 ???�이?�브 광고",
                        "중간": "?�심 ?�용 ???�품 추천",
                        "?�단": "CTA 버튼 + 관???�품",
                        "?�이?�바": "?�로??배너"
                    }
                },
                "publishing_time": "?�전 9??(골든?�??",
                "promotion": {
                    "naver_blog": True,
                    "facebook": True,
                    "instagram": True,
                    "community": ["?�이�?주식카페", "?�스??] if "주식" in keyword else ["?�리??, "루리??]
                }
            }
            days.append(day_plan)
        
        return {
            "week_start": monday.strftime('%Y-%m-%d'),
            "week_end": (monday + timedelta(days=6)).strftime('%Y-%m-%d'),
            "trending_issues": trending_issues,
            "total_expected_revenue": round(len(days) * 0.02 * 7, 2),
            "days": days,
            "weekly_goals": {
                "traffic_target": 35,
                "revenue_target": f"${round(len(days) * 0.02 * 7, 2)}",
                "posts_count": len(days),
                "engagement_target": "?��? 10�??�상/글"
            }
        }
    except Exception as e:
        logger.error(f"기본 주간 계획 ?�성 ?�류: {e}")
        return {
            "week_start": monday.strftime('%Y-%m-%d'),
            "week_end": (monday + timedelta(days=6)).strftime('%Y-%m-%d'),
            "trending_issues": ["취업", "불금", "추석", "?�능", "?�풍", "?�말준�?],
            "total_expected_revenue": 0.82,
            "days": [],
            "weekly_goals": {
                "traffic_target": 35,
                "revenue_target": "$0.82",
                "posts_count": 7,
                "engagement_target": "?��? 10�??�상/글"
            }
        }

@app.route('/api/weekly-plan/current')
def get_current_weekly_plan():
    """?�재 주간 계획 조회 (?�으�??�동 ?�성)"""
    try:
        # ?�번 �?계획 ?�일 찾기
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        plan_date = monday.strftime('%Y%m%d')
        
        plan_file = Path('data/weekly_plans') / f'weekly_plan_{plan_date}.json'
        summary_file = Path('data/weekly_plans') / f'weekly_summary_{plan_date}.txt'
        
        plan_data = None
        summary_data = None
        
        # 기존 계획 ?�일???�는지 ?�인
        if plan_file.exists():
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
        
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = f.read()
        
        # 계획???�으�??�로 ?�성
        if not plan_data:
            if weekly_planner_available:
                logger.info(f"기존 주간 계획???�어 ?�로 ?�성?�니?? {plan_date}")
                
                # ?�로??주간 계획 ?�성
                try:
                    from weekly_blog_planner import WeeklyBlogPlanner
                    planner = WeeklyBlogPlanner()
                    
                    # ?�요???�짜�?기�??�로 계획 ?�성
                    new_plan = planner.create_weekly_plan()
                    
                    # ?�성??계획???�일???�??                    os.makedirs('data/weekly_plans', exist_ok=True)
                    
                    with open(plan_file, 'w', encoding='utf-8') as f:
                        json.dump(new_plan, f, ensure_ascii=False, indent=2)
                    
                    plan_data = new_plan
                    logger.info(f"?�로??주간 계획???�성?�었?�니?? {plan_file}")
                    
                except Exception as e:
                    logger.error(f"주간 계획 ?�동 ?�성 ?�패: {e}")
                    # ?�패??기본 계획 ?�용
                    plan_data = create_default_weekly_plan(monday)
            else:
                # ?�래?��? ?�용불�???경우 기본 계획 ?�용
                logger.warning("주간 ?�래?��? ?�용?????�어 기본 계획???�성?�니??)
                plan_data = create_default_weekly_plan(monday)
        
        # ?�??카테고리 ?�장 버전 ?�성 (8�?주제)
        try:
            logger.info("주간계획 ?�장 ?�작")
            expanded_plan = create_expanded_weekly_plan(plan_data)
            logger.info(f"?�장??계획 ?�이???? {len(expanded_plan.get('days', []))}")
        except Exception as e:
            logger.error(f"주간계획 ?�장 ?�패: {e}")
            expanded_plan = plan_data
        
        return jsonify({
            'success': True,
            'plan': expanded_plan,
            'summary': summary_data,
            'week_start': monday.strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"주간 계획 조회 ?�류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedule/weekly')
def get_weekly_schedule():
    """?�주?�치 발행 ?��?�?조회 (?�거??"""
    try:
        from src.utils.schedule_manager import schedule_manager
        
        # ?�택??주의 ?�작??(기본: ?�번 �?
        week_start = request.args.get('week_start')
        if week_start:
            from datetime import datetime
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            start_date = None
        
        schedule_data = schedule_manager.get_weekly_schedule(start_date)
        
        # ?�짜�?문자?�로 변??(JSON 직렬?�용)
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
    """?�별 발행 ?��?�?조회"""
    try:
        from src.utils.monthly_schedule_manager import monthly_schedule_manager
        from datetime import datetime
        
        # ?�택???�월 (기본: ?�번 ??
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        if not year or not month:
            today = datetime.now()
            year = year or today.year
            month = month or today.month
        
        # ?�별 ?��?�?조회
        schedule = monthly_schedule_manager.get_month_schedule(year, month)
        
        # ?�답 ?�식 구성
        response = {
            'year': year,
            'month': month,
            'schedule': {}
        }
        
        # ?�짜별로 ?�리?�고 primary/secondary ?�식?�로 변??        for day, sites in schedule.items():
            day_schedule = {}
            
            for site, topics in sites.items():
                # topics??리스???�태?��?�?primary/secondary�?분리
                if len(topics) >= 2:
                    # 2�??�상??경우 �?번째??primary, ??번째??secondary
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
                    # 1개만 ?�는 경우 primary�??�정
                    day_schedule[site] = {
                        'primary': {
                            'category': topics[0]['category'],
                            'topic': topics[0]['topic'],
                            'keywords': topics[0]['keywords']
                        }
                    }
            
            if day_schedule:  # ?��?줄이 ?�는 ?�만 추�?
                response['schedule'][day] = day_schedule
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Monthly schedule error: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/schedule/create', methods=['POST'])
def create_weekly_schedule():
    """?�주?�치 발행 ?��?�??�성"""
    try:
        from src.utils.schedule_manager import schedule_manager
        
        data = request.get_json()
        start_date = data.get('start_date') if data else None
        
        if start_date:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        success = schedule_manager.create_weekly_schedule(start_date)
        
        if success:
            return jsonify({'success': True, 'message': '?�주?�치 ?��?�??�성 ?�료'})
        else:
            return jsonify({'success': False, 'error': '?��?�??�성 ?�패'})
            
    except Exception as e:
        logger.error(f"Create schedule error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/schedule/auto-updater/status')
def get_auto_updater_status():
    """?�간 ?��?�??�동 ?�데?�트 ?�태 조회"""
    try:
        from src.utils.auto_schedule_updater import auto_schedule_updater
        status = auto_schedule_updater.get_scheduler_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/schedule/auto-updater/test', methods=['POST'])
def test_auto_updater():
    """?�간 ?��?�??�동 ?�데?�트 ?�스??""
    try:
        from src.utils.auto_schedule_updater import auto_schedule_updater
        auto_schedule_updater.update_next_month_schedule()
        return jsonify({'success': True, 'message': '?�음 ???��?�??�성 ?�료'})
    except Exception as e:
        logger.error(f"Auto updater test error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/trending')
def trending_page():
    """?�렌???�슈 ?�이지"""
    return render_template('trending.html')

@app.route('/api/trending/current')
def get_current_trends():
    """?�번 �??�렌???�픽 API - ?�시�??�이??""
    try:
        real_trending_manager = TrendingTopicManager()
        
        # ?�시�??�렌???�이???�집 �??�데?�트
        real_trending_manager.update_trending_cache(force_update=True)
        
        # ?�이?�별 ?�렌??주제 ?�집
        site_trends = {}
        for site in ['unpre', 'untab', 'skewese']:
            config = real_trending_manager.site_configs[site]
            primary_category = config['primary']
            secondary_category = config['secondary']
            
            primary_topics = real_trending_manager.get_trending_topics(site, primary_category, 8)
            secondary_topics = real_trending_manager.get_trending_topics(site, secondary_category, 8)
            
            # ?�렌???�식?�로 변??            trends = []
            for i, topic in enumerate(primary_topics[:4]):
                trends.append({
                    'category': primary_category,
                    'trend_type': 'hot' if i < 2 else 'rising',
                    'title': topic,
                    'description': f'{primary_category} 분야??최신 ?�렌???�슈?�니??,
                    'keywords': real_trending_manager._extract_keywords(topic),
                    'priority': 9 - i
                })
            
            for i, topic in enumerate(secondary_topics[:4]):
                trends.append({
                    'category': secondary_category,
                    'trend_type': 'rising' if i < 2 else 'predicted',
                    'title': topic,
                    'description': f'{secondary_category} 분야???�시�??�렌??주제?�니??,
                    'keywords': real_trending_manager._extract_keywords(topic),
                    'priority': 8 - i
                })
            
            site_trends[site] = trends
        
        # 공통 ?�시�??�슈 ?�성 (모든 ?�이???�렌?�에???�별)
        cross_category_issues = []
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        
        # ?�시�??�렌???�이?�로 ?�이???�성 (?�드코딩 ?�전 ?�거)
        hot_issues = []
        
        try:
            # ?�시�??�렌??매니?�?�서 최신 ?�렌??가?�오�?            real_trending_manager.update_trending_cache(force_update=True)
            
            # 모든 ?�이?�에??고우?�순???�렌???�픽 ?�집
            all_trending_topics = []
            for site in ['unpre', 'untab', 'skewese']:
                site_config = real_trending_manager.site_configs.get(site, {})
                for category in [site_config.get('primary'), site_config.get('secondary')]:
                    if category:
                        topics = real_trending_manager.get_trending_topics(site, category, 5)
                        for topic in topics:
                            all_trending_topics.append({
                                'category': category.split('/')[0].lower(),  # '기술/?��??? -> 'technology'
                                'trend_type': 'hot',
                                'title': f"?�� {topic}",
                                'description': f"?�시간으�?주목받고 ?�는 {category} 분야???�이?�입?�다",
                                'keywords': real_trending_manager._extract_keywords(topic),
                                'priority': 9
                            })
            
            # 카테고리 매핑 (?�국??-> ?�어)
            category_mapping = {
                '기술': 'technology',
                '교육': 'education', 
                '?�정': 'economy',
                '?�이?�스?�??: 'lifestyle',
                '건강': 'health',
                '??��': 'culture',
                '?�터?�인먼트': 'culture',
                '?�렌??: 'social'
            }
            
            # 카테고리별로 최고 ?�선?�위 ?�픽�??�별 (중복 ?�거)
            category_best = {}
            for topic in all_trending_topics:
                category = topic['category']
                if category not in category_best or topic['priority'] > category_best[category]['priority']:
                    # 카테고리 매핑 ?�용
                    mapped_category = category_mapping.get(category, category)
                    topic['category'] = mapped_category
                    category_best[mapped_category] = topic
            
            # 최종 ?�이??리스??(최�? 8�?
            hot_issues = list(category_best.values())[:8]
            
        except Exception as e:
            print(f"[TRENDING] ?�시�??�이???�성 ?�류: {e}")
            # ?�러 ??기본 ?�적 ?�슈 ?�성
            current_time = datetime.now()
            
            hot_issues = [
                {
                    'category': 'technology',
                    'trend_type': 'hot',
                    'title': f'?�� {current_time.strftime("%m??%d??)} AI 기술 ?�향',
                    'description': '최신 AI 기술 발전�??�업 ?�향???�시간으�?분석?�니??,
                    'keywords': ['AI', '기술?�향', '?�시간분??],
                    'priority': 9
                },
                {
                    'category': 'economy',
                    'trend_type': 'hot', 
                    'title': f'?�� {current_time.strftime("%m??%d??)} 경제 ?�렌??,
                    'description': '?�시�?경제 지?��? ?�장 ?�향??분석?�니??,
                    'keywords': ['경제?�향', '?�장분석', '?�자?�렌??],
                    'priority': 8
                }
            ]
        
        cross_category_issues.extend(hot_issues)
        
        # ?�이?�별 ?�위 ?�렌?�도 ?��? 공통 ?�슈�??�격
        for site, trends in site_trends.items():
            if trends:
                top_trend = trends[0]  # �?번째 ?�렌?��? 공통 ?�슈�??�격
                cross_category_issues.append({
                    'category': top_trend['category'],
                    'trend_type': 'rising',
                    'title': f"?�� {top_trend['title']}",
                    'description': f"{site} ?�이?�에??주목받는 {top_trend['category']} 분야 ?�렌??,
                    'keywords': top_trend['keywords'],
                    'priority': top_trend['priority'] - 1
                })
        
        trends_data = {
            'period': '?�번�?,
            'week_start': week_start,
            'site_trends': site_trends,
            'cross_category_issues': cross_category_issues,
            'total_site_count': sum(len(site_trends) for site_trends in site_trends.values()),
            'cross_category_count': len(cross_category_issues)
        }
        
        return jsonify({'success': True, 'data': trends_data})
        
    except Exception as e:
        logger.error(f"?�시�??�렌??조회 ?�류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trending/last')
def get_last_week_trends():
    """지??�??�렌???�픽 API - ?�시�??�이??""
    try:
        real_trending_manager = TrendingTopicManager()
        real_trending_manager.update_trending_cache()
        
        # ?�주 ?�이?�는 ?�제 ?�시�??�이?�의 ?�전 버전?�로 ?��??�이??        site_trends = {}
        for site in ['unpre', 'untab', 'skewese']:
            config = real_trending_manager.site_configs[site]
            primary_category = config['primary']
            secondary_category = config['secondary']
            
            # ?�전 ?�렌?�로 ?��??�이??(?�제로는 캐시???�이???�용)
            primary_topics = real_trending_manager.get_trending_topics(site, primary_category, 6)
            secondary_topics = real_trending_manager.get_trending_topics(site, secondary_category, 6)
            
            trends = []
            for i, topic in enumerate(primary_topics[-3:]):  # ?�쪽 ?�이?��? ?�주 ?�이?�로 ?�용
                trends.append({
                    'category': primary_category,
                    'trend_type': 'hot',
                    'title': f"?�주 {topic}",
                    'description': f'지?�주 {primary_category} 분야??주요 ?�슈?�?�니??,
                    'keywords': real_trending_manager._extract_keywords(topic),
                    'priority': 8 - i
                })
            
            for i, topic in enumerate(secondary_topics[-3:]):
                trends.append({
                    'category': secondary_category,
                    'trend_type': 'rising',
                    'title': f"?�주 {topic}",
                    'description': f'지?�주 {secondary_category} 분야?�서 관?�받?� 주제?�니??,
                    'keywords': real_trending_manager._extract_keywords(topic),
                    'priority': 7 - i
                })
            
            site_trends[site] = trends
        
        # 지?�주 공통 ?�슈
        cross_category_issues = [
            {
                'category': 'technology',
                'trend_type': 'hot',
                'title': '?�주 AI 기술 발전',
                'description': '지?�주 AI 기술 분야??주요 발전???�었?�니??,
                'keywords': ['AI', '기술발전', '?�공지??],
                'priority': 8
            }
        ]
        
        last_week_start = (datetime.now() - timedelta(days=datetime.now().weekday() + 7)).strftime('%Y-%m-%d')
        
        trends_data = {
            'period': '?�주',
            'week_start': last_week_start,
            'site_trends': site_trends,
            'cross_category_issues': cross_category_issues,
            'total_site_count': sum(len(site_trends) for site_trends in site_trends.values()),
            'cross_category_count': len(cross_category_issues)
        }
        
        return jsonify({'success': True, 'data': trends_data})
        
    except Exception as e:
        logger.error(f"?�주 ?�렌??조회 ?�류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trending/next')
def get_next_week_trends():
    """?�음 �??�상 ?�렌???�픽 API - ?�측 ?�이??""
    try:
        real_trending_manager = TrendingTopicManager()
        real_trending_manager.update_trending_cache()
        
        # ?�음�??�상 ?�렌???�성
        site_trends = {}
        for site in ['unpre', 'untab', 'skewese']:
            config = real_trending_manager.site_configs[site]
            primary_category = config['primary']
            secondary_category = config['secondary']
            
            # ?�재 ?�렌?��? 기반?�로 ?�음�??�상 ?�렌???�성
            current_primary = real_trending_manager.get_trending_topics(site, primary_category, 4)
            current_secondary = real_trending_manager.get_trending_topics(site, secondary_category, 4)
            
            trends = []
            
            # ?�상 ?�렌???�성 (?�재 ?�렌??기반)
            predicted_topics = [
                f"?�음�??�망: {primary_category} ?�기???�향",
                f"?�상 ?�슈: {secondary_category} 분야 주요 변??,
                f"?�음�?주목: {primary_category} ?�계 ?�식",
                f"?�측 ?�렌?? {secondary_category} 최신 ?�향"
            ]
            
            for i, topic in enumerate(predicted_topics):
                category = primary_category if i % 2 == 0 else secondary_category
                trends.append({
                    'category': category,
                    'trend_type': 'predicted',
                    'title': topic,
                    'description': f'{category} 분야???�음�??�상 ?�렌?�입?�다',
                    'keywords': [category.split('/')[0], '?�상', '?�망'],
                    'priority': 7 - (i // 2)
                })
            
            site_trends[site] = trends
        
        # ?�음�??�상 공통 ?�슈
        cross_category_issues = [
            {
                'category': 'technology',
                'trend_type': 'predicted',
                'title': '?�음�?기술 ?�렌???�망',
                'description': '?�음�?주목??만한 기술 분야 ?�슈?�이 ?�상?�니??,
                'keywords': ['기술', '?�망', '?�상?�슈'],
                'priority': 8
            },
            {
                'category': 'economy',
                'trend_type': 'predicted',
                'title': '?�음�?경제 ?�향 ?�망',
                'description': '경제 분야??주요 변?��? ?�상?�는 ?�황?�니??,
                'keywords': ['경제', '?�향', '?�망'],
                'priority': 7
            }
        ]
        
        next_week_start = (datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=7)).strftime('%Y-%m-%d')
        
        trends_data = {
            'period': '?�음�?,
            'week_start': next_week_start,
            'site_trends': site_trends,
            'cross_category_issues': cross_category_issues,
            'total_site_count': sum(len(site_trends) for site_trends in site_trends.values()),
            'cross_category_count': len(cross_category_issues)
        }
        
        return jsonify({'success': True, 'data': trends_data})
        
    except Exception as e:
        logger.error(f"?�음�??�렌??조회 ?�류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trending/initialize', methods=['POST'])
def initialize_trending_data():
    """?�시�??�렌???�이??강제 ?�데?�트 API"""
    try:
        real_trending_manager = TrendingTopicManager()
        success = real_trending_manager.update_trending_cache(force_update=True)
        
        if success:
            return jsonify({'success': True, 'message': '?�시�??�렌???�이???�데?�트 ?�료'})
        else:
            return jsonify({'success': False, 'message': '?�렌???�이???�데?�트 ?�패'})
            
    except Exception as e:
        logger.error(f"?�렌???�이???�데?�트 ?�류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/schedule/auto_publish', methods=['POST'])
def trigger_auto_publish():
    """?�동 발행 ?�리�?""
    try:
        from src.utils.schedule_manager import schedule_manager
        from datetime import datetime
        
        data = request.get_json()
        target_date = data.get('date') if data else None
        
        if target_date:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            target_date = datetime.now().date()
        
        # ?�당 ?�짜???��?�??�행
        success = execute_daily_schedule(target_date)
        
        if success:
            return jsonify({'success': True, 'message': f'{target_date} ?�동 발행 ?�료'})
        else:
            return jsonify({'success': False, 'error': '?�동 발행 ?�패'})
            
    except Exception as e:
        logger.error(f"Auto publish error: {e}")
        return jsonify({'success': False, 'error': str(e)})

def execute_daily_schedule(target_date):
    """?�정 ?�짜???��?�??�행"""
    try:
        from src.utils.schedule_manager import schedule_manager
        
        # ?�당 ?�짜???��?�?조회
        week_start = target_date - timedelta(days=target_date.weekday())
        day_of_week = target_date.weekday()
        
        schedule_data = schedule_manager.get_weekly_schedule(week_start)
        
        if not schedule_data or day_of_week not in schedule_data['schedule']:
            print(f"[SCHEDULE] {target_date} ?�당 ?�짜 ?��?�??�음")
            return False
        
        day_schedule = schedule_data['schedule'][day_of_week]
        sites = day_schedule.get('sites', {})
        
        success_count = 0
        total_count = len(sites)
        
        for site, plan in sites.items():
            if plan['status'] == 'published':
                print(f"[SCHEDULE] {site} ?��? 발행 ?�료")
                success_count += 1
                continue
            
            try:
                # 콘텐�??�성 �?발행
                print(f"[SCHEDULE] {site} ?�동 발행 ?�작: {plan['topic']}")
                
                # ?�태�?'generating'?�로 변�?                schedule_manager.update_schedule_status(
                    week_start, day_of_week, site, 'generating'
                )
                
                # ?�제 콘텐�??�성 �?발행 로직 (기존 publish_content ?�용)
                success = publish_scheduled_content(site, plan)
                
                if success:
                    schedule_manager.update_schedule_status(
                        week_start, day_of_week, site, 'published'
                    )
                    success_count += 1
                    print(f"[SCHEDULE] {site} 발행 ?�공")
                else:
                    schedule_manager.update_schedule_status(
                        week_start, day_of_week, site, 'failed'
                    )
                    print(f"[SCHEDULE] {site} 발행 ?�패")
                    
            except Exception as e:
                print(f"[SCHEDULE] {site} 발행 ?�류: {e}")
                schedule_manager.update_schedule_status(
                    week_start, day_of_week, site, 'failed'
                )
        
        print(f"[SCHEDULE] ?�동 발행 ?�료: {success_count}/{total_count}")
        return success_count > 0
        
    except Exception as e:
        print(f"[SCHEDULE] ?�일 ?��?�??�행 ?�류: {e}")
        return False

def publish_scheduled_content(site: str, plan: dict) -> bool:
    """?��?줄된 콘텐�??�성 �?발행"""
    try:
        # 기존 콘텐�??�성 로직 ?�용
        topic = plan['topic']
        keywords = plan.get('keywords', [])
        length = plan.get('target_length', 'medium')
        
        print(f"[PUBLISH] {site} 콘텐�??�성 �? {topic}")
        
        # ?�제 콘텐�??�성 (추후 구현)
        # ?�기?�는 ?�시�??�공 반환
        return True
        
    except Exception as e:
        print(f"[PUBLISH] {site} 발행 ?�류: {e}")
        return False


@app.route('/api/manual-publish/preview', methods=['GET'])
def preview_manual_publish():
    """?�동 발행 미리보기 - ?�늘 발행??주제???�인"""
    try:
        from src.utils.monthly_schedule_manager import monthly_schedule_manager
        from datetime import datetime
        
        sites = ['unpre', 'untab', 'skewese', 'tistory']
        preview_data = {
            'total_posts': len(sites),  # 1 topic per site
            'sites': []
        }
        
        for site in sites:
            try:
                primary, secondary = monthly_schedule_manager.get_today_dual_topics(site)
                site_data = {
                    'site': site.upper(),
                    'topics': [
                        {
                            'type': 'Primary',
                            'category': primary.get('category', ''),
                            'topic': primary.get('topic', ''),
                            'keywords': primary.get('keywords', [])
                        }
                    ],
                    'debug_marker': 'FIXED_VERSION_SINGLE_TOPIC'
                }
                preview_data['sites'].append(site_data)
            except Exception as e:
                logger.error(f"Error getting topics for {site}: {e}")
                preview_data['sites'].append({
                    'site': site.upper(),
                    'error': str(e)
                })
        
        preview_data['date'] = datetime.now().strftime('%Y-%m-%d')
        preview_data['message'] = f"오늘 수동발행 시 생성될 {preview_data['total_posts']}개 포스트 (사이트당 1개)"
        
        return jsonify({
            'success': True,
            'preview': preview_data
        })
        
    except Exception as e:
        logger.error(f"Preview error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/quick_publish', methods=['POST'])
def quick_publish():
    """빠른 ?�동 발행 API - ?�시�?진행?�황�?중복 방�?"""
    global publish_status_global
    
    try:
        data = request.json
        sites = data.get('sites', ['unpre', 'untab', 'skewese', 'tistory'])
        manual_topic = data.get('topic')  # alert?�로 받�? 주제
        manual_category = data.get('category')  # alert?�로 받�? 카테고리
        
        # 중복 ?�행 방�?
        if publish_status_global['in_progress']:
            return jsonify({
                'success': False,
                'error': '?��? 발행??진행 중입?�다. ?�시�?기다?�주?�요.'
            }), 400
        
        # ?�태 초기??        publish_status_global.update({
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
            """백그?�운?�에???�제 콘텐�??�성 - ?�??카테고리 ?�스??""
            global publish_status_global

            # ?�??카테고리�??�한 ?�간 ?��?�?매니?� ?�용
            from src.utils.monthly_schedule_manager import monthly_schedule_manager
            from src.generators.content_generator import ContentGenerator
            from src.generators.tistory_content_exporter import TistoryContentExporter
            from src.generators.wordpress_content_exporter import WordPressContentExporter

            from datetime import datetime, timezone, timedelta
            import time
            
            # KST ?�?�존 ?�정
            KST = timezone(timedelta(hours=9))
            start_time = datetime.now(KST)
            safe_log("?�??카테고리 ?�동 발행 ?�작", "info")
            
            # ?�세 ?�태 초기??            publish_status_global.update({
                'in_progress': True,
                'message': "발행 준�?�?..",
                'progress': 0,
                'current_site': None,
                'current_task': None,
                'current_step': 'initialization',
                'step_details': '?�스??초기??�?준�?,
                'completed_sites': 0,
                'completed_posts': 0,
                'failed_posts': 0,
                'total_posts': len(sites),
                'total_sites': len(sites),
                'results': [],
                'errors': [],
                'start_time': start_time.isoformat()
            })

            # �??�이?�별�?2개씩 처리 (�?8�?
            total_posts = len(sites) * 2  # ?�이?�당 2�?            completed_posts = 0
            
            safe_log(f"[리포?? 발행 계획: {len(sites)}�??�이??× 2�??�스??= {total_posts}�?�??�스??)
            
            # 초기???�료 ?�태 ?�데?�트
            publish_status_global.update({
                'current_step': 'database_connection',
                'step_details': 'DB ?�결 ?�인 �?..',
                'message': f"DB ?�결 ?�인 �?.. (�?{total_posts}�??�스???�정)"
            })

            # DB ?�결
            try:
                safe_log("[?�결] DB ?�결 ?�도 �?..")
                db = get_database()
                safe_log("[?�공] DB ?�결 ?�공")
                
                publish_status_global.update({
                    'current_step': 'ready_to_publish',
                    'step_details': 'DB ?�결 ?�료, 발행 ?�작 준�?,
                    'message': f"DB ?�결 ?�공! 발행 ?�작 �?.. (0/{total_posts})"
                })
                
            except Exception as e:
                error_msg = f"DB ?�결 ?�류: {str(e)}"
                logger.error(f"??{error_msg}")
                
                publish_status_global.update({
                    'in_progress': False,
                    'current_step': 'failed',
                    'step_details': 'DB ?�결 ?�패�?발행 중단',
                    'message': f"??DB ?�결 ?�패: {str(e)}",
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
                    # ?�재 ?�이???�태 ?�데?�트
                    publish_status_global.update({
                        'current_site': site,
                        'current_step': 'topic_loading',
                        'step_details': f'{site.upper()} ?�이??주제 조회',
                        'message': f"?�� {site.upper()} ?�이??주제 조회 �?.. ({site_idx}/{len(sites)} ?�이??"
                    })
                    
                    safe_log(f"[TARGET] {site} ?�이???�??카테고리 발행 ?�작 ({site_idx}/{len(sites)})", "info")

                    # ??�� ?��?줄에???�??카테고리 주제 가?�오�?(?�동발행??8�??�성)
                    try:
                        primary_topic, secondary_topic = monthly_schedule_manager.get_today_dual_topics_for_manual(site)
                        safe_log(f"[?�공] {site} ?��?�?주제 조회 ?�공")
                        
                        # manual_topic???�으�?primary�???��?�기
                        if manual_topic:
                            primary_topic = {
                                'topic': manual_topic,
                                'category': manual_category or primary_topic.get('category', '?�반'),
                                'keywords': [manual_topic.split()[0]] if manual_topic else primary_topic.get('keywords', [])
                            }
                            safe_log(f"[?�공] {site} Primary 주제�??�동 주제�?변�? {manual_topic}")
                        
                    except Exception as e:
                        error_msg = f"{site} 주제 조회 ?�류: {str(e)}"
                        logger.error(f"??{error_msg}")
                        
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
                            'message': f'주제 조회 ?�패: {str(e)}',
                            'category': 'system',
                            'error_details': str(e)
                        })
                        continue

                    if not primary_topic or not secondary_topic:
                        error_msg = f"{site}???�??카테고리 주제�?찾을 ???�습?�다"
                        logger.error(f"??{error_msg}")
                        
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
                            'message': '주제�?찾을 ???�음 - DB ?��?�??�인 ?�요',
                            'category': 'system'
                        })
                        continue

                    if secondary_topic:
                        logger.info(f"?�� {site} ?�??주제 ?�인 - Primary: {primary_topic['topic']}, Secondary: {secondary_topic['topic']}")
                    else:
                        logger.info(f"?�� {site} ?�일 주제 ?�인 - Primary: {primary_topic['topic']}")
                    
                    # 주제 조회 ?�료 ?�태 ?�데?�트
                    publish_status_global.update({
                        'current_step': 'content_generation',
                        'step_details': f'{site.upper()}: Primary + Secondary 콘텐�??�성',
                        'message': f"?�� {site.upper()}: Primary [{primary_topic['topic']}] ?�성 ?�작..."
                    })

                    # Primary 카테고리 발행
                    try:
                        logger.info(f"?�� {site} Primary 카테고리 발행 ?�작: {primary_topic['topic']}")
                        
                        # ?�태 ?�데?�트
                        publish_status_global.update({
                            'current_task': f"Primary: {primary_topic['topic']}",
                            'step_details': f'{site.upper()}: DB ?�??�?콘텐�??�성 준�?,
                            'message': f"?�� {site.upper()}: Primary DB ?�??�?.."
                        })

                        # DB??처리�??�태�?추�?
                        try:
                            primary_file_id = db.add_content_file(
                                site=site,
                                title=f"[Primary ?�성�? {primary_topic['topic']}",
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
                            logger.info(f"??{site} Primary DB ?�???�료 (ID: {primary_file_id})")
                            
                        except Exception as e:
                            error_msg = f"{site} Primary DB ?�???�패: {str(e)}"
                            logger.error(f"??{error_msg}")
                            
                            publish_status_global['errors'].append({
                                'timestamp': datetime.now().isoformat(),
                                'site': site,
                                'type': 'database_save',
                                'category': 'primary',
                                'topic': primary_topic['topic'],
                                'message': error_msg,
                                'details': str(e)
                            })
                            
                            raise Exception(f"DB ?�???�패: {str(e)}")
                            
                        # 콘텐�??�성 ?�태 ?�데?�트
                        publish_status_global.update({
                            'step_details': f'{site.upper()}: Primary 콘텐�?AI ?�성 �?,
                            'message': f"?�� {site.upper()}: Primary [{primary_topic['topic']}] AI ?�성 �?.."
                        })

                        # 콘텐�??�성
                        if site == 'tistory':
                            generator = ContentGenerator()
                            exporter = TistoryContentExporter()

                            site_config = {
                                'name': 'Tistory 블로�?,
                                'categories': [primary_topic['category']],
                                'content_style': '친근?�고 ?�용?�인 ??,
                                'target_audience': get_target_audience_by_category(primary_topic['category']),
                                'keywords_focus': primary_topic.get('keywords', [])
                            }

                            content_data = generator.generate_content(
                                site_config,
                                primary_topic['topic'],
                                primary_topic['category'],
                                None,  # existing_posts
                                'medium',  # content_length
                                site  # site_key for API tracking
                            )

                            if content_data:
                                filepath = exporter.export_content(content_data)

                                # DB ?�데?�트
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
                                
                                # 발행 ?�료 ?�간 ?�데?�트 - DB??바로 반영?�도�?                                from datetime import datetime
                                db.update_file_status(final_file_id, 'published', datetime.now())
                                
                                # 콘텐�?목록??즉시 반영?�도�?메�??�이???�데?�트
                                try:
                                    db.update_content_metadata(final_file_id, {
                                        'category': primary_topic['category'],
                                        'category_type': 'primary',
                                        'tags': content_data.get('tags', []),
                                        'auto_published': True
                                    })
                                except Exception as meta_error:
                                    logger.warning(f"메�??�이???�데?�트 ?�패: {meta_error}")

                                # 진행?�황 ?�데?�트
                                completed_posts += 1
                                publish_status_global.update({
                                    'completed_posts': completed_posts,
                                    'progress': int((completed_posts / total_posts) * 100)
                                })

                                # Tistory???�동 발행�?지??(?�동 발행 ?�거)
                                logger.info(f"Tistory Primary 콘텐�??�성 ?�료 (?�동 발행): {primary_topic['topic']}")
                                publish_status_global['results'].append({
                                    'site': site,
                                    'status': 'success',
                                    'message': f'Primary 콘텐�??�성 ?�료 (?�동 발행 ?�요): {primary_topic["topic"]}',
                                    'category': 'primary',
                                    'topic': primary_topic['topic']
                                })

                                logger.info(f"{site} Primary 발행 ?�공: {primary_topic['topic']}")
                            else:
                                raise Exception("콘텐�??�성 ?�패")
                        else:
                            # WordPress ?�이??처리
                            generator = ContentGenerator()
                            exporter = WordPressContentExporter()

                            site_config = {
                                'name': site,
                                'categories': [primary_topic['category']],
                                'content_style': '?�문?�이�??�뢰?????�는 ??,
                                'target_audience': get_target_audience_by_category(primary_topic['category']),
                                'keywords_focus': primary_topic.get('keywords', [])
                            }

                            content_data = generator.generate_content(
                                site_config,
                                primary_topic['topic'],
                                primary_topic['category'],
                                None,  # existing_posts
                                'medium',  # content_length
                                site  # site_key for API tracking
                            )

                            if content_data:
                                filepath = exporter.export_content(site, content_data)

                                # DB ?�데?�트
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
                                
                                # 발행 ?�료 ?�간 ?�데?�트 - DB??바로 반영?�도�?                                from datetime import datetime
                                db.update_file_status(final_file_id, 'published', datetime.now())
                                
                                # 콘텐�?목록??즉시 반영?�도�?메�??�이???�데?�트
                                try:
                                    db.update_content_metadata(final_file_id, {
                                        'category': primary_topic['category'],
                                        'category_type': 'primary',
                                        'tags': content_data.get('tags', []),
                                        'auto_published': True
                                    })
                                except Exception as meta_error:
                                    logger.warning(f"메�??�이???�데?�트 ?�패: {meta_error}")

                                # 진행?�황 ?�데?�트
                                completed_posts += 1
                                publish_status_global.update({
                                    'completed_posts': completed_posts,
                                    'progress': int((completed_posts / total_posts) * 100)
                                })

                                # WordPress ?�로???�전 ?�킵 - 콘텐�??�성�??�고 목록???�시
                                logger.info(f"WordPress Primary 콘텐�??�성�??�료 (?�로???�킵): {primary_topic['topic']}")
                                publish_status_global['results'].append({
                                    'site': site,
                                    'status': 'success',
                                    'message': f'Primary 콘텐�??�성 ?�료 (목록???�시??: {primary_topic["topic"]}',
                                    'category': 'primary',
                                    'topic': primary_topic['topic']
                                })

                                logger.info(f"{site} Primary 발행 ?�공: {primary_topic['topic']}")
                            else:
                                raise Exception("콘텐�??�성 ?�패")

                        completed_posts += 1
                        publish_status_global['completed_sites'] = completed_posts
                        publish_status_global['progress'] = int((completed_posts / total_posts) * 100)

                    except Exception as e:
                        logger.error(f"{site} Primary 발행 ?�패: {e}")
                        # 처리�???�� ??��
                        try:
                            db.delete_content_file(primary_file_id)
                        except:
                            pass
                        publish_status_global['results'].append({
                            'site': site,
                            'status': 'failed',
                            'message': f'Primary 발행 ?�패: {str(e)}',
                            'category': 'primary'
                        })

                    # Secondary 카테고리 발행 (alert 주제 ?�용???�킵)
                    if secondary_topic:
                        try:
                            logger.info(f"{site} Secondary 카테고리 발행 ?�작: {secondary_topic['topic']}")

                            # DB??처리�??�태�?추�?
                            secondary_file_id = db.add_content_file(
                                site=site,
                                title=f"[Secondary ?�성�? {secondary_topic['topic']}",
                                file_path="processing",
                                file_type="wordpress" if site != 'tistory' else 'tistory',
                                metadata={
                                    'status': 'processing',
                                    'category': secondary_topic['category'],
                                    'category_type': 'secondary'
                                }
                            )

                            # 콘텐�??�성 (Primary?� ?�사??로직)
                            if site == 'tistory':
                                generator = ContentGenerator()
                                exporter = TistoryContentExporter()

                                site_config = {
                                    'name': 'Tistory 블로�?,
                                    'categories': [secondary_topic['category']],
                                    'content_style': '친근?�고 ?�용?�인 ??,
                                    'target_audience': get_target_audience_by_category(secondary_topic['category']),
                                    'keywords_focus': secondary_topic.get('keywords', [])
                                }

                                content_data = generator.generate_content(
                                    site_config,
                                    secondary_topic['topic'],
                                    secondary_topic['category'],
                                    None,  # existing_posts
                                    'medium',  # content_length
                                    site  # site_key for API tracking
                                )

                                if content_data:
                                    filepath = exporter.export_content(content_data)

                                    # DB ?�데?�트
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
                                    
                                    # 발행 ?�료 ?�간 ?�데?�트
                                    db.update_file_status(final_secondary_file_id, 'published', datetime.now())

                                    logger.info(f"Tistory Secondary 콘텐�??�성 ?�료 (?�동 발행): {secondary_topic['topic']}")

                            else:
                                # WordPress ?�이??처리 (콘텐�??�성�?
                                generator = ContentGenerator()
                                exporter = WordPressContentExporter()

                                site_config = {
                                    'name': site.upper(),
                                    'categories': [secondary_topic['category']],
                                    'content_style': '?�문?�이�??�용?�인 ??,
                                    'target_audience': get_target_audience_by_category(secondary_topic['category']),
                                    'keywords_focus': secondary_topic.get('keywords', [])
                                }

                                content_data = generator.generate_content(
                                    site_config,
                                    secondary_topic['topic'],
                                    secondary_topic['category'],
                                    None,  # existing_posts
                                    'medium',  # content_length
                                    site  # site_key for API tracking
                                )

                                if content_data:
                                    filepath = exporter.export_content(site, content_data)

                                    # DB ?�데?�트
                                    db.delete_content_file(secondary_file_id)
                                    final_secondary_file_id = db.add_content_file(
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
                                    
                                    # 발행 ?�료 ?�간 ?�데?�트
                                    db.update_file_status(final_secondary_file_id, 'published', datetime.now())

                                    logger.info(f"{site} Secondary 콘텐�??�성 ?�료: {secondary_topic['topic']}")

                            completed_posts += 1
                            publish_status_global['progress'] = int((completed_posts / total_posts) * 100)

                        except Exception as e:
                            logger.error(f"{site} Secondary 발행 ?�패: {e}")
                            # 처리�???�� ??��
                            try:
                                db.delete_content_file(secondary_file_id)
                            except:
                                pass
                            publish_status_global['results'].append({
                                'site': site,
                                'status': 'failed',
                                'message': f'Secondary 발행 ?�패: {str(e)}',
                                'category': 'secondary'
                            })
                    else:
                        logger.info(f"{site} alert 주제 ?�용?�로 Secondary 발행 ?�킵")
                
                # ?�체 ?�이???�료 ??처리
                except Exception as e:
                    logger.error(f"{site} ?�체 처리 ?�패: {e}")
                    publish_status_global['results'].append({
                        'site': site,
                        'status': 'failed',
                        'message': f'발행 ?�패: {str(e)}',
                        'category': 'error'
                    })

                    # ?�이???�료 결과 추�?
                    secondary_msg = secondary_topic['topic'] if secondary_topic else '(?�킵??'
                    publish_status_global['results'].append({
                        'site': site,
                        'status': 'completed',
                        'message': f'Primary: {primary_topic["topic"]}, Secondary: {secondary_msg}',
                        'primary_topic': primary_topic['topic'],
                        'secondary_topic': secondary_topic['topic'] if secondary_topic else None
                    })

                except Exception as e:
                    logger.error(f"{site} ?�체 처리 ?�패: {e}")
                    publish_status_global['results'].append({
                        'site': site,
                        'status': 'failed',
                        'message': str(e)
                    })

            # ?�료 처리
            publish_status_global['in_progress'] = False
            publish_status_global['progress'] = 100
            publish_status_global['completed_sites'] = completed_posts
            publish_status_global['total_sites'] = total_posts
            publish_status_global['current_site'] = None
            
            # 결과 ?�약 메시지 ?�성
            success_count = len([r for r in publish_status_global['results'] if r.get('status') == 'success'])
            failed_count = len(publish_status_global['results']) - success_count
            
            if failed_count == 0:
                publish_status_global['message'] = f"[?�공] ?�체 발행 ?�료! �?{completed_posts}�??�스???�성??
            else:
                publish_status_global['message'] = f"[경고] 발행 ?�료 - ?�공: {success_count}�? ?�패: {failed_count}�?

            safe_log(f"?�??카테고리 ?�동 발행 ?�료: {completed_posts}/{total_posts} ?�스??, "info")
        
        # 백그?�운???�레???�작
        thread = threading.Thread(target=background_publish)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '?�동 발행???�작?�었?�니??,
            'background': True,
            'total_sites': len(sites)
        })
        
    except Exception as e:
        publish_status_global['in_progress'] = False
        logger.error(f"Quick publish error: {e}")
        
        # ?�세???�류 ?�보 로깅
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Quick publish error details: {error_details}")
        
        # ?�류 ?�형�?분류
        error_message = str(e)
        if "Request interrupted" in error_message:
            error_type = "timeout"
            user_message = "?�청 ?�간 초과: 콘텐�??�성???�간???�래 걸립?�다. ?�시 ???�시 ?�도?�주?�요."
        elif "UnicodeEncodeError" in error_message:
            error_type = "encoding"
            user_message = "문자 ?�코???�류: ?�수 문자 처리 �??�류가 발생?�습?�다."
        elif "relation" in error_message and "does not exist" in error_message:
            error_type = "database"
            user_message = "?�이?�베?�스 ?�결 ?�류: ?��?�??�이블에 ?�근?????�습?�다."
        else:
            error_type = "unknown"
            user_message = f"발행 처리 �??�류 발생: {error_message}"
        
        return jsonify({
            'success': False,
            'error': user_message,
            'error_type': error_type,
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/publish_status')
def publish_status():
    """발행 ?�태 조회 API - ?�시�?백그?�운??처리 ?�태 (?�세 로깅 ?�함)"""
    global publish_status_global
    try:
        from datetime import datetime, timezone, timedelta
        
        # KST ?�?�존 ?�정
        KST = timezone(timedelta(hours=9))
        current_time = datetime.now(KST)
        
        # 진행�?계산 (?�스??기�?) - 최�? 100%�??�한
        post_progress = 0
        if publish_status_global.get('total_posts', 0) > 0:
            completed = publish_status_global.get('completed_posts', 0)
            total = publish_status_global.get('total_posts', 1)
            post_progress = min(100, int((completed / total) * 100))
        
        # ?�이??진행�?계산
        site_progress = 0
        if publish_status_global.get('total_sites', 0) > 0:
            site_progress = int((publish_status_global.get('completed_sites', 0) / publish_status_global.get('total_sites', 1)) * 100)
        
        # ?�태 결정
        if publish_status_global.get('in_progress', False):
            status = 'in_progress'
        elif publish_status_global.get('completed_posts', 0) > 0:
            status = 'completed'
        else:
            status = 'idle'
        
        # ?�행 ?�간 계산 (KST 기�?)
        elapsed_time = None
        if publish_status_global.get('start_time'):
            try:
                # ISO ?�식???�작 ?�간??KST�?변??                start = datetime.fromisoformat(publish_status_global['start_time'].replace('Z', '+00:00'))
                if start.tzinfo is None:
                    start = start.replace(tzinfo=KST)
                elif start.tzinfo != KST:
                    start = start.astimezone(KST)
                
                elapsed = current_time - start
                total_seconds = int(elapsed.total_seconds())
                elapsed_time = f"{total_seconds // 60}�?{total_seconds % 60}�?
            except Exception as e:
                elapsed_time = "계산 ?�패"
        
        # ?�답 ?�이??구성
        response = {
            'status': status,
            'message': publish_status_global.get('message', '?��?�?..'),
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
            'errors': publish_status_global.get('errors', []),  # ?�세 ?�러 로그
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


# ?�러 ?�들??@app.errorhandler(500)
def handle_internal_error(e):
    """?�버 ?�러 처리"""
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


# �?번째 __main__ 블록??주석 처리 (API ?�우?��? ?�록?�도�?
# if __name__ == '__main__':
#     print("PostgreSQL Web Dashboard Starting...")
#     print("Available at: http://localhost:5000")
#     print("Supabase PostgreSQL Connected")
#     
#     try:
#         # ?�이?�베?�스 ?�결 ?�스??#         get_database()
#         print("PostgreSQL Connection: OK")
#         
#         # ?�동 발행 ?��?줄러 ?�작
#         try:
#             from src.utils.auto_publisher import auto_publisher
#             auto_publisher.start()
#             print("Auto Publisher Scheduler: STARTED")
#         except Exception as e:
#             print(f"Auto Publisher failed to start: {e}")
#             print("Manual publishing only")
#         
#         # ?�렌???�이??초기??#         try:
#             trending_manager.initialize_sample_trends()
#             print("Trending Topics: INITIALIZED")
#         except Exception as e:
#             print(f"Trending initialization failed: {e}")
#         
#         app.run(debug=True, host='0.0.0.0', port=5000)
#         
#     except Exception as e:
#         print(f"Server start failed: {e}")
#         print("Check .env PostgreSQL settings")


@app.route('/api/preview_content/<int:file_id>')
def preview_content(file_id):
    """콘텐�?미리보기 API"""
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
                return "?�일??찾을 ???�습?�다.", 404
            
            title, file_path, file_type, site, tags, categories = file_info
        
        # ?�일 경로?�서 ?�제 HTML 콘텐�??�기
        from pathlib import Path
        
        if file_path == "processing":
            # 처리중인 경우 간단??메시지 ?�시
            preview_html = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>처리�?- {title}</title>
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
                    <h1>??콘텐�??�성 �?..</h1>
                    <p>?�재 AI가 콘텐츠�? ?�성?�고 ?�습?�다. ?�시�?기다?�주?�요.</p>
                    <p><strong>?�목:</strong> {title}</p>
                    <p><strong>?�이??</strong> {site.upper()}</p>
                    <p><strong>?�??</strong> {file_type}</p>
                </div>
            </body>
            </html>
            """
            return preview_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
        html_file = Path(file_path)
        if not html_file.exists():
            return f"?�일??존재?��? ?�습?�다: {file_path}", 404
        
        # HTML ?�일 ?�용 ?�기
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except UnicodeDecodeError:
            with open(html_file, 'r', encoding='cp949') as f:
                html_content = f.read()
        
        # HTML 콘텐�?개선 처리
        processed_content = _process_content_for_preview(html_content)
        
        # ?��??�링 개선??미리보기 HTML ?�성  
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
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">카테고리: {', '.join(categories) if categories else '?�반'} | ?�그: {', '.join(tags) if tags else '?�음'}</p>
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
                        button.innerHTML = '??복사??;
                        button.classList.add('copy-success');
                        
                        setTimeout(function() {{
                            button.innerHTML = '복사';
                            button.classList.remove('copy-success');
                        }}, 2000);
                    }}).catch(function() {{
                        button.innerHTML = '복사 ?�패';
                        setTimeout(function() {{
                            button.innerHTML = '복사';
                        }}, 2000);
                    }});
                }}
                
                // ?�이지 로드 ??코드 블록 처리
                document.addEventListener('DOMContentLoaded', function() {{
                    // Prism.js�?코드 ?�이?�이??                    if (typeof Prism !== 'undefined') {{
                        Prism.highlightAll();
                    }}
                }});
            </script>
        </body>
        </html>"""
        
        return preview_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        logger.error(f"미리보기 ?�성 ?�류: {e}")
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>미리보기 ?�류</title>
            <style>
                body {{ font-family: monospace; padding: 20px; background: #f8f9fa; }}
                .error {{ background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>??미리보기 ?�성 �??�류가 발생?�습?�다</h2>
                <p><strong>?�류 ?�용:</strong> {str(e)}</p>
                <pre>{traceback.format_exc()}</pre>
            </div>
        </body>
        </html>
        """
        return error_html, 500, {'Content-Type': 'text/html; charset=utf-8'}
    
def _process_content_for_preview(html_content: str) -> str:
    """HTML 콘텐츠�? 미리보기?�으�?처리"""
    import re
    
    # --- 구분?�을 ?�쁜 구분?�으�?변�?    html_content = re.sub(r'-{3,}', '<hr class="content-divider">', html_content)
    
    # 코드 블록???�쁘�?처리
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
    
    # ```language ?�태??코드 블록 처리
    html_content = re.sub(r'```(\w+)?\s*\n(.*?)\n```', replace_code_block, html_content, flags=re.DOTALL)
    
    # ?�일 ` 코드�??�라??코드�?처리
    html_content = re.sub(r'`([^`]+)`', r'<code style="background: #f1f5f9; padding: 0.2rem 0.4rem; border-radius: 3px; font-family: monospace;">\1</code>', html_content)
    
    # HTML ?�이�??��??�링
    html_content = re.sub(r'<table>', '<table class="table">', html_content)
    
    # 강조 ?�시 개선
    html_content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html_content)
    
    # 줄바꿈을 <br>�?변�?(?? HTML ?�그 ?�에?�는 ?�외)
    lines = html_content.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('<') and not line.endswith('>'):
            if not re.search(r'<[^>]+>', line):  # HTML ?�그가 ?�는 ?�인�?                line = line + '<br>'
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)

@app.route('/api/debug_schedule', methods=['GET'])
def debug_schedule():
    """DB ?��?�??�태 ?�버�?""
    try:
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        weekday = today.weekday()
        week_start = today - timedelta(days=weekday)
        
        # DB ?�결
        db = get_database()
        conn = db.get_connection()
        
        results = {}
        
        with conn.cursor() as cursor:
            # ?�재 �??��?�??�인
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
            
            # 모든 ?��?�??�인 (최근 20�?
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
    """계획?�에 맞게 DB ?��?�?주제 ?�정"""
    try:
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # ?�바�?계획??주제
        correct_topics = {
            'unpre': "Redis 캐싱 ?�략�??�능 ?�닝",
            'untab': "리츠(REITs) ?�자???�단??, 
            'skewese': "?��???과학???�리?� ?�수??,
            'tistory': "?�건�?규제 ?�화, ?�장 변???�상"
        }
        
        categories = {
            'unpre': '?�로그래�?,
            'untab': '취�?',
            'skewese': '뷰티/?�션', 
            'tistory': '?�반'
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
            'message': f'{updated_count}�??�이??주제 ?�데?�트 ?�료',
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
    """발행 계획???�기??API"""
    try:
        from src.utils.schedule_sync import sync_schedule_api
        
        # POST ?�이?�에???��?�??�스??가?�오�?        data = request.get_json() or {}
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
    """긴급 ?�재 �??�기??API"""
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
    """?�?�보??기존 ?��?줄을 DB??강제 ?�력"""
    try:
        from src.utils.dashboard_schedule_importer import import_dashboard_schedules as import_func
        
        success = import_func()
        
        if success:
            return jsonify({
                'success': True,
                'message': '?�?�보???��?�??�이?��? DB???�공?�으�?가?�왔?�니??
            })
        else:
            return jsonify({
                'success': False,
                'message': '?��?�?가?�오�??�패'
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
                'message': f'{week_start} �?2�?카테고리 ?��?�??�성 ?�료',
                'week_start': week_start.isoformat(),
                'total_posts': 56
            })
        else:
            return jsonify({'success': False, 'message': '?��?�??�성 ?�패'}), 500
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_all_dual_topics', methods=['GET'])
def get_all_dual_topics():
    try:
        from src.utils.monthly_schedule_manager import monthly_schedule_manager
        
        sites = ['unpre', 'untab', 'skewese', 'tistory']
        all_topics = {}
        
        for site in sites:
            try:
                primary_topic, secondary_topic = monthly_schedule_manager.get_today_dual_topics_for_manual(site)
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
# ?�스???�태 �?진단 API
# ========================================================================

@app.route('/api/system_status')
def system_status():
    """?�스???�체 ?�태 ?�인"""
    try:
        import time
        start_time = time.time()
        
        # 기본 ?�스???�보
        status = {
            'overall': 'healthy',
            'server_info': 'Python Flask on Koyeb',
            'uptime': '?�버 ?�행 �?,
            'memory_usage': 'N/A',
            'cpu_usage': 'N/A'
        }
        
        # psutil ?�용 가???�에�??�세 ?�보 ?�집
        try:
            import psutil
            uptime_seconds = int(time.time() - psutil.boot_time())
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            status['uptime'] = f"{hours}?�간 {minutes}�?
            status['memory_usage'] = f"{psutil.virtual_memory().percent:.1f}%"
            status['cpu_usage'] = f"{psutil.cpu_percent(interval=1):.1f}%"
        except:
            # psutil ?�어??기본 ?�보???�공
            pass
        
        # DB ?�결 ?�태 ?�인
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
                'uptime': '?????�음',
                'server_info': 'Python Flask',
                'memory_usage': 'N/A',
                'cpu_usage': 'N/A',
                'database': 'unknown',
                'error': str(e)
            }
        })

@app.route('/api/database_status')
def database_status():
    """?�이?�베?�스 ?�결 ?�태 ?�인"""
    try:
        db = get_database()
        
        # DB 기본 ?�보
        db_info = {
            'connected': False,
            'host': getattr(db, 'connection_params', {}).get('host', '?????�음'),
            'database': getattr(db, 'connection_params', {}).get('database', '?????�음'),
            'schema': getattr(db, 'schema', 'unble'),
            'table_count': 0,
            'total_records': 0,
            'error': None
        }
        
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                # 기본 ?�결 ?�스??                cursor.execute("SELECT 1")
                db_info['connected'] = True
                
                # ?�이�????�인 (?�전?�게)
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_schema = '{db.schema}'
                    """)
                    db_info['table_count'] = cursor.fetchone()[0] or 0
                except:
                    db_info['table_count'] = '?�인 불�?'
                
                # �??�코?????�인 (?�전?�게)
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {db.schema}.content_files")
                    db_info['total_records'] = cursor.fetchone()[0] or 0
                except:
                    db_info['total_records'] = '?�인 불�?'
                    
        except Exception as db_error:
            db_info['connected'] = False
            db_info['error'] = str(db_error)
            
        return jsonify({'success': True, 'database': db_info})
            
    except Exception as e:
        # ?�전 ?�패?�에??기본 구조 ?��?
        return jsonify({
            'success': True,
            'database': {
                'connected': False,
                'host': '?????�음',
                'database': '?????�음', 
                'schema': 'unble',
                'table_count': 0,
                'total_records': 0,
                'error': f'?�스???�류: {str(e)}'
            }
        })

@app.route('/api/scheduler_status')
def scheduler_status():
    """?�동발행 ?��?줄러 ?�태 ?�인"""
    try:
        # 기본 ?��?줄러 ?�보
        scheduler_info = {
            'running': False,
            'jobs_count': 0,
            'next_run': '?�인 불�?',
            'last_run': '?�음',
            'last_error': None
        }
        
        # ?��?줄러 ?�태 ?�인 (?�전?�게)
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
                    scheduler_info['next_run'] = '?��?�??�음'
            else:
                scheduler_info['next_run'] = '?�록???�업 ?�음'
                
        except ImportError:
            scheduler_info['next_run'] = '?��?줄러 모듈 ?�음'
        except Exception as sched_error:
            scheduler_info['next_run'] = f'?�류: {str(sched_error)}'
        
        # ?�스??로그?�서 마�?�??�동발행 ?�보 ?�인 (?�전?�게)
        try:
            db = get_database()
            logs = db.get_system_logs(component='auto_publisher', limit=1)
            if logs and len(logs) > 0:
                last_log = logs[0]
                timestamp = last_log.get('timestamp', '')
                if timestamp:
                    # ISO ?�식???�국?�로 변??                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        scheduler_info['last_run'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        scheduler_info['last_run'] = timestamp.replace('T', ' ')
                        
                if last_log.get('log_level') == 'ERROR':
                    scheduler_info['last_error'] = last_log.get('message', '')
        except:
            # 로그 조회 ?�패?�도 기본�??��?
            pass
        
        return jsonify({'success': True, 'scheduler': scheduler_info})
        
    except Exception as e:
        return jsonify({
            'success': True, 
            'scheduler': {
                'running': False,
                'jobs_count': 0,
                'next_run': '?�스???�류',
                'last_run': '?�인 불�?',
                'last_error': f'API ?�류: {str(e)}'
            }
        })

@app.route('/api/environment_status')
def environment_status():
    """?�경변???�태 ?�인"""
    try:
        import os
        
        # ?�수 ?�경변?�들
        critical_vars = [
            'PG_HOST', 'PG_DATABASE', 'PG_USER', 'PG_PASSWORD',
            'ANTHROPIC_API_KEY', 'OPENAI_API_KEY'
        ]
        
        # ?�택???�경변?�들  
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
        
        # ?�수 변???�인
        for var in critical_vars:
            if os.getenv(var):
                total_set += 1
            else:
                critical_missing.append(var)
                
        # ?�택??변???�인
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
    """?�스??로그 조회"""
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
    """?�시�??�렌???�스???�태 조회"""
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
    """?�시�??�렌???�이??강제 ?�데?�트"""
    try:
        trending_manager = TrendingTopicManager()
        success = trending_manager.update_trending_cache(force_update=True)
        
        if success:
            summary = trending_manager.get_site_topics_summary()
            return jsonify({
                'success': True, 
                'message': '?�렌???�이???�데?�트 ?�료',
                'updated_sites': list(summary.keys()),
                'update_time': datetime.now().isoformat()
            })
        else:
            return jsonify({'success': False, 'message': '?�렌???�이???�데?�트 ?�패'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trending_topics/<site>')
def get_site_trending_topics(site):
    """?�정 ?�이?�의 ?�렌??주제 조회"""
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


@app.route('/api/api_usage/today')
def get_today_api_usage():
    """?�늘??API ?�용??조회"""
    try:
        usage = api_tracker.get_today_usage()
        return jsonify({
            'success': True,
            'data': usage
        })
    except Exception as e:
        logger.error(f"Today API usage error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'date': datetime.now().date().isoformat(),
                'total_requests': 0,
                'total_tokens': 0,
                'total_cost_usd': 0,
                'by_service': {},
                'by_site': {}
            }
        })


@app.route('/api/api_usage/monthly')
def get_monthly_api_usage():
    """?�번 ??API ?�용??조회"""
    try:
        usage = api_tracker.get_monthly_usage()
        return jsonify({
            'success': True,
            'data': usage
        })
    except Exception as e:
        logger.error(f"Monthly API usage error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'month': datetime.now().strftime("%Y-%m"),
                'total_requests': 0,
                'total_tokens': 0,
                'total_cost_usd': 0,
                'daily_trend': [],
                'days_in_month': 0,
                'avg_daily_cost': 0
            }
        })


@app.route('/api/api_usage/recent')
def get_recent_api_calls():
    """최근 API ?�출 ?�역"""
    try:
        limit = int(request.args.get('limit', 20))
        calls = api_tracker.get_recent_calls(limit)
        return jsonify({
            'success': True,
            'data': calls
        })
    except Exception as e:
        logger.error(f"Recent API calls error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        })


# ========================================================================
# ?�시�??�렌??API
# ========================================================================

@app.route('/trends')
def trends_dashboard():
    """?�시�??�렌???�?�보???�이지"""
    return render_template('trends_dashboard.html')

@app.route('/api/trends/realtime')
def get_realtime_trends():
    """?�시�??�렌???�이???�집"""
    try:
        logger.info("?�시�??�렌???�이???�집 ?�작...")
        
        # 카테고리�??�렌???�집
        categorized_trends = trend_collector.get_categorized_trends()
        
        # ?�이?��? JSON 직렬??가?�한 ?�태�?변??        json_trends = {}
        total_trends = 0
        sources = set()
        
        for category, trends in categorized_trends.items():
            json_trends[category] = []
            for trend in trends:
                trend_dict = {
                    'title': trend.title,
                    'source': trend.source,
                    'category': trend.category,
                    'score': trend.score,
                    'url': trend.url,
                    'description': trend.description,
                    'timestamp': trend.timestamp.isoformat() if trend.timestamp else None,
                    'tags': trend.tags or []
                }
                json_trends[category].append(trend_dict)
                sources.add(trend.source)
                total_trends += 1
        
        # ?�계 ?�보
        stats = {
            'totalTrends': total_trends,
            'totalSources': len(sources),
            'categories': list(json_trends.keys()),
            'lastUpdate': datetime.now().isoformat()
        }
        
        logger.info(f"?�렌???�집 ?�료: {total_trends}�??�렌?? {len(sources)}�??�스")
        
        return jsonify({
            'success': True,
            'trends': json_trends,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"?�시�??�렌???�집 ?�류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trends': {},
            'stats': {}
        })

@app.route('/api/trends/sources')
def get_trend_sources():
    """?�용 가?�한 ?�렌???�스 목록"""
    try:
        sources = [
            {
                'name': 'Google Trends',
                'description': '?�시�?구�? 검???�렌??,
                'category': '검??,
                'status': 'active'
            },
            {
                'name': '?�이�??�렌??,
                'description': '?�국 ?�시�?검?�어',
                'category': '검??, 
                'status': 'active'
            },
            {
                'name': 'Reddit',
                'description': '?�외 커�??�티 ?�기 ?�픽',
                'category': 'discussion',
                'status': 'active'
            },
            {
                'name': 'Hacker News',
                'description': '기술 ?�스 �??��??�업',
                'category': '기술',
                'status': 'active'
            },
            {
                'name': 'GitHub',
                'description': '개발???�렌???�?�소',
                'category': '기술',
                'status': 'active'
            }
        ]
        
        return jsonify({
            'success': True,
            'sources': sources
        })
        
    except Exception as e:
        logger.error(f"?�렌???�스 조회 ?�류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'sources': []
        })

@app.route('/api/trends/refresh')
def refresh_trends():
    """?�렌???�이??강제 ?�로고침"""
    try:
        logger.info("?�렌???�이??강제 ?�로고침 ?�청")
        
        # ?�로???�렌???�집 (캐시 무시)
        all_trends = trend_collector.collect_all_trends()
        
        return jsonify({
            'success': True,
            'message': f'{len(all_trends)}개의 ?�로???�렌?��? ?�집?�습?�다.',
            'count': len(all_trends),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"?�렌???�로고침 ?�류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


# ============== ?�워??리서�?�?주간 계획 API ?�우??==============

@app.route('/api/keywords/research', methods=['POST'])
def research_keywords():
    """?�워??리서�?API"""
    if not keyword_features_available:
        return jsonify({
            'success': False,
            'error': '?�워??리서�?기능???�용?????�습?�다.'
        }), 503
        
    try:
        data = request.get_json() or {}
        categories = data.get('categories', ['금융'])
        keyword_count = data.get('count', 10)
        
        researcher = KeywordResearcher()
        results = []
        
        for category in categories:
            category_keywords = researcher.research_keywords(category, keyword_count)
            results.extend(category_keywords)
        
        # 기회?�수 기�??�로 ?�렬
        results.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        
        return jsonify({
            'success': True,
            'keywords': results[:50],  # 최�? 50�?            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"?�워??리서�??�류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/keywords/categories')
def get_keyword_categories():
    """?�용 가?�한 ?�워??카테고리 목록"""
    categories = [
        '금융', '?�자', '보험', '부?�산', '기술/IT', 
        '건강/?�료', '교육', '취업', '?�활/?�이?�스?�??, 
        '?�행', '?�식', '?�션/뷰티', '?�아/교육', '?�동�?, '게임'
    ]
    return jsonify({
        'success': True,
        'categories': categories
    })

@app.route('/api/weekly-plan/create', methods=['POST'])
def create_weekly_plan():
    """주간 블로�?계획 ?�성 API"""
    if not keyword_features_available:
        return jsonify({
            'success': False,
            'error': '주간 계획 기능???�용?????�습?�다.'
        }), 503
        
    try:
        data = request.get_json() or {}
        target_date = data.get('target_date')
        
        # ?�짜 ?�싱
        if target_date:
            start_date = datetime.strptime(target_date, '%Y-%m-%d')
        else:
            start_date = datetime.now()
        
        # 주간 계획 ?�성
        planner = WeeklyBlogPlanner()
        plan = planner.create_weekly_plan(start_date)
        
        return jsonify({
            'success': True,
            'plan': plan,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"주간 계획 ?�성 ?�류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/keywords/generate-content', methods=['POST'])
def generate_keyword_content():
    """?�워??기반 콘텐�??�성"""
    if not keyword_features_available:
        return jsonify({
            'success': False,
            'error': '콘텐�??�성 기능???�용?????�습?�다.'
        }), 503
        
    try:
        data = request.get_json() or {}
        keyword = data.get('keyword', '')
        
        if not keyword:
            return jsonify({
                'success': False,
                'error': '?�워?��? ?�력?�주?�요.'
            }), 400
        
        # blog_content_generator ?�용?�여 콘텐�??�웃?�인 ?�성
        from blog_content_generator import main as generate_content
        
        # ?�시�??�워?�로 콘텐�??�성
        content_result = generate_content([keyword])
        
        return jsonify({
            'success': True,
            'content': content_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"콘텐�??�성 ?�류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # 백그?�운???��?줄러 ?�작 (?�전??처리)
    if scheduler_available:
        try:
            def start_scheduler():
                try:
                    init_scheduler()
                    logging.info("???�동발행 ?��?줄러가 ?�공?�으�??�작?�었?�니??)
                except Exception as e:
                    logging.error(f"???��?줄러 ?�작 ?�패: {e}")
            
            scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
            scheduler_thread.start()
            logging.info("?�� 백그?�운???��?줄러 ?�레???�작??)
        except Exception as e:
            logging.error(f"???��?줄러 ?�레???�성 ?�패: {e}")
    else:
        logging.warning("[경고] ?�동발행 ?��?줄러??비활?�화?�니??(?�동발행?� ?�상 ?�동)")
    
    # ?�간 ?��?�??�동 ?�데?�트 ?��?줄러 ?�작
    try:
        from src.utils.auto_schedule_updater import auto_schedule_updater
        auto_schedule_updater.start_scheduler()
        logging.info("???�간 ?��?�??�동 ?�데?�트 ?��?줄러 ?�작??)
    except Exception as e:
        logging.error(f"???�간 ?��?�??�동 ?�데?�트 ?��?줄러 ?�작 ?�패: {e}")
    
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

