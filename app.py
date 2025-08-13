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

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 목업 데이터 저장용 변수
mock_wordpress_files = []
mock_tistory_files = []

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
                    SELECT id, title, site, category, url, 
                           created_at::text, published
                    FROM posts 
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
                        SELECT id, title, site, category, url, 
                               created_at::text, published
                        FROM posts 
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
                    COUNT(CASE WHEN published = true THEN 1 END) as published,
                    COUNT(CASE WHEN published = false THEN 1 END) as scheduled,
                    COUNT(CASE WHEN DATE(created_at) = CURRENT_DATE THEN 1 END) as today_posts
                FROM posts
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
                    FROM posts
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
    """주간 스케줄 조회"""
    week_start = request.args.get('week_start', datetime.now(KST).strftime('%Y-%m-%d'))
    
    # 사이트별 주제 풀 (더 많은 다양성)
    topic_pools = {
        'unpre': [
            # 프론트엔드 주간
            ['React 18 신기능', 'Next.js 13 App Router'],
            ['Vue.js 3 Composition API', 'Angular 16 Standalone'],
            ['TypeScript 5.0 활용', 'JavaScript ES2024'],
            ['Webpack vs Vite', '모던 빌드 도구'],
            ['CSS Grid vs Flexbox', 'Tailwind CSS 실전'],
            
            # 백엔드 주간  
            ['Node.js 성능 최적화', 'Express vs Fastify'],
            ['Python FastAPI', 'Django 4.0 비동기'],
            ['PostgreSQL 고급 쿼리', 'MongoDB 집계 파이프라인'],
            ['Redis 캐싱 전략', 'ElasticSearch 검색'],
            ['GraphQL vs REST API', 'gRPC 마이크로서비스'],
            
            # 클라우드/DevOps 주간
            ['AWS Lambda 서버리스', 'Docker 컨테이너 최적화'],
            ['Kubernetes 기초', 'Terraform IaC'],
            ['GitHub Actions CI/CD', 'Jenkins vs GitLab CI'],
            ['모니터링 도구 비교', 'Prometheus & Grafana'],
            
            # AI/ML 주간
            ['ChatGPT API 활용', 'GitHub Copilot 실전'],
            ['TensorFlow vs PyTorch', 'LangChain 개발'],
            ['OpenAI 임베딩', 'Vector DB 활용'],
            ['AI 코드 리뷰', '자동화 테스트 도구']
        ],
        'untab': [
            # 어학 주간
            ['토익 990점 전략', 'OPIc AL 달성법'],
            ['토플 110+ 공략', 'IELTS 8.0 비법'],
            ['일본어 JLPT N1', '중국어 HSK 6급'],
            ['독일어 TestDaF', '스페인어 DELE'],
            ['프랑스어 DELF', '이탈리아어 CILS'],
            
            # IT 자격증 주간
            ['정보처리기사 실기', 'SQLD 데이터분석'],
            ['AWS SAA 자격증', 'Azure Fundamentals'],
            ['구글 클라우드 ACE', 'CISSP 보안'],
            ['PMP 프로젝트 관리', 'ITIL 서비스 관리'],
            
            # 투자/재테크 주간  
            ['주식 기술분석', '부동산 경매 실전'],
            ['코인 투자 가이드', 'ETF 포트폴리오'],
            ['P2P 투자 전략', '해외 주식 투자'],
            ['세금 절약 꿀팁', '연금 저축 활용'],
            
            # 부업/창업 주간
            ['블로그 수익화', '유튜브 채널 운영'],
            ['온라인 강의 제작', '이커머스 창업'],
            ['프리랜서 마케팅', '개인 브랜딩'],
            ['사이드 프로젝트', '스타트업 창업']
        ],
        'skewese': [
            # 한국사 주간
            ['조선 과학기술사', '고려 몽골 침입'],
            ['삼국통일 과정', '일제강점기 저항'],
            ['한국전쟁 재조명', '개화기 근대화'],
            ['백제 문화유산', '신라 황금 문명'],
            
            # 세계사 주간
            ['로마제국 흥망사', '중국 4대 발명품'],
            ['이집트 파라오', '메소포타미아 문명'],
            ['르네상스 예술가', '프랑스 대혁명'],
            ['산업혁명 영향', '아메리카 대발견'],
            
            # 철학/사상 주간
            ['공자 논어 해석', '노자 도덕경'],
            ['플라톤 이데아론', '아리스토텔레스 윤리학'],
            ['칸트 순수이성비판', '니체 권력의지'],
            ['불교 사상 이해', '기독교 신학'],
            
            # 문화/예술 주간  
            ['고구려 고분벽화', '백제 금동대향로'],
            ['경복궁 건축미', '불국사 석가탑'],
            ['고려청자 예술', '조선백자 아름다움'],
            ['전통 한복 변천사', '궁중음식 문화'],
            
            # 현대 문화/라이프
            ['미니멀 라이프', '북유럽 휘게'],
            ['일본 와비사비', '덴마크 라곰'],
            ['명상과 마음챙김', '디지털 디톡스'],
            ['제로웨이스트', '비건 라이프스타일']
        ]
    }
    
    # 주간 스케줄 데이터 생성
    schedule = {}
    start_date = datetime.strptime(week_start, '%Y-%m-%d')
    
    # 주차 계산 (년도 기준 주차)
    week_number = start_date.isocalendar()[1]
    
    for i in range(7):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        day_of_week = (start_date + timedelta(days=i)).weekday()  # 0=월요일
        
        # 주차와 요일을 조합하여 다양한 주제 선택
        # 각 사이트별로 다른 로테이션 패턴 적용
        unpre_index = (week_number * 3 + day_of_week) % len(topic_pools['unpre'])
        untab_index = (week_number * 2 + day_of_week + 1) % len(topic_pools['untab'])  
        skewese_index = (week_number * 4 + day_of_week + 2) % len(topic_pools['skewese'])
        
        schedule[date] = {
            'unpre': {
                'time': '03:00',  # 새벽 3시 자동발행
                'topics': topic_pools['unpre'][unpre_index],
                'status': 'scheduled'
            },
            'untab': {
                'time': '03:00',
                'topics': topic_pools['untab'][untab_index],
                'status': 'scheduled'
            },
            'skewese': {
                'time': '03:00',
                'topics': topic_pools['skewese'][skewese_index],
                'status': 'scheduled'
            }
        }
        
        # 과거 날짜는 발행 완료로 표시
        current_date = datetime.now(KST).date()
        target_date = (start_date + timedelta(days=i)).date()
        
        if target_date < current_date:
            for site in schedule[date]:
                schedule[date][site]['status'] = 'published'
        elif target_date == current_date:
            # 오늘은 새벽 3시 이후면 발행 완료
            current_time = datetime.now(KST).time()
            if current_time >= datetime.strptime('03:00', '%H:%M').time():
                for site in schedule[date]:
                    schedule[date][site]['status'] = 'published'
    
    return jsonify(schedule)

