"""
Koyeb 배포용 웹 서버 앱
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file, make_response
from flask_cors import CORS
from datetime import datetime, timedelta, date, timezone
import pytz
import json
import logging
import logging.handlers
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import threading

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

# 환경변수 로드
load_dotenv()

# PostgreSQL 데이터베이스 import
from src.utils.postgresql_database import PostgreSQLDatabase
from src.utils.schedule_manager import ScheduleManager
from src.utils.api_tracker import api_tracker

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
# 로깅 설정 강화 - 파일과 콘솔 동시 출력
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blog_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 인메모리 로그 저장소
_memory_logs = []

def add_system_log(level: str, message: str, category: str = 'SYSTEM'):
    """시스템 로그 추가"""
    global _memory_logs
    
    log_entry = {
        'time': datetime.now().strftime('%H:%M:%S'),
        'level': level.lower(),
        'message': f"[{category}] {message}",
        'timestamp': datetime.now().timestamp()
    }
    
    _memory_logs.append(log_entry)
    
    # 최근 200개만 유지
    if len(_memory_logs) > 200:
        _memory_logs = _memory_logs[-200:]
    
    # 실제 로그도 기록
    if level.upper() == 'ERROR':
        logger.error(f"[{category}] {message}")
    elif level.upper() == 'WARNING':
        logger.warning(f"[{category}] {message}")
    else:
        logger.info(f"[{category}] {message}")

def get_recent_logs():
    """최근 로그 가져오기"""
    global _memory_logs
    return _memory_logs.copy()

# AI 콘텐츠 생성기 초기화
try:
    from src.generators.content_generator import ContentGenerator
    content_generator = ContentGenerator()
    logger.info("✅ Claude API 콘텐츠 생성기 초기화 완료 - v2.0")
    add_system_log('INFO', 'Claude API 콘텐츠 생성기 초기화 완료', 'STARTUP')
except Exception as e:
    logger.warning(f"⚠️ Claude API 초기화 실패: {e}")
    add_system_log('ERROR', f'Claude API 초기화 실패: {e}', 'STARTUP')
    content_generator = None

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# PostgreSQL 데이터베이스 인스턴스 (전역)
db = None
schedule_manager = None

def get_database():
    """데이터베이스 인스턴스 반환"""
    global db
    if db is None:
        db = PostgreSQLDatabase()
    return db

def get_schedule_manager():
    """스케줄 매니저 인스턴스 반환"""
    global schedule_manager
    if schedule_manager is None:
        schedule_manager = ScheduleManager()
    return schedule_manager

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
            },
            {
                'id': 4,
                'title': '📊 2025년 AI 시장 전망과 투자 트렌드',
                'site': 'tistory',
                'category': '트렌드/이슈',
                'url': None,  # 발행되지 않음
                'created_at': today_3am.strftime('%Y-%m-%d %H:%M:%S'),
                'published': False,
                'note': '생성됨 (수동 발행 필요)'
            }
        ])
    
    # 어제 발행된 포스트들
    yesterday_3am = today_3am - timedelta(days=1)
    posts.extend([
        {
            'id': 5,
            'title': 'React 18의 새로운 기능들',
            'site': 'unpre',
            'category': '프로그래밍',
            'url': 'https://unpre.co.kr/react-18-features',
            'created_at': yesterday_3am.strftime('%Y-%m-%d %H:%M:%S'),
            'published': True
        },
        {
            'id': 6,
            'title': '부동산 투자 전략 가이드',
            'site': 'untab',
            'category': '부동산',
            'url': 'https://untab.co.kr/real-estate-investment',
            'created_at': yesterday_3am.strftime('%Y-%m-%d %H:%M:%S'),
            'published': True
        },
        {
            'id': 7,
            'title': '🔥 MZ세대 소비 트렌드 변화 분석',
            'site': 'tistory',
            'category': '사회/트렌드',
            'url': None,
            'created_at': yesterday_3am.strftime('%Y-%m-%d %H:%M:%S'),
            'published': False,
            'note': '생성됨 (수동 발행 필요)'
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
    """메인 대시보드 페이지 (새로 개편됨)"""
    response = make_response(render_template('dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/old')
def old_dashboard():
    """기존 복잡한 대시보드 (백업용)"""
    response = make_response(render_template('dashboard_backup.html'))
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
            # WordPress 사이트들 + 티스토리 포함
            all_sites = ['unpre', 'untab', 'skewese', 'tistory']
            
            for site in all_sites:
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
                    
                    # 티스토리 콘텐츠는 특별 표시
                    if site == 'tistory' and site_posts:
                        for post in site_posts:
                            post['note'] = '생성됨 (수동 발행 필요)'
                            post['published'] = False  # 티스토리는 항상 발행되지 않은 상태
                    
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
    """트렌딩 토픽 조회 - 주간 업데이트"""
    try:
        from datetime import datetime, timedelta
        
        # 현재 주차 계산
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_number = week_start.isocalendar()[1]  # ISO 주차
        
        # 주차별 동적 트렌딩 생성
        trending_generator = WeeklyTrendingGenerator()
        
        if period == 'current':
            trends = trending_generator.generate_current_week_trends(week_start, week_number)
        elif period == 'next':
            next_week_start = week_start + timedelta(days=7)
            next_week_number = next_week_start.isocalendar()[1]
            trends = trending_generator.generate_next_week_trends(next_week_start, next_week_number)
        else:
            trends = trending_generator.generate_current_week_trends(week_start, week_number)
        
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

class WeeklyTrendingGenerator:
    """주간 트렌딩 토픽 생성기"""
    
    def __init__(self):
        # 2025년 주요 이슈들 (주차별로 다양하게 구성)
        self.global_trending_pool = [
            # AI & 기술
            {'title': 'ChatGPT-5 출시 임박', 'category': 'AI/Tech', 'keywords': ['ChatGPT', 'AI', '인공지능', 'OpenAI']},
            {'title': 'Apple Vision Pro 2세대 발표', 'category': 'Tech', 'keywords': ['Apple', 'VisionPro', '가상현실', 'AR']},
            {'title': '테슬라 자율주행 완전 상용화', 'category': 'Tech', 'keywords': ['Tesla', '자율주행', 'FSD', '전기차']},
            {'title': '구글 Gemini Ultra 업그레이드', 'category': 'AI', 'keywords': ['Google', 'Gemini', 'AI', '멀티모달']},
            {'title': 'NVIDIA RTX 5090 출시', 'category': 'Hardware', 'keywords': ['NVIDIA', 'RTX', 'GPU', '게이밍']},
            {'title': '메타 Quest 4 공개', 'category': 'VR/AR', 'keywords': ['Meta', 'Quest', 'VR', '메타버스']},
            {'title': '삼성 갤럭시 S25 AI 기능 강화', 'category': 'Mobile', 'keywords': ['Samsung', 'Galaxy', 'AI', '스마트폰']},
            {'title': 'Microsoft Copilot Pro 확장', 'category': 'Productivity', 'keywords': ['Microsoft', 'Copilot', 'AI', '생산성']},
            
            # 경제 & 금융
            {'title': '비트코인 10만 달러 돌파', 'category': 'Crypto', 'keywords': ['Bitcoin', '암호화폐', '10만달러', '투자']},
            {'title': '한국 기준금리 추가 인하', 'category': 'Economy', 'keywords': ['기준금리', '한국은행', '인하', '경제정책']},
            {'title': '미국 인플레이션 2% 목표 달성', 'category': 'Economy', 'keywords': ['인플레이션', '미국', '연준', '금리']},
            {'title': '일본 엔화 급등', 'category': 'Finance', 'keywords': ['엔화', '일본', '환율', '투자']},
            {'title': 'TSMC 3나노 칩 양산 확대', 'category': 'Semiconductor', 'keywords': ['TSMC', '3나노', '반도체', '칩']},
            {'title': '중국 부동산 시장 회복 신호', 'category': 'Real Estate', 'keywords': ['중국', '부동산', '회복', '시장']},
            
            # 정치 & 사회
            {'title': '2025년 대선 후보 등록 시작', 'category': 'Politics', 'keywords': ['대선', '후보등록', '2025년', '정치']},
            {'title': '기후변화 대응 글로벌 협약', 'category': 'Environment', 'keywords': ['기후변화', '협약', '탄소중립', '환경']},
            {'title': '우크라이나 전쟁 휴전 협상', 'category': 'International', 'keywords': ['우크라이나', '러시아', '휴전', '협상']},
            {'title': '북한 핵 협상 재개', 'category': 'International', 'keywords': ['북한', '핵협상', '외교', '평화']},
            {'title': 'EU 디지털 서비스법 시행', 'category': 'Policy', 'keywords': ['EU', '디지털법', '빅테크', '규제']},
            
            # 헬스케어 & 바이오
            {'title': 'mRNA 암 백신 임상 성공', 'category': 'Healthcare', 'keywords': ['mRNA', '암백신', '임상', '바이오']},
            {'title': '알츠하이머 신약 FDA 승인', 'category': 'Medicine', 'keywords': ['알츠하이머', '신약', 'FDA', '치매']},
            {'title': '줄기세포 치료법 상용화', 'category': 'Biotech', 'keywords': ['줄기세포', '치료법', '재생의학', '바이오']},
            {'title': '디지털 헬스케어 급성장', 'category': 'Digital Health', 'keywords': ['디지털헬스', '원격의료', '헬스테크', '의료']},
            
            # 문화 & 엔터테인먼트
            {'title': 'K-드라마 글로벌 흥행 지속', 'category': 'Entertainment', 'keywords': ['K드라마', '한류', '글로벌', '넷플릭스']},
            {'title': 'BTS 재결합 컴백 발표', 'category': 'K-Pop', 'keywords': ['BTS', '재결합', '컴백', 'K-Pop']},
            {'title': '올림픽 e스포츠 정식 종목 확정', 'category': 'Sports', 'keywords': ['올림픽', 'e스포츠', '게임', '스포츠']},
            {'title': 'AI 생성 영화 아카데미 후보', 'category': 'Cinema', 'keywords': ['AI영화', '아카데미', '영화제', '인공지능']},
            
            # 스타트업 & 비즈니스
            {'title': '한국 유니콘 기업 30개 돌파', 'category': 'Startup', 'keywords': ['유니콘', '스타트업', '한국', '투자']},
            {'title': '배달 로봇 상용화 확산', 'category': 'Robotics', 'keywords': ['배달로봇', '자동화', '물류', '로봇']},
            {'title': '메타버스 쇼핑몰 급성장', 'category': 'E-commerce', 'keywords': ['메타버스', '쇼핑몰', 'VR', '커머스']},
            {'title': '탄소 포집 기술 상용화', 'category': 'CleanTech', 'keywords': ['탄소포집', '기후기술', '탄소중립', '환경']},
        ]
        
        # 사이트별 전문 트렌딩
        self.site_trends = {
            'unpre': [
                {'title': 'GitHub Copilot 무료화', 'category': 'Developer Tools', 'keywords': ['GitHub', 'Copilot', '개발도구', 'AI']},
                {'title': 'Python 3.13 성능 혁신', 'category': 'Programming', 'keywords': ['Python', '3.13', '성능', '프로그래밍']},
                {'title': 'Rust 웹 프레임워크 급부상', 'category': 'Web Dev', 'keywords': ['Rust', '웹프레임워크', '성능', '백엔드']},
                {'title': 'WebAssembly 브라우저 표준화', 'category': 'Web Tech', 'keywords': ['WebAssembly', '브라우저', '표준', '성능']},
                {'title': 'Kubernetes 보안 강화', 'category': 'DevOps', 'keywords': ['Kubernetes', '보안', 'DevOps', '컨테이너']},
                {'title': 'React 19 서버 컴포넌트', 'category': 'Frontend', 'keywords': ['React', '19', '서버컴포넌트', '프론트엔드']},
                {'title': 'TypeScript 5.5 새 기능', 'category': 'Language', 'keywords': ['TypeScript', '5.5', '새기능', '개발']},
                {'title': 'AI 코드 리뷰 도구 확산', 'category': 'AI Tools', 'keywords': ['AI', '코드리뷰', '자동화', '개발도구']},
                {'title': 'Edge Computing 플랫폼 성장', 'category': 'Infrastructure', 'keywords': ['Edge', 'Computing', '플랫폼', '인프라']},
                {'title': 'NoSQL 데이터베이스 진화', 'category': 'Database', 'keywords': ['NoSQL', '데이터베이스', '진화', 'DB']},
            ],
            'untab': [
                {'title': '서울 아파트 가격 안정화', 'category': 'Real Estate', 'keywords': ['서울', '아파트', '가격안정', '부동산']},
                {'title': '부동산 PF 시장 회복', 'category': 'Finance', 'keywords': ['부동산PF', '시장회복', '금융', '투자']},
                {'title': '지방 부동산 투자 급증', 'category': 'Investment', 'keywords': ['지방', '부동산투자', '급증', '수익률']},
                {'title': '재개발 사업 활성화', 'category': 'Development', 'keywords': ['재개발', '사업', '활성화', '도시개발']},
                {'title': '전세금 반환보증 강화', 'category': 'Policy', 'keywords': ['전세금', '반환보증', '강화', '정책']},
                {'title': '부동산 세제 개편안', 'category': 'Tax', 'keywords': ['부동산세제', '개편', '세금', '정책']},
                {'title': '스마트홈 기술 확산', 'category': 'Smart Home', 'keywords': ['스마트홈', '기술확산', 'IoT', '주거']},
                {'title': '친환경 건축 인증 확대', 'category': 'Green Building', 'keywords': ['친환경건축', '인증', '그린빌딩', '건설']},
                {'title': '부동산 경매 시장 동향', 'category': 'Auction', 'keywords': ['부동산경매', '시장동향', '투자', '경매']},
                {'title': '임대주택 공급 확대', 'category': 'Rental', 'keywords': ['임대주택', '공급확대', '주거', '정책']},
            ],
            'skewese': [
                {'title': '조선왕조실록 디지털화', 'category': 'Digital Heritage', 'keywords': ['조선왕조실록', '디지털화', '문화재', '역사']},
                {'title': '한국사 교육과정 개편', 'category': 'Education', 'keywords': ['한국사', '교육과정', '개편', '역사교육']},
                {'title': '문화재 복원 기술 혁신', 'category': 'Cultural Heritage', 'keywords': ['문화재복원', '기술혁신', '전통', '보존']},
                {'title': 'K-컬처 역사 콘텐츠 인기', 'category': 'Culture', 'keywords': ['K컬처', '역사콘텐츠', '한류', '문화']},
                {'title': '전통 공예 현대적 재해석', 'category': 'Traditional Craft', 'keywords': ['전통공예', '현대재해석', '공예', '문화']},
                {'title': '박물관 디지털 전시 확산', 'category': 'Museum', 'keywords': ['박물관', '디지털전시', '가상현실', '문화']},
                {'title': '고고학 AI 발굴 기술', 'category': 'Archaeology', 'keywords': ['고고학', 'AI발굴', '기술', '역사']},
                {'title': '한복 글로벌 패션 트렌드', 'category': 'Fashion', 'keywords': ['한복', '글로벌', '패션트렌드', '전통']},
                {'title': '역사 다큐멘터리 르네상스', 'category': 'Documentary', 'keywords': ['역사다큐', '르네상스', '방송', '콘텐츠']},
                {'title': '전통음식 레시피 복원', 'category': 'Food Culture', 'keywords': ['전통음식', '레시피복원', '음식문화', '전통']},
            ]
        }
    
    def generate_current_week_trends(self, week_start, week_number):
        """이번주 트렌딩 생성"""
        import random
        
        # 주차에 따라 시드 설정 (일관성 있는 랜덤)
        random.seed(week_number * 100)
        
        # 글로벌 이슈 8-10개 선택
        global_issues = random.sample(self.global_trending_pool, 9)
        
        # 트렌드 타입과 우선순위 랜덤 할당
        trend_types = ['hot', 'rising', 'predicted', 'viral']
        for i, issue in enumerate(global_issues):
            issue['trend_type'] = random.choice(trend_types)
            issue['priority'] = 10 - i  # 우선순위 설정
            issue['description'] = f"{issue['title']}이(가) 이번주 주요 이슈로 떠오르고 있습니다."
        
        # 사이트별 트렌드 7-8개씩
        site_trends = {}
        for site, trends in self.site_trends.items():
            selected = random.sample(trends, 7)
            for i, trend in enumerate(selected):
                trend['trend_type'] = random.choice(trend_types)
                trend['priority'] = 8 - i
                trend['description'] = f"{trend['title']}이(가) {site} 분야에서 주목받고 있습니다."
            site_trends[site] = selected
        
        return {
            'period': f'이번주 트렌드 ({week_start})',
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_number': week_number,
            'cross_category_issues': global_issues,
            'site_trends': site_trends,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_next_week_trends(self, week_start, week_number):
        """다음주 예측 트렌딩 생성"""
        import random
        
        # 다음주용 시드
        random.seed(week_number * 200)
        
        # 예측된 이슈들
        predicted_issues = random.sample(self.global_trending_pool, 8)
        
        for i, issue in enumerate(predicted_issues):
            issue['trend_type'] = 'predicted'
            issue['priority'] = 9 - i
            issue['description'] = f"{issue['title']}이(가) 다음주 주요 이슈가 될 것으로 예측됩니다."
        
        # 사이트별 예측 트렌드
        site_trends = {}
        for site, trends in self.site_trends.items():
            selected = random.sample(trends, 7)
            for i, trend in enumerate(selected):
                trend['trend_type'] = 'predicted'
                trend['priority'] = 7 - i
                trend['description'] = f"{trend['title']}이(가) 다음주 {site} 분야 핫이슈가 될 전망입니다."
            site_trends[site] = selected
        
        return {
            'period': f'다음주 예측 트렌드 ({week_start})',
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_number': week_number,
            'cross_category_issues': predicted_issues,
            'site_trends': site_trends,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

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

@app.route('/api/scheduler/status')
def get_scheduler_status():
    """스케줄러 상태 확인 API"""
    try:
        global scheduler
        if scheduler and scheduler.running:
            jobs = scheduler.get_jobs()
            job_info = []
            for job in jobs:
                job_info.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S KST') if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            
            return jsonify({
                'status': 'running',
                'jobs': job_info,
                'message': '스케줄러가 정상 작동 중입니다.'
            })
        else:
            return jsonify({
                'status': 'stopped',
                'jobs': [],
                'message': '스케줄러가 실행되고 있지 않습니다.'
            })
    except Exception as e:
        logger.error(f"스케줄러 상태 확인 오류: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/scheduler/trigger', methods=['POST'])
def trigger_scheduler():
    """수동으로 자동 발행 작업 실행"""
    try:
        add_system_log('INFO', '수동 자동 발행 작업 트리거', 'API')
        
        # 백그라운드에서 실행
        thread = threading.Thread(target=auto_publish_task)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '자동 발행 작업이 시작되었습니다.'
        })
    except Exception as e:
        logger.error(f"수동 트리거 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedule/create', methods=['POST'])
def create_weekly_schedule():
    """주간 스케줄 수동 생성"""
    try:
        from src.utils.schedule_manager import schedule_manager
        from datetime import datetime, timedelta
        
        data = request.get_json()
        week_start = data.get('week_start')
        
        if week_start:
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            # 다음 주 월요일 기본값
            today = datetime.now().date()
            days_ahead = 7 - today.weekday()  
            start_date = today + timedelta(days=days_ahead)
        
        add_system_log('INFO', f'{start_date} 주간 스케줄 생성 시작', 'SCHEDULE')
        
        success = schedule_manager.create_weekly_schedule(start_date)
        
        if success:
            add_system_log('SUCCESS', f'{start_date} 주간 스케줄 생성 완료', 'SCHEDULE')
            return jsonify({
                'success': True,
                'message': f'{start_date} 주간 스케줄이 생성되었습니다.',
                'week_start': start_date.strftime('%Y-%m-%d')
            })
        else:
            return jsonify({
                'success': False,
                'message': '스케줄 생성에 실패했습니다.'
            }), 500
            
    except Exception as e:
        logger.error(f"주간 스케줄 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedule/save', methods=['POST'])
def save_schedule():
    """클라이언트에서 생성한 스케줄을 데이터베이스에 저장"""
    try:
        data = request.get_json()
        schedule_data = data.get('schedule_data')
        
        if not schedule_data:
            return jsonify({'success': False, 'error': '스케줄 데이터가 없습니다.'}), 400
        
        # 스케줄 매니저를 사용해 DB에 저장
        sm = get_schedule_manager()
        success = sm.save_client_schedule(schedule_data)
        
        if success:
            add_system_log('SUCCESS', f'클라이언트 스케줄 DB 저장 완료: {schedule_data.get("week_start")}', 'SCHEDULE')
            return jsonify({'success': True, 'message': '스케줄이 저장되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '스케줄 저장에 실패했습니다.'}), 500
            
    except Exception as e:
        add_system_log('ERROR', f'스케줄 저장 API 오류: {e}', 'SCHEDULE')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """실시간 로그 조회 - 자동발행 모니터링"""
    try:
        # 인메모리 로그 가져오기
        logs = get_recent_logs()
        
        # 로그 파일에서도 가져오기 (백업)
        import os
        log_file = 'blog_automation.log'
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-50:]  # 최근 50줄
                    for line in lines:
                        if line.strip():
                            parts = line.strip().split(' - ', 3)
                            if len(parts) >= 3:
                                log_time = parts[0]
                                log_level = parts[1].lower()
                                log_message = ' - '.join(parts[2:])
                                
                                # 시간 포맷 변환
                                try:
                                    parsed_time = datetime.strptime(log_time, '%Y-%m-%d %H:%M:%S,%f')
                                    formatted_time = parsed_time.strftime('%H:%M:%S')
                                except:
                                    formatted_time = log_time
                                
                                logs.append({
                                    'time': formatted_time,
                                    'level': log_level,
                                    'message': log_message
                                })
            except Exception as e:
                print(f"로그 파일 읽기 오류: {e}")
        
        # 시간순 정렬 (최신순)
        logs.sort(key=lambda x: x['time'], reverse=True)
        
        return jsonify(logs[:100])  # 최근 100개만
        
    except Exception as e:
        logger.error(f"로그 조회 오류: {e}")
        return jsonify([
            {
                'time': datetime.now(KST).strftime('%H:%M:%S'),
                'level': 'info',
                'message': '시스템 정상 작동 중'
            }
        ])


@app.route('/api/schedule/status')
def get_schedule_status():
    """자동발행 스케줄 상태 확인"""
    try:
        from config.sites_config import PUBLISHING_SCHEDULE
        import pytz
        
        now = datetime.now(pytz.timezone('Asia/Seoul'))
        today = now.date()
        current_time = now.strftime('%H:%M')
        
        schedule_info = {}
        
        for site, config in PUBLISHING_SCHEDULE.items():
            schedule_time = config['time']
            days = config['days']
            
            # 오늘 발행 예정인지 확인
            today_weekday = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][today.weekday()]
            is_today = today_weekday in days
            
            # 발행 시간까지 남은 시간 계산
            if is_today:
                schedule_datetime = datetime.combine(today, datetime.strptime(schedule_time, '%H:%M').time())
                schedule_datetime = pytz.timezone('Asia/Seoul').localize(schedule_datetime)
                
                if now < schedule_datetime:
                    time_until = schedule_datetime - now
                    hours, remainder = divmod(int(time_until.total_seconds()), 3600)
                    minutes, _ = divmod(remainder, 60)
                    status = f'{hours}시간 {minutes}분 후 발행 예정'
                else:
                    status = '오늘 발행 완료 또는 진행 중'
            else:
                # 다음 발행일 찾기
                next_publish_days = []
                for i in range(1, 8):
                    future_date = today + timedelta(days=i)
                    future_weekday = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][future_date.weekday()]
                    if future_weekday in days:
                        next_publish_days.append(future_date.strftime('%m/%d'))
                        break
                
                status = f'다음 발행: {next_publish_days[0] if next_publish_days else "없음"} {schedule_time}'
            
            schedule_info[site] = {
                'schedule_time': schedule_time,
                'is_today': is_today,
                'status': status,
                'days': days
            }
        
        add_system_log('INFO', f'스케줄 상태 조회 - 현재 시간: {current_time}', 'SCHEDULE_CHECK')
        
        return jsonify({
            'current_time': current_time,
            'current_date': today.strftime('%Y-%m-%d'),
            'schedule_info': schedule_info,
            'auto_publish_enabled': True
        })
        
    except Exception as e:
        logger.error(f"스케줄 상태 조회 오류: {e}")
        add_system_log('ERROR', f'스케줄 상태 조회 오류: {e}', 'SCHEDULE_CHECK')
        return jsonify({'error': str(e)}), 500

@app.route('/api/schedule/weekly')
def get_weekly_schedule():
    """주간 스케줄 조회 - 간단하고 확실한 동적 생성"""
    try:
        # 요청된 시작 날짜 파싱
        week_start = request.args.get('week_start') or request.args.get('start_date')
        if week_start:
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
            add_system_log('DEBUG', f'API 요청 날짜: {start_date}', 'SCHEDULE')
        else:
            # 현재 주 일요일 계산
            today = datetime.now(KST).date()
            days_since_sunday = (today.weekday() + 1) % 7  
            start_date = today - timedelta(days=days_since_sunday)
            add_system_log('DEBUG', f'계산된 날짜: {start_date} (오늘: {today})', 'SCHEDULE')
        
        # DB에서 실제 스케줄 데이터 조회
        from src.utils.schedule_manager import schedule_manager
        add_system_log('INFO', f'DB 스케줄 조회 시작: {start_date}', 'SCHEDULE')
        schedule_data = schedule_manager.get_weekly_schedule(start_date)
        add_system_log('INFO', f'DB 스케줄 조회 완료: week_start={schedule_data.get("week_start")}', 'SCHEDULE')
        
        # 대시보드용 간단한 포맷 변환
        formatted_schedule = {}
        
        if schedule_data and 'schedule' in schedule_data:
            for day_idx, day_info in schedule_data['schedule'].items():
                if not isinstance(day_info, dict) or 'date' not in day_info:
                    continue
                    
                date_str = day_info['date'].strftime('%Y-%m-%d')
                formatted_schedule[date_str] = {}
                
                sites_data = day_info.get('sites', {})
                current_date = datetime.now(KST).date()
                target_date = day_info['date']
                
                # DB에서 가져온 사이트 데이터 그대로 사용
                for site, site_info in sites_data.items():
                    if site_info and isinstance(site_info, dict):
                        topic = site_info.get('topic', f'{site} 주제 없음')
                        
                        # 티스토리의 경우 실시간 트렌드 마커 확인
                        if site == 'tistory':
                            # 오늘 이후 날짜면서 최근 업데이트된 경우 트렌드 마크
                            updated_at = site_info.get('updated_at')
                            if target_date >= current_date and updated_at:
                                # 최근 24시간 내 업데이트된 경우
                                from datetime import datetime, timezone
                                now = datetime.now(timezone.utc)
                                if isinstance(updated_at, str):
                                    updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                                else:
                                    updated_time = updated_at
                                
                                if (now - updated_time).total_seconds() < 86400:  # 24시간
                                    topic = f"🔥 {topic}"
                        
                        # 상태 결정
                        if target_date < current_date:
                            status = 'published' if site != 'tistory' else 'generated'
                        elif target_date == current_date:
                            current_time = datetime.now(KST).time()
                            if current_time >= datetime.strptime('03:00', '%H:%M').time():
                                status = 'published' if site != 'tistory' else 'generated'
                            else:
                                status = 'scheduled'
                        else:
                            status = 'scheduled'
                        
                        formatted_schedule[date_str][site] = {
                            'topic': topic,
                            'status': status,
                            'time': '03:00'
                        }
                        
                        if site == 'tistory':
                            formatted_schedule[date_str][site]['note'] = '콘텐츠 생성만 (수동 발행)'
                            # 실시간 트렌드 마커 추가
                            if target_date >= current_date:  # 오늘 이후 날짜
                                formatted_schedule[date_str][site]['trending'] = True
                                formatted_schedule[date_str][site]['topic'] = f"🔥 {topic}"
                else:
                    formatted_schedule[date_str][site] = {
                        'time': '03:00',
                        'topic': topic,
                        'status': status
                    }
        
        return jsonify(formatted_schedule)
        
    except Exception as e:
        logger.error(f"Weekly schedule error: {e}")
        return jsonify({}), 500

@app.route('/api/schedule/test')
def test_dynamic_schedule():
    """동적 스케줄 테스트 API"""
    start_date = request.args.get('start_date', '2025-08-24')
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    # 직접 테스트
    import random
    from datetime import timedelta
    
    week_seed = start_date_obj.toordinal()
    random.seed(week_seed)
    
    unpre_topics = ["JWT 토큰 기반 시큐리티 구현", "DDD(도메인 주도 설계) 실전 적용", "C++ 최신 프로그래밍 기법"]
    
    topic_index = (week_seed + 0 * 10 + hash('unpre')) % len(unpre_topics)
    selected_topic = unpre_topics[topic_index]
    
    return jsonify({
        'request_date': start_date,
        'week_seed': week_seed,
        'topic_index': topic_index,
        'selected_topic': selected_topic,
        'all_topics': unpre_topics
    })

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
                    
                    # 사이트별 설정
                    site_configs = {
                        'unpre': {
                            'name': 'unpre',
                            'target_audience': '개발자 및 IT 전문가',
                            'content_style': '실용적이고 기술적인',
                            'keywords_focus': data.get('keywords', [topic])
                        },
                        'untab': {
                            'name': 'untab',
                            'target_audience': '부동산 투자자 및 일반인',
                            'content_style': '실용적이고 상세한 가이드',
                            'keywords_focus': data.get('keywords', [topic])
                        },
                        'skewese': {
                            'name': 'skewese',
                            'target_audience': '역사와 문화에 관심있는 일반인',
                            'content_style': '흥미롭고 교육적인',
                            'keywords_focus': data.get('keywords', [topic])
                        }
                    }
                    
                    site_config = site_configs.get(site, site_configs['unpre'])
                    
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
                        
                        # 대표이미지 생성
                        featured_image_path = img_gen.generate_featured_image(title=generated_content['title'])
                        
                        if featured_image_path and os.path.exists(featured_image_path):
                            images = [{
                                'url': featured_image_path,
                                'type': 'thumbnail',  # 대표이미지로 설정
                                'alt': f"{generated_content['title']} 대표이미지"
                            }]
                        else:
                            images = []
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
                
                # JSON 메타데이터 파일 생성 (목록 표시용)
                import time
                import json
                json_file_path = file_path.replace('.html', '.json')
                metadata_content = {
                    'title': title,
                    'id': int(time.time()),
                    'site': site,
                    'status': 'draft',
                    'tags': data.get('keywords', [topic]),
                    'categories': [data.get('category', '기본')],
                    'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'file_path': file_path
                }
                
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata_content, f, ensure_ascii=False, indent=2)
                
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
                        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 1000,
                        'status': 'draft'  # 새로 생성된 콘텐츠는 draft로 설정
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
                    title = generated_content.get('title', f'{topic} 분석')
                    logger.info(f"Claude API Tistory 콘텐츠 생성 완료: {title[:50]}...")
                    
                else:
                    # Fallback 콘텐츠
                    logger.warning("Tistory ContentGenerator가 None입니다. 기본 콘텐츠를 생성합니다.")
                    content = f'<h1>{topic} 심화 분석</h1>\n<p>{topic}에 대한 상세한 분석입니다.</p>'
                    title = f'{topic} 심화 분석'
                    logger.warning(f"Claude API 미사용, Tistory 기본 콘텐츠 생성: {title}")
                
                # Tistory 파일로 저장 (목록 표시를 위해)
                import time
                import json
                from datetime import datetime
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', ' ')[:50]  # 제목 길이 제한
                
                html_filename = f"{timestamp}_{safe_title}.html"
                html_file_path = os.path.join('data', 'tistory_posts', html_filename)
                
                # 디렉토리 생성
                os.makedirs(os.path.dirname(html_file_path), exist_ok=True)
                
                # HTML 파일 저장
                with open(html_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # _meta.json 파일 생성 (목록 표시용)
                meta_filename = html_filename.replace('.html', '_meta.json')
                meta_file_path = os.path.join('data', 'tistory_posts', meta_filename)
                
                metadata_content = {
                    'title': title,
                    'tags': data.get('keywords', [topic]),
                    'category': data.get('category', '기본'),
                    'created_at': datetime.now().isoformat(),
                    'file_path': html_file_path.replace('\\', '/')
                }
                
                with open(meta_file_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata_content, f, ensure_ascii=False, indent=2)
                
                # 콘텐츠를 데이터베이스에도 저장
                file_id = database.add_content_file(
                    site='tistory',
                    title=title,
                    file_path=html_file_path,  # 파일 경로 저장
                    file_type='tistory',
                    metadata={
                        'categories': [data.get('category', '기본')],
                        'tags': data.get('keywords', [topic]),
                        'word_count': len(content.split()),
                        'reading_time': len(content.split()) // 200 + 1,
                        'file_size': len(content.encode('utf-8')),
                        'status': 'draft'  # 새로 생성된 콘텐츠는 draft로 설정
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

@app.route('/api/preview_content/<int:file_id>')
def preview_content(file_id):
    """콘텐츠 미리보기"""
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
                # content 필드에서 직접 콘텐츠 읽기 (수동발행 후 저장된 HTML)
                content = target_file.get('content')
                
                # content가 없으면 file_path에서 읽기 시도 (기존 방식)
                if not content:
                    file_path = target_file.get('file_path')
                    if file_path and os.path.exists(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            logger.info(f"파일에서 콘텐츠 읽기 성공: {file_path}")
                        except Exception as e:
                            logger.warning(f"파일 읽기 실패: {e}")
                            content = None
                
                # 콘텐츠가 없는 경우 기본 콘텐츠 생성
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
        <p>콘텐츠를 불러올 수 없습니다.</p>
    </div>
</body>
</html>"""
                
                # HTML 응답 반환
                response = make_response(content)
                response.headers['Content-Type'] = 'text/html; charset=utf-8'
                return response
        
        # 파일을 찾을 수 없는 경우
        return "파일을 찾을 수 없습니다.", 404
        
    except Exception as e:
        logger.error(f"미리보기 오류: {e}")
        return f"미리보기 오류: {str(e)}", 500

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
                # content 필드에서 직접 콘텐츠 읽기 (수동발행 후 저장된 HTML)
                content = target_file.get('content')
                
                # content가 없으면 file_path에서 읽기 시도 (기존 방식)
                if not content:
                    file_path = target_file.get('file_path')
                    if file_path and os.path.exists(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            logger.info(f"파일에서 콘텐츠 읽기 성공: {file_path}")
                        except Exception as e:
                            logger.warning(f"파일 읽기 실패: {e}")
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
        
        # 제목에서 도메인명 제거 (예: "제목 - unpre.co.kr" -> "제목")
        site_domains = [' - unpre.co.kr', ' - untab.co.kr', ' - skewese.com', ' - tistory.com']
        for domain in site_domains:
            if title.endswith(domain):
                title = title[:-len(domain)].strip()
                break
        
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
            
            # 대표이미지 생성
            featured_image_path = img_gen.generate_featured_image(title=title)
            
            if featured_image_path and os.path.exists(featured_image_path):
                images = [{
                    'url': featured_image_path,
                    'type': 'thumbnail',  # WordPress publisher가 인식할 수 있도록
                    'alt': f"{title} 대표이미지"
                }]
            else:
                images = []
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

@app.route('/api/bulk_delete_files', methods=['DELETE'])
def bulk_delete_files():
    """파일 기반 콘텐츠 일괄 삭제"""
    try:
        data = request.json
        file_paths = data.get('file_paths', [])
        
        logger.info(f"[DELETE] 삭제 요청 받음: {len(file_paths)}개 파일")
        logger.info(f"[DELETE] 파일 경로들: {file_paths}")
        
        if not file_paths:
            logger.warning("[DELETE] 삭제할 파일이 선택되지 않음")
            return jsonify({
                'success': False,
                'error': '삭제할 파일이 선택되지 않았습니다.'
            }), 400
        
        deleted_count = 0
        failed_files = []
        
        # DB 연결
        database = get_database()
        
        for file_path in file_paths:
            try:
                # 백슬래시를 슬래시로 변환 (모든 환경)
                file_path = file_path.replace('\\', '/')
                logger.info(f"[DELETE] 처리 중인 파일: {file_path}")
                
                # 운영 환경 경로 변환
                actual_file_path = file_path
                if os.getenv('KOYEB_SERVICE'):
                    # Koyeb 환경에서는 절대 경로로 변환
                    if not file_path.startswith('/workspace'):
                        if file_path.startswith('data/'):
                            actual_file_path = f"/workspace/{file_path}"
                        else:
                            actual_file_path = f"/workspace/data/{file_path}"
                
                logger.info(f"[DELETE] 변환된 경로: {actual_file_path}")
                
                # DB에서 먼저 삭제
                if database.is_connected:
                    try:
                        # 원본 경로와 변환된 경로 모두 시도
                        database.delete_content_by_path(file_path)
                        if file_path != actual_file_path:
                            database.delete_content_by_path(actual_file_path)
                        logger.info(f"DB에서 삭제 완료: {file_path}")
                    except Exception as db_error:
                        logger.warning(f"DB 삭제 실패 (파일은 삭제 진행): {db_error}")
                
                # 파일 경로 검증 및 삭제
                file_deleted = False
                for path_to_try in [actual_file_path, file_path]:
                    if os.path.exists(path_to_try):
                        os.remove(path_to_try)
                        file_deleted = True
                        logger.info(f"파일 삭제 완료: {path_to_try}")
                        
                        # JSON 메타데이터 파일도 삭제 (있는 경우)
                        # 일반 JSON 파일과 Tistory _meta.json 파일 모두 확인
                        json_paths = [
                            path_to_try.replace('.html', '.json'),
                            path_to_try.replace('.html', '_meta.json')
                        ]
                        
                        for json_path in json_paths:
                            if os.path.exists(json_path):
                                os.remove(json_path)
                                logger.info(f"메타데이터 파일 삭제 완료: {json_path}")
                        break
                
                if file_deleted:
                    deleted_count += 1
                else:
                    logger.warning(f"파일을 찾을 수 없음: {file_path} / {actual_file_path}")
                    # DB에서만 삭제되었으므로 카운트 증가
                    deleted_count += 1
                    
            except Exception as e:
                logger.error(f"파일 삭제 실패 {file_path}: {e}")
                failed_files.append(file_path)
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count}개의 콘텐츠가 삭제되었습니다.',
            'deleted_count': deleted_count,
            'failed_files': failed_files
        })
        
    except Exception as e:
        logger.error(f"일괄 삭제 오류: {e}")
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

