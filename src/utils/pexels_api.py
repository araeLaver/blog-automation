"""
Pexels API 연동 모듈
- 고품질 이미지 검색 및 다운로드
- 안전한 로컬 저장
"""

import os
import requests
import tempfile
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Optional, List, Dict
import time

class PexelsAPI:
    """Pexels API를 통한 고품질 이미지 검색"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {
            'Authorization': api_key,
            'User-Agent': 'BlogAutomation/1.0'
        }
        self.temp_dir = Path(tempfile.gettempdir()) / "blog_automation_images"
        self.temp_dir.mkdir(exist_ok=True)
        
        # 주제별 검색 키워드 맵핑
        self.theme_keywords = {
            'programming': ['programming', 'code', 'developer', 'computer', 'software'],
            'ai_ml': ['artificial intelligence', 'machine learning', 'data science', 'technology', 'robot'],
            'web': ['web development', 'website', 'internet', 'digital', 'computer'],
            'data': ['data analysis', 'database', 'analytics', 'charts', 'statistics'],
            'security': ['cyber security', 'protection', 'shield', 'lock', 'safe'],
            'mobile': ['mobile phone', 'smartphone', 'app development', 'mobile app', 'technology'],
            'default': ['technology', 'business', 'modern', 'digital', 'abstract']
        }
    
    def search_image(self, title: str, width: int = 1200, height: int = 630) -> Optional[str]:
        """
        제목 기반으로 적합한 이미지 검색 및 다운로드
        
        Args:
            title: 게시물 제목
            width: 원하는 이미지 너비
            height: 원하는 이미지 높이
            
        Returns:
            다운로드된 이미지 파일 경로 또는 None
        """
        try:
            # 1. 주제 감지 및 검색어 생성
            theme = self._detect_theme(title)
            search_query = self._generate_search_query(title, theme)
            
            print(f"[PEXELS] 이미지 검색: {search_query} (주제: {theme})")
            
            # 2. Pexels API 검색
            search_url = f"{self.base_url}/search"
            params = {
                'query': search_query,
                'per_page': 5,  # 상위 5개만
                'orientation': 'landscape',  # 가로형
                'size': 'large'
            }
            
            response = requests.get(search_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"[PEXELS] API 요청 실패: {response.status_code}")
                return None
            
            data = response.json()
            photos = data.get('photos', [])
            
            if not photos:
                print(f"[PEXELS] 검색 결과 없음: {search_query}")
                return None
            
            # 3. 가장 적합한 이미지 선택 (해상도 기준)
            best_photo = self._select_best_photo(photos, width, height)
            if not best_photo:
                print(f"[PEXELS] 적합한 이미지 없음")
                return None
            
            # 4. 이미지 다운로드
            image_path = self._download_image(best_photo, title)
            
            if image_path:
                print(f"[PEXELS] 이미지 다운로드 성공: {image_path}")
            
            return image_path
            
        except Exception as e:
            print(f"[PEXELS] 이미지 검색 오류: {e}")
            return None
    
    def _detect_theme(self, title: str) -> str:
        """제목에서 주제 감지"""
        title_lower = title.lower()
        
        # 한글 키워드 매핑
        korean_keywords = {
            'programming': ['프로그래밍', '코딩', '개발', '함수', '클래스', '알고리즘', 'python', 'java', 'javascript'],
            'ai_ml': ['ai', 'ml', '머신러닝', '딥러닝', '인공지능', '모델', '학습', '데이터사이언스'],
            'web': ['html', 'css', 'react', '웹', '프론트엔드', '백엔드', 'api', 'http'],
            'data': ['데이터', 'sql', '데이터베이스', '분석', '시각화', '빅데이터'],
            'security': ['보안', 'security', '암호화', '해킹', '방화벽'],
            'mobile': ['모바일', 'android', 'ios', '앱', 'flutter', 'react native']
        }
        
        for theme, keywords in korean_keywords.items():
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    return theme
        
        return 'default'
    
    def _generate_search_query(self, title: str, theme: str) -> str:
        """제목과 주제를 기반으로 검색어 생성"""
        # 주제별 키워드 선택
        theme_words = self.theme_keywords.get(theme, self.theme_keywords['default'])
        
        # 제목에서 영어 단어 추출
        import re
        english_words = re.findall(r'[a-zA-Z]+', title)
        
        # 검색어 조합
        if english_words:
            # 영어 단어가 있으면 우선 사용
            search_terms = english_words[:2] + theme_words[:1]
        else:
            # 없으면 주제 키워드만 사용
            search_terms = theme_words[:2]
        
        return ' '.join(search_terms[:3])  # 최대 3개 단어
    
    def _select_best_photo(self, photos: List[Dict], target_width: int, target_height: int) -> Optional[Dict]:
        """가장 적합한 사진 선택"""
        if not photos:
            return None
        
        best_photo = None
        best_score = 0
        
        for photo in photos:
            src = photo.get('src', {})
            
            # 사용 가능한 크기들 확인
            for size_name in ['large2x', 'large', 'medium']:
                if size_name in src:
                    # 해상도와 비율 고려한 점수 계산
                    width = photo.get('width', 0)
                    height = photo.get('height', 0)
                    
                    if width > 0 and height > 0:
                        # 비율 점수 (16:9 또는 1200:630에 가까울수록 높음)
                        target_ratio = target_width / target_height
                        actual_ratio = width / height
                        ratio_score = 1 - abs(target_ratio - actual_ratio) / target_ratio
                        
                        # 해상도 점수 (클수록 좋음, 단 너무 크면 감점)
                        res_score = min(width / target_width, 2.0) / 2.0
                        
                        total_score = ratio_score * 0.7 + res_score * 0.3
                        
                        if total_score > best_score:
                            best_score = total_score
                            best_photo = {
                                'url': src[size_name],
                                'photographer': photo.get('photographer', 'Unknown'),
                                'id': photo.get('id'),
                                'width': width,
                                'height': height
                            }
                            break
        
        return best_photo
    
    def _download_image(self, photo: Dict, title: str) -> Optional[str]:
        """이미지 다운로드"""
        try:
            url = photo['url']
            
            # 이미지 다운로드
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 안전한 파일명 생성
            safe_filename = self._get_safe_filename(title, photo['id'])
            filepath = self.temp_dir / f"{safe_filename}.jpg"
            
            # 파일 저장
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # 파일 크기 확인
            file_size = os.path.getsize(filepath)
            print(f"[PEXELS] 다운로드 완료: {file_size:,} bytes")
            
            return str(filepath)
            
        except Exception as e:
            print(f"[PEXELS] 다운로드 오류: {e}")
            return None
    
    def _get_safe_filename(self, title: str, photo_id: int) -> str:
        """안전한 파일명 생성"""
        title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"pexels_{timestamp}_{photo_id}_{title_hash}"
    
    def cleanup_old_images(self, max_age_hours: int = 24):
        """오래된 임시 이미지 파일 정리"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filepath in self.temp_dir.glob("pexels_*.jpg"):
                if current_time - filepath.stat().st_mtime > max_age_seconds:
                    filepath.unlink()
                    print(f"[PEXELS] 오래된 이미지 삭제: {filepath}")
        except Exception as e:
            print(f"[PEXELS] 이미지 정리 실패: {e}")

# 전역 인스턴스 (API 키는 환경변수나 설정에서 로드)
pexels_api = None

def init_pexels_api(api_key: str):
    """Pexels API 초기화"""
    global pexels_api
    pexels_api = PexelsAPI(api_key)
    return pexels_api