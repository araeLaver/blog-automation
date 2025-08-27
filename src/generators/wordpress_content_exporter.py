"""
WordPress 콘텐츠 파일 생성 모듈 - 발행 전 미리보기 및 백업
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class WordPressContentExporter:
    def __init__(self, export_dir: str = "./data/wordpress_posts"):
        """WordPress 콘텐츠 내보내기 초기화"""
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # 사이트별 디렉토리 생성
        for site in ['unpre', 'untab', 'skewese', 'tistory']:
            (self.export_dir / site).mkdir(parents=True, exist_ok=True)
    
    def export_content(self, site: str, content: Dict, images: List[Dict] = None, category_suffix: str = None) -> str:
        """
        WordPress 콘텐츠를 미리보기 HTML 파일로 저장
        
        Returns:
            생성된 파일 경로
        """
        # 파일명 생성
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in content['title'] if c.isalnum() or c in (' ', '-', '_'))[:50]
        filename = f"{date_str}_{safe_title}.html"
        
        site_dir = self.export_dir / site
        filepath = site_dir / filename
        
        # HTML 콘텐츠 생성
        html_content = self._create_full_html(site, content, images, safe_title)
        
        # 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 메타데이터 JSON 파일 생성
        metadata_file = filepath.with_suffix('.json')
        metadata = {
            "site": site,
            "title": content['title'],
            "tags": content.get('tags', []),
            "categories": content.get('categories', []),
            "keywords": content.get('keywords', []),
            "meta_description": content.get('meta_description', ''),
            "created_at": datetime.now().isoformat(),
            "file_path": str(filepath),
            "status": "draft",
            "word_count": len(self._extract_text_content(content)),
            "estimated_reading_time": self._calculate_reading_time(content)
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"WordPress {site} 콘텐츠 생성: {filepath}")
        
        return str(filepath)
    
    def _create_full_html(self, site: str, content: Dict, images: List[Dict], safe_title: str) -> str:
        """완전한 HTML 문서 생성"""
        
        # 사이트별 테마 색상
        themes = {
            "unpre": {"primary": "#1976d2", "secondary": "#e3f2fd", "name": "unpre.co.kr"},
            "untab": {"primary": "#388e3c", "secondary": "#e8f5e9", "name": "untab.co.kr"},
            "skewese": {"primary": "#f57c00", "secondary": "#fff3e0", "name": "skewese.com"},
            "tistory": {"primary": "#c2185b", "secondary": "#fce4ec", "name": "tistory.com"}
        }
        
        theme = themes.get(site, themes["unpre"])
        
        html = []
        
        # HTML 헤더
        html.append(f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content['title']} - {theme['name']}</title>
    <meta name="description" content="{content.get('meta_description', '')}">
    <meta name="keywords" content="{', '.join(content.get('keywords', []))}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{content['title']}">
    <meta property="og:description" content="{content.get('meta_description', '')}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="{theme['name']}">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{content['title']}">
    <meta name="twitter:description" content="{content.get('meta_description', '')}">
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css" rel="stylesheet">
    
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            line-height: 1.8;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .site-header {{
            background: linear-gradient(135deg, {theme['primary']} 0%, {theme['primary']}dd 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }}
        
        .site-badge {{
            background-color: {theme['primary']};
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 1rem;
        }}
        
        .content-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }}
        
        h1 {{
            color: {theme['primary']};
            font-weight: 700;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid {theme['secondary']};
        }}
        
        h2 {{
            color: {theme['primary']};
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-left: 15px;
            border-left: 4px solid {theme['primary']};
        }}
        
        .intro {{
            background-color: {theme['secondary']};
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            font-size: 1.1em;
            border-left: 4px solid {theme['primary']};
        }}
        
        .conclusion {{
            background-color: #fff9c4;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 2rem 0;
            border-left: 4px solid #ffc107;
        }}
        
        
        .tags {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 2px solid #e9ecef;
        }}
        
        .tag {{
            display: inline-block;
            background-color: {theme['secondary']};
            color: {theme['primary']};
            padding: 5px 12px;
            margin: 3px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .wordpress-actions {{
            background-color: #e7f3ff;
            border: 2px dashed #0066cc;
            padding: 1.5rem;
            margin: 2rem 0;
            border-radius: 8px;
            text-align: center;
        }}
        
        .btn-wp {{
            background-color: {theme['primary']};
            color: white;
            padding: 10px 25px;
            border: none;
            border-radius: 5px;
            font-weight: 600;
            margin: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        
        .btn-wp:hover {{
            background-color: {theme['primary']}dd;
            color: white;
            text-decoration: none;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin: 1.5rem auto;
            display: block;
        }}
        
        
        blockquote {{
            border-left: 4px solid {theme['primary']};
            padding-left: 1rem;
            margin: 1rem 0;
            font-style: italic;
            color: #555;
        }}
        
        .highlight {{
            background-color: #ffeb3b;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        
        .code-block {{
            background-color: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 8px;
            padding: 1rem;
            margin: 1.5rem 0;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            position: relative;
            overflow-x: auto;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .code-block pre {{
            margin: 0;
            color: #e2e8f0;
            white-space: pre-wrap;
            word-break: break-word;
            line-height: 1.5;
        }}
        
        .code-block code {{
            color: #81c784;
            font-size: 14px;
        }}
        
        .copy-btn {{
            position: absolute;
            top: 8px;
            right: 8px;
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            opacity: 0.8;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .copy-btn:hover {{
            opacity: 1;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .copy-btn.copied {{
            background: linear-gradient(45deg, #48bb78 0%, #38a169 100%);
        }}
        
        .copy-btn i {{
            font-size: 11px;
        }}
    </style>
</head>
<body>
    <div class="site-header text-center">
        <div class="container">
            <h1 class="display-4 mb-0" style="color: white;">{theme['name']}</h1>
            <p class="lead mb-0" style="color: rgba(255,255,255,0.8);">WordPress 콘텐츠 미리보기</p>
        </div>
    </div>
    
    <div class="container">
        <div class="content-container">
            <div class="site-badge">{site.upper()}</div>
            
            
            <h1>{self._fix_year_in_title(content['title'])}</h1>""")
        
        # 서론
        if content.get('introduction'):
            html.append(f'<div class="intro">{content["introduction"]}</div>')
        
        # 첫 번째 이미지
        if images and len(images) > 0:
            html.append(f'<img src="{images[0].get("url", "이미지_URL")}" alt="{images[0].get("alt", "메인 이미지")}" />')
        
        # 본문 섹션들
        for i, section in enumerate(content.get('sections', [])):
            html.append(f"<h2>{section['heading']}</h2>")
            
            paragraphs = section['content'].split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # ** 특수기호를 <strong> 태그로 변환
                    para_html = para.strip()
                    
                    # **텍스트** -> <strong>텍스트</strong>
                    import re
                    para_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para_html)
                    
                    # 코드 블록 감지 및 처리 (unpre 사이트용)
                    if site == 'unpre' and ('```' in para_html or 'def ' in para_html or 'function ' in para_html or 'class ' in para_html or 'import ' in para_html):
                        # 코드 블록으로 래핑
                        code_id = f"code_{i}_{len(html)}"
                        html.append(f'<div class="code-block">')
                        html.append(f'<button class="copy-btn" onclick="copyCode(\'{code_id}\')"><i class="bi bi-clipboard"></i> 복사</button>')
                        html.append(f'<pre><code id="{code_id}">{para_html.replace("<strong>", "").replace("</strong>", "")}</code></pre>')
                        html.append(f'</div>')
                    else:
                        # 키워드 하이라이팅
                        for keyword in content.get('keywords', [])[:3]:
                            if keyword in para_html and len(keyword) > 2:
                                para_html = para_html.replace(keyword, f'<span class="highlight">{keyword}</span>', 1)
                        html.append(f"<p>{para_html}</p>")
            
            # 중간 이미지
            if images and i == 1 and len(images) > 1:
                html.append(f'<img src="{images[1].get("url", "이미지_URL")}" alt="설명 이미지" />')
        
        # 결론/추가 내용
        if content.get('additional_content'):
            html.append(f'<div class="conclusion">')
            html.append(f"<h2><i class='bi bi-lightbulb'></i> 마무리</h2>")
            html.append(f"<p>{content['additional_content']}</p>")
            html.append(f'</div>')
        elif content.get('conclusion'):
            # 기존 호환성 유지
            html.append(f'<div class="conclusion">')
            html.append(f"<h2><i class='bi bi-lightbulb'></i> 마무리</h2>")
            html.append(f"<p>{content['conclusion']}</p>")
            html.append(f'</div>')
        
        # 태그
        if content.get('tags'):
            html.append('<div class="tags">')
            html.append('<strong><i class="bi bi-tags"></i> 태그:</strong><br>')
            for tag in content['tags']:
                html.append(f'<span class="tag">#{tag}</span>')
            html.append('</div>')
        
        # WordPress 발행 액션
        html.append(f'''
        <div class="wordpress-actions">
            <h5><i class="bi bi-wordpress"></i> WordPress 발행 준비</h5>
            <p>이 콘텐츠를 검토한 후 WordPress에 발행하세요.</p>
            <button class="btn-wp" onclick="copyForWordPress()">
                <i class="bi bi-clipboard"></i> WordPress용 복사
            </button>
            <a href="https://{theme['name']}/wp-admin/post-new.php" target="_blank" class="btn-wp">
                <i class="bi bi-box-arrow-up-right"></i> WordPress 관리자
            </a>
            <button class="btn-wp" onclick="downloadJSON()" style="background-color: #6c757d;">
                <i class="bi bi-download"></i> 메타데이터
            </button>
        </div>
        
        <div id="wordpress-content" style="display: none;">
            <h3>WordPress 에디터용 콘텐츠:</h3>
            <textarea id="wp-content" style="width: 100%; height: 400px;">
{self._create_wordpress_content(content, images)}
            </textarea>
        </div>
        
        </div>
    </div>
    
    <script>
        function copyForWordPress() {{
            const content = document.getElementById('wp-content').value;
            navigator.clipboard.writeText(content).then(() => {{
                alert('WordPress용 콘텐츠가 클립보드에 복사되었습니다!\\n\\nWordPress 에디터(HTML 모드)에서 붙여넣기 하세요.');
                document.getElementById('wordpress-content').style.display = 'block';
            }}).catch(() => {{
                document.getElementById('wordpress-content').style.display = 'block';
                alert('수동으로 아래 텍스트를 복사하세요.');
            }});
        }}
        
        function copyCode(codeId) {{
            const codeElement = document.getElementById(codeId);
            const btn = codeElement.parentElement.querySelector('.copy-btn');
            
            navigator.clipboard.writeText(codeElement.textContent).then(() => {{
                btn.innerHTML = '<i class="bi bi-check"></i> 복사됨';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.innerHTML = '<i class="bi bi-clipboard"></i> 복사';
                    btn.classList.remove('copied');
                }}, 2000);
            }}).catch(() => {{
                alert('복사하기를 실패했습니다.');
            }});
        }}
        
        function downloadJSON() {{
            const metadata = {{
                site: "{site}",
                title: "{content['title']}",
                meta_description: "{content.get('meta_description', '')}",
                tags: {json.dumps(content.get('tags', []))},
                categories: {json.dumps(content.get('categories', []))},
                keywords: {json.dumps(content.get('keywords', []))},
                created_at: "{datetime.now().isoformat()}"
            }};
            
            const blob = new Blob([JSON.stringify(metadata, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '{safe_title}_metadata.json';
            a.click();
            URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>''')
        
        return '\n'.join(html)
    
    def _create_wordpress_content(self, content: Dict, images: List[Dict]) -> str:
        """WordPress 에디터용 개선된 HTML 생성"""
        html = []
        
        # 서론 - 스타일링 개선
        if content.get('introduction'):
            html.append(f'<div class="intro-section" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 12px; margin: 20px 0; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">')
            html.append(f'<h3 style="color: white; margin-top: 0; font-size: 1.3em; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">📖 들어가며</h3>')
            html.append(f'<p style="font-size: 1.1em; line-height: 1.7; margin-bottom: 0; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">{self._format_text_content(content["introduction"])}</p>')
            html.append('</div>')
        
        # 첫 번째 이미지
        if images and len(images) > 0:
            html.append(f'<div style="text-align: center; margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 12px; border-left: 4px solid #007cba;">')
            html.append(f'<img class="aligncenter size-large" src="{images[0].get("url", "")}" alt="{images[0].get("alt", "")}" style="border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); max-width: 100%; height: auto;" />')
            html.append('</div>')
        
        # 본문 섹션들 - 향상된 구조
        for i, section in enumerate(content.get('sections', [])):
            # 섹션 헤더
            section_color = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'][i % 5]
            html.append(f'<div class="section-wrapper" style="margin: 40px 0; border: 2px solid {section_color}20; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">')
            html.append(f'<h2 style="background: linear-gradient(135deg, {section_color} 0%, {section_color}dd 100%); color: white; margin: 0; padding: 20px; font-size: 1.4em; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">📌 {section["heading"]}</h2>')
            html.append(f'<div style="padding: 25px; background: white;">')
            
            # 섹션 내용 파싱 및 포맷팅
            section_content = self._format_section_content(section['content'])
            html.append(section_content)
            
            html.append('</div></div>')
            
            # 중간 이미지
            if images and i == 1 and len(images) > 1:
                html.append(f'<div style="text-align: center; margin: 30px 0; padding: 20px; background: #fff3e0; border-radius: 12px; border-left: 4px solid #ff9800;">')
                html.append(f'<img class="aligncenter size-medium" src="{images[1].get("url", "")}" alt="설명 이미지" style="border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); max-width: 100%; height: auto;" />')
                html.append('</div>')
        
        # 결론/추가 내용 - 스타일링 개선
        conclusion_text = content.get('additional_content') or content.get('conclusion')
        if conclusion_text:
            html.append('<div class="conclusion-section" style="background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%); padding: 30px; border-radius: 12px; margin: 30px 0; box-shadow: 0 8px 32px rgba(86, 171, 47, 0.3);">')
            html.append('<h2 style="color: #2d5016; margin-top: 0; font-size: 1.4em; text-shadow: 0 1px 2px rgba(255,255,255,0.5);">💡 핵심 정리</h2>')
            html.append(f'<div style="color: #2d5016; font-size: 1.1em; line-height: 1.7;">{self._format_text_content(conclusion_text)}</div>')
            html.append('</div>')
        
        # 마지막에 CTA 섹션 추가
        html.append('<div class="cta-section" style="background: #f1f3f4; padding: 25px; border-radius: 12px; margin: 30px 0; text-align: center; border: 2px dashed #dadce0;">')
        html.append('<h3 style="color: #5f6368; margin-top: 0;">🔥 이 글이 도움이 되셨나요?</h3>')
        html.append('<p style="color: #5f6368; margin-bottom: 0;">댓글로 의견을 남겨주시고, 공유해서 더 많은 분들에게 도움을 주세요!</p>')
        html.append('</div>')
        
        return '\n'.join(html)
    
    def _extract_text_content(self, content: Dict) -> str:
        """텍스트 내용만 추출"""
        text_parts = [
            content.get('title', ''),
            content.get('introduction', ''),
            content.get('additional_content', '') or content.get('conclusion', '')
        ]
        
        for section in content.get('sections', []):
            text_parts.append(section.get('content', ''))
        
        return ' '.join(text_parts)
    
    def _calculate_reading_time(self, content: Dict) -> int:
        """예상 읽기 시간 계산 (분)"""
        text = self._extract_text_content(content)
        # 한국어 기준 약 300자/분
        words = len(text)
        return max(1, round(words / 300))
    
    def _format_text_content(self, text: str) -> str:
        """텍스트 내용 포맷팅 개선"""
        import re
        
        # **굵은글씨** -> <strong> 태그로 변환
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong style="color: #2c3e50; font-weight: 600;">\1</strong>', text)
        
        # 구분선 --- 처리
        text = re.sub(r'---', '<hr style="border: none; border-top: 2px solid #ecf0f1; margin: 20px 0;" />', text)
        
        # 목록 처리 (- 기호)
        lines = text.split('\n')
        formatted_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                if not in_list:
                    formatted_lines.append('<ul style="padding-left: 20px; margin: 15px 0;">')
                    in_list = True
                formatted_lines.append(f'<li style="margin: 8px 0; line-height: 1.6;">{line[2:]}</li>')
            elif line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
                if in_list and formatted_lines[-1] != '</ul>':
                    formatted_lines.append('</ul>')
                if not in_list or formatted_lines[-1] == '</ul>':
                    formatted_lines.append('<ol style="padding-left: 20px; margin: 15px 0;">')
                    in_list = True
                formatted_lines.append(f'<li style="margin: 8px 0; line-height: 1.6;">{line[3:]}</li>')
            else:
                if in_list:
                    formatted_lines.append('</ol>' if line.startswith(('1. ', '2. ')) else '</ul>')
                    in_list = False
                if line:
                    formatted_lines.append(f'<p style="margin: 15px 0; line-height: 1.7;">{line}</p>')
        
        if in_list:
            formatted_lines.append('</ul>')
        
        return '\n'.join(formatted_lines)
    
    def _format_section_content(self, content: str) -> str:
        """섹션 내용 고급 포맷팅"""
        import re
        
        # 테이블 처리 개선
        if '<table>' in content:
            content = re.sub(
                r'<table>',
                '<table style="width: 100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">',
                content
            )
            content = re.sub(
                r'<th>([^<]+)</th>',
                r'<th style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; text-align: left; font-weight: 600;">\1</th>',
                content
            )
            content = re.sub(
                r'<td>([^<]+)</td>',
                r'<td style="padding: 12px 15px; border-bottom: 1px solid #ecf0f1; background: #fafafa;">\1</td>',
                content
            )
        
        # 코드 블록 처리
        content = re.sub(
            r'```(\w+)?\n([^`]+)```',
            r'<div style="background: #2d3748; color: #e2e8f0; padding: 20px; border-radius: 8px; margin: 20px 0; font-family: \'Consolas\', \'Monaco\', monospace; overflow-x: auto; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"><pre style="margin: 0; white-space: pre-wrap;"><code>\2</code></pre></div>',
            content
        )
        
        # 인용구 처리
        content = re.sub(
            r'> ([^\n]+)',
            r'<blockquote style="border-left: 4px solid #3498db; background: #f8f9fa; padding: 15px 20px; margin: 20px 0; font-style: italic; color: #2c3e50;">\1</blockquote>',
            content
        )
        
        # 중요 알림 박스 (💡, ⚠️, 🎯 등이 포함된 문장)
        content = re.sub(
            r'(💡|⚠️|🎯|📌|✅|❌)([^\n]+)',
            r'<div style="background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #e17055; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"><strong style="color: #2d3436;">\1\2</strong></div>',
            content
        )
        
        return self._format_text_content(content)
    
    def _fix_year_in_title(self, title: str) -> str:
        """제목에서 잘못된 연도를 현재 연도로 수정"""
        import re
        current_year = datetime.now().year
        
        # 2024년을 현재 연도로 변경
        title = re.sub(r'2024년', f'{current_year}년', title)
        
        # [2024년]을 현재 연도로 변경
        title = re.sub(r'\[2024년\]', f'[{current_year}년]', title)
        
        return title
    
    def create_batch_export(self, site: str, contents: List[Dict]) -> str:
        """여러 콘텐츠를 한번에 내보내기"""
        batch_dir = self.export_dir / site / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        for content in contents:
            filepath = self.export_content(site, content)
            exported_files.append(filepath)
        
        # 인덱스 파일 생성
        index_file = batch_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f"""
            <html>
            <head>
                <title>{site.upper()} 포스트 일괄 생성</title>
                <meta charset="UTF-8">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="container mt-4">
                <h1>{site.upper()} 포스트 목록</h1>
                <div class="list-group">
            """)
            
            for filepath in exported_files:
                filename = Path(filepath).name
                title = filename.split('_', 2)[-1].replace('.html', '')
                f.write(f'''
                    <a href="../{filename}" class="list-group-item list-group-item-action">
                        <h5 class="mb-1">{title}</h5>
                        <small>파일: {filename}</small>
                    </a>
                ''')
            
            f.write("""
                </div>
            </body>
            </html>
            """)
        
        return str(batch_dir)