@app.route('/api/today-topics')
def get_today_topics():
    """오늘의 발행 주제 조회"""
    try:
        from src.utils.schedule_manager import schedule_manager
        from datetime import date
        
        today = date.today()
        weekday = today.weekday()
        week_start = today - timedelta(days=weekday)
        
        sites = ['unpre', 'untab', 'skewese', 'tistory']
        topics_data = {}
        
        conn = schedule_manager.db.get_connection()
        if conn:
            with conn.cursor() as cursor:
                for site in sites:
                    cursor.execute("""
                        SELECT topic_category, specific_topic, keywords, target_length, status
                        FROM publishing_schedule 
                        WHERE week_start_date = %s AND day_of_week = %s AND site = %s
                        AND status = 'planned'
                        ORDER BY topic_category
                    """, (week_start, weekday, site))
                    
                    results = cursor.fetchall()
                    topics_data[site] = []
                    
                    for row in results:
                        category, topic, keywords, length, status = row
                        topics_data[site].append({
                            'category': category,
                            'topic': topic,
                            'keywords': keywords if keywords else [],
                            'length': length or 'medium',
                            'status': status
                        })
        
        add_system_log('INFO', f'오늘의 주제 조회 완료: {sum(len(v) for v in topics_data.values())}개', 'API')
        return jsonify(topics_data)
        
    except Exception as e:
        logger.error(f"Today topics error: {e}")
        add_system_log('ERROR', f'오늘의 주제 조회 오류: {e}', 'API')
        return jsonify({'error': str(e)}), 500

