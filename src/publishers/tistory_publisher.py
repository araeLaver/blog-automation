"""
Tistory API 연동 모듈 - OAuth 2.0 인증 및 발행
"""

import os
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import urllib.parse
from dotenv import load_dotenv

load_dotenv()


class TistoryPublisher:
    def __init__(self):
        """Tistory 발행 클래스 초기화"""
        self.app_id = os.getenv("TISTORY_APP_ID")
        self.secret_key = os.getenv("TISTORY_SECRET_KEY")
        self.access_token = os.getenv("TISTORY_ACCESS_TOKEN")
        self.blog_name = os.getenv("TISTORY_BLOG_NAME", "untab")
        
        if not all([self.app_id, self.secret_key]):
            raise ValueError("Tistory API 설정이 없습니다")
        
        # API 엔드포인트
        self.api_base = "https://www.tistory.com/apis"
        
        # 액세스 토큰이 없으면 인증 URL 생성
        if not self.access_token:
            self._print_auth_url()
    
    def _print_auth_url(self):
        """OAuth 인증 URL 출력"""
        auth_url = (
            f"https://www.tistory.com/oauth/authorize?"
            f"client_id={self.app_id}&"
            f"redirect_uri=http://localhost:8080&"
            f"response_type=code"
        )
        print(f"\n티스토리 인증이 필요합니다:")
        print(f"1. 다음 URL로 접속: {auth_url}")
        print(f"2. 인증 후 리다이렉트된 URL의 code 파라미터 복사")
        print(f"3. get_access_token(code) 메서드 실행\n")
    
    def get_access_token(self, code: str) -> str:
        """인증 코드로 액세스 토큰 획득"""
        try:
            response = requests.post(
                "https://www.tistory.com/oauth/access_token",
                data={
                    "client_id": self.app_id,
                    "client_secret": self.secret_key,
                    "redirect_uri": "http://localhost:8080",
                    "code": code,
                    "grant_type": "authorization_code"
                }
            )
            
            if response.status_code == 200:
                # access_token=xxx 형식 파싱
                token = response.text.split('=')[1]
                self.access_token = token
                print(f"액세스 토큰 획득 성공!")
                print(f"TISTORY_ACCESS_TOKEN={token}")
                print(f".env 파일에 위 토큰을 추가하세요")
                return token
            else:
                print(f"토큰 획득 실패: {response.text}")
                return None
                
        except Exception as e:
            print(f"토큰 획득 오류: {e}")
            return None
    
    def test_connection(self) -> bool:
        """API 연결 테스트"""
        if not self.access_token:
            print("액세스 토큰이 없습니다")
            return False
        
        try:
            response = requests.get(
                f"{self.api_base}/blog/info",
                params={
                    "access_token": self.access_token,
                    "output": "json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['tistory']['status'] == '200':
                    blogs = data['tistory']['item']['blogs']
                    print(f"연결된 블로그: {[b['name'] for b in blogs]}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"연결 테스트 실패: {e}")
            return False
    
    def publish_post(self, content: Dict, images: List[Dict] = None,
                    visibility: int = 3, draft: bool = False) -> Tuple[bool, str]:
        """
        포스트 발행
        
        Args:
            content: 콘텐츠 딕셔너리
            images: 이미지 리스트
            visibility: 발행 상태 (0:비공개, 1:보호, 3:공개)
            draft: 초안 저장 여부
            
        Returns:
            (성공여부, URL 또는 에러메시지)
        """
        if not self.access_token:
            return False, "액세스 토큰이 없습니다"
        
        try:
            # 1. 이미지 업로드 및 콘텐츠에 삽입
            html_content = self._format_content_with_images(content, images)
            
            # 2. 카테고리 ID 가져오기
            category_id = self._get_category_id(content.get('category', ''))
            
            # 3. 포스트 데이터 구성
            post_data = {
                "access_token": self.access_token,
                "output": "json",
                "blogName": self.blog_name,
                "title": content['title'],
                "content": html_content,
                "visibility": 0 if draft else visibility,
                "tag": ",".join(content.get('tags', [])),
                "acceptComment": 1,
                "published": int(time.time()) if not draft else None
            }
            
            if category_id:
                post_data["category"] = category_id
            
            # None 값 제거
            post_data = {k: v for k, v in post_data.items() if v is not None}
            
            # 4. 포스트 발행
            response = requests.post(
                f"{self.api_base}/post/write",
                data=post_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['tistory']['status'] == '200':
                    post_id = data['tistory']['postId']
                    post_url = data['tistory']['url']
                    return True, post_url
                else:
                    return False, f"발행 실패: {data['tistory'].get('error_message', 'Unknown error')}"
            else:
                return False, f"HTTP 오류: {response.status_code}"
                
        except Exception as e:
            return False, f"발행 중 오류: {str(e)}"
    
    def _upload_image(self, image_path: str) -> Optional[str]:
        """이미지 업로드 및 URL 반환"""
        try:
            # 로컬 파일 읽기
            if image_path.startswith('http'):
                # URL인 경우 다운로드
                response = requests.get(image_path)
                file_data = response.content
                filename = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            else:
                # 로컬 파일
                path = Path(image_path)
                if not path.exists():
                    print(f"이미지 파일 없음: {path}")
                    return None
                
                with open(path, 'rb') as f:
                    file_data = f.read()
                filename = path.name
            
            # 업로드
            files = {'uploadedfile': (filename, file_data)}
            data = {
                'access_token': self.access_token,
                'output': 'json',
                'blogName': self.blog_name
            }
            
            response = requests.post(
                f"{self.api_base}/post/attach",
                data=data,
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['tistory']['status'] == '200':
                    return result['tistory']['url']
            
            return None
            
        except Exception as e:
            print(f"이미지 업로드 실패: {e}")
            return None
    
    def _format_content_with_images(self, content: Dict, images: List[Dict]) -> str:
        """이미지를 포함한 HTML 콘텐츠 생성"""
        html = []
        
        # 서론
        if content.get('introduction'):
            html.append(f"<p>{content['introduction']}</p>")
        
        # 첫 번째 이미지 (썸네일)
        if images and len(images) > 0:
            img_url = self._upload_image(images[0]['url'])
            if img_url:
                html.append(f'<p style="text-align: center;">')
                html.append(f'<img src="{img_url}" alt="{images[0].get("alt", "")}" />')
                html.append(f'</p>')
        
        # 본문 섹션들
        for i, section in enumerate(content.get('sections', [])):
            html.append(f"<h2>{section['heading']}</h2>")
            
            # 단락 처리
            paragraphs = section['content'].split('\n\n')
            for para in paragraphs:
                if para.strip():
                    html.append(f"<p>{para.strip()}</p>")
            
            # 중간 이미지 삽입
            if images and i == 1 and len(images) > 1:
                img_url = self._upload_image(images[1]['url'])
                if img_url:
                    html.append(f'<p style="text-align: center;">')
                    html.append(f'<img src="{img_url}" alt="{images[1].get("alt", "")}" />')
                    html.append(f'</p>')
        
        # 코드 블록 처리 (있는 경우)
        if content.get('code_blocks'):
            for code_block in content['code_blocks']:
                html.append('<pre><code>')
                html.append(code_block)
                html.append('</code></pre>')
        
        # 결론
        if content.get('conclusion'):
            html.append(f"<h2>마무리</h2>")
            html.append(f"<p>{content['conclusion']}</p>")
        
        # 마지막 이미지
        if images and len(images) > 2:
            img_url = self._upload_image(images[2]['url'])
            if img_url:
                html.append(f'<p style="text-align: center;">')
                html.append(f'<img src="{img_url}" alt="{images[2].get("alt", "")}" />')
                html.append(f'</p>')
        
        return "\n".join(html)
    
    def _get_category_id(self, category_name: str) -> Optional[str]:
        """카테고리 이름으로 ID 찾기"""
        if not category_name:
            return None
        
        try:
            response = requests.get(
                f"{self.api_base}/category/list",
                params={
                    "access_token": self.access_token,
                    "output": "json",
                    "blogName": self.blog_name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['tistory']['status'] == '200':
                    categories = data['tistory']['item']['categories']
                    for cat in categories:
                        if cat['name'].lower() == category_name.lower():
                            return cat['id']
            
            return None
            
        except Exception as e:
            print(f"카테고리 조회 실패: {e}")
            return None
    
    def get_recent_posts(self, count: int = 10) -> List[Dict]:
        """최근 포스트 목록 조회"""
        try:
            response = requests.get(
                f"{self.api_base}/post/list",
                params={
                    "access_token": self.access_token,
                    "output": "json",
                    "blogName": self.blog_name,
                    "page": 1,
                    "count": count
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['tistory']['status'] == '200':
                    posts = data['tistory']['item'].get('posts', [])
                    return [
                        {
                            "id": p['id'],
                            "title": p['title'],
                            "url": p['postUrl'],
                            "date": p['date'],
                            "visibility": p['visibility']
                        }
                        for p in posts
                    ]
            
            return []
            
        except Exception as e:
            print(f"포스트 목록 조회 실패: {e}")
            return []
    
    def update_post(self, post_id: str, updates: Dict) -> bool:
        """기존 포스트 수정"""
        try:
            post_data = {
                "access_token": self.access_token,
                "output": "json",
                "blogName": self.blog_name,
                "postId": post_id
            }
            
            # 업데이트 필드 추가
            if 'title' in updates:
                post_data['title'] = updates['title']
            if 'content' in updates:
                post_data['content'] = updates['content']
            if 'tags' in updates:
                post_data['tag'] = ",".join(updates['tags'])
            if 'visibility' in updates:
                post_data['visibility'] = updates['visibility']
            
            response = requests.post(
                f"{self.api_base}/post/modify",
                data=post_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['tistory']['status'] == '200'
            
            return False
            
        except Exception as e:
            print(f"포스트 수정 실패: {e}")
            return False
    
    def delete_post(self, post_id: str) -> bool:
        """포스트 삭제"""
        try:
            response = requests.post(
                f"{self.api_base}/post/delete",
                data={
                    "access_token": self.access_token,
                    "output": "json",
                    "blogName": self.blog_name,
                    "postId": post_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['tistory']['status'] == '200'
            
            return False
            
        except Exception as e:
            print(f"포스트 삭제 실패: {e}")
            return False
    
    def get_stats(self) -> Optional[Dict]:
        """블로그 통계 조회"""
        try:
            response = requests.get(
                f"{self.api_base}/blog/info",
                params={
                    "access_token": self.access_token,
                    "output": "json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['tistory']['status'] == '200':
                    blogs = data['tistory']['item']['blogs']
                    for blog in blogs:
                        if blog['name'] == self.blog_name:
                            return {
                                "title": blog['title'],
                                "description": blog['description'],
                                "url": blog['url'],
                                "statistics": blog.get('statistics', {})
                            }
            
            return None
            
        except Exception as e:
            print(f"통계 조회 실패: {e}")
            return None