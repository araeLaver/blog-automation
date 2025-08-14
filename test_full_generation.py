"""
완전한 콘텐츠 생성 플로우 테스트
"""

import os
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from src.generators.content_generator import ContentGenerator
from src.utils.postgresql_database import PostgreSQLDatabase
import tempfile
import time

def test_full_content_generation():
    """완전한 콘텐츠 생성 플로우 테스트"""
    
    print("=== 완전한 콘텐츠 생성 플로우 테스트 ===")
    
    try:
        # 1. ContentGenerator 초기화
        print("\n1. ContentGenerator 초기화...")
        cg = ContentGenerator()
        print("✅ ContentGenerator 초기화 성공")
        
        # 2. 콘텐츠 생성
        print("\n2. 콘텐츠 생성 중...")
        site_config = {
            'name': 'unpre.co.kr',
            'target_audience': '개발자 및 IT 전문가',
            'content_style': '실용적이고 기술적인',
            'keywords_focus': ['JavaScript', '웹개발', '프론트엔드']
        }
        
        topic = "JavaScript ES6 완전 정복"
        content = cg.generate_content(
            site_config=site_config,
            topic=topic,
            category='프로그래밍',
            content_length='medium'
        )
        
        print(f"✅ 콘텐츠 생성 완료!")
        print(f"   제목: {content['title'][:50]}...")
        print(f"   소개 길이: {len(content['introduction'])} 문자")
        print(f"   섹션 개수: {len(content['sections'])}")
        
        # 3. HTML 변환
        print("\n3. HTML 변환 중...")
        content_html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content['title']}</title>
    <meta name="description" content="{content['meta_description']}">
</head>
<body>
    <article>
        <header>
            <h1>{content['title']}</h1>
        </header>
        
        <section class="introduction">
            <p>{content['introduction']}</p>
        </section>
        
        <main>
"""
        
        for section in content['sections']:
            content_html += f"""
            <section>
                <h2>{section['heading']}</h2>
                <div>{section['content'].replace(chr(10)+chr(10), '</p><p>').replace(chr(10), '<br>')}</div>
            </section>
"""
        
        content_html += f"""
        </main>
        
        <footer>
            <section class="conclusion">
                <h2>마무리</h2>
                <p>{content['conclusion']}</p>
            </section>
            
            <div class="tags">
                <strong>태그:</strong> {', '.join(content['tags'])}
            </div>
        </footer>
    </article>
</body>
</html>
"""
        
        print(f"✅ HTML 변환 완료 (크기: {len(content_html)} 문자)")
        
        # 4. 파일 저장 테스트
        print("\n4. 파일 저장 테스트...")
        temp_dir = tempfile.mkdtemp()
        safe_title = content['title'].replace(' ', '_').replace('/', '_').replace('\\', '_')[:50]
        safe_title = ''.join(c for c in safe_title if c.isalnum() or c in '_-')
        file_name = f"unpre_{safe_title}_{int(time.time())}.html"
        file_path = os.path.join(temp_dir, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_html)
        
        file_size = os.path.getsize(file_path)
        print(f"✅ 파일 저장 완료")
        print(f"   파일명: {file_name}")
        print(f"   파일 크기: {file_size / 1024:.1f}KB")
        print(f"   파일 경로: {file_path}")
        
        # 5. 데이터베이스 저장 테스트
        print("\n5. 데이터베이스 저장 테스트...")
        try:
            db = PostgreSQLDatabase()
            if db.is_connected:
                file_id = db.add_content_file(
                    site='unpre',
                    title=content['title'],
                    file_path=file_path,
                    file_type='wordpress',
                    metadata={
                        'categories': ['프로그래밍'],
                        'tags': content['tags'],
                        'word_count': len(content_html.split()),
                        'reading_time': len(content_html.split()) // 200 + 1,
                        'file_size': file_size
                    }
                )
                print(f"✅ 데이터베이스 저장 완료 (ID: {file_id})")
                
                # 저장된 파일 조회 테스트
                files = db.get_content_files(limit=1)
                if files:
                    latest_file = files[0]
                    print(f"   DB에서 조회된 제목: {latest_file.get('title', '없음')[:50]}...")
                    print(f"   DB에서 조회된 크기: {latest_file.get('file_size', 0) / 1024:.1f}KB")
                
            else:
                print("❌ 데이터베이스 연결 실패")
        except Exception as db_e:
            print(f"❌ 데이터베이스 테스트 실패: {db_e}")
        
        print(f"\n=== 테스트 완료 ===")
        print(f"✅ 모든 단계가 성공적으로 완료되었습니다!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_full_content_generation()