@app.route('/api/schedule/monthly')
def get_monthly_schedule():
    """당월 전체 계획표 조회 - 대시보드 호환 형식"""
    try:
        # 월 파라미터 (기본값: 현재 월)
        month = request.args.get('month')
        if month:
            year, month = map(int, month.split('-'))
            target_date = date(year, month, 1)
        else:
            today = date.today()
            target_date = date(today.year, today.month, 1)
        
        # 해당 월의 첫째 날과 마지막 날
        if target_date.month == 12:
            next_month = target_date.replace(year=target_date.year + 1, month=1)
        else:
            next_month = target_date.replace(month=target_date.month + 1)
        
        last_day = (next_month - timedelta(days=1)).day
        
        add_system_log('INFO', f'월별 계획표 조회: {target_date.year}-{target_date.month:02d}', 'SCHEDULE')
        
        # DB에서 해당 월 전체 스케줄 조회
        from src.utils.schedule_manager import schedule_manager
        
        conn = schedule_manager.db.get_connection()
        monthly_schedule = {}
        
        if conn:
            with conn.cursor() as cursor:
                # 해당 월의 모든 스케줄 조회
                cursor.execute("""
                    SELECT week_start_date, day_of_week, site, topic_category, 
                           specific_topic, keywords, target_length, status, updated_at
                    FROM publishing_schedule 
                    WHERE week_start_date + (day_of_week * INTERVAL '1 day') >= %s
                    AND week_start_date + (day_of_week * INTERVAL '1 day') < %s
                    ORDER BY week_start_date, day_of_week, site, topic_category
                """, (target_date, next_month))
                
                results = cursor.fetchall()
                
                # 날짜별로 그룹화
                for row in results:
                    week_start, day_of_week, site, category, topic, keywords, length, status, updated_at = row
                    
                    # 실제 날짜 계산
                    actual_date = week_start + timedelta(days=day_of_week)
                    date_str = actual_date.strftime('%Y-%m-%d')
                    
                    if date_str not in monthly_schedule:
                        monthly_schedule[date_str] = {
                            'date': date_str,
                            'day_name': ['월', '화', '수', '목', '금', '토', '일'][actual_date.weekday()],
                            'sites': {}
                        }
                    
                    if site not in monthly_schedule[date_str]['sites']:
                        monthly_schedule[date_str]['sites'][site] = []
                    
                    # 티스토리 실시간 트렌드 마커
                    if site == 'tistory' and updated_at:
                        from datetime import datetime, timezone
                        now = datetime.now(timezone.utc)
                        if isinstance(updated_at, str):
                            updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        else:
                            updated_time = updated_at.replace(tzinfo=timezone.utc) if updated_at.tzinfo is None else updated_at
                        
                        # 최근 24시간 내 업데이트면 트렌드 마크
                        if (now - updated_time).total_seconds() < 86400:
                            topic = f"🔥 {topic}"
                    
                    monthly_schedule[date_str]['sites'][site].append({
                        'category': category,
                        'topic': topic,
                        'keywords': keywords,
                        'length': length,
                        'status': status
                    })
        
        # 날짜순 정렬된 리스트로 변환
        sorted_schedule = []
        for day in range(1, last_day + 1):
            date_str = f"{target_date.year}-{target_date.month:02d}-{day:02d}"
            day_data = monthly_schedule.get(date_str, {
                'date': date_str,
                'day_name': ['월', '화', '수', '목', '금', '토', '일'][date(target_date.year, target_date.month, day).weekday()],
                'sites': {}
            })
            sorted_schedule.append(day_data)
        
        response_data = {
            'year': target_date.year,
            'month': target_date.month,
            'month_name': f"{target_date.year}년 {target_date.month}월",
            'total_days': last_day,
            'schedule': sorted_schedule
        }
        
        add_system_log('INFO', f'월별 계획표 응답: {len(sorted_schedule)}일', 'SCHEDULE')
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Monthly schedule error: {e}")
        add_system_log('ERROR', f'월별 계획표 오류: {e}', 'SCHEDULE')
        return jsonify({'error': str(e)}), 500

