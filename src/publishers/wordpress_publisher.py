"""
WordPress API 연동 모듈 - 높은 안정성과 에러 처리
"""

import os
import base64
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import mimetypes
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()


class WordPressPublisher:
    def __init__(self, site_key: str):
        """
        WordPress 발행 클래스 초기화
        
        Args:
            site_key: 사이트 식별자 (unpre, untab, skewese)
        """
        self.site_key = site_key
        
        # 환경변수에서 먼저 시도
        self.base_url = os.getenv(f"{site_key.upper()}_URL")
        self.username = os.getenv(f"{site_key.upper()}_USERNAME")
        self.password = os.getenv(f"{site_key.upper()}_PASSWORD")
        
        # 환경변수가 없으면 하드코딩된 값 사용 (운영 환경 대비)
        if not all([self.base_url, self.username, self.password]):
            site_configs = {
                'unpre': {
                    'url': 'https://unpre.co.kr',
                    'username': 'unpre',
                    'password': 'Kdwyyr1527!'
                },
                'untab': {
                    'url': 'https://untab.co.kr',
                    'username': 'untab',
                    'password': 'Kdwyyr1527!'
                },
                'skewese': {
                    'url': 'https://skewese.com',
                    'username': 'skewese',
                    'password': 'Kdwyyr1527!'
                }
            }
            
            if site_key in site_configs:
                config = site_configs[site_key]
                self.base_url = self.base_url or config['url']
                self.username = self.username or config['username']
                self.password = self.password or config['password']
                print(f"WordPress 설정 로드됨 (하드코딩): {site_key}")
            else:
                raise ValueError(f"WordPress 설정이 없습니다: {site_key}")
        
        if not all([self.base_url, self.username, self.password]):
            raise ValueError(f"WordPress 설정이 없습니다: {site_key}")
        
        # API 엔드포인트
        self.api_url = urljoin(self.base_url, "/wp-json/wp/v2/")
        
        # Application Password 방식 인증 헤더 (더 안전하고 호환성 좋음)
        credentials = f"{self.username}:{self.password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        self.headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
            "User-Agent": "BlogAutomation/1.0",
            "Accept": "application/json"
        }
        
        # 카테고리 캐시
        self._categories_cache = None
        self._tags_cache = None
        
    def test_connection(self) -> bool:
        """API 연결 테스트 (다중 방식 시도)"""
        try:
            # 1차 시도: 일반 API 테스트
            response = requests.get(
                f"{self.api_url}posts?per_page=1",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return True
            
            # 2차 시도: 다른 헤더로 테스트
            alt_headers = {
                "Authorization": self.headers["Authorization"],
                "Content-Type": "application/json",
                "X-WP-Nonce": "wp_rest"
            }
            response = requests.get(
                f"{self.api_url}posts?per_page=1",
                headers=alt_headers,
                timeout=10
            )
            if response.status_code == 200:
                self.headers = alt_headers  # 성공한 헤더로 업데이트
                return True
            
            print(f"연결 테스트 실패: {response.status_code} - {response.text[:200]}")
            return False
            
        except Exception as e:
            print(f"연결 테스트 실패: {e}")
            return False
    
    def publish_post(self, content: Dict, images: List[Dict] = None, 
                    draft: bool = False) -> Tuple[bool, str]:
        """
        포스트 발행
        
        Args:
            content: 콘텐츠 딕셔너리 (title, content, meta_description 등)
            images: 이미지 리스트
            draft: 초안으로 저장 여부
            
        Returns:
            (성공여부, URL 또는 에러메시지)
        """
        try:
            # 1. 안전한 이미지 업로드 (로컬 파일만, 외부 API 없음)
            content_images = []
            featured_media_id = None
            
            if images:
                print(f"[SAFE_IMG] 안전한 이미지 업로드 시작: {len(images)}개")
                for img in images:
                    try:
                        # 안전장치: 로컬 파일만 처리
                        if not img.get('url') or not os.path.exists(img.get('url', '')):
                            print(f"[SAFE_IMG] 건너뜀 - 로컬 파일 아님: {img.get('url')}")
                            continue
                            
                        media_id = self._upload_media(img)
                        if media_id:
                            if img.get('type') == 'thumbnail':
                                featured_media_id = media_id
                                print(f"[SAFE_IMG] 대표이미지 설정: {featured_media_id}")
                            else:
                                content_images.append(media_id)
                                print(f"[SAFE_IMG] 콘텐츠 이미지 추가: {media_id}")
                        else:
                            print(f"[SAFE_IMG] 업로드 실패 (무시하고 계속): {img.get('url')}")
                            
                    except Exception as e:
                        print(f"[SAFE_IMG] 이미지 처리 오류 (무시하고 계속): {e}")
                        continue
            else:
                print("[SAFE_IMG] 업로드할 이미지 없음")
            
            # 2. 카테고리/태그 처리
            category_ids = self._get_or_create_categories(
                content.get('categories', [])
            )
            tag_ids = self._get_or_create_tags(
                content.get('tags', [])
            )
            
            # 3. 콘텐츠 포맷팅 (대표이미지 제외한 이미지들만 전달)
            post_content = self._format_content(content, content_images)
            print(f"포맷팅된 콘텐츠 길이: {len(post_content)}")
            print(f"포맷팅된 콘텐츠 미리보기: {post_content[:300]}...")
            print(f"포맷팅된 콘텐츠 전체 (디버깅): {post_content}")
            
            # 콘텐츠가 비어있는지 확인
            if not post_content or post_content.strip() == "":
                print("경고: 포맷팅된 콘텐츠가 비어있습니다!")
                return False, "콘텐츠가 비어있어서 발행할 수 없습니다"
            
            # 4. 포스트 데이터 구성
            post_data = {
                "title": content['title'],
                "content": post_content,
                "excerpt": content.get('meta_description', ''),
                "status": "draft" if draft else "publish",
                "categories": category_ids,
                "tags": tag_ids,
                "format": "standard",
                "meta": {
                    "_yoast_wpseo_metadesc": content.get('meta_description', ''),
                    "_yoast_wpseo_focuskw": content.get('keywords', [''])[0] if content.get('keywords') else ''
                }
            }
            
            # 안전한 대표 이미지 설정
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
                print(f"[SAFE_IMG] WordPress 포스트에 대표이미지 설정: {featured_media_id}")
            else:
                print("[SAFE_IMG] 대표이미지 없음 - 텍스트만 발행")
            
            # 5. 포스트 발행 (다중 시도 방식)
            print(f"[POST] 최종 포스트 데이터: title={post_data.get('title')}, featured_media={post_data.get('featured_media')}")
            for attempt in range(3):  # 최대 3회 시도
                try:
                    if attempt == 1:
                        # 2차 시도: 다른 헤더 사용
                        headers = {
                            "Authorization": self.headers["Authorization"],
                            "Content-Type": "application/json",
                            "User-Agent": "WordPress/BlogAutomation",
                            "Cache-Control": "no-cache"
                        }
                    elif attempt == 2:
                        # 3차 시도: 최소 헤더와 JSON 파라미터
                        headers = {"Authorization": self.headers["Authorization"]}
                        response = requests.post(
                            f"{self.api_url}posts",
                            headers=headers,
                            json=post_data,  # json 파라미터 사용
                            timeout=30
                        )
                    else:
                        # 1차 시도: 기본 헤더
                        headers = self.headers
                    
                    # 1차, 2차 시도만 여기서 실행 (3차는 위에서 이미 실행됨)
                    if attempt != 2:
                        response = requests.post(
                            f"{self.api_url}posts",
                            headers=headers,
                            data=json.dumps(post_data),
                            timeout=30
                        )
                    
                    if response.status_code in [200, 201]:
                        post = response.json()
                        post_id = post['id']
                        
                        # 이미지 관련 코드 제거
                        
                        return True, post['link']
                    elif response.status_code == 401 and attempt < 2:
                        print(f"인증 실패 (시도 {attempt + 1}/3), 다른 방식으로 재시도...")
                        continue
                    else:
                        error_msg = f"발행 실패 (시도 {attempt + 1}/3): {response.status_code} - {response.text[:500]}"
                        if attempt == 2:  # 마지막 시도
                            return False, error_msg
                        print(error_msg)
                        
                except requests.exceptions.RequestException as e:
                    if attempt == 2:
                        return False, f"네트워크 오류: {str(e)}"
                    print(f"네트워크 오류 (시도 {attempt + 1}/3): {e}")
                    time.sleep(1)  # 1초 대기 후 재시도
                
        except Exception as e:
            return False, f"발행 중 오류: {str(e)}"
    
    def _set_featured_image_separately(self, post_id: int, media_id: int) -> bool:
        """포스트 생성 후 별도로 대표이미지 설정"""
        try:
            # 방법 1: 포스트 업데이트로 featured_media 설정
            update_data = {"featured_media": media_id}
            response = requests.post(
                f"{self.api_url}posts/{post_id}",
                headers=self.headers,
                data=json.dumps(update_data),
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"[FEATURED] 포스트 업데이트로 대표이미지 설정 성공: {media_id}")
                return True
            else:
                print(f"[FEATURED] 포스트 업데이트 실패: {response.status_code} - {response.text[:200]}")
            
            # 방법 2: 메타 필드 직접 설정
            meta_data = {"_thumbnail_id": str(media_id)}
            response = requests.post(
                f"{self.api_url}posts/{post_id}/meta",
                headers=self.headers,
                data=json.dumps(meta_data),
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                print(f"[FEATURED] 메타 필드로 대표이미지 설정 성공: {media_id}")
                return True
            else:
                print(f"[FEATURED] 메타 필드 설정 실패: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"[FEATURED] 별도 대표이미지 설정 오류: {e}")
        
        return False
    
    def _upload_media(self, image: Dict) -> Optional[int]:
        """미디어 업로드"""
        try:
            print(f"[UPLOAD] Starting upload: {image}")
            
            # 이미지 파일 읽기
            if 'url' in image and image['url'].startswith('http'):
                # 외부 URL인 경우 다운로드 (단순화)
                print(f"[UPLOAD] Downloading from URL: {image['url']}")
                try:
                    img_response = requests.get(image['url'], timeout=10)  # timeout 단축
                    print(f"[UPLOAD] Download status code: {img_response.status_code}")
                    
                    if img_response.status_code != 200:
                        print(f"[UPLOAD] Download failed: {img_response.status_code}")
                        return None
                except Exception as e:
                    print(f"[UPLOAD] Download exception: {e}")
                    return None
                    
                img_data = img_response.content
                print(f"[UPLOAD] Downloaded image size: {len(img_data)} bytes")
                filename = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            else:
                # 로컬 파일
                img_path = Path(image['url'])
                if not img_path.exists():
                    print(f"이미지 파일 없음: {img_path}")
                    return None
                
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                filename = img_path.name
            
            # 미디어 업로드
            headers = {
                "Authorization": self.headers["Authorization"],
                "Content-Type": mimetypes.guess_type(filename)[0] or "image/jpeg",
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
            
            print(f"WordPress 미디어 업로드 중: {filename}")
            response = requests.post(
                f"{self.api_url}media",
                headers=headers,
                data=img_data,
                timeout=60
            )
            
            print(f"업로드 응답 상태: {response.status_code}")
            
            if response.status_code in [200, 201]:
                media = response.json()
                print(f"미디어 업로드 성공! ID: {media['id']}, URL: {media.get('source_url', 'N/A')}")
                return media['id']
            else:
                print(f"미디어 업로드 실패: {response.status_code}")
                print(f"응답 내용: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"미디어 업로드 오류: {e}")
            return None
    
    def _get_or_create_categories(self, category_names: List[str]) -> List[int]:
        """카테고리 ID 가져오기 또는 생성"""
        if not category_names:
            return []
        
        # 캐시 확인
        if self._categories_cache is None:
            self._load_categories()
        
        category_ids = []
        for name in category_names:
            # 기존 카테고리 찾기
            cat_id = None
            for cat in self._categories_cache:
                if cat['name'].lower() == name.lower():
                    cat_id = cat['id']
                    break
            
            # 없으면 생성
            if not cat_id:
                cat_id = self._create_category(name)
            
            if cat_id:
                category_ids.append(cat_id)
        
        return category_ids
    
    def _load_categories(self):
        """모든 카테고리 로드"""
        try:
            response = requests.get(
                f"{self.api_url}categories?per_page=100",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                self._categories_cache = response.json()
            else:
                self._categories_cache = []
        except:
            self._categories_cache = []
    
    def _create_category(self, name: str) -> Optional[int]:
        """카테고리 생성"""
        try:
            data = {"name": name}
            response = requests.post(
                f"{self.api_url}categories",
                headers=self.headers,
                data=json.dumps(data),
                timeout=10
            )
            if response.status_code in [200, 201]:
                category = response.json()
                # 캐시 업데이트
                if self._categories_cache is not None:
                    self._categories_cache.append(category)
                return category['id']
        except Exception as e:
            print(f"카테고리 생성 실패: {e}")
        return None
    
    def _get_or_create_tags(self, tag_names: List[str]) -> List[int]:
        """태그 ID 가져오기 또는 생성"""
        if not tag_names:
            return []
        
        # 캐시 확인
        if self._tags_cache is None:
            self._load_tags()
        
        tag_ids = []
        for name in tag_names:
            # 기존 태그 찾기
            tag_id = None
            for tag in self._tags_cache:
                if tag['name'].lower() == name.lower():
                    tag_id = tag['id']
                    break
            
            # 없으면 생성
            if not tag_id:
                tag_id = self._create_tag(name)
            
            if tag_id:
                tag_ids.append(tag_id)
        
        return tag_ids
    
    def _load_tags(self):
        """모든 태그 로드"""
        try:
            response = requests.get(
                f"{self.api_url}tags?per_page=100",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                self._tags_cache = response.json()
            else:
                self._tags_cache = []
        except:
            self._tags_cache = []
    
    def _create_tag(self, name: str) -> Optional[int]:
        """태그 생성"""
        try:
            data = {"name": name}
            response = requests.post(
                f"{self.api_url}tags",
                headers=self.headers,
                data=json.dumps(data),
                timeout=10
            )
            if response.status_code in [200, 201]:
                tag = response.json()
                # 캐시 업데이트
                if self._tags_cache is not None:
                    self._tags_cache.append(tag)
                return tag['id']
        except Exception as e:
            print(f"태그 생성 실패: {e}")
        return None
    
    def _format_content(self, content: Dict, image_ids: List[int]) -> str:
        """콘텐츠 HTML 포맷팅"""
        
        # 이미 완성된 HTML이 있으면 그대로 사용 (하위 호환성)
        if 'content' in content and content['content'] and not content.get('sections'):
            raw_html = content['content']
            print(f"원본 HTML 콘텐츠 길이: {len(raw_html)}")
            print(f"HTML 콘텐츠 미리보기: {raw_html[:200]}...")
            
            # HTML에서 본문 내용만 추출 (WordPress용)
            import re
            from bs4 import BeautifulSoup
            
            try:
                # BeautifulSoup을 사용해서 더 정확하게 파싱
                print("BeautifulSoup 파싱 시작...")
                soup = BeautifulSoup(raw_html, 'html.parser')
                
                # content-container div 찾기
                container_div = soup.find('div', class_='content-container')
                if container_div:
                    print(f"content-container div 발견! 원본 길이: {len(str(container_div))}")
                    
                    # 불필요한 요소들 제거
                    removed_count = 0
                    for element in container_div.find_all(['div'], class_=['meta-info', 'wordpress-actions', 'site-badge']):
                        print(f"제거하는 요소: {element.name} with class {element.get('class')}")
                        element.decompose()
                        removed_count += 1
                    
                    # script 태그 제거
                    for script in container_div.find_all('script'):
                        print("script 태그 제거")
                        script.decompose()
                        removed_count += 1
                    
                    print(f"총 {removed_count}개 요소 제거됨")
                    
                    # 내용 추출 (HTML 태그 유지)
                    extracted = str(container_div)
                    print(f"str() 변환 후 길이: {len(extracted)}")
                    
                    # content-container div 태그 자체는 제거
                    before_regex = len(extracted)
                    extracted = re.sub(r'^<div[^>]*class="[^"]*content-container[^"]*"[^>]*>|</div>\s*$', '', extracted, flags=re.MULTILINE)
                    after_regex = len(extracted)
                    print(f"div 태그 제거: {before_regex} -> {after_regex}")
                    
                    final_result = extracted.strip()
                    print(f"최종 추출된 콘텐츠 길이: {len(final_result)}")
                    if final_result:
                        print(f"추출된 콘텐츠 처음 200자: {final_result[:200]}...")
                        print(f"추출된 콘텐츠 마지막 200자: ...{final_result[-200:]}")
                    else:
                        print("경고: 최종 결과가 비어있음!")
                    
                    # 콘텐츠 서식 개선
                    final_result = self._improve_content_formatting(final_result)
                    
                    return final_result
                else:
                    print("경고: content-container div를 찾을 수 없음!")
                    # 전체 body에서 찾아보기
                    body = soup.find('body')
                    if body:
                        print(f"body 태그 발견, 길이: {len(str(body))}")
                    else:
                        print("body 태그도 없음!")
            except Exception as e:
                print(f"BeautifulSoup 파싱 오류: {e}")
                import traceback
                traceback.print_exc()
            
            # BeautifulSoup 실패시 정규식 백업
            body_match = re.search(r'<body[^>]*>(.*?)</body>', raw_html, re.DOTALL | re.IGNORECASE)
            if body_match:
                print("정규식 백업 방식 사용")
                return body_match.group(1).strip()
            else:
                print("body 태그를 찾을 수 없음, 원본 HTML 사용")
                return raw_html
        
        html = []
        
        # 서론
        if content.get('introduction'):
            html.append(f"<p>{content['introduction']}</p>")
        
        # 첫 번째 이미지 삽입
        if image_ids and len(image_ids) > 0:
            html.append(f'[caption align="aligncenter"]'
                       f'[gallery ids="{image_ids[0]}"]'
                       f'[/caption]')
        
        # 본문 섹션들
        for i, section in enumerate(content.get('sections', [])):
            html.append(f"<h2>{section['heading']}</h2>")
            
            # 단락 나누기 및 서식 개선
            paragraphs = section['content'].split('\n\n')
            for para in paragraphs:
                if para.strip():
                    formatted_para = self._improve_text_formatting(para.strip())
                    html.append(f"<p>{formatted_para}</p>")
                    # 문단 간 구분선 추가 (긴 문단인 경우)
                    if len(para.strip()) > 300:
                        html.append('<hr class="wp-block-separator has-alpha-channel-opacity" />')
            
            # 중간 이미지 삽입
            if image_ids and i == 1 and len(image_ids) > 1:
                html.append(f'[caption align="aligncenter"]'
                           f'[gallery ids="{image_ids[1]}"]'
                           f'[/caption]')
        
        # 결론
        if content.get('conclusion'):
            html.append(f"<h2>마무리</h2>")
            html.append(f"<p>{content['conclusion']}</p>")
        
        # 관련 링크 (내부 링크)
        if content.get('internal_links'):
            html.append("<h3>관련 글</h3>")
            html.append("<ul>")
            for link in content['internal_links']:
                html.append(f'<li><a href="{link["url"]}">{link["title"]}</a></li>')
            html.append("</ul>")
        
        return "\n".join(html)
    
    def _improve_content_formatting(self, html_content: str) -> str:
        """HTML 콘텐츠 서식 개선"""
        import re
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 모든 텍스트 노드에서 마크다운 스타일 개선
            for element in soup.find_all(text=True):
                if element.parent.name not in ['script', 'style']:
                    improved_text = self._improve_text_formatting(str(element))
                    element.replace_with(improved_text)
            
            # 문단 간 구분선 추가 (긴 단락들 사이에)
            paragraphs = soup.find_all('p')
            for i, p in enumerate(paragraphs):
                if p.get_text() and len(p.get_text().strip()) > 300:
                    # 긴 문단 뒤에 구분선 추가
                    if i < len(paragraphs) - 1:  # 마지막 문단이 아닌 경우
                        hr = soup.new_tag('hr', **{'class': 'wp-block-separator has-alpha-channel-opacity'})
                        p.insert_after(hr)
            
            return str(soup)
            
        except Exception as e:
            print(f"콘텐츠 서식 개선 오류: {e}")
            return html_content
    
    def _improve_text_formatting(self, text: str) -> str:
        """텍스트 서식 개선 (마크다운 스타일 -> HTML)"""
        import re
        
        # ** -> <strong> (굵은 글씨)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # * -> <em> (기울임)  
        text = re.sub(r'(?<!\*)\*(?!\*)([^*]+)\*(?!\*)', r'<em>\1</em>', text)
        
        # ``` -> <code> (인라인 코드)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # ### -> <strong> (소제목 강조)
        text = re.sub(r'###\s*([^\n]+)', r'<strong>\1</strong>', text)
        
        # 번호 목록 개선 (1. 2. 3. -> HTML 목록)
        text = re.sub(r'(\d+)\.\s+([^\n]+)', r'<span class="list-item"><strong>\1.</strong> \2</span>', text)
        
        # • 또는 - 로 시작하는 목록 개선
        text = re.sub(r'[•-]\s+([^\n]+)', r'<span class="bullet-item">• \1</span>', text)
        
        return text
    
    def update_post(self, post_id: int, updates: Dict) -> bool:
        """기존 포스트 업데이트"""
        try:
            response = requests.post(
                f"{self.api_url}posts/{post_id}",
                headers=self.headers,
                data=json.dumps(updates),
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            print(f"포스트 업데이트 실패: {e}")
            return False
    
    def get_recent_posts(self, count: int = 10) -> List[Dict]:
        """최근 포스트 가져오기"""
        try:
            response = requests.get(
                f"{self.api_url}posts",
                headers=self.headers,
                params={"per_page": count, "orderby": "date", "order": "desc"},
                timeout=10
            )
            if response.status_code == 200:
                posts = response.json()
                return [
                    {
                        "id": p['id'],
                        "title": p['title']['rendered'],
                        "url": p['link'],
                        "date": p['date']
                    }
                    for p in posts
                ]
        except Exception as e:
            print(f"포스트 조회 실패: {e}")
        return []
    
    def delete_post(self, post_id: int, force: bool = False) -> bool:
        """포스트 삭제"""
        try:
            params = {"force": force}  # force=True면 완전 삭제, False면 휴지통
            response = requests.delete(
                f"{self.api_url}posts/{post_id}",
                headers=self.headers,
                params=params,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"포스트 삭제 실패: {e}")
            return False