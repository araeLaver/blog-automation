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
        
        # SSL 검증 비활성화된 세션 생성
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update(self.headers)
        
        # SSL 경고 비활성화
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def test_connection(self) -> bool:
        """API 연결 테스트 (타임아웃 연장 및 상세 오류 진단)"""
        try:
            # 1차 시도: 세션을 사용한 API 테스트 (타임아웃 연장)
            response = self.session.get(
                f"{self.api_url}posts?per_page=1",
                timeout=60  # 30초 → 60초로 더 연장
            )
            if response.status_code == 200:
                print(f"✅ WordPress REST API 연결 성공: {self.base_url}")
                return True
            
            # 2차 시도: 다른 헤더로 테스트
            alt_headers = {
                "Authorization": self.headers["Authorization"],
                "Content-Type": "application/json",
                "X-WP-Nonce": "wp_rest"
            }
            response = self.session.get(
                f"{self.api_url}posts?per_page=1",
                headers=alt_headers,
                timeout=60  # 타임아웃 60초로 연장
            )
            if response.status_code == 200:
                self.session.headers.update(alt_headers)  # 성공한 헤더로 업데이트
                print(f"✅ WordPress REST API 연결 성공 (alt headers): {self.base_url}")
                return True
            
            print(f"❌ 연결 테스트 실패: {response.status_code} - {response.text[:200]}")
            return False
            
        except requests.exceptions.ConnectTimeout:
            print(f"❌ {self.site} WordPress 연결 타임아웃 - 호스팅에서 외부 접근 차단")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ {self.site} WordPress 응답 타임아웃 - 서버 응답 지연")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ {self.site} WordPress 연결 오류 - DNS 또는 서버 다운")
            return False
        except Exception as e:
            print(f"❌ {self.site} 연결 테스트 실패: {e}")
            return False
    
    def _fix_year_in_content(self, content: Dict) -> Dict:
        """콘텐츠에서 잘못된 연도 수정"""
        import re
        from datetime import datetime
        
        current_year = datetime.now().year
        fixed_content = content.copy()
        
        # 제목에서 2024년을 현재 연도로 수정
        if 'title' in fixed_content:
            fixed_content['title'] = re.sub(r'2024년?', f'{current_year}년', fixed_content['title'])
            fixed_content['title'] = re.sub(r'\[2024년?\]', f'[{current_year}년]', fixed_content['title'])
        
        # 메타 설명에서도 수정
        if 'meta_description' in fixed_content:
            fixed_content['meta_description'] = re.sub(r'2024년?', f'{current_year}년', fixed_content['meta_description'])
        
        # 소개글에서도 수정
        if 'introduction' in fixed_content:
            fixed_content['introduction'] = re.sub(r'2024년?', f'{current_year}년', fixed_content['introduction'])
        
        # 섹션 내용에서도 수정
        if 'sections' in fixed_content:
            for section in fixed_content['sections']:
                if 'content' in section:
                    section['content'] = re.sub(r'2024년?', f'{current_year}년', section['content'])
                if 'heading' in section:
                    section['heading'] = re.sub(r'2024년?', f'{current_year}년', section['heading'])
        
        # 추가 콘텐츠에서도 수정
        if 'additional_content' in fixed_content:
            fixed_content['additional_content'] = re.sub(r'2024년?', f'{current_year}년', fixed_content['additional_content'])
        
        return fixed_content

    def publish_post(self, content: Dict, images: List[Dict] = None, 
                    draft: bool = False, text_only: bool = False) -> Tuple[bool, str]:
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
            # 콘텐츠 크기 사전 체크 및 최적화
            original_size = len(content.get('content', ''))
            if original_size > 15000:  # 15KB 초과시 자동 축소
                print(f"[OPTIMIZE] 콘텐츠 크기 초과 ({original_size:,} bytes), 15KB 이하로 최적화")
                content['content'] = content['content'][:14000]  # 14KB로 제한 (여유분)
                print(f"[OPTIMIZE] 최적화 완료: {len(content['content']):,} bytes")
            
            # 연도 수정 적용
            content = self._fix_year_in_content(content)
            
            # 1. 텍스트 전용 모드일 때는 이미지 업로드 완전 스킵
            content_images = []
            featured_media_id = None
            
            if not text_only and images:
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
            
            # 2. 카테고리/태그 처리 (텍스트 전용 모드에서는 간소화)
            if text_only:
                # 텍스트 전용: 기본 카테고리만 사용, 태그는 스킵
                category_ids = [1]  # 기본 카테고리 ID
                tag_ids = []
                print("[TEXT_ONLY] 카테고리/태그 처리 완전 스킵")
            else:
                # 일반 모드도 빠른 처리를 위해 타임아웃 단축
                category_ids = self._get_or_create_categories(
                    content.get('categories', [])
                )
                tag_ids = self._get_or_create_tags(
                    content.get('tags', [])
                )
            
            # 3. HTML 구조 그대로 유지하면서 최소한만 정리
            if 'content' in content and content['content']:
                # 이미 완성된 HTML이 있으면 그대로 사용 (디자인 유지)
                post_content = content['content']
                print(f"[HTML_PRESERVED] 원본 HTML 그대로 사용, 길이: {len(post_content)}")
                
                # 최소한의 정리만 (WordPress에서 문제가 될 수 있는 요소만)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(post_content, 'html.parser')
                
                # WordPress 발행시 충돌할 수 있는 요소만 제거
                for unwanted in soup.find_all(['script']):
                    unwanted.decompose()
                for meta_div in soup.find_all('div', class_=['wordpress-actions']):
                    meta_div.decompose()
                    
                post_content = str(soup)
            else:
                # 섹션 기반 콘텐츠는 기존 방식 사용
                post_content = self._format_content(content, content_images)
            
            print(f"최종 콘텐츠 길이: {len(post_content)}")
            print(f"콘텐츠 미리보기: {post_content[:300]}...")
            
            # 콘텐츠가 비어있는지 확인
            if not post_content or post_content.strip() == "":
                print("경고: 콘텐츠가 비어있습니다!")
                return False, "콘텐츠가 비어있어서 발행할 수 없습니다"
            
            # 4. 포스트 데이터 구성 (텍스트 전용 모드에서는 간소화)
            if text_only:
                # 텍스트 전용: 최소한의 데이터만 사용
                post_data = {
                    "title": content['title'],
                    "content": post_content,
                    "status": "draft" if draft else "publish",
                    "categories": category_ids
                }
                print("[TEXT_ONLY] 간소화된 포스트 데이터 사용")
            else:
                # 일반 모드: 전체 메타데이터 포함
                post_data = {
                    "title": content['title'],
                    "content": post_content,  # HTML 코드 그대로
                    "excerpt": content.get('meta_description', ''),
                    "status": "draft" if draft else "publish", 
                    "categories": category_ids,
                    "tags": tag_ids,
                    "format": "standard",
                    "meta": {
                        # WordPress 코드 편집기 모드 강제 설정
                        "_classic_editor_remember": "classic-editor",
                        "_wp_editor_expand": "on",
                        "_edit_lock": "",
                        "_edit_last": "1",
                        # Gutenberg 비활성화
                        "_gutenberg_editor_disabled": "1",
                        "_classic_editor_disabled": "0",
                        # SEO 설정
                        "_yoast_wpseo_metadesc": content.get('meta_description', ''),
                        "_yoast_wpseo_focuskw": content.get('keywords', [''])[0] if content.get('keywords') else '',
                        # HTML 그대로 저장하도록 설정
                        "_wp_page_template": "default"
                    }
                }
            
            # 안전한 대표 이미지 설정
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
                print(f"[SAFE_IMG] WordPress 포스트에 대표이미지 설정: {featured_media_id}")
            else:
                print("[SAFE_IMG] 대표이미지 없음 - 텍스트만 발행")
            
            # 5. 포스트 발행 (메모리 효율적인 다중 시도 방식)
            print(f"[POST] 최종 포스트 데이터: title={post_data.get('title')}, featured_media={post_data.get('featured_media')}")
            
            # 메모리 부족 오류를 위해 콘텐츠 크기 체크
            content_size = len(json.dumps(post_data, ensure_ascii=False))
            print(f"[POST] 콘텐츠 크기: {content_size:,} bytes")
            
            # 128MB PHP 메모리 제한을 고려하여 콘텐츠 크기 조정
            if content_size > 100000:  # 100KB 이상이면 축소
                print(f"[POST] 콘텐츠가 큼 ({content_size:,} bytes), 축소 시도")
                original_content = post_data.get('content', '')
                if len(original_content) > 50000:
                    # 콘텐츠 절반으로 축소
                    truncated_content = original_content[:len(original_content)//2] + "\n\n[콘텐츠가 길어 일부만 표시됩니다]"
                    post_data['content'] = truncated_content
                    print(f"[POST] 콘텐츠 축소 완료: {len(truncated_content):,} chars -> {len(json.dumps(post_data, ensure_ascii=False)):,} bytes")
            
            # 텍스트 전용 모드에서는 재시도 횟수 줄임, 타임아웃도 대폭 단축
            max_attempts = 1 if text_only else 2
            publish_timeout = 10 if text_only else 30  # 텍스트 전용: 10초, 일반: 30초
            for attempt in range(max_attempts):  # 텍스트 전용시 1회, 일반 모드 3회 시도
                try:
                    if attempt == 1:
                        # 2차 시도: 더 간단한 포스트 데이터로 재시도
                        simple_post_data = {
                            'title': post_data.get('title', ''),
                            'content': post_data.get('content', '')[:8000],  # 8KB로 더 엄격하게 제한
                            'status': 'publish',
                            'format': 'standard'
                        }
                        post_data = simple_post_data
                        print(f"[POST] 간소화된 데이터 사용: {len(json.dumps(post_data, ensure_ascii=False)):,} bytes")
                        
                        headers = {
                            "Authorization": self.headers["Authorization"],
                            "Content-Type": "application/json"
                        }
                    elif attempt == 2:
                        # 3차 시도: 최소 콘텐츠로 재시도
                        minimal_post_data = {
                            'title': post_data.get('title', '')[:100],  # 제목도 축소
                            'content': f"<p>{post_data.get('title', '')}</p><p>콘텐츠 메모리 제한으로 인한 요약 발행</p>",
                            'status': 'publish'
                        }
                        post_data = minimal_post_data
                        print(f"[POST] 최소 데이터 사용: {len(json.dumps(post_data, ensure_ascii=False)):,} bytes")
                        
                        headers = {"Authorization": self.headers["Authorization"]}
                        response = self.session.post(
                            f"{self.api_url}posts",
                            headers=headers,
                            json=post_data,  # json 파라미터 사용
                            timeout=publish_timeout
                        )
                    else:
                        # 1차 시도: 기본 헤더
                        headers = self.headers
                    
                    # 1차, 2차 시도만 여기서 실행 (3차는 위에서 이미 실행됨)
                    if attempt != 2:
                        response = self.session.post(
                            f"{self.api_url}posts",
                            headers=headers,
                            data=json.dumps(post_data),
                            timeout=publish_timeout
                        )
                    
                    print(f"[PUBLISH] 응답 상태코드: {response.status_code}")
                    print(f"[PUBLISH] 응답 헤더: {dict(response.headers)}")
                    
                    if response.status_code in [200, 201]:
                        post = response.json()
                        post_id = post['id']
                        print(f"[SUCCESS] 포스트 발행 성공! ID: {post_id}, URL: {post.get('link')}")
                        
                        # 이미지 관련 코드 제거
                        
                        return True, post['link']
                    elif response.status_code == 401 and attempt < 2:
                        print(f"[AUTH] 인증 실패 (시도 {attempt + 1}/3), 다른 방식으로 재시도...")
                        continue
                    else:
                        print(f"[ERROR] 발행 실패 (시도 {attempt + 1}/3)")
                        print(f"[ERROR] 상태코드: {response.status_code}")
                        print(f"[ERROR] 응답 내용: {response.text[:1000]}")
                        
                        # PHP 메모리 부족 오류 특별 처리
                        if response.status_code == 500 and 'memory size' in response.text:
                            print("[MEMORY] PHP 메모리 부족 오류 감지 - 콘텐츠 더 축소")
                            if attempt < 2:  # 아직 시도 남음
                                continue
                        
                        error_msg = f"발행 실패: {response.status_code} - {response.text[:500]}"
                        if attempt == 2:  # 마지막 시도
                            return False, error_msg
                        
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
            response = self.session.post(
                f"{self.api_url}posts/{post_id}",
                data=json.dumps(update_data),
                timeout=30  # 15초 → 30초로 증가
            )
            
            if response.status_code == 200:
                print(f"[FEATURED] 포스트 업데이트로 대표이미지 설정 성공: {media_id}")
                return True
            else:
                print(f"[FEATURED] 포스트 업데이트 실패: {response.status_code} - {response.text[:200]}")
            
            # 방법 2: 메타 필드 직접 설정
            meta_data = {"_thumbnail_id": str(media_id)}
            response = self.session.post(
                f"{self.api_url}posts/{post_id}/meta",
                data=json.dumps(meta_data),
                timeout=30  # 15초 → 30초로 증가
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
                    img_response = self.session.get(image['url'], timeout=10)  # timeout 단축
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
            response = self.session.post(
                f"{self.api_url}media",
                headers=headers,
                data=img_data,
                timeout=120  # 업로드는 더 긴 타임아웃 필요
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
        """카테고리 ID 가져오기 또는 생성 (미분류 방지)"""
        if not category_names:
            print("[CATEGORY] 카테고리가 없어 기본 카테고리 사용")
            return [1]  # WordPress 기본 카테고리 ID (일반적으로 1)
        
        # 캐시 확인
        if self._categories_cache is None:
            self._load_categories()
        
        category_ids = []
        for name in category_names:
            print(f"[CATEGORY] 카테고리 처리 중: {name}")
            # 기존 카테고리 찾기
            cat_id = None
            for cat in self._categories_cache:
                if cat['name'].lower() == name.lower():
                    cat_id = cat['id']
                    print(f"[CATEGORY] 기존 카테고리 찾음: {name} -> ID {cat_id}")
                    break
            
            # 없으면 생성
            if not cat_id:
                print(f"[CATEGORY] 새 카테고리 생성: {name}")
                cat_id = self._create_category(name)
                if cat_id:
                    print(f"[CATEGORY] 카테고리 생성 성공: {name} -> ID {cat_id}")
                else:
                    print(f"[CATEGORY] 카테고리 생성 실패: {name}, 기본 카테고리 사용")
                    cat_id = 1  # 실패 시 기본 카테고리
            
            if cat_id:
                category_ids.append(cat_id)
        
        # 빈 리스트면 기본 카테고리 추가
        if not category_ids:
            print("[CATEGORY] 모든 카테고리 실패, 기본 카테고리 사용")
            category_ids = [1]
        
        print(f"[CATEGORY] 최종 카테고리 IDs: {category_ids}")
        return category_ids
    
    def _load_categories(self):
        """모든 카테고리 로드"""
        try:
            response = self.session.get(
                f"{self.api_url}categories?per_page=100",
                timeout=5  # 카테고리 로드 빠른 타임아웃
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
            response = self.session.post(
                f"{self.api_url}categories",
                data=json.dumps(data),
                timeout=3  # 카테고리 생성 최대 3초
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
            response = self.session.get(
                f"{self.api_url}tags?per_page=100",
                timeout=3  # 태그 로드 빠른 타임아웃
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
            response = self.session.post(
                f"{self.api_url}tags",
                data=json.dumps(data),
                timeout=3  # 태그 생성 최대 3초
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
        """콘텐츠 HTML 포맷팅 - 실제 발행용 (태그 제거 및 깨끗한 HTML)"""
        
        # 이미 완성된 HTML이 있으면 WordPress 발행용으로 변환
        if 'content' in content and content['content'] and not content.get('sections'):
            raw_html = content['content']
            print(f"[WP_FORMAT] 원본 HTML 길이: {len(raw_html)}")
            
            # HTML에서 본문 내용만 추출하고 불필요한 요소들 제거
            import re
            from bs4 import BeautifulSoup
            
            try:
                soup = BeautifulSoup(raw_html, 'html.parser')
                
                # content-container div 찾기
                container_div = soup.find('div', class_='content-container')
                if container_div:
                    print(f"[WP_FORMAT] content-container 발견")
                    
                    # 1. 불필요한 요소들 완전 제거
                    for selector in [
                        {'class': ['meta-info', 'wordpress-actions', 'site-badge', 'tags', 'metadata']},
                        {'name': 'script'},
                        {'name': 'style'},
                        {'class': lambda x: x and any(cls in x for cls in ['meta', 'badge', 'action', 'tag'])},
                    ]:
                        if 'class' in selector and callable(selector['class']):
                            elements = container_div.find_all(attrs={'class': selector['class']})
                        elif 'class' in selector:
                            elements = container_div.find_all(class_=selector['class'])
                        else:
                            elements = container_div.find_all(selector['name'])
                        
                        for element in elements:
                            element.decompose()
                    
                    # 2. div class="tags" 완전 제거
                    tags_divs = container_div.find_all('div', class_='tags')
                    for tags_div in tags_divs:
                        tags_div.decompose()
                    
                    # 3. 모든 span class="tag" 제거
                    tag_spans = container_div.find_all('span', class_='tag')
                    for tag_span in tag_spans:
                        tag_span.decompose()
                    
                    # 4. #으로 시작하는 태그 텍스트 제거
                    for text_node in container_div.find_all(text=True):
                        if text_node.strip().startswith('#'):
                            text_node.replace_with('')
                    
                    # 5. container div 내용만 추출 (div 태그 자체는 제거)
                    clean_content = ''
                    for child in container_div.children:
                        if hasattr(child, 'name'):  # 태그인 경우
                            clean_content += str(child)
                        elif child.strip():  # 텍스트인 경우
                            clean_content += str(child)
                    
                    print(f"[WP_FORMAT] 정리된 콘텐츠 길이: {len(clean_content)}")
                    
                    # 6. 추가 정리 - 빈 태그들과 불필요한 구조 제거
                    clean_soup = BeautifulSoup(clean_content, 'html.parser')
                    
                    # 빈 p, div 태그 제거
                    for empty_tag in clean_soup.find_all(['p', 'div']):
                        if not empty_tag.get_text().strip():
                            empty_tag.decompose()
                    
                    # 연속된 br 태그 정리
                    clean_html = str(clean_soup)
                    clean_html = re.sub(r'(<br\s*/?>\s*){3,}', '<br><br>', clean_html)
                    
                    # WordPress 스타일 구분선 추가
                    clean_html = re.sub(r'<hr[^>]*>', '<hr class="wp-block-separator" />', clean_html)
                    
                    print(f"[WP_FORMAT] 최종 WordPress 콘텐츠 길이: {len(clean_html)}")
                    print(f"[WP_FORMAT] 최종 콘텐츠 미리보기: {clean_html[:300]}...")
                    
                    return clean_html.strip()
                    
                else:
                    print("[WP_FORMAT] content-container를 찾을 수 없음, body에서 추출")
                    body = soup.find('body')
                    if body:
                        # body 내용에서도 불필요한 요소들 제거
                        for unwanted in body.find_all(['script', 'style']):
                            unwanted.decompose()
                        for meta_div in body.find_all('div', class_=['meta-info', 'tags', 'wordpress-actions']):
                            meta_div.decompose()
                        return str(body).replace('<body>', '').replace('</body>', '').strip()
                    
            except Exception as e:
                print(f"[WP_FORMAT] BeautifulSoup 파싱 오류: {e}")
            
            # 백업: 정규식으로 기본 정리
            clean_content = raw_html
            
            # 태그 div와 관련 요소들 정규식으로 제거
            clean_content = re.sub(r'<div[^>]*class="[^"]*tags[^"]*"[^>]*>.*?</div>', '', clean_content, flags=re.DOTALL)
            clean_content = re.sub(r'<span[^>]*class="[^"]*tag[^"]*"[^>]*>.*?</span>', '', clean_content, flags=re.DOTALL)
            clean_content = re.sub(r'<div[^>]*class="[^"]*meta-info[^"]*"[^>]*>.*?</div>', '', clean_content, flags=re.DOTALL)
            clean_content = re.sub(r'#[가-힣a-zA-Z0-9\s]+(?=\s|$)', '', clean_content)  # 해시태그 제거
            
            # body 내용만 추출
            body_match = re.search(r'<body[^>]*>(.*?)</body>', clean_content, re.DOTALL | re.IGNORECASE)
            if body_match:
                return body_match.group(1).strip()
            
            return clean_content
        
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
        
        # 추가 유용한 내용
        if content.get('additional_content'):
            # 마무리 제목 없이 자연스럽게 추가 내용 삽입
            html.append(f"<div class='additional-content' style='margin-top: 2rem; padding: 1.5rem; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #0073aa;'>")
            html.append(f"<p style='margin: 0; font-style: italic;'>{content['additional_content']}</p>")
            html.append(f"</div>")
        elif content.get('conclusion'):
            # 기존 호환성 유지 - 제목 없이 자연스럽게
            html.append(f"<div class='conclusion-content' style='margin-top: 2rem; padding: 1.5rem; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #0073aa;'>")
            html.append(f"<p style='margin: 0; font-style: italic;'>{content['conclusion']}</p>")
            html.append(f"</div>")
        
        # 관련 링크 (내부 링크)
        if content.get('internal_links'):
            html.append("<h3>관련 글</h3>")
            html.append("<ul>")
            for link in content['internal_links']:
                html.append(f'<li><a href="{link["url"]}">{link["title"]}</a></li>')
            html.append("</ul>")
        
        # 커스텀 CSS 스타일 추가 - 대폭 개선된 디자인
        custom_css = """
<style>
/* 기본 레이아웃 개선 */
.wp-blog-content {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.8;
    color: #2c3e50;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

/* 강조 텍스트 스타일 */
.highlight-text strong { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    position: relative;
}
.highlight-text strong::before {
    content: '★';
    color: #f39c12;
    margin-right: 5px;
}

/* 포인트 텍스트 */
.point-text em { 
    background: linear-gradient(45deg, #3498db, #2ecc71);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-style: normal;
    font-weight: 600;
    position: relative;
}
.point-text em::before {
    content: '◆';
    color: #e74c3c;
    margin-right: 3px;
}

/* 코드 블록 개선 */
.code-block { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    margin: 20px 0;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    position: relative;
    overflow: hidden;
}
.code-block::before {
    content: '{ }';
    position: absolute;
    top: 10px;
    right: 15px;
    font-size: 18px;
    opacity: 0.7;
}
.code-block code {
    background: none;
    color: #ffffff;
    font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
    font-size: 14px;
}

/* 인라인 코드 */
.inline-code {
    background: linear-gradient(135deg, #ff7eb3, #ff758c);
    color: white;
    padding: 4px 10px;
    border-radius: 20px;
    font-family: 'Fira Code', monospace;
    font-size: 0.9em;
    box-shadow: 0 2px 10px rgba(255, 126, 179, 0.3);
}

/* 헤딩 스타일 개선 */
.sub-heading { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.3em;
    font-weight: 700;
    margin: 30px 0 15px 0;
    position: relative;
    padding-left: 20px;
}
.sub-heading::before {
    content: '▶';
    color: #e74c3c;
    position: absolute;
    left: 0;
    top: 0;
}

.section-heading { 
    background: linear-gradient(135deg, #ff7eb3, #ff758c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.5em;
    font-weight: 800;
    margin: 35px 0 20px 0;
    position: relative;
    padding-left: 25px;
    border-left: 5px solid #ff758c;
    padding-left: 15px;
}

/* 번호 목록 개선 */
.numbered-item { 
    margin: 15px 0;
    padding: 15px;
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(252, 182, 159, 0.3);
    position: relative;
    padding-left: 60px;
}
.number-badge { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 8px 12px;
    border-radius: 50%;
    font-size: 1em;
    font-weight: bold;
    position: absolute;
    left: 15px;
    top: 50%;
    transform: translateY(-50%);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

/* 불릿 목록 */
.bullet-item { 
    margin: 12px 0;
    padding: 12px 15px;
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    border-radius: 8px;
    padding-left: 45px;
    position: relative;
    box-shadow: 0 3px 10px rgba(168, 237, 234, 0.3);
}
.bullet-icon { 
    color: #e67e22;
    font-size: 1.2em;
    position: absolute;
    left: 15px;
    top: 50%;
    transform: translateY(-50%);
}

/* 키워드 배지들 */
.keyword-badge { 
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: bold;
    box-shadow: 0 5px 15px rgba(240, 147, 251, 0.4);
    margin: 0 3px;
}
.success-badge { 
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: bold;
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
    margin: 0 3px;
}
.error-badge { 
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: bold;
    box-shadow: 0 5px 15px rgba(250, 112, 154, 0.4);
    margin: 0 3px;
}

/* 수치 강조 */
.percentage { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    font-size: 1.1em;
}
.money { 
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    font-size: 1.1em;
}
.date { 
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    font-size: 1.05em;
}

/* 링크 스타일 */
.external-link { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-decoration: none;
    padding: 8px 15px;
    border-radius: 25px;
    font-weight: 600;
    display: inline-block;
    margin: 5px 0;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
}
.external-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}
.email-link { 
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    color: #8e44ad;
    text-decoration: none;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: 600;
    display: inline-block;
    margin: 3px 0;
    box-shadow: 0 3px 10px rgba(168, 237, 234, 0.3);
}

/* 구분선 스타일 */
.wp-block-separator {
    border: none;
    height: 3px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 30px 0;
    border-radius: 2px;
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

/* 추가 장식 요소들 */
.content-wrapper {
    background: #fafafa;
    border-radius: 15px;
    padding: 30px;
    margin: 20px 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
    .wp-blog-content { padding: 15px; }
    .numbered-item, .bullet-item { padding: 10px; }
    .code-block { padding: 15px; }
}
</style>
"""
        
        # HTML을 wrapper로 감싸서 스타일 적용
        newline = "\n"
        wrapped_html = f'<div class="wp-blog-content">{newline.join(html)}</div>'
        return custom_css + "\n" + wrapped_html
    
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
        """텍스트 서식 개선 (마크다운 → 예쁜 HTML)"""
        import re
        
        # ** -> 강조 스타일 (굵은 글씨)
        text = re.sub(r'\*\*(.*?)\*\*', r'<span class="highlight-text"><strong>\1</strong></span>', text)
        
        # * -> 포인트 강조 (기울임)  
        text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<span class="point-text"><em>※ \1</em></span>', text)
        
        # ``` -> 코드 박스
        text = re.sub(r'```([^`]+)```', r'<div class="code-block">【코드】 <code>\1</code></div>', text)
        text = re.sub(r'`([^`]+)`', r'<span class="inline-code">『\1』</span>', text)
        
        # ### -> 소제목 강조
        text = re.sub(r'###\s*([^\n]+)', r'<h4 class="sub-heading">◆ \1</h4>', text)
        
        # ## -> 중간 제목
        text = re.sub(r'##\s*([^\n]+)', r'<h3 class="section-heading">■ \1</h3>', text)
        
        # 번호 목록 개선 (1. 2. 3. -> 예쁜 HTML 목록)
        text = re.sub(r'(\d+)\.\s+([^\n]+)', r'<div class="numbered-item"><span class="number-badge">❶ \1</span> \2</div>', text)
        
        # • 또는 - 로 시작하는 목록 개선
        text = re.sub(r'[•-]\s+([^\n]+)', r'<div class="bullet-item"><span class="bullet-icon">→</span> \1</div>', text)
        
        # 특수 키워드 강조
        text = re.sub(r'\b(중요|주의|참고|팁|TIP|NOTE)\b', r'<span class="keyword-badge">【\1】</span>', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(완료|성공|SUCCESS)\b', r'<span class="success-badge">✓ \1</span>', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(오류|에러|ERROR|실패)\b', r'<span class="error-badge">X \1</span>', text, flags=re.IGNORECASE)
        
        # 퍼센트, 숫자 강조
        text = re.sub(r'(\d+)%', r'<span class="percentage">【\1%】</span>', text)
        text = re.sub(r'(\d{1,3}(?:,\d{3})*)(원|달러|\$)', r'<span class="money">￦ \1\2</span>', text)
        
        # 날짜 형식 예쁘게
        text = re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', r'<span class="date">» \1년 \2월 \3일</span>', text)
        text = re.sub(r'(\d{4})년\s*(\d{1,2})월', r'<span class="date">▷ \1년 \2월</span>', text)
        
        # 링크 형태 개선
        text = re.sub(r'(https?://[^\s]+)', r'<a href="\1" class="external-link" target="_blank">→ 참조링크</a>', text)
        
        # 이메일 주소 개선
        text = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'<a href="mailto:\1" class="email-link">@ \1</a>', text)
        
        return text
    
    def update_post(self, post_id: int, updates: Dict) -> bool:
        """기존 포스트 업데이트"""
        try:
            response = self.session.post(
                f"{self.api_url}posts/{post_id}",
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
            response = self.session.get(
                f"{self.api_url}posts",
                params={"per_page": count, "orderby": "date", "order": "desc"},
                timeout=30  # 10초 → 30초로 증가
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
                timeout=30  # 10초 → 30초로 증가
            )
            return response.status_code == 200
        except Exception as e:
            print(f"포스트 삭제 실패: {e}")
            return False