# 새 대시보드용 API 엔드포인트들
@app.route('/api/content/<site>')
def get_content_list(site):
    """사이트별 콘텐츠 목록 조회 - DB 기반 안정성 강화"""
    try:
        import os
        import json
        from datetime import datetime

        # 로깅으로 디버깅 정보 추가
        logger.info(f"콘텐츠 목록 조회 요청: {site}")

        # 사이트 유효성 검사
        valid_sites = ['skewese', 'tistory', 'unpre', 'untab']
        if site not in valid_sites:
            logger.warning(f"지원하지 않는 사이트: {site}")
            return jsonify([])

        contents = []

        # 먼저 DB에서 콘텐츠 조회 (우선)
        try:
            from src.utils.postgresql_database import PostgreSQLDatabase
            db = PostgreSQLDatabase()
            conn = db.get_connection()

            if conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        SELECT id, site, title, file_path, created_at, status, metadata
                        FROM blog_automation.content_files
                        WHERE site = %s
                        ORDER BY created_at DESC
                        LIMIT 50
                    ''', (site,))

                    db_results = cursor.fetchall()

                    for row in db_results:
                        content_data = {
                            'id': row[0],
                            'site': row[1],
                            'title': row[2],
                            'file_path': row[3],
                            'created_at': row[4].isoformat() if row[4] else datetime.now().isoformat(),
                            'status': row[5],
                            'metadata': row[6] if row[6] else {}
                        }

                        # 운영 환경에서 경로 정규화
                        if os.getenv('KOYEB_SERVICE') and content_data.get('file_path'):
                            content_data['file_path'] = content_data['file_path'].replace('\\', '/')

                        contents.append(content_data)

                    logger.info(f"{site} DB에서 {len(contents)}개 콘텐츠 조회 완료")

                    if contents:
                        return jsonify(contents)

        except Exception as db_error:
            logger.warning(f"DB 조회 실패, 파일시스템 폴백 사용: {db_error}")
            # 시스템 로그에 DB 오류 기록
            try:
                add_system_log('WARNING', f'콘텐츠 목록 DB 조회 실패: {db_error}', 'DB_ERROR')
            except:
                pass

        # DB 조회 실패 시 파일시스템 폴백
        site_map = {
            'skewese': 'wordpress_posts/skewese',
            'tistory': 'tistory_posts',
            'unpre': 'wordpress_posts/unpre',
            'untab': 'wordpress_posts/untab'
        }

        current_dir = os.path.dirname(os.path.abspath(__file__))
        content_dir = os.path.join(current_dir, 'data', site_map[site])

        logger.info(f"파일시스템 폴백 - 콘텐츠 디렉토리: {content_dir}")

        if not os.path.exists(content_dir):
            logger.info(f"콘텐츠 디렉토리 없음: {content_dir}")
            return jsonify([])

        # 안전한 파일 검색
        try:
            for filename in os.listdir(content_dir):
                if (site == 'tistory' and filename.endswith('_meta.json')) or \
                   (site != 'tistory' and filename.endswith('.json') and not filename.endswith('_meta.json')):
                    json_file_path = os.path.join(content_dir, filename)
                    try:
                        with open(json_file_path, 'r', encoding='utf-8') as f:
                            content_data = json.load(f)

                            # 경로 정규화
                            if 'file_path' in content_data and os.getenv('KOYEB_SERVICE'):
                                content_data['file_path'] = content_data['file_path'].replace('\\', '/')

                            contents.append(content_data)
                    except Exception as e:
                        logger.warning(f"JSON 파일 로드 오류 {filename}: {e}")
        except Exception as e:
            logger.error(f"디렉토리 읽기 오류 {content_dir}: {e}")
            return jsonify([])

        # 최신순 정렬
        contents.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        logger.info(f"{site} 파일시스템에서 {len(contents)}개 콘텐츠 조회 완료")
        return jsonify(contents[:50])

    except Exception as e:
        logger.error(f"콘텐츠 목록 조회 오류 {site}: {e}")
        # 시스템 로그에 에러 기록
        try:
            add_system_log('ERROR', f'콘텐츠 목록 조회 실패 ({site}): {e}', 'API_ERROR')
        except:
            pass
        return jsonify({'error': f'콘텐츠 조회 실패: {str(e)}', 'site': site}), 500

@app.route('/api/content/<site>/preview')
def get_content_preview(site):
    """콘텐츠 미리보기"""
    try:
        file_path = request.args.get('file')
        if not file_path:
            return jsonify({'error': '파일 경로가 필요합니다'}), 400
            
        # URL 디코딩 및 경로 정규화
        from urllib.parse import unquote_plus, unquote
        import re
        
        # 다양한 방법으로 URL 디코딩 시도
        original_path = file_path
        decoded_path = None
        
        # 방법 1: unquote_plus 시도
        try:
            decoded_path = unquote_plus(file_path)
            if '%' in decoded_path:
                decoded_path = unquote_plus(decoded_path)
        except:
            pass
        
        # 방법 2: unquote 시도 (plus가 실패한 경우)
        if not decoded_path or decoded_path == original_path:
            try:
                decoded_path = unquote(file_path)
                if '%' in decoded_path:
                    decoded_path = unquote(decoded_path)
            except:
                pass
        
        # 방법 3: 한글 인코딩 문제 해결 시도
        if not decoded_path or decoded_path == original_path:
            try:
                decoded_path = unquote(file_path, encoding='utf-8', errors='replace')
                if '%' in decoded_path:
                    decoded_path = unquote(decoded_path, encoding='utf-8', errors='replace')
            except:
                pass
        
        # 최종적으로 디코딩된 경로 사용
        file_path = decoded_path if decoded_path else file_path
        
        # 특수 문자 정리
        file_path = re.sub(r'[\t\r\n\x00-\x08\x0b\x0c\x0e-\x1f]', '', file_path)
        
        # 경로 정규화
        file_path = os.path.normpath(file_path)
        
        # 절대 경로로 변환 (보안상 현재 디렉토리 기준)
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        logger.info(f"[PREVIEW] Original path: {request.args.get('file')}, Decoded+Normalized: {file_path}")
        
        # JSON 메타데이터 로드
        json_path = file_path.replace('.html', '.json')
        logger.info(f"[PREVIEW] Checking JSON: {json_path}, exists: {os.path.exists(json_path)}")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}
            
        # HTML 콘텐츠 로드
        logger.info(f"[PREVIEW] Checking HTML: {file_path}, exists: {os.path.exists(file_path)}")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = '파일이 존재하지 않습니다.'
            
        # 이미지 경로를 웹 경로로 변환
        import re
        from bs4 import BeautifulSoup
        
        def replace_image_path(match):
            original_path = match.group(1)
            if 'blog_automation_images' in original_path:
                # 로컬 temp 이미지 경로를 웹 경로로 변환
                filename = os.path.basename(original_path)
                return f'src="/api/images/{filename}"'
            return match.group(0)
        
        # HTML 내 이미지 src 경로를 웹 경로로 변환
        content = re.sub(r'src="([^"]*)"', replace_image_path, content)
        
        # HTML에서 body 내용만 추출
        try:
            soup = BeautifulSoup(content, 'html.parser')
            body = soup.find('body')
            if body:
                # body 내의 모든 내용을 추출
                content = str(body)
                # body 태그 자체는 제거하고 내용만 남김
                content = re.sub(r'^<body[^>]*>', '', content)
                content = re.sub(r'</body>$', '', content)
            else:
                # body가 없으면 원본 그대로 사용
                pass
        except Exception as e:
            logger.warning(f"HTML 파싱 실패, 원본 사용: {e}")
            pass
        
        return jsonify({
            'title': metadata.get('title', ''),
            'categories': metadata.get('categories', []),
            'tags': metadata.get('tags', []),
            'keywords': metadata.get('keywords', []),
            'content': content,
            'word_count': metadata.get('word_count', 0),
            'created_at': metadata.get('created_at', '')
        })
        
    except Exception as e:
        logger.error(f"미리보기 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/images/<filename>')
def serve_image(filename):
    """임시 이미지 파일 서빙"""
    try:
        import tempfile
        temp_dir = tempfile.gettempdir()
        image_dir = os.path.join(temp_dir, 'blog_automation_images')
        
        # 보안상 파일명 검증
        if '..' in filename or '/' in filename or '\\' in filename:
            return "Invalid filename", 400
            
        image_path = os.path.join(image_dir, filename)
        
        if os.path.exists(image_path):
            return send_file(image_path)
        else:
            return "Image not found", 404
            
    except Exception as e:
        logger.error(f"이미지 서빙 오류: {e}")
        return "Error serving image", 500

@app.route('/api/content/<site>/download')
def get_content_download(site):
    """콘텐츠 다운로드"""
    try:
        file_path = request.args.get('file')
        if not file_path:
            return "파일 경로가 필요합니다", 400
            
        # URL 디코딩 및 경로 정규화
        from urllib.parse import unquote_plus, unquote
        import re
        
        # 다양한 방법으로 URL 디코딩 시도
        original_path = file_path
        decoded_path = None
        
        # 방법 1: unquote_plus 시도
        try:
            decoded_path = unquote_plus(file_path)
            if '%' in decoded_path:
                decoded_path = unquote_plus(decoded_path)
        except:
            pass
        
        # 방법 2: unquote 시도 (plus가 실패한 경우)
        if not decoded_path or decoded_path == original_path:
            try:
                decoded_path = unquote(file_path)
                if '%' in decoded_path:
                    decoded_path = unquote(decoded_path)
            except:
                pass
        
        # 방법 3: 한글 인코딩 문제 해결 시도
        if not decoded_path or decoded_path == original_path:
            try:
                decoded_path = unquote(file_path, encoding='utf-8', errors='replace')
                if '%' in decoded_path:
                    decoded_path = unquote(decoded_path, encoding='utf-8', errors='replace')
            except:
                pass
        
        # 최종적으로 디코딩된 경로 사용
        file_path = decoded_path if decoded_path else file_path
        
        # 특수 문자 정리
        file_path = re.sub(r'[\t\r\n\x00-\x08\x0b\x0c\x0e-\x1f]', '', file_path)
        
        # 경로 정규화
        file_path = os.path.normpath(file_path)
        
        # 절대 경로로 변환 (보안상 현재 디렉토리 기준)
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        logger.info(f"[DOWNLOAD] Original path: {request.args.get('file')}, Decoded+Normalized: {file_path}")
        
        if not os.path.exists(file_path):
            return "파일이 존재하지 않습니다", 404
            
        return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
        
    except Exception as e:
        logger.error(f"다운로드 오류: {e}")
        return "다운로드 실패", 500

@app.route('/api/system/status')
def system_status():
    """시스템 상태 조회"""
    try:
        return jsonify({
            'server_status': 'running',
            'scheduler_active': True,
            'database_connected': True,
            'next_run': '내일 새벽 3시',
            'total_content': 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/api_usage/today')
def get_api_usage_today():
    """오늘의 API 사용량 조회"""
    try:
        usage = api_tracker.get_today_usage()
        return jsonify(usage)
    except Exception as e:
        logger.error(f"API 사용량 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/api_usage/monthly')
def get_api_usage_monthly():
    """이번 달 API 사용량 조회"""
    try:
        usage = api_tracker.get_monthly_usage()
        return jsonify(usage)
    except Exception as e:
        logger.error(f"월간 API 사용량 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/api_usage/recent')
def get_api_usage_recent():
    """최근 API 호출 내역 조회"""
    try:
        limit = request.args.get('limit', 20, type=int)
        calls = api_tracker.get_recent_calls(limit)
        return jsonify(calls)
    except Exception as e:
        logger.error(f"최근 API 호출 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/publish_status/reset', methods=['POST'])
def reset_publish_status():
    """수동 발행 상태 초기화"""
    global publish_status
    publish_status = {
        'in_progress': False,
        'current_site': '',
        'progress': 0,
        'total_sites': 0,
        'results': [],
        'message': '상태 초기화됨'
    }
    add_system_log('INFO', '발행 상태 강제 초기화됨', 'RESET')
    return jsonify({
        'success': True,
        'message': '발행 상태가 초기화되었습니다.'
    })

@app.route('/api/quick-publish/preview', methods=['GET'])
def quick_publish_preview():
    """수동발행 미리보기: 오늘의 수익 최우선 주제 표시"""
    try:
        from auto_weekly_planner import ProfitWeeklyPlanner
        from datetime import datetime
        
        planner = ProfitWeeklyPlanner()
        today_topics = planner.get_today_profit_topics()
        
        preview_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sites': {}
        }
        
        for topic_info in today_topics:
            site = topic_info['site']
            preview_data['sites'][site] = {
                'title': topic_info['title'],
                'category': topic_info['category'],
                'keywords': topic_info.get('keywords', []),
                'trend_score': topic_info.get('trend_score', 0),
                'profit_type': 'ultra_profit' if topic_info.get('trend_score', 0) >= 90 else 
                              'high_profit' if topic_info.get('trend_score', 0) >= 80 else 
                              'profit_optimized'
            }
        
        return jsonify(preview_data)
        
    except Exception as e:
        logger.error(f"미리보기 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick_publish', methods=['POST'])
def quick_publish():
    """수동 발행: 오늘 스케줄 주제로 직접 발행 + WordPress 업로드"""
    try:
        data = request.json or {}
        sites = data.get('sites', ['unpre', 'untab', 'skewese', 'tistory'])
        upload_to_wordpress = data.get('upload_to_wordpress', True)  # 기본값: 업로드 활성화
        
        # 중복 실행 방지
        global publish_status
        if publish_status.get('in_progress', False):
            return jsonify({
                'success': False,
                'error': '이미 발행이 진행 중입니다. 잠시만 기다려주세요.'
            }), 400
        
        # 발행 시작
        publish_status.update({
            'in_progress': True,
            'current_site': '',
            'progress': 0,
            'total_sites': len(sites),
            'results': [],
            'message': '발행 준비 중...'
        })
        
        def background_publish():
            try:
                from datetime import datetime, timedelta
                from src.utils.schedule_manager import schedule_manager
                import requests
                
                today = datetime.now().date()
                add_system_log('INFO', f'수동발행 시작: {today} - {len(sites)}개 사이트', 'MANUAL')
                
                for i, site in enumerate(sites):
                    publish_status.update({
                        'current_site': site,
                        'progress': int((i / len(sites)) * 100),
                        'message': f'{site} 발행 중...'
                    })
                    
                    try:
                        # API에서 주간 스케줄 가져오기
                        weekday = today.weekday()
                        week_start = today - timedelta(days=weekday)
                        
                        # 미리보기 API와 동일한 로직으로 주제 가져오기
                        today_str = today.strftime('%Y-%m-%d')
                        database = get_database()
                        conn = database.get_connection()
                        
                        # 수익 최우선 계획표에서 가져오기
                        from auto_weekly_planner import ProfitWeeklyPlanner
                        planner = ProfitWeeklyPlanner()
                        
                        topic_data = None
                        try:
                            # 오늘의 수익 최우선 주제 가져오기
                            today_topics = planner.get_today_profit_topics()
                            
                            # 사이트별 주제 찾기
                            for topic_info in today_topics:
                                if topic_info['site'] == site:
                                    topic_data = {
                                        'topic': topic_info['title'],
                                        'category': topic_info['category'],
                                        'keywords': topic_info.get('keywords', [])
                                    }
                                    add_system_log('INFO', f'{site} 수익 최우선 계획 사용: {topic_data["topic"]} (카테고리: {topic_data["category"]}, 트렌드점수: {topic_info.get("trend_score", 0)})', 'PROFIT_SCHEDULE')
                                    break
                        except Exception as e:
                            add_system_log('WARNING', f'수익 계획표 조회 실패, DB 폴백: {e}', 'SCHEDULE')
                            
                            # 폴백: DB에서 가져오기
                            with conn.cursor() as cursor:
                                days_since_monday = today.weekday()
                                week_start = today - timedelta(days=days_since_monday)
                                
                                cursor.execute('''
                                SELECT plan_data FROM blog_automation.weekly_plans 
                                WHERE week_start = %s
                                ORDER BY created_at DESC
                                LIMIT 1
                                ''', (week_start,))
                                
                                result = cursor.fetchone()
                                if result:
                                    plan_data = result[0]
                                    plans = plan_data.get('plans', [])
                                    
                                    # 오늘 날짜, 현재 사이트에 해당하는 계획 찾기
                                    today_plan = next((plan for plan in plans 
                                                     if plan.get('date') == today_str and plan.get('site') == site), None)
                                    
                                    if today_plan:
                                        topic_data = {
                                            'topic': today_plan.get('title'),
                                            'category': today_plan.get('category'),
                                            'keywords': today_plan.get('keywords', [site])
                                        }
                                        add_system_log('INFO', f'{site} DB 계획 사용: {topic_data["topic"]}', 'SCHEDULE')
                        
                        if topic_data:
                            topic = topic_data['topic']
                            category = topic_data['category'] 
                            keywords = topic_data.get('keywords', [site])
                            add_system_log('INFO', f'{site}: {topic}', 'SCHEDULE')
                        else:
                            # 미리보기 API와 동일한 대체 주제 사용
                            topic = f'오늘의 {site.upper()} 추천 주제'
                            category = '일반'
                            keywords = ['오늘', '추천', '주제']
                            add_system_log('WARNING', f'{site}: 대체 주제 사용 - {topic}', 'FALLBACK')
                        
                        # 직접 콘텐츠 생성 (HTTP 호출 대신)
                        try:
                            # 콘텐츠 생성기 사용
                            generator = ContentGenerator()
                            
                            # 사이트별 설정
                            if site == 'tistory':
                                from src.generators.tistory_content_exporter import TistoryContentExporter
                                exporter = TistoryContentExporter()
                                site_config = {
                                    'name': 'TISTORY',
                                    'categories': [category],
                                    'content_style': '친근하고 읽기 쉬운 톤',
                                    'target_audience': '일반 대중',
                                    'keywords_focus': keywords
                                }
                            else:
                                from src.generators.wordpress_content_exporter import WordPressContentExporter
                                exporter = WordPressContentExporter()
                                site_config = {
                                    'name': site.upper(),
                                    'categories': [category],
                                    'content_style': '전문적이고 신뢰할 수 있는 톤',
                                    'target_audience': '관심 있는 독자들',
                                    'keywords_focus': keywords
                                }
                            
                            # 콘텐츠 생성
                            content_data = generator.generate_content(
                                site_config,
                                topic,
                                category,
                                None,  # existing_posts
                                'medium',  # content_length
                                site  # site_key for API tracking
                            )
                            
                            if content_data:
                                # 파일로 내보내기
                                if site == 'tistory':
                                    filepath = exporter.export_content(content_data)
                                else:
                                    filepath = exporter.export_content(site, content_data)
                                
                                # DB에 저장
                                file_id = db.add_content_file(
                                    site=site,
                                    title=content_data['title'],
                                    file_path=filepath,
                                    file_type='tistory' if site == 'tistory' else 'wordpress',
                                    metadata={
                                        'category': category,
                                        'tags': content_data.get('tags', []),
                                        'manual_published': True,
                                        'published_at': datetime.now(timezone(timedelta(hours=9))).isoformat()
                                    }
                                )
                                
                                # 발행 상태 업데이트
                                db.update_file_status(file_id, 'published', datetime.now())

                                # WordPress 업로드 (WordPress 사이트만)
                                upload_result = None
                                publish_url = None
                                if upload_to_wordpress and site in ['unpre', 'untab', 'skewese']:
                                    try:
                                        from src.publishers.wordpress_publisher import WordPressPublisher
                                        import json
                                        
                                        # WordPress 설정 로드
                                        config_path = 'config/wordpress_sites.json'
                                        if os.path.exists(config_path):
                                            with open(config_path, 'r', encoding='utf-8') as f:
                                                wp_config = json.load(f)
                                            
                                            if site in wp_config:
                                                publisher = WordPressPublisher(wp_config[site])
                                                
                                                wp_content = {
                                                    'title': content_data['title'],
                                                    'content': content_data['content'],
                                                    'excerpt': content_data.get('summary', '')[:100],
                                                    'status': 'publish'
                                                }
                                                
                                                upload_result = publisher.publish_post(wp_content)
                                                if upload_result and upload_result.get('success'):
                                                    publish_url = upload_result.get('url')
                                                    add_system_log('INFO', f'{site} WordPress 업로드 성공: {publish_url}', 'SUCCESS')
                                                else:
                                                    add_system_log('ERROR', f'{site} WordPress 업로드 실패: {upload_result.get("error")}', 'ERROR')
                                    except Exception as wp_error:
                                        add_system_log('ERROR', f'{site} WordPress 업로드 오류: {wp_error}', 'ERROR')

                                # 발행 이력 기록 (publish_history 테이블)
                                try:
                                    from datetime import timezone, timedelta
                                    kst = timezone(timedelta(hours=9))
                                    publish_status_val = 'success' if (not upload_to_wordpress or site == 'tistory' or upload_result.get('success')) else 'partial'
                                    error_msg = None if publish_status_val == 'success' else upload_result.get('error') if upload_result else None

                                    conn = db.get_connection()
                                    with conn.cursor() as cursor:
                                        cursor.execute(f'''
                                            INSERT INTO {db.schema}.publish_history
                                            (site, content_file_id, publish_type, publish_status, error_message,
                                             published_at, publish_url, response_data)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                                        ''', (
                                            site,
                                            file_id,
                                            'manual',
                                            publish_status_val,
                                            error_msg,
                                            datetime.now(kst),
                                            publish_url,
                                            json.dumps({'manual_publish': True, 'upload_to_wordpress': upload_to_wordpress}, ensure_ascii=False)
                                        ))
                                        conn.commit()
                                except Exception as history_error:
                                    add_system_log('WARNING', f'{site} 발행 이력 기록 실패: {history_error}', 'WARNING')

                                # 결과에 WordPress 업로드 정보 포함
                                result_message = f'{site} 발행 성공'
                                if upload_result:
                                    if upload_result.get('success'):
                                        result_message += f' + WordPress 업로드 성공'
                                    else:
                                        result_message += f' (WordPress 업로드 실패)'
                                
                                publish_status['results'].append({
                                    'site': site,
                                    'success': True,
                                    'message': result_message,
                                    'topic': topic,
                                    'wordpress_upload': upload_result
                                })
                                add_system_log('INFO', f'{site} 발행 성공: {topic}', 'SUCCESS')
                            else:
                                publish_status['results'].append({
                                    'site': site,
                                    'success': False,
                                    'message': f'{site} 콘텐츠 생성 실패',
                                    'topic': topic
                                })
                                add_system_log('ERROR', f'{site} 콘텐츠 생성 실패', 'ERROR')
                        
                        except Exception as content_error:
                            publish_status['results'].append({
                                'site': site,
                                'success': False,
                                'message': f'{site} 콘텐츠 생성 오류: {str(content_error)}',
                                'topic': topic
                            })
                            add_system_log('ERROR', f'{site} 콘텐츠 생성 오류: {content_error}', 'ERROR')
                            
                    except Exception as site_error:
                        publish_status['results'].append({
                            'site': site,
                            'success': False,
                            'message': f'{site} 오류: {str(site_error)}',
                            'topic': topic if 'topic' in locals() else '알 수 없음'
                        })
                        add_system_log('ERROR', f'{site} 오류: {site_error}', 'ERROR')
                
                # 완료 처리
                success_count = sum(1 for r in publish_status['results'] if r['success'])
                publish_status.update({
                    'in_progress': False,
                    'progress': 100,
                    'message': f'발행 완료: {success_count}/{len(sites)} 성공'
                })
                add_system_log('INFO', f'수동발행 완료: {success_count}/{len(sites)} 성공', 'COMPLETE')
                
            except Exception as e:
                publish_status.update({
                    'in_progress': False,
                    'message': f'발행 오류: {str(e)}'
                })
                add_system_log('ERROR', f'전체 발행 오류: {e}', 'ERROR')
        
        import threading
        threading.Thread(target=background_publish, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': f'{len(sites)}개 사이트 발행이 시작되었습니다.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'발행 시작 실패: {str(e)}'
        }), 500

@app.route('/api/manual-publish', methods=['POST'])
def manual_publish():
    """수동 발행 (대시보드용)"""
    # quick_publish와 동일한 로직을 사용
    return quick_publish()

@app.route('/api/schedule/auto_publish', methods=['POST'])
def manual_auto_publish():
    """수동으로 자동 발행 실행"""
    try:
        data = request.json
        sites = data.get('sites', ['unpre', 'untab', 'skewese', 'tistory'])
        
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
                from src.utils.schedule_manager import ScheduleManager
                from datetime import datetime, timedelta
                
                schedule_manager = ScheduleManager()
                
                # 오늘의 계획된 주제 가져오기
                scheduled_topic = schedule_manager.get_today_scheduled_topic(site)
                
                if scheduled_topic:
                    topic = scheduled_topic['topic']
                    keywords = scheduled_topic['keywords']
                    category = scheduled_topic['category']
                    logger.info(f"[SCHEDULE] {site} 스케줄 주제 사용: {topic}")
                else:
                    # 스케줄에 없으면 기본 주제 사용
                    topic_map = {
                        'unpre': 'Python 기초 프로그래밍 완벽 가이드',
                        'untab': '2025년 부동산 투자 전략 분석',
                        'skewese': '조선왕조 역사 속 숨겨진 이야기'
                    }
                    topic = topic_map.get(site, 'IT 기술 트렌드')
                    keywords = [site, '가이드']
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
                                    if scheduled_topic:
                                        try:
                                            today = datetime.now().date()
                                            week_start = today - timedelta(days=today.weekday())
                                            day_of_week = today.weekday()
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
    <title>{generated_content.get('title', '제목')}</title>
    <meta name="description" content="{generated_content.get('meta_description', '설명')}"
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
                    <h2>{section.get('heading', '섹션')}</h2>
                    <div class="section-content">
                        {_format_section_content(section.get('content', '내용'))}
                    </div>
                </section>
''' for section in generated_content.get('sections', [])])}
            </main>
            
            <footer>
                <section class="conclusion">
                    <h2>마무리</h2>
                    <p>{generated_content.get('conclusion', generated_content.get('additional_content', '이상으로 마무리하겠습니다.'))}</p>
                </section>
                
                <div class="tags">
                    <strong style="display: block; margin-bottom: 15px; color: #667eea; font-size: 1.1em;">🏷️ 관련 태그</strong>
                    {''.join([f'<span class="tag">{tag}</span>' for tag in generated_content.get('tags', [])])}
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

