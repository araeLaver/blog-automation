#!/usr/bin/env python3
"""
ContentGenerator 테스트 스크립트
"""

import os
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_content_generator():
    """ContentGenerator 테스트"""
    print("ContentGenerator 테스트 시작...")
    
    try:
        # API 키 확인
        api_key = os.getenv("ANTHROPIC_API_KEY")
        print(f"API Key 확인: {api_key[:20] if api_key else 'None'}...")
        
        if not api_key:
            print("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다!")
            return False
        
        # ContentGenerator 초기화
        from src.generators.content_generator import ContentGenerator
        generator = ContentGenerator()
        print("ContentGenerator 초기화 성공")
        
        # 테스트 콘텐츠 생성
        site_config = {
            'name': 'unpre',
            'target_audience': '개발자',
            'content_style': '실용적',
            'keywords_focus': ['Python', '프로그래밍']
        }
        
        print("Claude API로 콘텐츠 생성 시작...")
        import time
        start_time = time.time()
        
        content = generator.generate_content(
            site_config=site_config,
            topic="Python 프로그래밍 기초",
            category="프로그래밍",
            content_length="short"  # 짧은 콘텐츠로 테스트
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"생성 시간: {duration:.2f}초")
        print(f"생성된 제목: {content.get('title', 'N/A')}")
        print(f"섹션 수: {len(content.get('sections', []))}")
        
        if duration < 2:
            print("생성 시간이 너무 빠름 - Claude API가 실제로 호출되지 않았을 수 있음")
            return False
        else:
            print("정상적인 생성 시간")
            return True
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_content_generator()
    if success:
        print("테스트 성공!")
    else:
        print("테스트 실패!")