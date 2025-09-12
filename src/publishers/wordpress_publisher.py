"""
WordPress 자동 발행 모듈
WordPress REST API를 사용하여 콘텐츠를 직접 업로드
"""

import requests
import base64
import json
import os
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WordPressPublisher:
    def __init__(self, site_config: Dict):
        """
        WordPress 발행기 초기화
        
        site_config = {
            'url': 'https://unpre.co.kr',
            'username': 'admin',
            'password': 'application_password'
        }
        """
        self.site_url = site_config.get('url', '').rstrip('/')
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.username = site_config.get('username')
        self.password = site_config.get('password')
        
        # Basic Auth 헤더 생성
        if self.username and self.password:
            credentials = f"{self.username}:{self.password}"
            token = base64.b64encode(credentials.encode()).decode('utf-8')
            self.headers = {
                'Authorization': f'Basic {token}',
                'Content-Type': 'application/json'
            }
        else:
            self.headers = {'Content-Type': 'application/json'}
    
    def test_connection(self) -> bool:
        """WordPress 연결 테스트"""
        try:
            response = requests.get(
                f"{self.api_url}/posts?per_page=1",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"WordPress 연결 테스트 실패: {e}")
            return False
    
    def publish_post(self, content_data: Dict) -> Optional[Dict]:
        """
        WordPress에 포스트 발행
        
        content_data = {
            'title': '포스트 제목',
            'content': 'HTML 콘텐츠',
            'excerpt': '요약',
            'categories': [1, 2],  # 카테고리 ID
            'tags': [3, 4],  # 태그 ID
            'status': 'publish'  # draft, publish
        }
        """
        try:
            # 포스트 데이터 준비
            post_data = {
                'title': content_data.get('title', ''),
                'content': content_data.get('content', ''),
                'excerpt': content_data.get('excerpt', ''),
                'status': content_data.get('status', 'draft'),
                'format': 'standard',
                'comment_status': 'open',
                'ping_status': 'open'
            }
            
            # 카테고리 설정
            if 'categories' in content_data:
                post_data['categories'] = content_data['categories']
            
            # 태그 설정
            if 'tags' in content_data:
                post_data['tags'] = content_data['tags']
            
            # 포스트 생성 API 호출
            response = requests.post(
                f"{self.api_url}/posts",
                headers=self.headers,
                json=post_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"✅ WordPress 포스트 발행 성공: {result.get('link')}")
                return {
                    'success': True,
                    'post_id': result.get('id'),
                    'url': result.get('link'),
                    'guid': result.get('guid', {}).get('rendered')
                }
            else:
                logger.error(f"WordPress 발행 실패: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
        except Exception as e:
            logger.error(f"WordPress 발행 오류: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_categories(self) -> list:
        """카테고리 목록 조회"""
        try:
            response = requests.get(
                f"{self.api_url}/categories",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"카테고리 조회 실패: {e}")
        return []
    
    def create_category(self, name: str, slug: str = None) -> Optional[int]:
        """카테고리 생성"""
        try:
            data = {'name': name}
            if slug:
                data['slug'] = slug
                
            response = requests.post(
                f"{self.api_url}/categories",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json().get('id')
        except Exception as e:
            logger.error(f"카테고리 생성 실패: {e}")
        return None
