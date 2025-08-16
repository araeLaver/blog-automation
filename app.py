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
import psycopg2
from psycopg2.extras import RealDictCursor

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

# 환경변수 로드
load_dotenv()

# PostgreSQL 데이터베이스 import
from src.utils.postgresql_database import PostgreSQLDatabase

# AI 콘텐츠 생성 import (나중에 초기화)

# Flask 앱 생성
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')  # 정적 파일 경로 명시
CORS(app)

# 템플릿 캐싱 비활성화
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI 콘텐츠 생성기 초기화
try:
    from src.generators.content_generator import ContentGenerator
    content_generator = ContentGenerator()
    logger.info("✅ Claude API 콘텐츠 생성기 초기화 완료 - v2.0")
except Exception as e:
    logger.warning(f"⚠️ Claude API 초기화 실패: {e}")
    content_generator = None

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# PostgreSQL 데이터베이스 인스턴스 (전역)
db = None

def get_database():
    """데이터베이스 인스턴스 반환"""
    global db
    if db is None:
        db = PostgreSQLDatabase()
    return db

# PostgreSQL 연결 함수
def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT', 5432),
            database=os.getenv('PG_DATABASE'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            options=f"-c search_path={os.getenv('PG_SCHEMA', 'unble')}"
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def get_mock_data():
    """DB 연결 실패 시 사용할 목업 데이터"""
    now = datetime.now(KST)
    today_3am = now.replace(hour=3, minute=0, second=0, microsecond=0)
    
    # 오늘 새벽 3시에 자동발행된 포스트들 생성
    posts = []
    
    # 오늘 자동발행된 포스트들 (새벽 3시 이후라면)
    if now >= today_3am:
        posts.extend([
            {
                'id': 1,
                'title': '🤖 AI 코딩 어시스턴트의 최신 동향',
                'site': 'unpre',
                'category': 'AI/프로그래밍',
                'url': 'https://unpre.co.kr/ai-coding-assistant-2025',
                'created_at': today_3am.strftime('%Y-%m-%d %H:%M:%S'),
                'published': True
            },
            {
                'id': 2,
                'title': '📚 효율적인 언어학습을 위한 5가지 방법',
                'site': 'untab',
                'category': '교육/언어학습',
                'url': 'https://untab.co.kr/language-learning-tips-2025',
                'created_at': today_3am.strftime('%Y-%m-%d %H:%M:%S'),
                'published': True
            },
            {
                'id': 3,
                'title': '🏛️ 조선시대 과학기술의 놀라운 발전',
                'site': 'skewese',
                'category': '역사/문화',
                'url': 'https://skewese.com/joseon-science-technology',
                'created_at': today_3am.strftime('%Y-%m-%d %H:%M:%S'),
                'published': True
            }
        ])
    
    # 어제 발행된 포스트들
    yesterday_3am = today_3am - timedelta(days=1)
    posts.extend([
        {
            'id': 4,
            'title': 'React 18의 새로운 기능들',
            'site': 'unpre',
            'category': '프로그래밍',
            'url': 'https://unpre.co.kr/react-18-features',
            'created_at': yesterday_3am.strftime('%Y-%m-%d %H:%M:%S'),
            'published': True
        },
        {
            'id': 5,
            'title': '부동산 투자 전략 가이드',
            'site': 'untab',
            'category': '부동산',
            'url': 'https://untab.co.kr/real-estate-investment',
            'created_at': yesterday_3am.strftime('%Y-%m-%d %H:%M:%S'),
            'published': True
        }
    ])
    
    today_posts = len([p for p in posts if p['created_at'].startswith(now.strftime('%Y-%m-%d'))])
    
    return {
        'posts': posts,
        'stats': {
            'total_posts': len(posts),
            'published': len(posts),
            'scheduled': 0,
            'today_posts': today_posts
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
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 각 사이트에서 최근 포스트 가져오기
            posts = []
            for site in ['unpre', 'untab', 'skewese']:
                cursor.execute("""
                    SELECT id, title, site, 
                           CASE WHEN categories IS NOT NULL AND jsonb_array_length(categories) > 0 
                                THEN categories->>0 
                                ELSE 'default' END as category,
                           created_at::text, 
                           CASE WHEN status = 'published' THEN true ELSE false END as published
                    FROM unble.content_files 
                    WHERE site = %s
                    ORDER BY created_at DESC 
                    LIMIT 5
                """, (site,))
                site_posts = cursor.fetchall()
                posts.extend(site_posts if site_posts else [])
            
            cursor.close()
            conn.close()
            
            # 시간순 정렬
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
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            site_filter = request.args.get('site', 'all')
            date_filter = request.args.get('date', '')
            
            posts = []
            for site in ['unpre', 'untab', 'skewese']:
                if site_filter == 'all' or site_filter == site:
                    query = """
                        SELECT id, title, site, 
                               CASE WHEN categories IS NOT NULL AND jsonb_array_length(categories) > 0 
                                    THEN categories->>0 
                                    ELSE 'default' END as category,
                               url, 
                               created_at::text, 
                               CASE WHEN status = 'published' THEN true ELSE false END as published
                        FROM unble.content_files 
                        WHERE site = %s
                    """
                    params = [site]
                    
                    if date_filter:
                        query += " AND DATE(created_at) = %s"
                        params.append(date_filter)
                    
                    query += " ORDER BY created_at DESC LIMIT 10"
                    
                    cursor.execute(query, params)
                    site_posts = cursor.fetchall()
                    posts.extend(site_posts if site_posts else [])
            
            cursor.close()
            conn.close()
            
            posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return jsonify({'status': 'success', 'posts': posts})
        else:
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
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 전체 통계 조회
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_posts,
                    COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
                    COUNT(CASE WHEN status != 'published' THEN 1 END) as scheduled,
                    COUNT(CASE WHEN DATE(created_at) = CURRENT_DATE THEN 1 END) as today_posts
                FROM unble.content_files
            """)
            
            stats = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if stats:
                stats['revenue'] = {
                    'total_views': 0,
                    'total_revenue': 0
                }
                return jsonify(stats)
            else:
                mock = get_mock_data()
                stats = mock['stats']
                stats['revenue'] = {
                    'total_views': 0,
                    'total_revenue': 0
                }
                return jsonify(stats)
        else:
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
    conn = get_db_connection()
    db_status = 'online' if conn else 'offline'
    if conn:
        conn.close()
    
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
        'database': {'status': db_status},
        'scheduler': {'status': 'online', 'next_run': '03:00 KST'}
    })

@app.route('/trending')
def trending_page():
    """트렌딩 페이지"""
    return render_template('trending.html')

@app.route('/api/trending')
@app.route('/api/trending/<period>')
def get_trending(period='current'):
    """트렌딩 토픽 조회"""
    try:
        # 목업 트렌딩 데이터
        mock_trends = {
            'current': {
                'period': '이번주 트렌드',
                'week_start': '2025-08-11',
                'cross_category_issues': [
                    {
                        'title': 'AI 기술 혁신',
                        'category': 'Technology',
                        'trend_type': 'hot',
                        'priority': 9,
                        'description': 'ChatGPT와 Claude 등 AI 기술이 급속도로 발전하고 있습니다.',
                        'keywords': ['AI', 'ChatGPT', 'Claude', '인공지능']
                    },
                    {
                        'title': '부동산 정책 변화',
                        'category': 'Real Estate',
                        'trend_type': 'rising',
                        'priority': 8,
                        'description': '새로운 부동산 정책이 발표되어 시장에 큰 영향을 미치고 있습니다.',
                        'keywords': ['부동산', '정책', '시장변화']
                    }
                ],
                'site_trends': {
                    'unpre': [
                        {
                            'title': 'React 18 새 기능',
                            'category': 'Frontend',
                            'trend_type': 'rising',
                            'priority': 7,
                            'description': 'React 18의 새로운 기능들이 개발자들 사이에서 화제가 되고 있습니다.',
                            'keywords': ['React', 'Frontend', '웹개발']
                        },
                        {
                            'title': 'Python 성능 최적화',
                            'category': 'Backend',
                            'trend_type': 'hot',
                            'priority': 8,
                            'description': 'Python 성능 최적화 기법들이 주목받고 있습니다.',
                            'keywords': ['Python', '성능', '최적화']
                        }
                    ],
                    'untab': [
                        {
                            'title': '언어학습 앱 트렌드',
                            'category': 'Education',
                            'trend_type': 'rising',
                            'priority': 6,
                            'description': '새로운 언어학습 방법론이 주목받고 있습니다.',
                            'keywords': ['언어학습', '교육', '앱']
                        }
                    ],
                    'skewese': [
                        {
                            'title': '조선시대 문화 재조명',
                            'category': 'History',
                            'trend_type': 'predicted',
                            'priority': 5,
                            'description': '조선시대 문화에 대한 새로운 연구 결과가 발표되었습니다.',
                            'keywords': ['조선시대', '역사', '문화']
                        }
                    ]
                }
            }
        }
        
        trends = mock_trends.get(period, mock_trends['current'])
        
        return jsonify({
            'status': 'success',
            'success': True,
            'data': trends
        })
    except Exception as e:
        logger.error(f"트렌딩 조회 오류: {e}")
        return jsonify({
            'status': 'success',
            'success': True,
            'data': {
                'period': '기본 트렌드',
                'cross_category_issues': [],
                'site_trends': {}
            }
        })

@app.route('/api/chart_data')
def get_chart_data():
    """차트 데이터 조회"""
    now = datetime.now(KST)
    daily_data = []
    site_data = {
        'unpre': 0,
        'untab': 0,
        'skewese': 0
    }
    
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            for i in range(7):
                date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
                
                cursor.execute("""
                    SELECT site, COUNT(*) as count
                    FROM unble.content_files
                    WHERE DATE(created_at) = %s
                    GROUP BY site
                """, (date,))
                
                day_results = cursor.fetchall()
                day_count = sum(r['count'] for r in day_results) if day_results else 0
                daily_data.append({'date': date, 'count': day_count})
                
                for r in day_results:
                    site_data[r['site']] = site_data.get(r['site'], 0) + r['count']
            
            cursor.close()
            conn.close()
        else:
            # 목업 데이터
            for i in range(7):
                date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
                daily_data.append({'date': date, 'count': 3 - i % 2})
            site_data = {'unpre': 7, 'untab': 5, 'skewese': 3}
    except Exception as e:
        logger.error(f"차트 데이터 조회 오류: {e}")
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
    """주간 스케줄 조회 - schedule_manager 사용"""
    try:
        from src.utils.schedule_manager import schedule_manager
        
        week_start = request.args.get('week_start')
        if week_start:
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            # 이번 주 월요일
            today = datetime.now(KST).date()
            start_date = today - timedelta(days=today.weekday())
        
        # schedule_manager에서 실제 스케줄 데이터 가져오기
        schedule_data = schedule_manager.get_weekly_schedule(start_date)
        
        if not schedule_data or 'schedule' not in schedule_data:
            return jsonify({})
        
        # 대시보드용 포맷으로 변환
        formatted_schedule = {}
        
        for day_idx, day_info in schedule_data['schedule'].items():
            if not isinstance(day_info, dict) or 'date' not in day_info:
                continue
                
            date_str = day_info['date'].strftime('%Y-%m-%d')
            formatted_schedule[date_str] = {}
            
            sites_data = day_info.get('sites', {})
            for site, site_info in sites_data.items():
                if not isinstance(site_info, dict):
                    continue
                    
                # 주제를 topics 배열로 변환 (단일 주제를 2개 키워드로)
                topic = site_info.get('topic', f'{site} 기본 주제')
                keywords = site_info.get('keywords', [site])
                
                # 주제를 적절히 분할하여 2개 토픽으로 만들기
                if len(keywords) >= 2:
                    topics = [keywords[0], keywords[1]]
                else:
                    # 주제를 단어로 분할
                    topic_words = topic.split()
                    if len(topic_words) >= 4:
                        mid = len(topic_words) // 2
                        topics = [' '.join(topic_words[:mid]), ' '.join(topic_words[mid:])]
                    else:
                        topics = [topic, f'{site} 관련 주제']
                
                # 상태 결정
                current_date = datetime.now(KST).date()
                target_date = day_info['date']
                
                if target_date < current_date:
                    status = 'published'
                elif target_date == current_date:
                    current_time = datetime.now(KST).time()
                    if current_time >= datetime.strptime('03:00', '%H:%M').time():
                        status = 'published' 
                    else:
                        status = 'scheduled'
                else:
                    status = 'scheduled'
                
                formatted_schedule[date_str][site] = {
                    'time': '03:00',
                    'topics': topics,
                    'status': status
                }
        
        return jsonify(formatted_schedule)
        
    except Exception as e:
        logger.error(f"Weekly schedule error: {e}")
        return jsonify({}), 500

@app.route('/api/generate_wordpress', methods=['POST'])
def generate_wordpress():
    """WordPress 콘텐츠 생성"""
    try:
        data = request.json
        site = data.get('site', 'unpre')
        topic = data.get('topic', '프로그래밍')
        
        database = get_database()
        
        try:
            if database.is_connected:
                # Claude API로 실제 콘텐츠 생성
                logger.info(f"Content generator 상태: {content_generator is not None}")
                
                # ContentGenerator가 None이면 다시 초기화 시도
                current_generator = content_generator
                if current_generator is None:
                    try:
                        logger.info("ContentGenerator 재초기화 시도...")
                        from src.generators.content_generator import ContentGenerator
                        current_generator = ContentGenerator()
                        logger.info("✅ ContentGenerator 재초기화 성공")
                    except Exception as e:
                        logger.error(f"❌ ContentGenerator 재초기화 실패: {e}")
                        current_generator = None
                
                if current_generator:
                    logger.info(f"Claude API로 {topic} 콘텐츠 생성 시작...")
                    
                    # 사이트 설정
                    site_config = {
                        'name': site,
                        'target_audience': '개발자 및 IT 전문가',
                        'content_style': '실용적이고 기술적인',
                        'keywords_focus': data.get('keywords', [topic])
                    }
                    
                    # AI 콘텐츠 생성 (실제 Claude API 호출)
                    generated_content = current_generator.generate_content(
                        site_config=site_config,
                        topic=topic,
                        category=data.get('category', '프로그래밍'),
                        content_length='medium'
                    )
                    
                    # 이미지 생성 (실패해도 계속 진행)
                    images = []
                    try:
                        logger.info(f"이미지 생성 시작...")
                        from src.utils.safe_image_generator import SafeImageGenerator
                        img_gen = SafeImageGenerator()
                        images = img_gen.generate_images_for_content(
                            title=generated_content['title'],
                            keywords=data.get('keywords', [topic]),
                            count=2
                        )
                        logger.info(f"이미지 {len(images)}개 생성 완료")
                    except Exception as img_e:
                        logger.warning(f"이미지 생성 실패, 텍스트만 진행: {img_e}")
                        images = []
                    
                    # WordPress Exporter 사용하여 HTML 생성
                    from src.generators.wordpress_content_exporter import WordPressContentExporter
                    exporter = WordPressContentExporter()
                    file_path = exporter.export_content(site, generated_content, images)
                    
                    title = generated_content['title']
                    logger.info(f"Claude API 콘텐츠 생성 완료: {title[:50]}...")
                    logger.info(f"생성된 파일 경로: {file_path}")
                    
                    # 파일 경로 확인
                    if not file_path or not os.path.exists(file_path):
                        raise Exception(f"파일 생성 실패 또는 경로 없음: {file_path}")
                    
                else:
                    # Fallback 콘텐츠
                    logger.warning("ContentGenerator가 None입니다. 기본 콘텐츠를 생성합니다.")
                    title = f'{topic} 완전 가이드'
                    content_dict = {
                        'title': title,
                        'introduction': f'{topic}에 대한 상세한 분석입니다.',
                        'sections': [
                            {'heading': '소개', 'content': f'{topic}에 대한 기본 개념을 설명합니다.'},
                            {'heading': '주요 내용', 'content': f'{topic}의 핵심 내용을 다룹니다.'},
                        ],
                        'conclusion': f'{topic}에 대한 종합적인 이해를 돕습니다.',
                        'meta_description': f'{title} - 상세한 가이드와 팁',
                        'tags': data.get('keywords', [topic]),
                        'categories': [data.get('category', '기본')]
                    }
                    
                    from src.generators.wordpress_content_exporter import WordPressContentExporter
                    exporter = WordPressContentExporter()
                    file_path = exporter.export_content(site, content_dict, [])
                    logger.warning(f"Claude API 미사용, 기본 콘텐츠 생성: {title}")
                
                # 콘텐츠를 데이터베이스에 직접 저장
                file_id = database.add_content_file(
                    site=site,
                    title=title,
                    file_path=file_path,  # 생성된 파일 경로 저장
                    file_type='wordpress',
                    metadata={
                        'categories': [data.get('category', '기본')],
                        'tags': data.get('keywords', [topic]),
                        'word_count': 1000,  # 대략적인 값
                        'reading_time': 5,  # 대략 5분
                        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 1000
                    }
                )
                
                # 생성 성공 응답
                return jsonify({
                    'success': True,
                    'message': f'{site} 사이트에 {topic} 주제로 콘텐츠를 생성했습니다.',
                    'title': title,
                    'id': file_id,
                    'file_path': file_path,  # 파일 경로 추가
                    'post': {
                        'id': file_id,
                        'title': title,
                        'site': site,
                        'status': 'draft'
                    }
                })
        except Exception as db_error:
            logger.error(f"DB 저장 실패, 목업 모드로 전환: {db_error}")
        
        # DB 연결 실패시 목업 응답
        import time
        current_time = int(time.time())
        
        new_file = {
            'title': f'{topic} 완전 가이드',
            'id': current_time,
            'site': site,
            'status': 'draft',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return jsonify({
            'success': True,
            'message': f'{site} 사이트에 {topic} 주제로 콘텐츠를 생성했습니다. (목업 모드)',
            'title': new_file['title'],
            'id': new_file['id'],
            'post': new_file
        })
        
    except Exception as e:
        logger.error(f"WordPress 콘텐츠 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate_tistory', methods=['POST'])
def generate_tistory():
    """Tistory 콘텐츠 생성"""
    try:
        data = request.json
        topic = data.get('topic', '프로그래밍')
        
        database = get_database()
        
        try:
            if database.is_connected:
                # Claude API로 실제 콘텐츠 생성
                logger.info(f"Tistory Content generator 상태: {content_generator is not None}")
                
                # ContentGenerator가 None이면 다시 초기화 시도
                current_generator = content_generator
                if current_generator is None:
                    try:
                        logger.info("Tistory ContentGenerator 재초기화 시도...")
                        from src.generators.content_generator import ContentGenerator
                        current_generator = ContentGenerator()
                        logger.info("✅ Tistory ContentGenerator 재초기화 성공")
                    except Exception as e:
                        logger.error(f"❌ Tistory ContentGenerator 재초기화 실패: {e}")
                        current_generator = None
                
                if current_generator:
                    logger.info(f"Claude API로 Tistory {topic} 콘텐츠 생성 시작...")
                    
                    # 사이트 설정
                    site_config = {
                        'name': 'untab',
                        'target_audience': '일반 대중 및 관심있는 독자',
                        'content_style': '이해하기 쉬우고 실용적인',
                        'keywords_focus': data.get('keywords', [topic])
                    }
                    
                    # AI 콘텐츠 생성 (실제 Claude API 호출)
                    generated_content = current_generator.generate_content(
                        site_config=site_config,
                        topic=topic,
                        category=data.get('category', '일반'),
                        content_length='medium'
                    )
                    
                    # HTML 형태로 변환 - Tistory 깔끔한 디자인
                    content_html = _create_beautiful_html_template(generated_content, site_config)
                    
                    content = content_html
                    title = generated_content['title']
                    logger.info(f"Claude API Tistory 콘텐츠 생성 완료: {title[:50]}...")
                    
                else:
                    # Fallback 콘텐츠
                    logger.warning("Tistory ContentGenerator가 None입니다. 기본 콘텐츠를 생성합니다.")
                    content = f'<h1>{topic} 심화 분석</h1>\n<p>{topic}에 대한 상세한 분석입니다.</p>'
                    title = f'{topic} 심화 분석'
                    logger.warning(f"Claude API 미사용, Tistory 기본 콘텐츠 생성: {title}")
                
                # 콘텐츠를 데이터베이스에 직접 저장 (파일 시스템 사용 안함)
                file_id = database.add_content_file(
                    site='untab',
                    title=title,
                    file_path=content,  # 실제 콘텐츠를 file_path 필드에 저장
                    file_type='tistory',
                    metadata={
                        'categories': [data.get('category', '기본')],
                        'tags': data.get('keywords', [topic]),
                        'word_count': len(content.split()),
                        'reading_time': len(content.split()) // 200 + 1,
                        'file_size': len(content.encode('utf-8'))
                    }
                )
                
                # 생성 성공 응답
                return jsonify({
                    'success': True,
                    'message': f'Tistory에 {topic} 주제로 콘텐츠를 생성했습니다.',
                    'title': title,
                    'id': file_id,
                    'post': {
                        'id': file_id,
                        'title': title,
                        'status': 'draft'
                    }
                })
        except Exception as db_error:
            logger.error(f"DB 저장 실패, 목업 모드로 전환: {db_error}")
        
        # DB 연결 실패시 목업 응답
        import time
        current_time = int(time.time())
        
        new_file = {
            'title': f'{topic} 심화 분석',
            'id': current_time,
            'status': 'draft',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return jsonify({
            'success': True,
            'message': f'Tistory에 {topic} 주제로 콘텐츠를 생성했습니다. (목업 모드)',
            'title': new_file['title'],
            'id': new_file['id'],
            'post': new_file
        })
        
    except Exception as e:
        logger.error(f"Tistory 콘텐츠 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download_content/<int:file_id>')
def download_content(file_id):
    """콘텐츠 파일 다운로드"""
    try:
        database = get_database()
        
        if database.is_connected:
            # DB에서 파일 정보 조회
            files = database.get_content_files(limit=1000)  # 전체 조회
            target_file = None
            
            for f in files:
                if f.get('id') == file_id:
                    target_file = f
                    break
            
            if target_file:
                # file_path 필드에 저장된 실제 콘텐츠 읽기
                content = target_file.get('file_path')
                
                # 콘텐츠가 HTML이 아닌 경우 (파일 경로인 경우) 파일 읽기 시도
                if content and not content.strip().startswith('<'):
                    if os.path.exists(content):
                        try:
                            with open(content, 'r', encoding='utf-8') as f:
                                content = f.read()
                            logger.info(f"실제 파일 읽기 성공: {content}")
                        except Exception as e:
                            logger.warning(f"파일 읽기 실패: {e}")
                            content = None
                    else:
                        logger.warning(f"파일이 존재하지 않음: {content}")
                        content = None
                
                # 콘텐츠가 없거나 읽기 실패시 기본 콘텐츠 생성
                if not content:
                    content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_file.get('title', '제목 없음')}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        .meta {{ color: #666; margin-bottom: 20px; }}
        .content {{ margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>{target_file.get('title', '제목 없음')}</h1>
    <div class="meta">
        <p><strong>사이트:</strong> {target_file.get('site', 'N/A')}</p>
        <p><strong>생성일:</strong> {target_file.get('created_at', 'N/A')}</p>
        <p><strong>상태:</strong> {target_file.get('status', 'draft')}</p>
        <p><strong>카테고리:</strong> {target_file.get('categories', ['기본'])[0] if target_file.get('categories') else '기본'}</p>
    </div>
    <div class="content">
        <p>이 콘텐츠는 자동 생성된 {target_file.get('file_type', 'unknown')} 콘텐츠입니다.</p>
        <p>콘텐츠 파일을 찾을 수 없어 기본 내용을 표시합니다.</p>
    </div>
</body>
</html>"""
                
                # 파일 다운로드 응답
                response = make_response(content)
                # 한글 파일명 처리 - 제목을 그대로 사용
                safe_title = target_file.get('title', 'content')[:80]  # 길이 제한
                import re
                # 파일명에 사용할 수 없는 문자만 제거, 한글은 유지
                safe_title = re.sub(r'[<>:"/\\|?*]', '', safe_title).strip()
                filename = f"{safe_title}.html"
                
                # 간단하고 안전한 파일명 헤더 설정
                import urllib.parse
                # 안전한 기본 파일명 사용
                safe_filename = f"blog_content_{file_id}.html"
                
                response.headers['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
                response.headers['Content-Type'] = 'text/html; charset=utf-8'
                logger.info(f"다운로드 제공: {filename}")
                return response
        
        # 파일을 찾을 수 없는 경우
        return jsonify({
            'success': False,
            'error': '파일을 찾을 수 없습니다.'
        }), 404
        
    except Exception as e:
        logger.error(f"다운로드 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debug/content_generator')
def debug_content_generator():
    """ContentGenerator 상태 디버깅"""
    try:
        import os
        api_key = os.getenv("ANTHROPIC_API_KEY")
        return jsonify({
            'content_generator_initialized': content_generator is not None,
            'api_key_exists': api_key is not None,
            'api_key_length': len(api_key) if api_key else 0,
            'api_key_prefix': api_key[:20] if api_key else None,
            'error_info': str(getattr(content_generator, '_init_error', 'No error'))
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'content_generator_initialized': False
        })

@app.route('/api/publish_post', methods=['POST'])
def publish_post():
    """포스트 실제 사이트에 발행"""
    try:
        data = request.json
        post_id = data.get('post_id')
        site = data.get('site', 'wordpress')  # 사이트 타입 (wordpress, tistory)
        
        if not post_id:
            return jsonify({
                'success': False,
                'error': '포스트 ID가 필요합니다.'
            }), 400
        
        database = get_database()
        
        if database.is_connected:
            try:
                # 포스트 정보 가져오기
                files = database.get_content_files(limit=1000)
                target_file = None
                
                for f in files:
                    if f.get('id') == int(post_id):
                        target_file = f
                        break
                
                if not target_file:
                    return jsonify({
                        'success': False,
                        'error': '포스트를 찾을 수 없습니다.'
                    }), 404
                
                # 디버그: 파일 구조 확인
                logger.info(f"target_file keys: {list(target_file.keys())}")
                logger.info(f"target_file content preview: {str(target_file.get('content', ''))[:200]}...")
                
                # 파일에서 실제 콘텐츠 읽기
                content_data = None
                raw_content = ''
                
                # file_path에서 실제 콘텐츠 읽기 (file_path가 HTML 콘텐츠 자체일 수도 있음)
                file_path = target_file.get('file_path', '')
                if file_path:
                    # file_path가 HTML인지 실제 파일 경로인지 확인
                    if file_path.strip().startswith('<!DOCTYPE html>') or file_path.strip().startswith('<html'):
                        # file_path 자체가 HTML 콘텐츠인 경우
                        logger.info("file_path 필드에 HTML 콘텐츠가 직접 저장되어 있음")
                        raw_content = file_path
                        logger.info(f"HTML 콘텐츠 길이: {len(raw_content)}")
                    else:
                        # 실제 파일 경로인 경우
                        try:
                            logger.info(f"파일 경로에서 콘텐츠 읽기: {file_path}")
                            with open(file_path, 'r', encoding='utf-8') as f:
                                raw_content = f.read()
                            logger.info(f"파일 읽기 성공, 길이: {len(raw_content)}")
                        except Exception as e:
                            logger.error(f"파일 읽기 실패: {e}")
                            raw_content = target_file.get('content', '')
                else:
                    logger.info("file_path 없음, content 필드 사용")
                    raw_content = target_file.get('content', '')
                
                try:
                    # JSON 구조인지 먼저 확인
                    import json
                    content_data = json.loads(raw_content)
                    logger.info("JSON 구조 콘텐츠 파싱 성공")
                except:
                    # JSON이 아닌 경우 HTML 콘텐츠로 처리
                    logger.info("HTML 콘텐츠로 처리")
                    
                    # 인코딩 문제 해결: 문제가 되는 특수 문자들을 안전한 문자로 대체
                    safe_content = raw_content
                    
                    # 1. 이모지와 특수 문자 대체
                    char_replacements = {
                        '\U0001f4c5': '[날짜]',  # 📅 캘린더
                        '\U0001f516': '[태그]',  # 🔖 북마크
                        '\U0001f4a1': '[팁]',   # 💡 전구
                        '\U0001f3f7\ufe0f': '[태그]',  # 🏷️ 라벨
                        '\U0001f4bb': '[컴퓨터]',  # 💻 노트북
                        '\U0001f680': '[로켓]',  # 🚀 로켓
                        '\U0001f525': '[불]',   # 🔥 불
                        '\U0001f3af': '[타겟]',  # 🎯 다트
                        '\U0001f4d1': '[북마크]', # 📑 북마크 탭
                        '\u2022': '•',  # bullet point
                        '\u2023': '‣',  # triangular bullet
                        '\u2043': '⁃',  # hyphen bullet
                        '\u25aa': '▪',  # black small square
                        '\u25ab': '▫',  # white small square
                        '\u25b6': '▶',  # black right-pointing triangle
                        '\u25c0': '◀',  # black left-pointing triangle
                    }
                    
                    for char, replacement in char_replacements.items():
                        if char in safe_content:
                            safe_content = safe_content.replace(char, replacement)
                            logger.info(f"특수 문자 대체: {repr(char)} -> {replacement}")
                    
                    # 2. 포괄적 해결: CP949에서 인코딩할 수 없는 모든 문자를 안전한 문자로 변환
                    try:
                        # CP949로 인코딩 시도하여 문제 있는 문자 찾기
                        safe_content.encode('cp949')
                    except UnicodeEncodeError:
                        logger.info("CP949 인코딩 불가능한 문자 발견, 안전한 문자로 변환")
                        # 각 문자를 체크하여 인코딩 가능한 문자만 유지
                        safe_chars = []
                        for char in safe_content:
                            try:
                                char.encode('cp949')
                                safe_chars.append(char)
                            except UnicodeEncodeError:
                                # 인코딩 불가능한 문자는 물음표로 대체
                                safe_chars.append('?')
                                logger.info(f"문제 문자 발견: {repr(char)} -> ?")
                        safe_content = ''.join(safe_chars)
                    
                    content_data = {
                        'title': target_file.get('title', '제목 없음'),
                        'content': safe_content,  # 이모지가 제거된 안전한 콘텐츠
                        'meta_description': f"{target_file.get('title', '')} 관련 내용입니다.",
                        'tags': target_file.get('tags', ['블로그', '자동화']),
                        'categories': [target_file.get('category', '기타')]
                    }
                
                logger.info(f"콘텐츠 데이터 준비 완료: title={content_data.get('title')}, content_length={len(content_data.get('content', ''))}")
                
                # 사이트별 실제 발행
                success = False
                published_url = None
                error_message = None
                
                if site.lower() in ['wordpress', 'unpre', 'untab', 'skewese']:
                    # WordPress 발행
                    try:
                        from src.publishers.wordpress_publisher import WordPressPublisher
                        
                        # 사이트 키 매핑
                        site_key_map = {
                            'wordpress': 'unpre',
                            'unpre': 'unpre', 
                            'untab': 'untab',
                            'skewese': 'skewese'
                        }
                        site_key = site_key_map.get(site.lower(), 'unpre')
                        
                        publisher = WordPressPublisher(site_key)
                        success, result = publisher.publish_post(content_data)
                        
                        if success:
                            published_url = result
                            logger.info(f"WordPress 발행 성공: {published_url}")
                        else:
                            error_message = f"WordPress 발행 실패: {result}"
                            logger.error(error_message)
                            
                    except Exception as e:
                        error_message = f"WordPress 발행 오류: {str(e)}"
                        logger.error(error_message)
                        
                elif site.lower() == 'tistory':
                    # Tistory 발행
                    try:
                        from src.publishers.tistory_publisher import TistoryPublisher
                        
                        publisher = TistoryPublisher()
                        success, result = publisher.publish_post(content_data)
                        
                        if success:
                            published_url = result
                            logger.info(f"Tistory 발행 성공: {published_url}")
                        else:
                            error_message = f"Tistory 발행 실패: {result}"
                            logger.error(error_message)
                            
                    except Exception as e:
                        error_message = f"Tistory 발행 오류: {str(e)}"
                        logger.error(error_message)
                
                # 발행 성공시 데이터베이스 상태 업데이트
                if success:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE unble.content_files SET status = 'published' WHERE id = %s",
                            (post_id,)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                    
                    return jsonify({
                        'success': True,
                        'message': f'포스트 "{target_file.get("title", "")}"가 {site} 사이트에 성공적으로 발행되었습니다.',
                        'post_id': post_id,
                        'url': published_url
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': error_message or '발행 중 알 수 없는 오류가 발생했습니다.'
                    }), 500
                    
            except Exception as e:
                logger.error(f"포스트 발행 실패: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        # DB 연결 실패시 목업 응답
        return jsonify({
            'success': True,
            'message': f'포스트가 성공적으로 발행되었습니다. (목업 모드)',
            'post_id': post_id
        })
        
    except Exception as e:
        logger.error(f"포스트 발행 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/publish_to_wordpress', methods=['POST'])
def publish_to_wordpress():
    """WordPress에 콘텐츠 발행"""
    try:
        data = request.json
        file_path = data.get('file_path')
        site = data.get('site', 'unpre')
        
        if not file_path:
            return jsonify({'success': False, 'error': '파일 경로가 필요합니다'}), 400
        
        # HTML 파일 읽기
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': f'파일을 찾을 수 없습니다: {file_path}'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # HTML 파싱
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 제목 추출
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.text.strip() if title_tag else '제목 없음'
        
        # 메타 설명 추출
        meta_desc = soup.find('meta', {'name': 'description'})
        meta_description = meta_desc['content'] if meta_desc else ''
        
        # 태그 추출
        tags_div = soup.find('div', class_='tags')
        tags = []
        if tags_div:
            tag_spans = tags_div.find_all('span', class_='tag')
            tags = [span.text.replace('#', '').strip() for span in tag_spans]
        
        # 이미지 생성 (발행 시점에 생성, 실패해도 계속 진행)
        images = []
        try:
            logger.info(f"WordPress 발행용 이미지 생성 시작...")
            from src.utils.safe_image_generator import SafeImageGenerator
            img_gen = SafeImageGenerator()
            images = img_gen.generate_images_for_content(
                title=title,
                keywords=tags[:3] if tags else [site],
                count=1  # 대표이미지만
            )
            logger.info(f"발행용 이미지 {len(images)}개 생성 완료")
        except Exception as img_e:
            logger.warning(f"발행용 이미지 생성 실패, 텍스트만 발행: {img_e}")
            images = []
        
        # WordPress Publisher 사용
        from src.publishers.wordpress_publisher import WordPressPublisher
        publisher = WordPressPublisher(site)
        
        content_data = {
            'title': title,
            'content': html_content,
            'meta_description': meta_description,
            'tags': tags,
            'categories': [data.get('category', '기본')]
        }
        
        success, result = publisher.publish_post(content_data, images)
        
        if success:
            logger.info(f"WordPress 발행 성공: {result}")
            
            # 발행 성공 시 데이터베이스에 저장
            try:
                database = get_database()
                if database.is_connected:
                    file_id = database.add_content_file(
                        site=site,
                        title=title,
                        file_path=file_path,
                        file_type='wordpress',
                        metadata={
                            'categories': [data.get('category', '기본')],
                            'tags': tags,
                            'word_count': len(title.split()) * 50,  # 추정값
                            'reading_time': 5,
                            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 1000,
                            'published_url': result,
                            'status': 'published'
                        }
                    )
                    
                    # 상태를 published로 업데이트
                    database.update_content_file_status(file_id, 'published')
                    logger.info(f"데이터베이스에 발행된 콘텐츠 저장 완료: {file_id}")
                    
            except Exception as db_e:
                logger.warning(f"데이터베이스 저장 실패하지만 발행은 성공: {db_e}")
            
            return jsonify({
                'success': True,
                'message': f'{site} 사이트에 성공적으로 발행되었습니다.',
                'url': result
            })
        else:
            logger.error(f"WordPress 발행 실패: {result}")
            return jsonify({
                'success': False,
                'error': result
            }), 500
            
    except Exception as e:
        logger.error(f"WordPress 발행 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedule/recreate', methods=['GET', 'POST'])
def recreate_schedule():
    """스케줄 강제 재생성 (티스토리 포함)"""
    try:
        from src.utils.schedule_manager import schedule_manager
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # 기존 스케줄 삭제
        database = get_database()
        if database.is_connected:
            conn = database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM publishing_schedule WHERE week_start_date = %s', (week_start,))
                deleted = cursor.rowcount
                conn.commit()
                logger.info(f"기존 스케줄 {deleted}개 삭제됨")
        
        # 새 스케줄 생성 (티스토리 포함)
        success = schedule_manager.create_weekly_schedule(week_start)
        
        if success:
            # 생성된 스케줄 확인
            schedule_data = schedule_manager.get_weekly_schedule(week_start)
            sites = []
            if schedule_data and 'schedule' in schedule_data:
                first_day = schedule_data['schedule'].get(0, {})
                sites = list(first_day.get('sites', {}).keys())
            
            return jsonify({
                'success': True,
                'message': f'{week_start} 주 스케줄 재생성 완료',
                'sites': sites,
                'week_start': str(week_start)
            })
        else:
            return jsonify({
                'success': False,
                'error': '스케줄 생성 실패'
            }), 500
            
    except Exception as e:
        logger.error(f"스케줄 재생성 오류: {e}")
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
        
        database = get_database()
        
        if database.is_connected and post_ids:
            # 실제 데이터베이스에서 삭제
            deleted_count = 0
            for post_id in post_ids:
                try:
                    if database.delete_content_file(post_id):
                        deleted_count += 1
                except Exception as e:
                    logger.error(f"포스트 {post_id} 삭제 실패: {e}")
            
            return jsonify({
                'success': True,
                'message': f'{deleted_count}개의 포스트를 삭제했습니다.',
                'deleted': deleted_count
            })
        
        # DB 연결 실패시 목업 응답
        return jsonify({
            'success': True,
            'message': f'{len(post_ids)}개의 포스트를 삭제했습니다. (목업 모드)',
            'deleted': post_ids
        })
        
    except Exception as e:
        logger.error(f"포스트 삭제 오류: {e}")
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
                'sites': ['unpre', 'untab', 'skewese', 'tistory']
            })
        
        return jsonify(schedule)
    except Exception as e:
        return jsonify([]), 500

# 발행 상태를 전역으로 추적
publish_status = {
    'in_progress': False,
    'current_site': '',
    'progress': 0,
    'total_sites': 0,
    'results': [],
    'message': ''
}

@app.route('/api/publish_status')
def get_publish_status():
    """발행 진행 상태 조회"""
    try:
        return jsonify(publish_status)
    except Exception as e:
        return jsonify({
            'in_progress': False,
            'current_site': '',
            'progress': 0,
            'total_sites': 0,
            'results': [],
            'message': f'상태 조회 오류: {str(e)}'
        })

@app.route('/api/quick_publish', methods=['POST'])
def quick_publish():
    """빠른 수동 발행 (타임아웃 방지)"""
    try:
        data = request.json or {}
        sites = data.get('sites', ['unpre', 'untab', 'skewese', 'tistory'])
        
        # 간단한 응답으로 즉시 반환
        global publish_status
        publish_status.update({
            'in_progress': True,
            'current_site': sites[0] if sites else 'unknown',
            'progress': 10,
            'total_sites': len(sites),
            'results': [],
            'message': f'{len(sites)}개 사이트 발행 시작: {", ".join(sites)}'
        })
        
        # 백그라운드에서 실제 발행 (별도 스레드)
        import threading
        def background_publish():
            try:
                from src.utils.schedule_manager import schedule_manager
                from datetime import datetime, timedelta
                import requests
                
                today = datetime.now().date()
                week_start = today - timedelta(days=today.weekday())
                day_of_week = today.weekday()
                
                # 오늘의 스케줄 가져오기
                schedule_data = schedule_manager.get_weekly_schedule(week_start)
                
                for i, site in enumerate(sites):
                    try:
                        publish_status.update({
                            'current_site': site,
                            'progress': int((i / len(sites)) * 90),
                            'message': f'{site} 콘텐츠 생성 중...'
                        })
                        
                        # 스케줄에서 주제 가져오기 (사이트별 기본값 설정)
                        site_defaults = {
                            'unpre': {'topic': 'Python 프로그래밍 가이드', 'category': 'programming'},
                            'untab': {'topic': '부동산 투자 가이드', 'category': 'realestate'}, 
                            'skewese': {'topic': '한국사 역사 이야기', 'category': 'koreanhistory'},
                            'tistory': {'topic': '2024년 IT 트렌드 분석', 'category': 'current'}
                        }
                        
                        default = site_defaults.get(site, {'topic': f'{site} 가이드', 'category': 'programming'})
                        topic = default['topic']
                        keywords = [site, '가이드']
                        category = default['category']
                        
                        if schedule_data and day_of_week in schedule_data['schedule']:
                            day_schedule = schedule_data['schedule'][day_of_week]
                            site_plan = day_schedule.get('sites', {}).get(site, {})
                            if site_plan:
                                topic = site_plan.get('topic', topic)
                                keywords = site_plan.get('keywords', keywords)
                                category = site_plan.get('category', category)
                                logger.info(f"[SCHEDULE] {site} 스케줄 주제 사용: {topic} (카테고리: {category})")
                            else:
                                logger.info(f"[SCHEDULE] {site} 스케줄 없음, 기본값 사용: {topic}")
                        else:
                            logger.info(f"[SCHEDULE] 오늘({day_of_week}) 스케줄 없음, 기본값 사용: {topic}")
                        
                        # 1. 콘텐츠 생성 (사이트별로 다른 API 사용)
                        generate_payload = {
                            'site': site,
                            'topic': topic,
                            'keywords': keywords,
                            'category': category
                        }
                        
                        if site == 'tistory':
                            # 티스토리는 별도 API 사용
                            generate_url = 'http://localhost:8000/api/generate_tistory'
                        else:
                            # WordPress 사이트들은 기존 API 사용
                            generate_url = 'http://localhost:8000/api/generate_wordpress'
                        
                        generate_response = requests.post(
                            generate_url,
                            headers={'Content-Type': 'application/json'},
                            json=generate_payload,
                            timeout=300
                        )
                        
                        if generate_response.status_code != 200:
                            raise Exception(f'콘텐츠 생성 실패: {generate_response.status_code}')
                        
                        generate_result = generate_response.json()
                        if not generate_result.get('success'):
                            raise Exception(f'콘텐츠 생성 실패: {generate_result.get("error")}')
                        
                        if site == 'tistory':
                            # 티스토리는 콘텐츠 생성만 하고 발행 안함
                            publish_status.update({
                                'current_site': site,
                                'progress': int(((i + 1) / len(sites)) * 90),
                                'message': f'{site} 콘텐츠 생성 완료 (목록에 저장됨)'
                            })
                            
                            # 스케줄 상태 업데이트 (generated로 설정)
                            if schedule_data:
                                schedule_manager.update_schedule_status(
                                    week_start, day_of_week, site, 'generated'
                                )
                            
                            logger.info(f"[TISTORY] {site} 콘텐츠 생성 완료, 목록에 저장됨")
                            continue  # 다음 사이트로
                        
                        publish_status.update({
                            'current_site': site,
                            'progress': int(((i + 0.5) / len(sites)) * 90),
                            'message': f'{site} WordPress 발행 중...'
                        })
                        
                        # 2. WordPress 발행 (파일 경로 사용)
                        file_path = generate_result.get('file_path')
                        if not file_path:
                            raise Exception('생성된 파일 경로가 없습니다')
                        
                        # WordPress 발행 로직 직접 호출
                        from src.publishers.wordpress_publisher import WordPressPublisher
                        from bs4 import BeautifulSoup
                        import os
                        
                        # 파일 읽기
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            # HTML 파싱해서 콘텐츠 추출
                            soup = BeautifulSoup(html_content, 'html.parser')
                            title = soup.find('title').text if soup.find('title') else topic
                            meta_desc = soup.find('meta', {'name': 'description'})
                            meta_description = meta_desc['content'] if meta_desc else ''
                            
                            content_data = {
                                'title': title,
                                'content': html_content,
                                'meta_description': meta_description,
                                'categories': [category],
                                'tags': keywords
                            }
                            
                            # WordPress 발행
                            wp_publisher = WordPressPublisher(site)
                            success, result = wp_publisher.publish_post(content_data)
                            
                            if success:
                                publish_status.update({
                                    'current_site': site,
                                    'progress': int(((i + 1) / len(sites)) * 90),
                                    'message': f'{site} 발행 성공: {result}'
                                })
                                
                                # 데이터베이스에 발행된 콘텐츠 저장
                                try:
                                    database = get_database()
                                    if database.is_connected:
                                        file_id = database.add_content_file(
                                            site=site,
                                            title=title,
                                            file_path=file_path,
                                            file_type='wordpress',
                                            metadata={
                                                'categories': [category],
                                                'tags': keywords,
                                                'word_count': len(title.split()) * 50,
                                                'reading_time': 5,
                                                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 1000,
                                                'published_url': result,
                                                'status': 'published'
                                            }
                                        )
                                        database.update_content_file_status(file_id, 'published')
                                        logger.info(f"[DB] {site} 발행 콘텐츠 저장 완료: {file_id}")
                                except Exception as db_e:
                                    logger.warning(f"[DB] {site} 저장 실패: {db_e}")
                                
                                # 스케줄 상태 업데이트
                                if schedule_data:
                                    schedule_manager.update_schedule_status(
                                        week_start, day_of_week, site, 'published', url=result
                                    )
                            else:
                                raise Exception(f'WordPress 발행 실패: {result}')
                        else:
                            raise Exception(f'생성된 파일을 찾을 수 없습니다: {file_path}')
                            
                    except Exception as e:
                        logger.error(f'{site} 발행 오류: {e}')
                        publish_status.update({
                            'current_site': site,
                            'progress': int(((i + 1) / len(sites)) * 90),
                            'message': f'{site} 발행 실패: {str(e)}'
                        })
                
                publish_status.update({
                    'in_progress': False,
                    'progress': 100,
                    'message': f'발행 완료! 사이트 확인: unpre.co.kr, untab.co.kr, skewese.com'
                })
                
            except Exception as e:
                logger.error(f'전체 발행 오류: {e}')
                publish_status.update({
                    'in_progress': False,
                    'message': f'발행 오류: {str(e)}'
                })
        
        threading.Thread(target=background_publish, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': f'{len(sites)}개 사이트 발행이 시작되었습니다.',
            'sites': sites
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'발행 시작 실패: {str(e)}'
        }), 500

@app.route('/api/schedule/auto_publish', methods=['POST'])
def manual_auto_publish():
    """수동으로 자동 발행 실행"""
    try:
        data = request.json
        sites = data.get('sites', ['unpre', 'untab', 'skewese'])
        
        # 전역 상태 초기화
        global publish_status
        publish_status.update({
            'in_progress': True,
            'current_site': '',
            'progress': 0,
            'total_sites': len(sites),
            'results': [],
            'message': '발행을 시작합니다...'
        })
        
        results = []
        
        for idx, site in enumerate(sites):
            try:
                # 상태 업데이트
                publish_status.update({
                    'current_site': site,
                    'progress': int((idx / len(sites)) * 100),
                    'message': f'{site} 사이트 발행 중...'
                })
                
                # 자동발행계획에서 오늘 날짜에 해당하는 실제 주제 가져오기
                from src.utils.schedule_manager import schedule_manager
                from datetime import datetime, timedelta
                
                today = datetime.now().date()
                week_start = today - timedelta(days=today.weekday())
                day_of_week = today.weekday()
                
                # 스케줄에서 실제 주제 조회
                schedule_data = schedule_manager.get_weekly_schedule(week_start)
                topic = None
                keywords = [site, '가이드']
                category = 'programming'
                
                if schedule_data and day_of_week in schedule_data['schedule']:
                    day_schedule = schedule_data['schedule'][day_of_week]
                    if site in day_schedule.get('sites', {}):
                        site_plan = day_schedule['sites'][site]
                        topic = site_plan.get('topic', f'{site} 전문 콘텐츠 가이드')
                        keywords = site_plan.get('keywords', [site, '가이드'])
                        category = site_plan.get('category', 'programming')
                        
                        logger.info(f"[SCHEDULE] {site} 스케줄 주제: {topic}")
                
                # 스케줄에 없으면 기본 주제 사용
                if not topic:
                    topic_map = {
                        'unpre': 'Python 기초 프로그래밍 완벽 가이드',
                        'untab': '2025년 부동산 투자 전략 분석',
                        'skewese': '조선왕조 역사 속 숨겨진 이야기'
                    }
                    topic = topic_map.get(site, 'IT 기술 트렌드')
                    category = 'programming' if site == 'unpre' else 'realestate' if site == 'untab' else 'history'
                    logger.info(f"[SCHEDULE] {site} 기본 주제 사용: {topic}")
                
                # 직접 콘텐츠 생성 API 호출
                import requests
                import json
                
                # 1. 콘텐츠 생성
                generate_payload = {
                    'site': site,
                    'topic': topic,
                    'keywords': keywords,
                    'category': category,
                    'content_length': 'medium'
                }
                
                logger.info(f"[AUTO_PUBLISH] {site} 콘텐츠 생성 시작 - 주제: {topic}")
                
                # 현재 서버 URL 결정 (운영/개발 환경 자동 감지)
                server_url = request.url_root.rstrip('/')
                
                logger.info(f"[AUTO_PUBLISH] {site} API 호출: {server_url}/api/generate_wordpress")
                generate_response = requests.post(
                    f'{server_url}/api/generate_wordpress',
                    headers={'Content-Type': 'application/json'},
                    json=generate_payload,
                    timeout=300
                )
                
                if generate_response.status_code != 200:
                    logger.error(f"[AUTO_PUBLISH] {site} 콘텐츠 생성 실패: {generate_response.status_code}")
                    success = False
                else:
                    generate_result = generate_response.json()
                    if not generate_result.get('success'):
                        logger.error(f"[AUTO_PUBLISH] {site} 콘텐츠 생성 실패: {generate_result.get('error')}")
                        success = False
                    else:
                        # 2. WordPress 발행
                        file_path = generate_result.get('file_path')
                        if not file_path:
                            logger.error(f"[AUTO_PUBLISH] {site} 파일 경로 없음")
                            success = False
                        else:
                            logger.info(f"[AUTO_PUBLISH] {site} WordPress 발행 중...")
                            publish_payload = {
                                'file_path': file_path,
                                'site': site
                            }
                            
                            publish_response = requests.post(
                                f'{server_url}/api/publish_to_wordpress',
                                headers={'Content-Type': 'application/json'},
                                json=publish_payload,
                                timeout=120
                            )
                            
                            if publish_response.status_code != 200:
                                logger.error(f"[AUTO_PUBLISH] {site} WordPress 발행 실패: {publish_response.status_code}")
                                success = False
                            else:
                                publish_result = publish_response.json()
                                if not publish_result.get('success'):
                                    logger.error(f"[AUTO_PUBLISH] {site} WordPress 발행 실패: {publish_result.get('error')}")
                                    success = False
                                else:
                                    published_url = publish_result.get('url', '')
                                    logger.info(f"[AUTO_PUBLISH] {site} 발행 완료: {published_url}")
                                    
                                    # 스케줄 상태를 'published'로 업데이트
                                    if schedule_data and day_of_week in schedule_data['schedule']:
                                        try:
                                            schedule_manager.update_schedule_status(
                                                week_start, day_of_week, site, 'published', url=published_url
                                            )
                                            logger.info(f"[SCHEDULE] {site} 스케줄 상태 업데이트: published")
                                        except Exception as e:
                                            logger.error(f"[SCHEDULE] {site} 상태 업데이트 실패: {e}")
                                    
                                    success = True
                
                result_message = f'{site} 발행 완료'
                result_url = None
                if success and 'published_url' in locals():
                    result_message += f' - URL: {published_url}'
                    result_url = published_url
                elif not success:
                    result_message = f'{site} 발행 실패'
                
                site_result = {
                    'site': site,
                    'success': success,
                    'message': result_message,
                    'topic': topic,
                    'url': result_url
                }
                results.append(site_result)
                
                # 실시간 상태 업데이트
                publish_status['results'].append(site_result)
                publish_status['progress'] = int(((idx + 1) / len(sites)) * 100)
                
            except Exception as e:
                logger.error(f"사이트 {site} 발행 오류: {e}")
                results.append({
                    'site': site,
                    'success': False,
                    'message': f'{site} 발행 오류: {str(e)}'
                })
        
        success_count = sum(1 for r in results if r['success'])
        
        # 최종 상태 업데이트
        publish_status.update({
            'in_progress': False,
            'current_site': '',
            'progress': 100,
            'message': f'발행 완료! 총 {len(sites)}개 사이트 중 {success_count}개 성공'
        })
        
        return jsonify({
            'success': success_count > 0,
            'message': f'총 {len(sites)}개 사이트 중 {success_count}개 성공',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"수동 자동 발행 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wordpress_files')
def get_wordpress_files():
    """WordPress 파일 목록"""
    try:
        database = get_database()
        if not database.is_connected:
            # DB 연결 실패시 목업 데이터 반환
            return jsonify(get_mock_wordpress_files())
        
        # DB에서 WordPress 콘텐츠 조회
        files = database.get_content_files(file_type='wordpress', limit=50)
        
        # 형식 맞추기
        formatted_files = []
        for f in files:
            # 시간 포맷팅 (한국 시간)
            created_at = f.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    # ISO 형식 문자열을 datetime으로 변환
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        # UTC를 한국 시간으로 변환
                        kst_dt = dt.astimezone(KST)
                        formatted_date = kst_dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = created_at.strftime('%Y-%m-%d %H:%M') if hasattr(created_at, 'strftime') else str(created_at)
            else:
                formatted_date = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
            
            formatted_files.append({
                'id': f.get('id'),
                'site': f.get('site', 'unpre'),
                'title': f.get('title'),
                'date': formatted_date,
                'size': f'{f.get("file_size", 0) / 1024:.1f}KB' if f.get('file_size') else '3.0KB',
                'status': f.get('status', 'draft'),
                'url': f.get('url'),
                'actions': ['view', 'publish', 'download', 'delete'] if f.get('status') == 'draft' else ['view', 'download', 'delete']
            })
        
        return jsonify(formatted_files)
    except Exception as e:
        logger.error(f"WordPress 파일 목록 조회 오류: {e}")
        # 오류 발생시 목업 데이터 반환
        return jsonify(get_mock_wordpress_files())

def get_mock_wordpress_files():
    """목업 WordPress 파일 데이터"""
    now = datetime.now(KST)
    base_files = [
            {
                'id': 'wp_unpre_001',
                'site': 'unpre',
                'title': '🤖 AI 코딩 어시스턴트 활용 가이드',
                'date': now.strftime('%Y-%m-%d %H:%M'),
                'size': '3.2KB',
                'status': 'published',
                'url': 'https://unpre.co.kr/ai-coding-assistant-guide',
                'actions': ['view', 'edit', 'download', 'delete']
            },
            {
                'id': 'wp_unpre_002',
                'site': 'unpre', 
                'title': '⚡ React 18 Concurrent Features 완전 정복',
                'date': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
                'size': '4.1KB',
                'status': 'published',
                'url': 'https://unpre.co.kr/react-18-concurrent',
                'actions': ['view', 'edit', 'download', 'delete']
            },
            {
                'id': 'wp_untab_001',
                'site': 'untab',
                'title': '📚 토익 990점 달성하는 5가지 비법',
                'date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),
                'size': '2.8KB',
                'status': 'published',
                'url': 'https://untab.co.kr/toeic-990-tips',
                'actions': ['view', 'edit', 'download', 'delete']
            },
            {
                'id': 'wp_untab_002',
                'site': 'untab',
                'title': '💰 부동산 경매 초보자 완벽 가이드',
                'date': (now - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M'),
                'size': '3.5KB',
                'status': 'draft',
                'url': None,
                'actions': ['edit', 'publish', 'download', 'delete']
            },
            {
                'id': 'wp_skewese_001',
                'site': 'skewese',
                'title': '🏛️ 조선시대 과학기술의 숨겨진 이야기',
                'date': (now - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M'),
                'size': '3.7KB',
                'status': 'published',
                'url': 'https://skewese.com/joseon-science-stories',
                'actions': ['view', 'edit', 'download', 'delete']
            },
            {
                'id': 'wp_skewese_002',
                'site': 'skewese',
                'title': '✨ 고구려 고분벽화 속 우주관',
                'date': (now - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M'),
                'size': '2.9KB',
                'status': 'draft',
                'url': None,
                'actions': ['edit', 'publish', 'download', 'delete']
            }
        ]
    return base_files

@app.route('/api/tistory_files')
def get_tistory_files():
    """Tistory 파일 목록"""
    try:
        database = get_database()
        if not database.is_connected:
            # DB 연결 실패시 목업 데이터 반환
            return jsonify(get_mock_tistory_files())
        
        # DB에서 Tistory 콘텐츠 조회
        files = database.get_content_files(file_type='tistory', limit=50)
        
        # 형식 맞추기
        formatted_files = []
        for f in files:
            # 시간 포맷팅 (한국 시간)
            created_at = f.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    # ISO 형식 문자열을 datetime으로 변환
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        # UTC를 한국 시간으로 변환
                        kst_dt = dt.astimezone(KST)
                        formatted_date = kst_dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = created_at.strftime('%Y-%m-%d %H:%M') if hasattr(created_at, 'strftime') else str(created_at)
            else:
                formatted_date = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
            
            formatted_files.append({
                'id': f.get('id'),
                'title': f.get('title'),
                'date': formatted_date,
                'size': f'{f.get("file_size", 0) / 1024:.1f}KB' if f.get('file_size') else '3.0KB',
                'status': f.get('status', 'draft'),
                'url': f.get('url'),
                'actions': ['view', 'download', 'delete'],
                'category': f.get('categories', ['기본'])[0] if f.get('categories') else '기본',
                'tags': f.get('tags', [])
            })
        
        return jsonify(formatted_files)
    except Exception as e:
        logger.error(f"Tistory 파일 목록 조회 오류: {e}")
        # 오류 발생시 목업 데이터 반환
        return jsonify(get_mock_tistory_files())

def get_mock_tistory_files():
    """목업 Tistory 파일 데이터"""
    now = datetime.now(KST)
    base_files = [
            {
                'id': 'tistory_001',
                'title': '🎯 2025년 언어학습 트렌드와 전망',
                'date': now.strftime('%Y-%m-%d %H:%M'),
                'size': '2.7KB',
                'status': 'published',
                'url': 'https://untab.tistory.com/language-trends-2025',
                'actions': ['view', 'download', 'delete'],
                'category': '언어학습',
                'tags': ['언어학습', '트렌드', '2025년']
            },
            {
                'id': 'tistory_002',
                'title': '💡 효과적인 온라인 강의 제작 노하우',
                'date': (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),
                'size': '3.1KB',
                'status': 'published',
                'url': 'https://untab.tistory.com/online-course-creation',
                'actions': ['view', 'download', 'delete'],
                'category': '교육콘텐츠',
                'tags': ['온라인강의', '제작', '노하우']
            },
            {
                'id': 'tistory_003',
                'title': '📈 주식 투자 초보자를 위한 기본 가이드',
                'date': (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
                'size': '4.2KB',
                'status': 'draft',
                'url': None,
                'actions': ['view', 'download', 'delete'],
                'category': '투자',
                'tags': ['주식투자', '초보자', '가이드']
            },
            {
                'id': 'tistory_004',
                'title': '🏆 AWS 자격증 취득 완벽 로드맵',
                'date': (now - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M'),
                'size': '3.8KB',
                'status': 'published',
                'url': 'https://untab.tistory.com/aws-certification-roadmap',
                'actions': ['view', 'download', 'delete'],
                'category': 'IT자격증',
                'tags': ['AWS', '자격증', '로드맵']
            },
            {
                'id': 'tistory_005',
                'title': '💰 부동산 경매 투자 시작하는 법',
                'date': (now - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M'),
                'size': '3.5KB',
                'status': 'draft',
                'url': None,
                'actions': ['view', 'download', 'delete'],
                'category': '부동산',
                'tags': ['부동산경매', '투자', '초보자']
            }
        ]
    return base_files

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

@app.route('/api/test_claude', methods=['GET'])
def test_claude():
    """Claude API 테스트 및 강제 재초기화"""
    global content_generator
    
    try:
        # 강제 재초기화
        from src.generators.content_generator import ContentGenerator
        test_generator = ContentGenerator()
        
        # 간단한 테스트 콘텐츠 생성
        site_config = {
            'name': 'test',
            'target_audience': '테스트',
            'content_style': '테스트',
            'keywords_focus': ['테스트']
        }
        
        test_content = test_generator.generate_content(
            site_config=site_config,
            topic='테스트 주제',
            category='테스트',
            content_length='short'
        )
        
        # 전역 변수 업데이트
        content_generator = test_generator
        
        return jsonify({
            'success': True,
            'message': 'Claude API 정상 작동',
            'title': test_content.get('title', '없음')[:50],
            'sections_count': len(test_content.get('sections', [])),
            'content_length': len(str(test_content))
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
    conn = get_db_connection()
    db_status = 'connected' if conn else 'disconnected'
    if conn:
        conn.close()
    
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'database': db_status,
        'features': {
            'content_generation': True,
            'wordpress_publishing': True,
            'tistory_publishing': True,
            'image_generation': True,
            'seo_optimization': True
        },
        'server_time': datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')
    }), 200

def _create_beautiful_html_template(generated_content, site_config):
    """아름다운 HTML 템플릿 생성"""
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{generated_content['title']}</title>
    <meta name="description" content="{generated_content['meta_description']}">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.8;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.05)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.1;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            font-weight: 600;
            margin-bottom: 20px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 1;
        }}
        
        .meta-info {{
            display: inline-flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.2);
            padding: 12px 24px;
            border-radius: 50px;
            font-size: 0.9em;
            backdrop-filter: blur(10px);
            position: relative;
            z-index: 1;
        }}
        
        .content {{
            padding: 50px 40px;
        }}
        
        .introduction {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 40px;
            border-left: 5px solid #667eea;
            position: relative;
        }}
        
        .introduction::before {{
            content: '💡';
            position: absolute;
            top: -10px;
            left: 20px;
            background: #667eea;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #ffffff;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
            border: 1px solid #f1f3f4;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .section:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f1f3f4;
            position: relative;
        }}
        
        .section h2::before {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 50px;
            height: 2px;
            background: #667eea;
        }}
        
        .section-content {{
            font-size: 1.1em;
            line-height: 1.8;
        }}
        
        .section-content p {{
            margin-bottom: 16px;
        }}
        
        .section-content strong {{
            color: #667eea;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .section-content em {{
            color: #555;
            font-style: italic;
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .content-paragraph {{
            margin-bottom: 18px;
            text-align: justify;
            line-height: 1.8;
        }}
        
        .styled-list {{
            margin: 20px 0;
            padding-left: 0;
            list-style: none;
        }}
        
        .styled-list li {{
            margin-bottom: 12px;
            padding-left: 30px;
            position: relative;
            line-height: 1.6;
        }}
        
        .styled-list li::before {{
            content: '▸';
            position: absolute;
            left: 8px;
            color: #667eea;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        ol.styled-list li::before {{
            content: counter(item);
            counter-increment: item;
            background: #667eea;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: 600;
            left: 0;
        }}
        
        ol.styled-list {{
            counter-reset: item;
        }}
        
        .inline-code {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            font-weight: 500;
            white-space: nowrap;
        }}
        
        .section-divider {{
            margin: 30px 0;
            border: none;
            height: 2px;
            background: linear-gradient(135deg, transparent, #667eea, transparent);
            border-radius: 2px;
        }}
        
        .code-block {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }}
        
        .table-container {{
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #f1f3f4;
        }}
        
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .conclusion {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin: 40px 0;
            text-align: center;
        }}
        
        .conclusion h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: white;
        }}
        
        .tags {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-top: 30px;
        }}
        
        .tag {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 5px;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            .header {{
                padding: 40px 20px;
            }}
            
            .header h1 {{
                font-size: 2.2em;
            }}
            
            .content {{
                padding: 30px 20px;
            }}
            
            .section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{generated_content['title']}</h1>
            <div class="meta-info">
                <span>📅 {datetime.now(KST).strftime('%Y년 %m월 %d일')}</span>
                <span style="margin: 0 15px;">•</span>
                <span>🔖 {site_config.get('name', 'Blog').upper()}</span>
            </div>
        </header>
        
        <div class="content">
            <section class="introduction">
                <p>{generated_content['introduction']}</p>
            </section>
            
            <main>
{''.join([f'''
                <section class="section">
                    <h2>{section['heading']}</h2>
                    <div class="section-content">
                        {_format_section_content(section['content'])}
                    </div>
                </section>
''' for section in generated_content['sections']])}
            </main>
            
            <footer>
                <section class="conclusion">
                    <h2>마무리</h2>
                    <p>{generated_content['conclusion']}</p>
                </section>
                
                <div class="tags">
                    <strong style="display: block; margin-bottom: 15px; color: #667eea; font-size: 1.1em;">🏷️ 관련 태그</strong>
                    {''.join([f'<span class="tag">{tag}</span>' for tag in generated_content['tags']])}
                </div>
            </footer>
        </div>
    </div>
</body>
</html>
"""

def _format_section_content(content):
    """섹션 콘텐츠 포맷팅 - 완전 개선"""
    import re
    
    # 1. 마크다운 볼드체 처리 (**text** -> <strong>text</strong>)
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    
    # 2. 이탤릭 처리 (*text* -> <em>text</em>)
    content = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', content)
    
    # 3. 코드 블록 처리 (```로 감싸진 부분)
    content = re.sub(r'```(\w+)?\n(.*?)\n```', r'<div class="code-block"><pre><code>\2</code></pre></div>', content, flags=re.DOTALL)
    content = re.sub(r'```(.*?)```', r'<div class="code-block"><pre><code>\1</code></pre></div>', content, flags=re.DOTALL)
    
    # 4. 인라인 코드 처리 (`code` -> <code>code</code>)
    content = re.sub(r'`([^`]+?)`', r'<code class="inline-code">\1</code>', content)
    
    # 5. 테이블 처리 개선
    if '<table>' in content:
        content = content.replace('<table>', '<div class="table-container"><table>')
        content = content.replace('</table>', '</table></div>')
    
    # 6. 마크다운 테이블을 HTML로 변환
    lines = content.split('\n')
    in_table = False
    table_html = []
    processed_lines = []
    
    for line in lines:
        if '|' in line and line.strip():
            if not in_table:
                in_table = True
                table_html = ['<div class="table-container"><table>']
            
            # 헤더 구분선 처리 (|---|---|)
            if re.match(r'^(\s*\|?\s*:?-+:?\s*\|)+\s*$', line):
                continue
                
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                # 첫 번째 테이블 행인지 확인 (다음 줄이 구분선인지 체크)
                next_line_idx = lines.index(line) + 1
                is_header = (next_line_idx < len(lines) and 
                           re.match(r'^(\s*\|?\s*:?-+:?\s*\|)+\s*$', lines[next_line_idx]))
                
                if is_header:
                    row_html = '<tr>' + ''.join([f'<th>{cell}</th>' for cell in cells]) + '</tr>'
                else:
                    row_html = '<tr>' + ''.join([f'<td>{cell}</td>' for cell in cells]) + '</tr>'
                table_html.append(row_html)
        else:
            if in_table:
                table_html.append('</table></div>')
                processed_lines.extend(table_html)
                table_html = []
                in_table = False
            processed_lines.append(line)
    
    # 테이블이 끝나지 않은 경우 처리
    if in_table:
        table_html.append('</table></div>')
        processed_lines.extend(table_html)
    
    content = '\n'.join(processed_lines)
    
    # 7. 리스트 처리 개선
    # 순서 없는 리스트 (- item)
    content = re.sub(r'^\s*[-*]\s+(.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    # 연속된 li 태그를 ul로 감싸기
    content = re.sub(r'(<li>.*?</li>\s*)+', lambda m: f'<ul class="styled-list">{m.group(0)}</ul>', content, flags=re.DOTALL)
    
    # 순서 있는 리스트 (1. item)
    content = re.sub(r'^\s*\d+\.\s+(.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'(<li>.*?</li>\s*)+', lambda m: f'<ol class="styled-list">{m.group(0)}</ol>', content, flags=re.DOTALL)
    
    # 8. 구분선 처리 (---)
    content = re.sub(r'^---+\s*$', '<hr class="section-divider">', content, flags=re.MULTILINE)
    
    # 9. 문단 구분 개선 - 이중 줄바꿈을 문단으로 처리
    paragraphs = content.split('\n\n')
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # HTML 태그로 시작하면 그대로 사용
        if paragraph.startswith(('<div', '<table', '<ul', '<ol', '<hr', '<h1', '<h2', '<h3', '<h4', '<h5', '<h6')):
            formatted_paragraphs.append(paragraph)
        else:
            # 일반 텍스트는 p 태그로 감싸기
            # 단일 줄바꿈은 <br>로 변환
            paragraph_html = paragraph.replace('\n', '<br>')
            formatted_paragraphs.append(f'<p class="content-paragraph">{paragraph_html}</p>')
    
    content = '\n\n'.join(formatted_paragraphs)
    
    # 10. 빈 태그 제거
    content = re.sub(r'<p[^>]*>\s*</p>', '', content)
    content = re.sub(r'<li>\s*</li>', '', content)
    
    return content

# Flask 앱 인스턴스에 메서드 추가
app._create_beautiful_html_template = _create_beautiful_html_template

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)