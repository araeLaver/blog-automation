"""
Tistory 콘텐츠 파일 생성 모듈 - HTML 파일로 내보내기
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class TistoryContentExporter:
    def __init__(self, export_dir: str = "./data/tistory_posts"):
        """Tistory 콘텐츠 내보내기 초기화"""
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_content(self, content: Dict, images: List[Dict] = None) -> str:
        """
        콘텐츠를 Tistory에 바로 붙여넣을 수 있는 HTML 파일로 저장
        
        Returns:
            생성된 파일 경로
        """
        # 파일명 생성 (날짜_제목)
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in content['title'] if c.isalnum() or c in (' ', '-', '_'))[:50]
        filename = f"{date_str}_{safe_title}.html"
        filepath = self.export_dir / filename
        
        # HTML 콘텐츠 생성
        html_content = self._create_full_html(content, images)
        
        # 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 메타데이터 JSON 파일도 생성
        metadata_file = self.export_dir / f"{date_str}_{safe_title}_meta.json"
        metadata = {
            "title": content['title'],
            "tags": content.get('tags', []),
            "category": content.get('category', '언어'),
            "created_at": datetime.now().isoformat(),
            "file_path": str(filepath)
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"[완료] Tistory 콘텐츠 생성 완료: {filepath}")
        print(f"[메타] 메타데이터: {metadata_file}")
        
        return str(filepath)
    
    def _create_full_html(self, content: Dict, images: List[Dict]) -> str:
        """완전한 HTML 문서 생성"""
        html = []
        
        # HTML 헤더
        html.append("""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>""" + content['title'] + """</title>
    <style>
        body {
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid #3498db;
        }
        p {
            margin-bottom: 15px;
            text-align: justify;
        }
        .intro {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .conclusion {
            background-color: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
            border-left: 4px solid #ffc107;
        }
        .tags {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
        }
        .tag {
            display: inline-block;
            background-color: #e9ecef;
            padding: 5px 15px;
            margin: 5px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .copy-section {
            background-color: #f0f8ff;
            border: 2px dashed #007bff;
            padding: 20px;
            margin: 30px 0;
            border-radius: 8px;
        }
        .copy-section h3 {
            color: #007bff;
            margin-top: 0;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .highlight {
            background-color: #ffeb3b;
            padding: 2px 4px;
            border-radius: 3px;
        }
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            color: #555;
        }
    </style>
</head>
<body>
""")
        
        # 제목
        html.append(f"<h1>{content['title']}</h1>")
        
        # 복사용 섹션 (Tistory 에디터에 바로 붙여넣기용)
        html.append("""
<div class="copy-section">
    <h3>📋 아래 내용을 복사하여 Tistory 에디터(HTML 모드)에 붙여넣으세요:</h3>
</div>
        """)
        
        # 실제 콘텐츠 시작
        html.append('<div id="content-to-copy" style="border: 1px solid #dee2e6; padding: 20px; background: white;">')
        
        # 서론
        if content.get('introduction'):
            html.append(f'<div class="intro">{content["introduction"]}</div>')
        
        # 이미지 (있는 경우)
        if images and len(images) > 0:
            html.append(f'<p style="text-align: center;">')
            html.append(f'<img src="{images[0].get("url", "이미지_URL_입력")}" alt="{images[0].get("alt", "메인 이미지")}" />')
            html.append(f'</p>')
        
        # 본문 섹션들
        for i, section in enumerate(content.get('sections', [])):
            html.append(f"<h2>{section['heading']}</h2>")
            
            # 단락 처리
            paragraphs = section['content'].split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # 중요 키워드 강조
                    para_html = para.strip()
                    for keyword in content.get('keywords', [])[:3]:
                        if keyword in para_html:
                            para_html = para_html.replace(keyword, f'<span class="highlight">{keyword}</span>', 1)
                    html.append(f"<p>{para_html}</p>")
            
            # 중간 이미지 삽입
            if images and i == 0 and len(images) > 1:
                html.append(f'<p style="text-align: center;">')
                html.append(f'<img src="{images[1].get("url", "이미지_URL_입력")}" alt="설명 이미지" />')
                html.append(f'</p>')
        
        # 결론
        if content.get('conclusion'):
            html.append(f'<div class="conclusion">')
            html.append(f"<h2>마무리</h2>")
            html.append(f"<p>{content['conclusion']}</p>")
            html.append(f'</div>')
        
        # 태그
        if content.get('tags'):
            html.append('<div class="tags">')
            html.append('<strong>태그:</strong> ')
            for tag in content['tags']:
                html.append(f'<span class="tag">#{tag}</span>')
            html.append('</div>')
        
        html.append('</div>') # content-to-copy 끝
        
        # 복사 버튼 및 스크립트
        html.append("""
<div style="text-align: center; margin: 30px 0;">
    <button onclick="copyContent()" style="
        background-color: #007bff;
        color: white;
        border: none;
        padding: 12px 30px;
        font-size: 16px;
        border-radius: 5px;
        cursor: pointer;
    ">📋 HTML 복사하기</button>
</div>

<script>
function copyContent() {
    const content = document.getElementById('content-to-copy').innerHTML;
    const tempTextarea = document.createElement('textarea');
    tempTextarea.value = content;
    document.body.appendChild(tempTextarea);
    tempTextarea.select();
    document.execCommand('copy');
    document.body.removeChild(tempTextarea);
    alert('HTML이 복사되었습니다! Tistory 에디터에 붙여넣으세요.');
}
</script>
        """)
        
        # HTML 푸터
        html.append("""
</body>
</html>
        """)
        
        return '\n'.join(html)
    
    def create_batch_export(self, contents: List[Dict]) -> str:
        """여러 콘텐츠를 한번에 내보내기"""
        batch_dir = self.export_dir / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        for content in contents:
            filepath = self.export_content(content)
            exported_files.append(filepath)
        
        # 인덱스 파일 생성
        index_file = batch_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("<html><body><h1>Tistory 포스트 목록</h1><ul>")
            for filepath in exported_files:
                filename = Path(filepath).name
                f.write(f'<li><a href="../{filename}">{filename}</a></li>')
            f.write("</ul></body></html>")
        
        return str(batch_dir)