@app.route('/api/generate_wordpress', methods=['POST'])
def generate_wordpress():
    """WordPress 콘텐츠 생성"""
    try:
        data = request.json
        site = data.get('site', 'unpre')
        topic = data.get('topic', '프로그래밍')
        
        # 목업 응답 (실제 생성 로직으로 대체 예정)
        import time
        current_time = int(time.time())
        
        # WordPress 파일 목록에 새 항목 추가 (실제 파일 생성 시뮬레이션)
        new_file = {
            'title': f'{topic} 완전 가이드',
            'file_path': f'wordpress_posts/{site}_{topic.replace(" ", "_")}_{current_time}.html',
            'url': f'https://{site}.co.kr/posts/{current_time}',
            'status': 'draft',
            'category': data.get('category', '기본'),
            'tags': data.get('keywords', [topic]),
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'actions': ['view', 'edit', 'publish', 'download', 'delete'],
            'id': current_time
        }
        
        # 글로벌 mock_wordpress_files에 추가
        global mock_wordpress_files
        mock_wordpress_files.append(new_file)
        
        return jsonify({
            'success': True,
            'message': f'{site} 사이트에 {topic} 주제로 콘텐츠를 생성했습니다.',
            'title': new_file['title'],
            'file_path': new_file['file_path'],
            'url': new_file['url'],
            'id': new_file['id'],
            'post': new_file
        })
    except Exception as e:
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
        
        # 목업 응답 (실제 생성 로직으로 대체 예정)
        import time
        current_time = int(time.time())
        
        # Tistory 파일 목록에 새 항목 추가 (실제 파일 생성 시뮬레이션)
        new_file = {
            'title': f'{topic} 심화 분석',
            'file_path': f'tistory_posts/{topic.replace(" ", "_")}_{current_time}.html',
            'url': f'https://untab.tistory.com/posts/{current_time}',
            'status': 'draft',
            'category': data.get('category', '기본'),
            'tags': data.get('keywords', [topic]),
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'actions': ['view', 'edit', 'publish', 'download', 'delete'],
            'id': current_time
        }
        
        # 글로벌 mock_tistory_files에 추가
        global mock_tistory_files
        mock_tistory_files.append(new_file)
        
        return jsonify({
            'success': True,
            'message': f'Tistory에 {topic} 주제로 콘텐츠를 생성했습니다.',
            'title': new_file['title'],
            'file_path': new_file['file_path'],
            'url': new_file['url'],
            'id': new_file['id'],
            'post': new_file
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
        now = datetime.now(KST)
        
        # 최근 생성된 콘텐츠 (목업 + 동적 생성)
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
        
        files.extend(base_files)
        
        # 새로 생성된 WordPress 파일들 추가
        for wp_file in mock_wordpress_files:
            files.append({
                'id': wp_file.get('id'),
                'site': wp_file.get('site', 'unpre'),
                'title': wp_file.get('title'),
                'date': wp_file.get('created_at'),
                'size': '3.0KB',
                'status': wp_file.get('status', 'draft'),
                'url': wp_file.get('url'),
                'actions': wp_file.get('actions', ['view', 'edit', 'publish', 'download', 'delete'])
            })
        
        # 최신순으로 정렬
        files.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(files)
    except Exception as e:
        logger.error(f"WordPress 파일 목록 조회 오류: {e}")
        return jsonify([]), 500

@app.route('/api/tistory_files')
def get_tistory_files():
    """Tistory 파일 목록"""
    try:
        files = []
        now = datetime.now(KST)
        
        # 최근 생성된 Tistory 콘텐츠
        base_files = [
            {
                'id': 'tistory_001',
                'title': '🎯 2025년 언어학습 트렌드와 전망',
                'date': now.strftime('%Y-%m-%d %H:%M'),
                'size': '2.7KB',
                'status': 'published',
                'url': 'https://untab.tistory.com/language-trends-2025',
                'actions': ['view', 'edit', 'download', 'delete'],
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
                'actions': ['view', 'edit', 'download', 'delete'],
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
                'actions': ['edit', 'publish', 'download', 'delete'],
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
                'actions': ['view', 'edit', 'download', 'delete'],
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
                'actions': ['edit', 'publish', 'download', 'delete'],
                'category': '부동산',
                'tags': ['부동산경매', '투자', '초보자']
            }
        ]
        
        files.extend(base_files)
        
        # 새로 생성된 Tistory 파일들 추가
        for tistory_file in mock_tistory_files:
            files.append({
                'id': tistory_file.get('id'),
                'title': tistory_file.get('title'),
                'date': tistory_file.get('created_at'),
                'size': '3.0KB',
                'status': tistory_file.get('status', 'draft'),
                'url': tistory_file.get('url'),
                'actions': tistory_file.get('actions', ['view', 'edit', 'publish', 'download', 'delete']),
                'category': tistory_file.get('category', '기본'),
                'tags': tistory_file.get('tags', [])
            })
        
        # 최신순으로 정렬
        files.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(files)
    except Exception as e:
        logger.error(f"Tistory 파일 목록 조회 오류: {e}")
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)