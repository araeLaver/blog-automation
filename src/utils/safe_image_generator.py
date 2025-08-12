"""
안전한 이미지 생성 모듈
- Pexels API를 통한 고품질 이미지 우선
- 실패시 로컬 PIL 이미지 생성으로 폴백
- 최소한의 리소스 사용
"""

import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime
import hashlib
from .pexels_api import init_pexels_api

class SafeImageGenerator:
    """안전한 이미지 생성기 - Pexels API 우선, 로컬 폴백"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "blog_automation_images"
        self.temp_dir.mkdir(exist_ok=True)
        self.pexels_api = None
        
        # 주제별 색상 팔레트 및 키워드
        self.theme_colors = {
            'programming': [('#2E3440', '#88C0D0'), ('#3B4252', '#81A1C1')],  # 개발 관련
            'ai_ml': [('#1A1A2E', '#E94560'), ('#16213E', '#0F3460')],        # AI/ML 관련  
            'web': [('#FF6B6B', '#FFFFFF'), ('#4ECDC4', '#FFFFFF')],          # 웹 관련
            'data': [('#6C5CE7', '#FFFFFF'), ('#A29BFE', '#2D3436')],         # 데이터 관련
            'security': [('#2D3436', '#DDD'), ('#636E72', '#FFFFFF')],        # 보안 관련
            'mobile': [('#00B894', '#FFFFFF'), ('#00CEC9', '#2D3436')],       # 모바일 관련
            'default': [('#4A90E2', '#FFFFFF'), ('#7B68EE', '#FFFFFF')]       # 기본
        }
        
        # 주제별 키워드
        self.theme_keywords = {
            'programming': ['python', 'java', 'javascript', '프로그래밍', '코딩', '개발', '함수', '클래스', '알고리즘'],
            'ai_ml': ['ai', 'ml', '머신러닝', '딥러닝', '인공지능', '모델', '학습', '데이터사이언스'],
            'web': ['html', 'css', 'react', '웹', '프론트엔드', '백엔드', 'api', 'http'],
            'data': ['데이터', 'sql', '데이터베이스', '분석', '시각화', '빅데이터'],
            'security': ['보안', 'security', '암호화', '해킹', '방화벽'],
            'mobile': ['모바일', 'android', 'ios', '앱', 'flutter', 'react native']
        }
    
    def set_pexels_api_key(self, api_key: str):
        """Pexels API 키 설정"""
        try:
            self.pexels_api = init_pexels_api(api_key)
            print("[PEXELS] API 초기화 완료")
        except Exception as e:
            print(f"[PEXELS] API 초기화 실패: {e}")
            self.pexels_api = None
    
    def generate_featured_image(self, title: str, width: int = 1200, height: int = 630) -> str:
        """
        제목을 기반으로 대표이미지 생성 (Pexels API 우선, 로컬 폴백)
        
        Args:
            title: 게시물 제목
            width: 이미지 너비
            height: 이미지 높이
            
        Returns:
            생성된 이미지 파일 경로
        """
        try:
            # 1차 시도: Pexels API로 고품질 이미지 검색
            if self.pexels_api:
                print(f"[IMG] Pexels API로 이미지 검색 중: {title}")
                pexels_image = self.pexels_api.search_image(title, width, height)
                if pexels_image and os.path.exists(pexels_image):
                    print(f"[IMG] Pexels 이미지 사용: {pexels_image}")
                    return pexels_image
                else:
                    print("[IMG] Pexels 검색 실패, 로컬 생성으로 폴백")
            else:
                print("[IMG] Pexels API 없음, 로컬 생성 사용")
            
            # 2차 시도: 로컬 이미지 생성 (폴백)
            return self._generate_local_image(title, width, height)
            
        except Exception as e:
            print(f"[IMG] 이미지 생성 실패: {e}")
            return None
    
    def _generate_local_image(self, title: str, width: int = 1200, height: int = 630) -> str:
        """로컬 PIL을 사용한 이미지 생성"""
        try:
            print(f"[LOCAL_IMG] 로컬 이미지 생성 시작: {title}")
            
            # 제목을 분석해서 주제 결정
            theme = self._detect_theme(title)
            
            # 주제에 맞는 색상 선택
            theme_colors = self.theme_colors.get(theme, self.theme_colors['default'])
            color_index = abs(hash(title)) % len(theme_colors)
            bg_color, text_color = theme_colors[color_index]
            
            # 그라데이션 배경 생성
            image = self._create_gradient_background(width, height, bg_color)
            draw = ImageDraw.Draw(image)
            
            # 텍스트 준비 (긴 제목 줄바꿈)
            display_text = self._prepare_text(title, max_length=40)
            
            # 기본 폰트 사용 (안전함)
            try:
                font_size = min(width // 15, height // 8)  # 적당한 크기
                font = ImageFont.load_default()
            except:
                font = None
            
            # 텍스트 위치 계산 (중앙 정렬)
            text_bbox = draw.textbbox((0, 0), display_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # 텍스트 그리기
            draw.text((x, y), display_text, fill=text_color, font=font, align='center')
            
            # 파일 저장 (안전한 파일명)
            safe_filename = self._get_safe_filename(title)
            filepath = self.temp_dir / f"{safe_filename}.jpg"
            
            # JPEG로 저장 (용량 최적화)
            image.save(filepath, 'JPEG', quality=85, optimize=True)
            
            print(f"[LOCAL_IMG] 로컬 이미지 생성 완료: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"[LOCAL_IMG] 로컬 이미지 생성 실패: {e}")
            return None
    
    def _prepare_text(self, text: str, max_length: int = 40) -> str:
        """텍스트 줄바꿈 및 정리"""
        if len(text) <= max_length:
            return text
        
        # 긴 제목은 줄바꿈
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # 최대 3줄까지만
        return '\n'.join(lines[:3])
    
    def _get_safe_filename(self, title: str) -> str:
        """안전한 파일명 생성"""
        # 해시를 사용해서 안전한 파일명 생성
        title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"featured_{timestamp}_{title_hash}"
    
    def _detect_theme(self, title: str) -> str:
        """제목을 분석해서 주제 감지"""
        title_lower = title.lower()
        
        for theme, keywords in self.theme_keywords.items():
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    return theme
        
        return 'default'
    
    def _create_gradient_background(self, width: int, height: int, base_color: str) -> Image.Image:
        """그라데이션 배경 생성"""
        try:
            # 기본 색상에서 약간 다른 색상으로 그라데이션
            image = Image.new('RGB', (width, height), color=base_color)
            
            # 간단한 선형 그라데이션 효과
            draw = ImageDraw.Draw(image)
            
            # 어두운 오버레이로 깊이감 추가
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 30))
            image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
            
            return image
        except:
            # 실패시 단색 배경
            return Image.new('RGB', (width, height), color=base_color)
    
    def cleanup_old_images(self, max_age_hours: int = 24):
        """오래된 임시 이미지 파일 정리"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filepath in self.temp_dir.glob("featured_*.jpg"):
                if current_time - filepath.stat().st_mtime > max_age_seconds:
                    filepath.unlink()
                    print(f"[SAFE_IMG] 오래된 이미지 삭제: {filepath}")
        except Exception as e:
            print(f"[SAFE_IMG] 이미지 정리 실패: {e}")

# 전역 인스턴스
safe_image_generator = SafeImageGenerator()