# 자동 발행 스케줄러 설정
scheduler = None

def auto_publish_task():
    """매일 새벽 3시 자동 발행 작업 - 날짜별 스케줄 기반"""
    try:
        add_system_log('INFO', '🚀 자동 발행 작업 시작 (새벽 3시)', 'SCHEDULER')
        logger.info("🚀 새벽 3시 자동 발행 작업 시작")
        
        # 시간 기록
        from datetime import datetime, timedelta
        import pytz
        from src.scheduler import BlogAutomationScheduler
        kst = pytz.timezone('Asia/Seoul')
        start_time = datetime.now(kst)
        
        # BlogAutomationScheduler 초기화
        blog_scheduler = BlogAutomationScheduler()
        
        # 오늘 날짜 기반 스케줄 계산 (수동 발행과 동일한 로직)
        today = start_time.date()
        day_of_week_raw = today.weekday()  # 0=월요일, 6=일요일
        if day_of_week_raw == 6:  # 일요일인 경우
            week_start = today + timedelta(days=1)
            day_of_week = 6
        else:
            week_start = today - timedelta(days=day_of_week_raw)
            day_of_week = day_of_week_raw
        
        add_system_log('INFO', f'발행 대상 날짜: {today} (주차: {week_start}, 요일: {day_of_week})', 'SCHEDULER')
        
        # WordPress 사이트들 자동 발행 (스케줄러를 통해 계획된 주제 사용)
        wordpress_sites = ['unpre', 'untab', 'skewese']
        
        # 스케줄 데이터 로드
        from src.utils.schedule_manager import schedule_manager
        schedule_data = schedule_manager.get_weekly_schedule(week_start)
        
        # DB 연결 실패시 목업 스케줄 데이터 생성
        if not schedule_data or not schedule_data.get('schedule'):
            add_system_log('WARNING', 'DB 연결 실패로 목업 스케줄 데이터 사용', 'SCHEDULER')
            schedule_data = {
                'week_start': week_start,
                'schedule': {}
            }
            
            # 이번 주 7일간 스케줄 생성
            for day_idx in range(7):
                day_date = week_start + timedelta(days=day_idx)
                day_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
                
                # 날짜별 다양한 주제 자동 생성
                day_seed = day_date.toordinal()  # 날짜를 숫자로 변환 (일관성 있는 랜덤 시드)
                import random
                random.seed(day_seed)
                
                # 사이트별 주제 풀
                unpre_topics = [
                    f"Python {day_date.year}년 {day_date.month}월 최신 라이브러리와 프레임워크",
                    f"JavaScript ES6+ 고급 기능 완벽 가이드 ({day_date.month}/{day_date.day})",
                    f"React vs Vue.js 성능 비교 분석 - {day_date.year}년 버전", 
                    f"Docker와 Kubernetes 실전 활용법 {day_date.month}월 업데이트",
                    f"AI/ML 개발자를 위한 TensorFlow 최신 기능 ({day_date.day}일 특집)",
                    f"웹 개발 보안 가이드 - {day_date.year}.{day_date.month:02d} 보안 패치",
                    f"클라우드 네이티브 개발 전략과 도구 ({day_date.month}월 {day_date.day}일)",
                    f"DevOps 자동화 파이프라인 구축 가이드 - {day_date.year}년 최신판",
                    f"마이크로서비스 아키텍처 설계 패턴 ({day_date.month}/{day_date.day} 업데이트)",
                    f"GraphQL vs REST API 선택 가이드 - {day_date.year}년 {day_date.month}월 기준"
                ]
                
                untab_topics = [
                    f"{day_date.year}년 {day_date.month}월 부동산 시장 전망과 투자 전략",
                    f"경매 부동산 투자 가이드 - {day_date.month}/{day_date.day} 시장 분석",
                    f"서울 아파트 가격 동향과 미래 전망 ({day_date.year}.{day_date.month:02d})",
                    f"부동산 정책 변화가 투자에 미치는 영향 - {day_date.month}월 {day_date.day}일",
                    f"지방 부동산 투자의 새로운 기회 ({day_date.year}년 {day_date.month}월)",
                    f"부동산 펀드 vs 직접 투자 비교 분석 - {day_date.day}일 특집",
                    f"상업용 부동산 투자 트렌드와 수익률 ({day_date.month}/{day_date.day})",
                    f"재개발·재건축 투자 전략 가이드 - {day_date.year}년 상반기",
                    f"부동산 세금 절약 전략과 팁 ({day_date.month}월 {day_date.day}일 버전)",
                    f"해외 부동산 투자 기회와 리스크 - {day_date.year}.{day_date.month:02d}"
                ]
                
                skewese_topics = [
                    f"조선왕조 {day_date.month}월의 역사적 사건들과 그 의미",
                    f"고구려 문화유산 탐방기 - {day_date.year}년 {day_date.month}월 {day_date.day}일",
                    f"한국 전통 음식의 역사와 유래 ({day_date.month}/{day_date.day} 특집)",
                    f"조선시대 과거제도와 교육 시스템 - {day_date.year}년 재조명",
                    f"백제 역사 재발견 - {day_date.month}월 {day_date.day}일 고고학 뉴스",
                    f"한국사 속 여성 인물들의 삶과 업적 ({day_date.year}.{day_date.month:02d})",
                    f"조선 후기 문화 르네상스와 실학 사상 - {day_date.month}/{day_date.day}",
                    f"고려시대 불교 문화와 예술 ({day_date.year}년 {day_date.month}월 연구)",
                    f"한국 전통 건축의 과학적 원리 - {day_date.day}일 건축사 탐구",
                    f"조선왕조실록에서 찾은 흥미로운 이야기들 ({day_date.month}월)"
                ]
                
                tistory_topics = [
                    f"{day_date.year}년 {day_date.month}월 IT 산업 주요 뉴스와 트렌드",
                    f"AI 기술 발전이 일상에 미치는 영향 - {day_date.month}/{day_date.day}",
                    f"메타버스 플랫폼 최신 동향과 미래 ({day_date.year}.{day_date.month:02d})",
                    f"블록체인과 암호화폐 시장 분석 - {day_date.month}월 {day_date.day}일",
                    f"스마트폰 기술 혁신과 차세대 디바이스 ({day_date.year}년 전망)",
                    f"5G와 6G 통신 기술 발전 현황 - {day_date.day}일 통신 뉴스",
                    f"클라우드 컴퓨팅 시장 동향과 전망 ({day_date.month}/{day_date.day})",
                    f"게임 산업 트렌드와 e스포츠 성장 - {day_date.year}년 {day_date.month}월",
                    f"자율주행차 기술 발전과 상용화 전망 ({day_date.month}월 업데이트)",
                    f"스타트업 생태계와 투자 트렌드 - {day_date.year}.{day_date.month:02d}"
                ]
                
                schedule_data['schedule'][day_idx] = {
                    'day_name': day_names[day_idx],
                    'date': day_date,
                    'sites': {
                        'unpre': {
                            'category': 'programming',
                            'topic': random.choice(unpre_topics),
                            'keywords': ['프로그래밍', '개발', 'IT', 'Python', 'JavaScript'],
                            'status': 'planned'
                        },
                        'untab': {
                            'category': 'realestate', 
                            'topic': random.choice(untab_topics),
                            'keywords': ['부동산', '투자', '아파트', '경매', '정책'],
                            'status': 'planned'
                        },
                        'skewese': {
                            'category': 'koreanhistory',
                            'topic': random.choice(skewese_topics),
                            'keywords': ['조선시대', '한국사', '전통문화', '역사', '문화재'],
                            'status': 'planned'
                        },
                        'tistory': {
                            'category': 'current',
                            'topic': random.choice(tistory_topics),
                            'keywords': ['IT', '기술', '트렌드', 'AI', '뉴스'],
                            'status': 'planned'
                        }
                    }
                }
        
        add_system_log('INFO', f'스케줄 데이터 로드 완료: {len(schedule_data.get("schedule", {}))}일', 'SCHEDULER')
        
        # 모든 사이트 자동 발행 (WordPress 3개 + tistory)
        sites_to_publish = ['unpre', 'untab', 'skewese', 'tistory']
        success_count = 0
        
        for site in sites_to_publish:
            try:
                add_system_log('INFO', f'{site.upper()} 발행 시작...', 'SCHEDULER')
                # 스케줄러의 create_and_publish_post는 스케줄 매니저를 통해 오늘 주제를 가져옴
                success = blog_scheduler.create_and_publish_post(site)
                if success:
                    success_count += 1
                    add_system_log('SUCCESS', f'✅ {site.upper()} 자동 발행 성공', 'SCHEDULER')
                    logger.info(f"✅ {site.upper()} 자동 발행 성공")
                else:
                    add_system_log('WARNING', f'⚠️ {site.upper()} 자동 발행 실패', 'SCHEDULER')
                    logger.warning(f"⚠️ {site.upper()} 자동 발행 실패")
                        
            except Exception as e:
                add_system_log('ERROR', f'❌ {site.upper()} 발행 오류: {str(e)}', 'SCHEDULER')
                logger.error(f"❌ {site.upper()} 자동 발행 오류: {e}")
        
        # 작업 완료 통계
        end_time = datetime.now(kst)
        duration = (end_time - start_time).total_seconds()
        
        add_system_log('INFO', f'📊 자동 발행 완료: {success_count}/{len(sites_to_publish)} 성공, 소요시간: {duration:.1f}초', 'SCHEDULER')
        logger.info(f"✅ 새벽 3시 자동 발행 작업 완료 ({success_count}/{len(sites_to_publish)} 성공)")
        
    except Exception as e:
        add_system_log('ERROR', f'❌ 자동 발행 작업 실패: {str(e)}', 'SCHEDULER')
        logger.error(f"❌ 자동 발행 작업 실패: {e}")

