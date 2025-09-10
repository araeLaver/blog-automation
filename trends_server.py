#!/usr/bin/env python3
"""
실시간 트렌드 대시보드 전용 서버
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.trend_collector import trend_collector
from src.utils.keyword_research import keyword_researcher

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """메인 페이지 - 트렌드 대시보드로 리다이렉트"""
    return render_template('trends_dashboard.html')

@app.route('/trends')
def trends_dashboard():
    """실시간 트렌드 대시보드 페이지"""
    return render_template('trends_dashboard.html')

@app.route('/api/trends/realtime')
def get_realtime_trends():
    """실시간 트렌드 데이터 수집"""
    try:
        logger.info("실시간 트렌드 데이터 수집 시작...")
        
        # 카테고리별 트렌드 수집
        categorized_trends = trend_collector.get_categorized_trends()
        
        # 데이터를 JSON 직렬화 가능한 형태로 변환
        json_trends = {}
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
        
        # 통계 정보
        stats = {
            'totalTrends': total_trends,
            'totalSources': len(sources),
            'categories': list(json_trends.keys()),
            'lastUpdate': datetime.now().isoformat()
        }
        
        logger.info(f"트렌드 수집 완료: {total_trends}개 트렌드, {len(sources)}개 소스")
        
        return jsonify({
            'success': True,
            'trends': json_trends,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"실시간 트렌드 수집 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trends': {},
            'stats': {}
        })

@app.route('/api/trends/sources')
def get_trend_sources():
    """사용 가능한 트렌드 소스 목록"""
    try:
        sources = [
            {
                'name': 'Google Trends',
                'description': '실시간 구글 검색 트렌드',
                'category': '검색',
                'status': 'active'
            },
            {
                'name': '네이버 트렌드',
                'description': '한국 실시간 검색어',
                'category': '검색', 
                'status': 'active'
            },
            {
                'name': 'Reddit',
                'description': '해외 커뮤니티 인기 토픽',
                'category': 'discussion',
                'status': 'active'
            },
            {
                'name': 'Hacker News',
                'description': '기술 뉴스 및 스타트업',
                'category': '기술',
                'status': 'active'
            },
            {
                'name': 'GitHub',
                'description': '개발자 트렌딩 저장소',
                'category': '기술',
                'status': 'active'
            }
        ]
        
        return jsonify({
            'success': True,
            'sources': sources
        })
        
    except Exception as e:
        logger.error(f"트렌드 소스 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'sources': []
        })

@app.route('/api/trends/refresh')
def refresh_trends():
    """트렌드 데이터 강제 새로고침"""
    try:
        logger.info("트렌드 데이터 강제 새로고침 요청")
        
        # 새로운 트렌드 수집 (캐시 무시)
        all_trends = trend_collector.collect_all_trends()
        
        return jsonify({
            'success': True,
            'message': f'{len(all_trends)}개의 새로운 트렌드를 수집했습니다.',
            'count': len(all_trends),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"트렌드 새로고침 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

# ========================================================================
# 키워드 리서치 API
# ========================================================================

@app.route('/keywords')
def keyword_dashboard():
    """키워드 리서치 대시보드 페이지"""
    return render_template('keyword_dashboard.html')

@app.route('/api/keywords/research')
def keyword_research():
    """카테고리별 키워드 리서치"""
    try:
        category = request.args.get('category')
        limit = int(request.args.get('limit', 30))
        
        logger.info(f"키워드 리서치 시작: 카테고리={category}, 제한={limit}")
        
        # 키워드 리서치 수행
        keywords = keyword_researcher.research_high_volume_keywords(
            category=category, 
            limit=limit
        )
        
        # 데이터를 JSON 직렬화 가능한 형태로 변환
        keywords_json = []
        for kw in keywords:
            keywords_json.append({
                'keyword': kw.keyword,
                'search_volume': kw.search_volume,
                'trend_score': kw.trend_score,
                'competition': kw.competition,
                'category': kw.category,
                'related_keywords': kw.related_keywords,
                'search_intent': kw.search_intent,
                'difficulty': kw.difficulty,
                'opportunity_score': kw.opportunity_score,
                'timestamp': kw.timestamp.isoformat()
            })
        
        logger.info(f"키워드 리서치 완료: {len(keywords_json)}개 키워드")
        
        return jsonify({
            'success': True,
            'keywords': keywords_json,
            'category': category or '전체',
            'total_count': len(keywords_json)
        })
        
    except Exception as e:
        logger.error(f"키워드 리서치 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'keywords': []
        })

@app.route('/api/keywords/analyze')
def analyze_keyword():
    """개별 키워드 분석"""
    try:
        keyword = request.args.get('keyword')
        if not keyword:
            return jsonify({
                'success': False,
                'error': '키워드를 입력해주세요.'
            })
        
        logger.info(f"키워드 분석 시작: {keyword}")
        
        # 키워드 분석 수행
        keyword_data = keyword_researcher.analyze_keyword_opportunity(keyword)
        
        if keyword_data is None:
            return jsonify({
                'success': False,
                'error': '키워드 분석에 실패했습니다.'
            })
        
        # JSON 형태로 변환
        keyword_json = {
            'keyword': keyword_data.keyword,
            'search_volume': keyword_data.search_volume,
            'trend_score': keyword_data.trend_score,
            'competition': keyword_data.competition,
            'category': keyword_data.category,
            'related_keywords': keyword_data.related_keywords,
            'search_intent': keyword_data.search_intent,
            'difficulty': keyword_data.difficulty,
            'opportunity_score': keyword_data.opportunity_score,
            'timestamp': keyword_data.timestamp.isoformat()
        }
        
        logger.info(f"키워드 분석 완료: {keyword}")
        
        return jsonify({
            'success': True,
            'keyword': keyword_json
        })
        
    except Exception as e:
        logger.error(f"키워드 분석 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/keywords/categories')
def get_keyword_categories():
    """키워드 카테고리 목록"""
    try:
        categories = [
            {'name': '기술/IT', 'icon': '💻', 'description': 'AI, 프로그래밍, 개발 관련 키워드'},
            {'name': '투자/경제', 'icon': '💰', 'description': '주식, 부동산, 재테크 관련 키워드'},
            {'name': '건강/의료', 'icon': '💪', 'description': '다이어트, 운동, 건강관리 키워드'},
            {'name': '교육/학습', 'icon': '📚', 'description': '자격증, 공부법, 온라인 강의 키워드'},
            {'name': '생활/라이프', 'icon': '🏠', 'description': '요리, 인테리어, 생활용품 키워드'},
            {'name': '여행/관광', 'icon': '✈️', 'description': '여행지, 맛집, 호텔 관련 키워드'},
            {'name': '패션/뷰티', 'icon': '💄', 'description': '화장품, 스킨케어, 패션 키워드'},
            {'name': '연예/문화', 'icon': '🎭', 'description': '드라마, K팝, 연예인 관련 키워드'}
        ]
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        logger.error(f"카테고리 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'categories': []
        })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    logger.info("🚀 실시간 트렌드 대시보드 서버 시작...")
    logger.info("📊 접속 URL: http://localhost:8000")
    logger.info("🔄 1분마다 자동 새로고침")
    
    app.run(debug=False, host='0.0.0.0', port=8000)