"""
이미지 생성 및 처리 모듈
"""

import os
import requests
import json
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import io
import base64
from datetime import datetime
from pathlib import Path
import random
from dotenv import load_dotenv

load_dotenv()


class ImageGenerator:
    def __init__(self):
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.image_cache_dir = Path("./data/images")
        self.image_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 폰트 설정 (Windows 기준)
        self.font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕
        
    def generate_images_for_post(self, site: str, title: str, 
                                 content: Dict, count: int = 3) -> List[Dict]:
        """포스트용 이미지 세트 생성"""
        images = []
        
        # 1. 메인 썸네일 이미지
        thumbnail = self._generate_thumbnail(site, title, content.get('category', ''))
        images.append({
            "type": "thumbnail",
            "url": thumbnail,
            "alt": f"{title} 대표 이미지"
        })
        
        # 2. 콘텐츠 관련 이미지
        keywords = content.get('keywords', [])
        
        # 사이트별 이미지 전략
        if site == "unpre":  # IT/개발
            # 코드 스니펫 이미지
            if 'code_example' in content:
                code_img = self._generate_code_snippet(content['code_example'])
                images.append({
                    "type": "code",
                    "url": code_img,
                    "alt": "코드 예제"
                })
            
            # 기술 스택 다이어그램
            if 'tech_stack' in content:
                diagram = self._generate_tech_diagram(content['tech_stack'])
                images.append({
                    "type": "diagram",
                    "url": diagram,
                    "alt": "기술 스택 다이어그램"
                })
        
        elif site == "untab":  # 부동산
            # 통계 차트
            if 'statistics' in content:
                chart = self._generate_chart(content['statistics'])
                images.append({
                    "type": "chart",
                    "url": chart,
                    "alt": "부동산 시장 통계"
                })
            
            # 지역 지도 (실제 구현시 카카오맵 API 등 활용)
            if 'location' in content:
                map_img = self._generate_map_placeholder(content['location'])
                images.append({
                    "type": "map",
                    "url": map_img,
                    "alt": f"{content['location']} 위치"
                })
        
        elif site == "skewese":  # 역사
            # AI 생성 역사 이미지 (DALL-E)
            if keywords:
                historical_img = self._generate_with_dalle(
                    f"Historical scene: {keywords[0]}, artistic style, museum quality"
                )
                if historical_img:
                    images.append({
                        "type": "historical",
                        "url": historical_img,
                        "alt": f"{keywords[0]} 역사적 장면"
                    })
        
        elif site == "tistory":  # 언어학습
            # 문법 도표
            if 'grammar_points' in content:
                grammar_chart = self._generate_grammar_chart(content['grammar_points'])
                images.append({
                    "type": "grammar",
                    "url": grammar_chart,
                    "alt": "문법 설명 도표"
                })
        
        # 3. 무료 스톡 이미지로 부족한 개수 채우기
        while len(images) < count:
            stock_img = self._fetch_stock_image(keywords)
            if stock_img:
                images.append(stock_img)
            else:
                break
        
        return images
    
    def _generate_thumbnail(self, site: str, title: str, category: str) -> str:
        """주제별 관련 썸네일 이미지 생성"""
        # 주제에서 키워드 추출하여 관련 이미지 검색
        keywords = self._extract_keywords_from_title(title, site)
        
        # 먼저 외부 이미지 API로 관련 이미지 검색 시도
        related_image = self._search_related_image(keywords, site)
        if related_image:
            return related_image
        
        # 외부 이미지가 없으면 커스텀 썸네일 생성
        return self._create_custom_thumbnail(site, title, category, keywords)
    
    def _extract_keywords_from_title(self, title: str, site: str) -> List[str]:
        """제목에서 이미지 검색용 키워드 추출"""
        keywords = []
        
        # 사이트별 주요 키워드 매핑
        if site == "unpre":  # IT/개발
            tech_keywords = {
                "Redis": ["redis", "cache", "database"],
                "Docker": ["docker", "container", "devops"],
                "React": ["react", "javascript", "frontend"],
                "Python": ["python", "programming", "code"],
                "TypeScript": ["typescript", "javascript", "web"],
                "GraphQL": ["graphql", "api", "backend"],
                "Kubernetes": ["kubernetes", "container", "orchestration"]
            }
            
            for tech, related in tech_keywords.items():
                if tech in title:
                    keywords.extend(related)
                    break
            
            # 기본 IT 키워드
            if not keywords:
                keywords = ["technology", "computer", "software", "programming"]
        
        elif site == "untab":  # 투자/부동산
            investment_keywords = {
                "리츠": ["REIT", "real estate", "investment"],
                "부동산": ["real estate", "property", "building"],
                "투자": ["investment", "money", "finance"],
                "경매": ["auction", "property", "real estate"],
                "ESG": ["ESG", "sustainable", "investment"]
            }
            
            for term, related in investment_keywords.items():
                if term in title:
                    keywords.extend(related)
                    break
            
            if not keywords:
                keywords = ["investment", "money", "finance", "property"]
        
        elif site == "skewese":  # 역사/문화
            history_keywords = {
                "한글": ["korean", "hangul", "writing"],
                "역사": ["history", "korea", "traditional"],
                "조선": ["joseon", "korea", "traditional"],
                "고구려": ["goguryeo", "korea", "ancient"],
                "실학": ["practical learning", "korea", "philosophy"]
            }
            
            for term, related in history_keywords.items():
                if term in title:
                    keywords.extend(related)
                    break
            
            if not keywords:
                keywords = ["korea", "traditional", "culture", "history"]
        
        elif site == "tistory":  # 일반/트렌드
            trend_keywords = {
                "재건축": ["construction", "building", "urban"],
                "AI": ["artificial intelligence", "technology", "future"],
                "월드컵": ["world cup", "soccer", "sports"],
                "전기차": ["electric car", "tesla", "technology"]
            }
            
            for term, related in trend_keywords.items():
                if term in title:
                    keywords.extend(related)
                    break
            
            if not keywords:
                keywords = ["trend", "news", "technology", "business"]
        
        return keywords[:3]  # 최대 3개
    
    def _search_related_image(self, keywords: List[str], site: str) -> Optional[str]:
        """관련 이미지 검색 (Unsplash API 활용)"""
        if not self.unsplash_key or not keywords:
            return None
        
        try:
            query = " ".join(keywords)
            url = f"https://api.unsplash.com/search/photos"
            
            params = {
                "query": query,
                "per_page": 5,
                "orientation": "landscape",
                "client_id": self.unsplash_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    # 첫 번째 결과 사용
                    photo = data["results"][0]
                    return photo["urls"]["regular"]
        
        except Exception as e:
            print(f"이미지 검색 실패: {e}")
        
        return None
    
    def _create_custom_thumbnail(self, site: str, title: str, category: str, keywords: List[str]) -> str:
        """커스텀 썸네일 생성 (관련 이미지가 없을 때)"""
        # 이미지 크기
        width, height = 1200, 630  # OG 이미지 표준 크기
        
        # 사이트별 색상 테마 (주제별로 더 세분화)
        theme = self._get_theme_by_keywords(site, keywords)
        
        # 이미지 생성
        img = Image.new('RGB', (width, height), theme['bg'])
        draw = ImageDraw.Draw(img)
        
        try:
            # 폰트 설정
            title_font = ImageFont.truetype(self.font_path, 60)
            category_font = ImageFont.truetype(self.font_path, 30)
            site_font = ImageFont.truetype(self.font_path, 24)
        except:
            # 폰트 로드 실패시 기본 폰트
            title_font = ImageFont.load_default()
            category_font = ImageFont.load_default()
            site_font = ImageFont.load_default()
        
        # 배경 패턴 추가
        for i in range(0, width, 50):
            draw.line([(i, 0), (i + height, height)], fill=theme['accent'], width=1)
        
        # 반투명 오버레이
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 180))
        img.paste(overlay, (0, 0), overlay)
        
        # 텍스트 그리기
        # 카테고리
        draw.text((60, 100), category.upper(), font=category_font, fill=theme['accent'])
        
        # 제목 (줄바꿈 처리)
        title_lines = self._wrap_text(title, 30)
        y_offset = 200
        for line in title_lines[:2]:  # 최대 2줄
            draw.text((60, y_offset), line, font=title_font, fill=theme['text'])
            y_offset += 80
        
        # 사이트 이름
        draw.text((60, height - 100), site.upper(), font=site_font, fill=theme['accent'])
        
        # 날짜
        date_str = datetime.now().strftime("%Y.%m.%d")
        draw.text((width - 200, height - 100), date_str, font=site_font, fill=theme['text'])
        
        # 이미지 저장
        img_path = self.image_cache_dir / f"thumbnail_{site}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        img.save(img_path, quality=95)
        
        return str(img_path)
    
    def _generate_code_snippet(self, code: str, language: str = "python") -> str:
        """코드 스니펫 이미지 생성"""
        # Carbon.now.sh API 스타일로 코드 이미지 생성
        width, height = 800, 600
        img = Image.new('RGB', (width, height), '#1e1e1e')
        draw = ImageDraw.Draw(img)
        
        try:
            code_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 14)
        except:
            code_font = ImageFont.load_default()
        
        # 코드 하이라이팅 (간단한 구현)
        lines = code.split('\n')
        y_offset = 40
        
        for line in lines[:20]:  # 최대 20줄
            # 간단한 구문 강조
            if line.strip().startswith('#'):
                color = '#608b4e'  # 주석
            elif 'def ' in line or 'class ' in line:
                color = '#569cd6'  # 키워드
            elif '"' in line or "'" in line:
                color = '#ce9178'  # 문자열
            else:
                color = '#d4d4d4'  # 일반 텍스트
            
            draw.text((20, y_offset), line, font=code_font, fill=color)
            y_offset += 25
        
        # 윈도우 프레임 효과
        draw.rectangle([(0, 0), (width-1, 30)], fill='#2d2d30')
        draw.ellipse([(10, 10), (20, 20)], fill='#ff5f56')
        draw.ellipse([(30, 10), (40, 20)], fill='#ffbd2e')
        draw.ellipse([(50, 10), (60, 20)], fill='#27c93f')
        
        img_path = self.image_cache_dir / f"code_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        img.save(img_path)
        
        return str(img_path)
    
    def _generate_chart(self, data: Dict) -> str:
        """차트 이미지 생성"""
        fig = go.Figure()
        
        # 데이터 타입에 따라 다른 차트 생성
        if 'time_series' in data:
            # 시계열 차트
            fig.add_trace(go.Scatter(
                x=data['time_series']['x'],
                y=data['time_series']['y'],
                mode='lines+markers',
                name='시세 변동',
                line=dict(color='#10b981', width=3)
            ))
            fig.update_layout(
                title=data.get('title', '부동산 시장 동향'),
                xaxis_title='기간',
                yaxis_title='가격(만원)',
                template='plotly_white'
            )
        
        elif 'comparison' in data:
            # 비교 차트
            fig.add_trace(go.Bar(
                x=data['comparison']['categories'],
                y=data['comparison']['values'],
                marker_color='#3b82f6'
            ))
            fig.update_layout(
                title=data.get('title', '지역별 비교'),
                template='plotly_white'
            )
        
        else:
            # 기본 파이 차트
            fig.add_trace(go.Pie(
                labels=['데이터1', '데이터2', '데이터3'],
                values=[30, 45, 25],
                hole=.3
            ))
        
        # 이미지로 저장
        img_path = self.image_cache_dir / f"chart_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        fig.write_image(str(img_path))
        
        return str(img_path)
    
    def _fetch_stock_image(self, keywords: List[str]) -> Optional[Dict]:
        """무료 스톡 이미지 가져오기"""
        if not keywords:
            return None
        
        keyword = random.choice(keywords)
        
        # Unsplash API 시도
        if self.unsplash_key:
            try:
                response = requests.get(
                    "https://api.unsplash.com/photos/random",
                    params={"query": keyword, "orientation": "landscape"},
                    headers={"Authorization": f"Client-ID {self.unsplash_key}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "type": "stock",
                        "url": data['urls']['regular'],
                        "alt": data.get('description', keyword),
                        "credit": f"Photo by {data['user']['name']} on Unsplash"
                    }
            except Exception as e:
                print(f"Unsplash API 오류: {e}")
        
        # Pexels API 시도
        if self.pexels_key:
            try:
                response = requests.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": keyword, "per_page": 1},
                    headers={"Authorization": self.pexels_key}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data['photos']:
                        photo = data['photos'][0]
                        return {
                            "type": "stock",
                            "url": photo['src']['large'],
                            "alt": photo.get('alt', keyword),
                            "credit": f"Photo by {photo['photographer']} on Pexels"
                        }
            except Exception as e:
                print(f"Pexels API 오류: {e}")
        
        return None
    
    def _generate_with_dalle(self, prompt: str) -> Optional[str]:
        """DALL-E로 이미지 생성"""
        if not self.openai_key:
            return None
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # 이미지 다운로드 및 저장
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                img_path = self.image_cache_dir / f"dalle_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                with open(img_path, 'wb') as f:
                    f.write(img_response.content)
                return str(img_path)
            
        except Exception as e:
            print(f"DALL-E API 오류: {e}")
        
        return None
    
    def _wrap_text(self, text: str, max_length: int) -> List[str]:
        """텍스트 줄바꿈"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _generate_map_placeholder(self, location: str) -> str:
        """지도 플레이스홀더 이미지 생성"""
        width, height = 800, 600
        img = Image.new('RGB', (width, height), '#f3f4f6')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(self.font_path, 30)
        except:
            font = ImageFont.load_default()
        
        # 간단한 지도 표현
        draw.rectangle([(50, 50), (width-50, height-50)], outline='#6b7280', width=2)
        draw.text((width//2 - 100, height//2), location, font=font, fill='#1f2937')
        
        # 마커 아이콘
        marker_x, marker_y = width//2, height//2 - 50
        draw.ellipse([(marker_x-20, marker_y-20), (marker_x+20, marker_y+20)], 
                    fill='#ef4444')
        
        img_path = self.image_cache_dir / f"map_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        img.save(img_path)
        
        return str(img_path)
    
    def _generate_tech_diagram(self, tech_stack: List[str]) -> str:
        """기술 스택 다이어그램 생성"""
        width, height = 800, 400
        img = Image.new('RGB', (width, height), '#ffffff')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(self.font_path, 20)
        except:
            font = ImageFont.load_default()
        
        # 기술 스택을 박스로 표현
        x_offset = 50
        y_offset = 150
        box_width = 120
        box_height = 60
        spacing = 30
        
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        
        for i, tech in enumerate(tech_stack[:5]):
            color = colors[i % len(colors)]
            x = x_offset + (box_width + spacing) * i
            
            # 박스 그리기
            draw.rounded_rectangle(
                [(x, y_offset), (x + box_width, y_offset + box_height)],
                radius=10,
                fill=color
            )
            
            # 텍스트
            text_width = draw.textlength(tech, font=font)
            text_x = x + (box_width - text_width) // 2
            text_y = y_offset + (box_height - 20) // 2
            draw.text((text_x, text_y), tech, font=font, fill='#ffffff')
        
        img_path = self.image_cache_dir / f"tech_diagram_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        img.save(img_path)
        
        return str(img_path)
    
    def _generate_grammar_chart(self, grammar_points: List[Dict]) -> str:
        """문법 도표 생성"""
        width, height = 800, 600
        img = Image.new('RGB', (width, height), '#ffffff')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype(self.font_path, 24)
            content_font = ImageFont.truetype(self.font_path, 16)
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
        
        # 제목
        draw.text((50, 30), "문법 포인트", font=title_font, fill='#1f2937')
        
        # 테이블 형식으로 문법 표시
        y_offset = 100
        for point in grammar_points[:5]:
            # 문법 항목
            draw.rectangle([(50, y_offset), (350, y_offset + 40)], 
                         fill='#eff6ff', outline='#3b82f6')
            draw.text((60, y_offset + 10), point.get('grammar', ''), 
                     font=content_font, fill='#1f2937')
            
            # 예문
            draw.rectangle([(360, y_offset), (750, y_offset + 40)], 
                         fill='#f9fafb', outline='#6b7280')
            draw.text((370, y_offset + 10), point.get('example', ''), 
                     font=content_font, fill='#4b5563')
            
            y_offset += 50
        
        img_path = self.image_cache_dir / f"grammar_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        img.save(img_path)
        
        return str(img_path)
    
    def _get_theme_by_keywords(self, site: str, keywords: List[str]) -> Dict[str, str]:
        """키워드별 색상 테마 반환"""
        # 기본 사이트별 색상
        base_themes = {
            'unpre': {'bg': '#1e293b', 'text': '#f8fafc', 'accent': '#0ea5e9'},  # IT - 블루
            'untab': {'bg': '#064e3b', 'text': '#f0fdf4', 'accent': '#10b981'},  # 투자 - 그린
            'skewese': {'bg': '#7c2d12', 'text': '#fef7ff', 'accent': '#f59e0b'},  # 역사 - 오렌지
            'tistory': {'bg': '#4c1d95', 'text': '#faf5ff', 'accent': '#a855f7'}  # 일반 - 퍼플
        }
        
        # 키워드별 테마 오버라이드
        keyword_themes = {
            # IT/개발 키워드
            'redis': {'bg': '#dc2626', 'text': '#fef2f2', 'accent': '#fecaca'},
            'docker': {'bg': '#2563eb', 'text': '#eff6ff', 'accent': '#93c5fd'},
            'react': {'bg': '#0891b2', 'text': '#f0f9ff', 'accent': '#67e8f9'},
            'python': {'bg': '#ca8a04', 'text': '#fefce8', 'accent': '#fde047'},
            'typescript': {'bg': '#3730a3', 'text': '#eef2ff', 'accent': '#a5b4fc'},
            'graphql': {'bg': '#e11d48', 'text': '#fff1f2', 'accent': '#fda4af'},
            'kubernetes': {'bg': '#326ce5', 'text': '#f0f9ff', 'accent': '#7dd3fc'},
            
            # 투자 키워드
            'investment': {'bg': '#065f46', 'text': '#f0fdf4', 'accent': '#34d399'},
            'reit': {'bg': '#134e4a', 'text': '#f0fdfa', 'accent': '#5eead4'},
            'property': {'bg': '#166534', 'text': '#f7fee7', 'accent': '#84cc16'},
            'finance': {'bg': '#0f766e', 'text': '#f0fdfa', 'accent': '#2dd4bf'},
            
            # 역사 키워드
            'korean': {'bg': '#a16207', 'text': '#fffbeb', 'accent': '#fbbf24'},
            'history': {'bg': '#92400e', 'text': '#fff7ed', 'accent': '#fb923c'},
            'traditional': {'bg': '#b45309', 'text': '#fff7ed', 'accent': '#fdba74'},
            
            # 일반 키워드
            'technology': {'bg': '#6366f1', 'text': '#eef2ff', 'accent': '#c7d2fe'},
            'trend': {'bg': '#7c3aed', 'text': '#faf5ff', 'accent': '#c4b5fd'},
            'business': {'bg': '#059669', 'text': '#f0fdf4', 'accent': '#6ee7b7'}
        }
        
        # 키워드 매칭으로 테마 선택
        for keyword in keywords:
            if keyword.lower() in keyword_themes:
                return keyword_themes[keyword.lower()]
        
        # 기본 사이트 테마 반환
        return base_themes.get(site, base_themes['tistory'])