def init_scheduler():
    """스케줄러 초기화 및 시작"""
    global scheduler
    
    try:
        # 타임존 명시적 설정
        from datetime import datetime
        import pytz
        kst = pytz.timezone('Asia/Seoul')
        
        scheduler = BackgroundScheduler(
            timezone=kst,
            job_defaults={'misfire_grace_time': 3600}  # 1시간 지연까지 허용
        )
        
        # 매일 새벽 3시에 자동 발행 (월-일 매일)
        scheduler.add_job(
            func=auto_publish_task,
            trigger=CronTrigger(
                hour=3, 
                minute=0, 
                second=0,
                timezone=kst
            ),
            id='daily_auto_publish',
            name='Daily Auto Publishing at 3AM KST',
            replace_existing=True,
            max_instances=1,  # 중복 실행 방지
            coalesce=True     # 누락된 실행을 하나로 합침
        )
        
        # 추가 안전장치: 매일 오전 9시에도 체크 (발행 안 된 경우)
        scheduler.add_job(
            func=check_and_retry_publish,
            trigger=CronTrigger(
                hour=9, 
                minute=0, 
                second=0,
                timezone=kst
            ),
            id='daily_check_publish',
            name='Daily Check and Retry at 9AM KST',
            replace_existing=True,
            max_instances=1
        )
        
        # 스케줄러 시작
        scheduler.start()
        
        # 프로세스 종료 시 스케줄러 정리
        atexit.register(lambda: scheduler.shutdown() if scheduler else None)
        
        # 현재 시간과 다음 실행 시간 로그
        now = datetime.now(kst)
        add_system_log('SUCCESS', f'🎯 자동 발행 스케줄러 시작 완료! 현재: {now.strftime("%Y-%m-%d %H:%M:%S")}', 'SCHEDULER')
        logger.info("✅ 자동 발행 스케줄러 시작됨 (매일 새벽 3시 KST)")
        
        # 등록된 작업 목록 로그
        jobs = scheduler.get_jobs()
        for job in jobs:
            next_run = job.next_run_time
            add_system_log('INFO', f'⏰ {job.name}: {next_run.strftime("%Y-%m-%d %H:%M:%S KST")}', 'SCHEDULER')
            logger.info(f"⏰ {job.name}: {next_run}")
        
        # 🔥 매주 일요일 밤 11시 30분에 다음주 수익성 최우선 계획 자동 생성
        def auto_generate_next_week_profit_plan():
            """다음주 수익성 최우선 주간계획 자동 생성 - 철저한 에러 방지"""
            try:
                add_system_log('INFO', '🔥 다음주 수익성 최우선 주간계획 자동 생성 시작', 'WEEKLY_PLANNER')
                logger.info("🔥 다음주 수익성 최우선 주간계획 자동 생성 시작")
                
                # 1. 다음주 월요일 계산 (에러 방지)
                try:
                    today = datetime.now(kst).date()
                    days_until_next_monday = (7 - today.weekday()) % 7
                    if days_until_next_monday == 0:  # 오늘이 월요일이면 다다음주
                        days_until_next_monday = 7
                    next_monday = today + timedelta(days=days_until_next_monday)
                    
                    add_system_log('INFO', f'다음주 계획 기준일: {next_monday}', 'WEEKLY_PLANNER')
                    logger.info(f"다음주 계획 기준일: {next_monday}")
                except Exception as date_error:
                    add_system_log('ERROR', f'날짜 계산 실패: {date_error}', 'WEEKLY_PLANNER')
                    logger.error(f"날짜 계산 실패: {date_error}")
                    return
                
                # 2. 기존 다음주 계획 체크 (중복 방지)
                try:
                    from src.utils.postgresql_database import PostgreSQLDatabase
                    db = PostgreSQLDatabase()
                    conn = db.get_connection()
                    
                    with conn.cursor() as cursor:
                        cursor.execute('''
                        SELECT id FROM blog_automation.weekly_plans 
                        WHERE week_start = %s
                        ''', (next_monday,))
                        
                        existing_plan = cursor.fetchone()
                        if existing_plan:
                            add_system_log('INFO', f'다음주 계획이 이미 존재함: {next_monday}', 'WEEKLY_PLANNER')
                            logger.info(f"다음주 계획이 이미 존재함: {next_monday}")
                            return  # 이미 있으면 생성하지 않음
                            
                except Exception as db_check_error:
                    add_system_log('WARNING', f'기존 계획 체크 실패, 계속 진행: {db_check_error}', 'WEEKLY_PLANNER')
                    logger.warning(f"기존 계획 체크 실패, 계속 진행: {db_check_error}")
                
                # 3. 수익성 최우선 주간계획 생성 (안전한 subprocess 실행)
                try:
                    import subprocess
                    import sys
                    
                    # subprocess로 안전하게 실행 (timeout 설정)
                    result = subprocess.run(
                        [sys.executable, 'auto_weekly_planner.py'],
                        cwd=os.path.dirname(os.path.abspath(__file__)),
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5분 timeout
                        encoding='utf-8'
                    )
                    
                    if result.returncode == 0:
                        add_system_log('SUCCESS', '🎉 다음주 수익성 최우선 주간계획 자동 생성 완료!', 'WEEKLY_PLANNER')
                        logger.info("🎉 다음주 수익성 최우선 주간계획 자동 생성 완료!")
                        
                        # 성공 로그에 결과 요약 포함
                        output_lines = result.stdout.split('\n')[-10:]  # 마지막 10줄만
                        for line in output_lines:
                            if line.strip():
                                add_system_log('INFO', f'생성결과: {line.strip()}', 'WEEKLY_PLANNER')
                    else:
                        add_system_log('ERROR', f'주간계획 생성 실패 (exit code: {result.returncode})', 'WEEKLY_PLANNER')
                        add_system_log('ERROR', f'stderr: {result.stderr}', 'WEEKLY_PLANNER')
                        logger.error(f"주간계획 생성 실패: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    add_system_log('ERROR', '주간계획 생성 타임아웃 (5분)', 'WEEKLY_PLANNER')
                    logger.error("주간계획 생성 타임아웃")
                except Exception as subprocess_error:
                    add_system_log('ERROR', f'주간계획 생성 프로세스 실패: {subprocess_error}', 'WEEKLY_PLANNER')
                    logger.error(f"주간계획 생성 프로세스 실패: {subprocess_error}")
                
                # 4. 생성 완료 후 검증
                try:
                    time.sleep(2)  # 잠깐 대기
                    with conn.cursor() as cursor:
                        cursor.execute('''
                        SELECT plan_data FROM blog_automation.weekly_plans 
                        WHERE week_start = %s
                        ORDER BY created_at DESC LIMIT 1
                        ''', (next_monday,))
                        
                        new_plan = cursor.fetchone()
                        if new_plan:
                            plan_data = json.loads(new_plan[0])
                            plan_count = len(plan_data.get('plans', []))
                            add_system_log('SUCCESS', f'✅ 생성 검증 완료: {plan_count}개 계획 저장됨', 'WEEKLY_PLANNER')
                            logger.info(f"✅ 생성 검증 완료: {plan_count}개 계획")
                        else:
                            add_system_log('WARNING', '⚠️ 계획 생성 후 DB에서 확인되지 않음', 'WEEKLY_PLANNER')
                            
                except Exception as verify_error:
                    add_system_log('WARNING', f'생성 검증 실패: {verify_error}', 'WEEKLY_PLANNER')
                    
            except Exception as main_error:
                add_system_log('ERROR', f'주간계획 자동생성 메인 에러: {main_error}', 'WEEKLY_PLANNER')
                logger.error(f"주간계획 자동생성 메인 에러: {main_error}")
            finally:
                add_system_log('INFO', '다음주 주간계획 자동생성 작업 종료', 'WEEKLY_PLANNER')
        
        # 매주 일요일 밤 11시 30분에 다음주 계획 생성
        scheduler.add_job(
            func=auto_generate_next_week_profit_plan,
            trigger=CronTrigger(
                day_of_week=6,  # 일요일 (0=월요일, 6=일요일)
                hour=23,
                minute=30,
                second=0,
                timezone=kst
            ),
            id='weekly_plan_auto_generate',
            name='Next Week Profit-First Plan Auto Generator',
            replace_existing=True,
            max_instances=1,  # 중복 실행 방지
            coalesce=True     # 누락된 실행을 하나로 합침
        )
        
        # 테스트용 즉시 실행 (첫 시작 시에만)
        from datetime import timedelta
        add_system_log('INFO', '🔧 스케줄러 테스트를 위해 30초 후 테스트 실행 예약', 'SCHEDULER')
        scheduler.add_job(
            func=test_scheduler_health,
            trigger='date',
            run_date=datetime.now(kst) + timedelta(seconds=30),
            id='scheduler_test',
            name='Scheduler Health Test'
        )
        
        return True
        
    except Exception as e:
        add_system_log('ERROR', f'❌ 스케줄러 초기화 실패: {str(e)}', 'SCHEDULER')
        logger.error(f"❌ 스케줄러 초기화 실패: {e}")
        return False

def check_and_retry_publish():
    """오전 9시 체크: 새벽 3시에 발행되지 않은 경우 재시도"""
    try:
        from datetime import datetime, timedelta
        import pytz
        kst = pytz.timezone('Asia/Seoul')
        
        today = datetime.now(kst).date()
        today_3am = datetime.combine(today, datetime.min.time().replace(hour=3)).replace(tzinfo=kst)
        
        add_system_log('INFO', '🔍 오전 9시 발행 상태 체크 시작', 'SCHEDULER')
        
        # 오늘 새벽 3시 이후 발행된 게시물 확인
        db = get_database()
        sites_to_retry = []
        
        for site in ['unpre', 'untab', 'skewese']:
            recent_posts = db.get_recent_posts(site, 1)
            
            if not recent_posts:
                sites_to_retry.append(site)
                add_system_log('WARNING', f'{site.upper()}: 오늘 발행된 게시물 없음', 'SCHEDULER')
            else:
                last_post_time = recent_posts[0].get('created_at')
                if last_post_time:
                    # 날짜 문자열을 datetime으로 변환
                    if isinstance(last_post_time, str):
                        last_post_dt = datetime.fromisoformat(last_post_time.replace('Z', '+00:00'))
                        if last_post_dt.tzinfo is None:
                            last_post_dt = last_post_dt.replace(tzinfo=kst)
                    else:
                        last_post_dt = last_post_time
                    
                    if last_post_dt < today_3am:
                        sites_to_retry.append(site)
                        add_system_log('WARNING', f'{site.upper()}: 마지막 발행이 새벽 3시 이전', 'SCHEDULER')
                    else:
                        add_system_log('SUCCESS', f'{site.upper()}: 오늘 정상 발행됨', 'SCHEDULER')
        
        # 재시도가 필요한 사이트들 발행
        if sites_to_retry:
            add_system_log('INFO', f'🔄 재시도 발행 시작: {", ".join(sites_to_retry)}', 'SCHEDULER')
            
            from src.scheduler import BlogAutomationScheduler
            blog_scheduler = BlogAutomationScheduler()
            
            for site in sites_to_retry:
                try:
                    success = blog_scheduler.create_and_publish_post(site)
                    if success:
                        add_system_log('SUCCESS', f'✅ {site.upper()} 재시도 발행 성공', 'SCHEDULER')
                    else:
                        add_system_log('ERROR', f'❌ {site.upper()} 재시도 발행 실패', 'SCHEDULER')
                except Exception as e:
                    add_system_log('ERROR', f'❌ {site.upper()} 재시도 오류: {str(e)}', 'SCHEDULER')
        else:
            add_system_log('SUCCESS', '✅ 모든 사이트 정상 발행 확인됨', 'SCHEDULER')
            
    except Exception as e:
        add_system_log('ERROR', f'❌ 발행 상태 체크 실패: {str(e)}', 'SCHEDULER')

def test_scheduler_health():
    """스케줄러 상태 테스트"""
    try:
        from datetime import datetime
        import pytz
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        
        add_system_log('SUCCESS', f'✅ 스케줄러 정상 작동 중! 테스트 시간: {now.strftime("%H:%M:%S")}', 'SCHEDULER')
        logger.info(f"✅ 스케줄러 헬스 체크 성공: {now}")
        
        # 다음 예정 작업들 확인
        global scheduler
        if scheduler:
            jobs = scheduler.get_jobs()
            add_system_log('INFO', f'📋 등록된 작업 수: {len(jobs)}개', 'SCHEDULER')
            for job in jobs:
                if job.next_run_time:
                    add_system_log('INFO', f'  - {job.name}: {job.next_run_time.strftime("%m/%d %H:%M")}', 'SCHEDULER')
        
    except Exception as e:
        add_system_log('ERROR', f'❌ 스케줄러 헬스 체크 실패: {str(e)}', 'SCHEDULER')


def generate_dynamic_schedule(start_date):
    """주차별로 동적 스케줄 생성 (주차별 다른 시드 사용)"""
    import random
    from datetime import timedelta
    
    # 주차별 고유 시드 생성 (start_date 기준)
    week_seed = start_date.toordinal()
    random.seed(week_seed)
    
    # 사이트별 주제 풀
    unpre_topics = [
        "JWT 토큰 기반 시큐리티 구현", "DDD(도메인 주도 설계) 실전 적용", "C++ 최신 프로그래밍 기법",
        "Kotlin으로 Android 앱 개발", "Python 데이터 분석 마스터", "React Hook 고급 활용법",
        "Docker 컨테이너 최적화", "Spring Boot 마이크로서비스", "GraphQL API 설계 원칙"
    ]
    
    untab_topics = [
        "친환경 부동산 그린 리모델링 트렌드", "고령화 사회와 실버타운 투자", "인플레이션 시대의 투자 가이드",
        "공모주 투자 전략 분석", "메타버스 부동산 투자", "ESG 투자의 미래 전망",
        "부동산 경매 투자의 새로운 기회", "암호화폐와 전통 자산 포트폴리오"
    ]
    
    skewese_topics = [
        "조선시대 과학기술의 발전과 역사", "수면의 과학과 질 좋은 잠자리", "신라 통일의 과정과 역사적 의미",
        "고려 몽골 침입과 강화도 항쟁", "4.19혁명과 민주주의 발전", "임진왜란과 이순신의 활약",
        "한국 전통 건축의 아름다움과 과학", "정조의 개혁 정치와 화성 건설"
    ]
    
    tistory_topics = [
        "2025년 ChatGPT-5와 차세대 AI 혁신", "재건축 규제 완화, 시장 변화 예상", "MZ세대 투자 패턴 분석, 부작용은?",
        "인플레이션 재부상? 2025년 전망", "2026 월드컵 공동개최, 한국 축구 재도약", "K-문화 글로벌 확산 현황",
        "비트코인 10만달러 돌파 후 전망", "저출산 대책 실효성 논란"
    ]
    
    site_topics = {
        'unpre': unpre_topics,
        'untab': untab_topics, 
        'skewese': skewese_topics,
        'tistory': tistory_topics
    }
    
    schedule = {}
    day_names = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일']
    
    for day in range(7):
        schedule[day] = {
            'day_name': day_names[day],
            'date': start_date + timedelta(days=day),
            'sites': {}
        }
        
        for site, topics in site_topics.items():
            # 주차+요일+사이트별 고유 인덱스 계산
            topic_index = (week_seed + day * 10 + hash(site)) % len(topics)
            topic = topics[topic_index]
            
            schedule[day]['sites'][site] = {
                'category': 'programming' if site == 'unpre' else 
                           'realestate' if site == 'untab' else
                           'koreanhistory' if site == 'skewese' else 'current',
                'topic': topic,
                'keywords': [site, topic.split()[0]],
                'length': 'long' if len(topic) > 20 else 'medium',
                'status': 'planned',
                'url': None
            }
    
    return {
        'week_start': start_date,
        'schedule': schedule
    }


# 누락된 API 엔드포인트 추가

@app.route('/api/weekly-plan/current')
def get_current_weekly_plan():
    """현재 주간 계획표 조회"""
    try:
        from datetime import datetime, timedelta
        import json
        
        # 현재 주의 월요일 구하기
        today = datetime.now().date()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        database = get_database()
        conn = database.get_connection()
        
        with conn.cursor() as cursor:
            cursor.execute('''
            SELECT plan_data FROM blog_automation.weekly_plans 
            WHERE week_start = %s
            ORDER BY created_at DESC
            LIMIT 1
            ''', (week_start,))
            
            result = cursor.fetchone()
            
            if result:
                plan_data = result[0]  # JSONB 데이터
                return jsonify({
                    'success': True,
                    'data': plan_data
                })
            else:
                # 주간계획이 없으면 빈 데이터 반환
                return jsonify({
                    'success': True,
                    'data': {
                        'week_start': week_start.strftime('%Y-%m-%d'),
                        'week_end': (week_start + timedelta(days=6)).strftime('%Y-%m-%d'),
                        'plans': [],
                        'message': '주간계획이 없습니다. 자동 생성을 실행해주세요.'
                    }
                })
                
    except Exception as e:
        logger.error(f"주간계획 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/manual-publish/preview')
def get_manual_publish_preview():
    """수동 발행 미리보기 - 오늘 날짜에 해당하는 주간계획 주제 표시"""
    try:
        from datetime import datetime, date, timedelta
        import json
        
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        
        # 오늘 날짜의 주간계획 조회
        database = get_database()
        conn = database.get_connection()
        
        with conn.cursor() as cursor:
            # 현재 주의 월요일 계산
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
            
            cursor.execute('''
            SELECT plan_data FROM blog_automation.weekly_plans 
            WHERE week_start = %s
            ORDER BY created_at DESC
            LIMIT 1
            ''', (week_start,))
            
            result = cursor.fetchone()
            today_contents = []
            
            if result:
                plan_data = result[0]  # JSONB 데이터
                plans = plan_data.get('plans', [])
                
                # 오늘 날짜에 해당하는 계획들 필터링
                today_plans = [plan for plan in plans if plan.get('date') == today_str]
                
                for plan in today_plans:
                    today_contents.append({
                        'site': plan.get('site'),
                        'title': plan.get('title'),
                        'category': plan.get('category'),
                        'priority': plan.get('priority'),
                        'trend_score': plan.get('trend_score'),
                        'keywords': plan.get('keywords', []),
                        'source': plan.get('source'),
                        'original_topic': plan.get('original_topic'),
                        'status': 'ready_to_publish'
                    })
            
            # 기본 사이트 목록
            available_sites = ['unpre', 'untab', 'skewese', 'tistory']
            
            # 오늘 계획이 없는 사이트들을 위한 대체 주제
            planned_sites = [content['site'] for content in today_contents]
            for site in available_sites:
                if site not in planned_sites:
                    # 대체 주제 추가
                    today_contents.append({
                        'site': site,
                        'title': f'오늘의 {site.upper()} 추천 주제',
                        'category': '일반',
                        'priority': 'medium',
                        'trend_score': 50,
                        'keywords': ['오늘', '추천', '주제'],
                        'source': '자동생성',
                        'original_topic': '일반 주제',
                        'status': 'fallback'
                    })
            
            return jsonify({
                'success': True,
                'data': {
                    'date': today_str,
                    'available_sites': available_sites,
                    'contents': today_contents,
                    'total_plans': len(today_contents)
                }
            })
                
    except Exception as e:
        logger.error(f"수동 발행 미리보기 오류: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'data': {
                'available_sites': ['unpre', 'untab', 'skewese', 'tistory'],
                'contents': []
            }
        }), 500

@app.route('/api/trends/realtime')
def get_realtime_trends():
    """실시간 트렌드"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'trends': [],
                'last_updated': '2025-09-08 11:19:49'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/weekly-plan/generate', methods=['POST'])
def generate_weekly_plan():
    """주간계획 자동 생성"""
    try:
        import subprocess
        import sys
        
        # 자동 주간계획 생성기 실행
        result = subprocess.run(
            [sys.executable, 'auto_weekly_planner.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': '주간계획이 성공적으로 생성되었습니다.',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': f'주간계획 생성 실패: {result.stderr}',
                'output': result.stdout
            }), 500
            
    except Exception as e:
        logger.error(f"주간계획 생성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 스케줄러 초기화 (앱 시작 시)
scheduler_initialized = init_scheduler()

if __name__ == "__main__":
    # 시작 로그
    add_system_log('INFO', '블로그 자동화 시스템 시작', 'STARTUP')
    add_system_log('INFO', '새벽 3시 자동발행 스케줄 활성화됨', 'STARTUP')
    add_system_log('INFO', f'웹 대시보드 서버 시작 - http://localhost:8000', 'STARTUP')
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)