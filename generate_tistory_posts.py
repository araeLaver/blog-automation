"""
Tistory용 콘텐츠 자동 생성 및 파일 저장
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Windows 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.generators.content_generator import ContentGenerator
from src.generators.image_generator import ImageGenerator
from src.generators.tistory_content_exporter import TistoryContentExporter
from src.utils.database import ContentDatabase
from config.sites_config import SITE_CONFIGS


def generate_tistory_post(topic: str = None):
    """Tistory용 포스트 생성 및 HTML 파일로 저장"""
    
    print("🚀 Tistory 콘텐츠 생성 시작...")
    
    # 생성기 초기화
    content_generator = ContentGenerator()
    image_generator = ImageGenerator()
    exporter = TistoryContentExporter()
    database = ContentDatabase()
    
    # Tistory 주제들 (언어학습 관련)
    tistory_topics = [
        "토익 파트7 독해 시간 단축 전략",
        "JLPT N2 필수 문법 정리",
        "영어 이메일 작성 실전 템플릿",
        "일본 여행 필수 회화 50선",
        "토익 스피킹 파트1 고득점 전략",
        "비즈니스 영어 프레젠테이션 표현",
        "일본어 경어 완벽 정리",
        "토익 LC 파트3,4 노트테이킹 기법",
        "영어 전화 회화 필수 표현",
        "JLPT 한자 효율적 암기법"
    ]
    
    # 주제 선택
    if not topic:
        import random
        topic = random.choice(tistory_topics)
    
    print(f"📝 주제: {topic}")
    
    # 사이트 설정 (unpre에 언어학습 카테고리 추가했으므로 그것 사용)
    site_config = SITE_CONFIGS["unpre"].copy()
    site_config["content_style"] = "친근하고 실용적인 톤, 예문과 팁 중심"
    site_config["target_audience"] = "토익/JLPT 수험생, 어학 학습자"
    
    try:
        # 1. 콘텐츠 생성
        print("✍️ AI로 콘텐츠 생성 중...")
        content = content_generator.generate_content(
            site_config=site_config,
            topic=topic,
            category="언어학습",
            existing_posts=[]
        )
        
        # 2. 이미지 생성 (선택사항)
        print("🎨 이미지 생성 중...")
        images = image_generator.generate_images_for_post(
            site="tistory",
            title=content["title"],
            content=content,
            count=2
        )
        
        # 3. HTML 파일로 내보내기
        print("💾 HTML 파일 생성 중...")
        filepath = exporter.export_content(content, images)
        
        # 4. 데이터베이스에 기록
        database.add_content(
            site="tistory_export",
            title=content["title"],
            category="언어학습",
            keywords=content.get("keywords", []),
            content=str(content),
            url=filepath
        )
        
        print("\n" + "="*60)
        print("✅ Tistory 콘텐츠 생성 완료!")
        print("="*60)
        print(f"📁 파일 위치: {filepath}")
        print(f"📋 제목: {content['title']}")
        print(f"🏷️ 태그: {', '.join(content.get('tags', []))}")
        print("\n사용 방법:")
        print("1. 위 HTML 파일을 브라우저에서 열기")
        print("2. '📋 HTML 복사하기' 버튼 클릭")
        print("3. Tistory 글쓰기 → HTML 모드로 전환")
        print("4. 붙여넣기 후 발행")
        print("="*60)
        
        # 파일 자동 열기 (Windows)
        import subprocess
        subprocess.run(['start', filepath], shell=True)
        
        return filepath
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None


def generate_multiple_posts(count: int = 5):
    """여러 개의 포스트 한번에 생성"""
    print(f"📚 {count}개의 Tistory 포스트를 생성합니다...")
    
    generated_files = []
    for i in range(count):
        print(f"\n[{i+1}/{count}] 포스트 생성 중...")
        filepath = generate_tistory_post()
        if filepath:
            generated_files.append(filepath)
        
        # API 제한 방지를 위한 대기
        if i < count - 1:
            import time
            time.sleep(5)
    
    print(f"\n✅ 총 {len(generated_files)}개 포스트 생성 완료!")
    print("생성된 파일들:")
    for filepath in generated_files:
        print(f"  - {filepath}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tistory 콘텐츠 생성기")
    parser.add_argument("--count", type=int, default=1, help="생성할 포스트 개수")
    parser.add_argument("--topic", type=str, help="특정 주제 지정")
    
    args = parser.parse_args()
    
    if args.count > 1:
        generate_multiple_posts(args.count)
    else:
        generate_tistory_post(args.topic)