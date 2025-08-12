#!/usr/bin/env python3
"""간단한 테스트용 WordPress 콘텐츠 생성"""

import json
from datetime import datetime
from pathlib import Path

def generate_test_content():
    # 테스트용 콘텐츠 생성
    title = f"Python 프로그래밍 팁 - {datetime.now().strftime('%H%M%S')}"
    
    content = {
        'title': title,
        'meta_description': 'Python 프로그래밍 효율성을 높이는 실용적인 팁과 트릭',
        'introduction': 'Python은 강력하고 유연한 프로그래밍 언어입니다. 이 글에서는 Python 개발을 더욱 효율적으로 만드는 팁을 소개합니다.',
        'sections': [
            {
                'heading': '리스트 컴프리헨션 활용하기',
                'content': '리스트 컴프리헨션은 Python의 강력한 기능 중 하나입니다. 코드를 간결하게 만들고 성능도 향상시킵니다.'
            },
            {
                'heading': 'with 문으로 리소스 관리',
                'content': 'with 문을 사용하면 파일이나 네트워크 연결 같은 리소스를 안전하게 관리할 수 있습니다.'
            }
        ],
        'conclusion': 'Python의 다양한 기능을 활용하면 더 나은 코드를 작성할 수 있습니다.',
        'tags': ['Python', '프로그래밍', '개발팁'],
        'categories': ['개발'],
        'keywords': ['Python', '프로그래밍 팁', '개발']
    }
    
    # HTML 파일 생성 (간단한 형태)
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <div class="content-container">
        <h1>{title}</h1>
        <div class="intro">{content['introduction']}</div>
        {"".join(f'<h2>{s["heading"]}</h2><p>{s["content"]}</p>' for s in content["sections"])}
        <div class="conclusion">{content['conclusion']}</div>
    </div>
</body>
</html>"""
    
    # 파일 저장
    export_dir = Path("data/wordpress_posts/unpre")
    export_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
    
    html_file = export_dir / f"{date_str}_{safe_title}.html"
    json_file = export_dir / f"{date_str}_{safe_title}.json"
    
    # HTML 저장
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # JSON 메타데이터 저장 (구조화된 데이터 포함)
    metadata = {
        **content,  # 모든 콘텐츠 데이터 포함
        'site': 'unpre',
        'created_at': datetime.now().isoformat(),
        'file_path': str(html_file),
        'status': 'draft',
        'word_count': len(content['introduction'] + ' '.join(s['content'] for s in content['sections']) + content['conclusion']),
        'estimated_reading_time': 2
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"테스트 콘텐츠 생성 완료:")
    print(f"  HTML: {html_file}")
    print(f"  JSON: {json_file}")
    
    # DB에 등록
    from src.utils.postgresql_database import PostgreSQLDatabase
    
    db = PostgreSQLDatabase()
    file_id = db.add_content_file(
        site='unpre',
        title=title,
        file_path=str(html_file),
        file_type='wordpress',
        metadata={
            'tags': content['tags'],
            'categories': content['categories'],
            'word_count': metadata['word_count'],
            'reading_time': metadata['estimated_reading_time'],
            'file_size': len(html_content),
            'content_hash': ''
        }
    )
    
    print(f"  DB ID: {file_id}")
    return file_id

if __name__ == "__main__":
    generate_test_content()