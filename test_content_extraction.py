#!/usr/bin/env python3
"""Test script to verify WordPress content extraction"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

def test_content_extraction():
    """Test the NEW BeautifulSoup content extraction logic"""
    
    # Read the HTML file
    html_file = Path(r"C:\Develop\unble\blog-automation\data\wordpress_posts\unpre\20250811_173453_카카오 개발자 입사를 위한 완벽 가이드 합격자가 알려주는 실전 준비 전략.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        raw_html = f.read()
    
    print(f"원본 HTML 콘텐츠 길이: {len(raw_html)}")
    print(f"HTML 콘텐츠 미리보기: {raw_html[:200]}...")
    
    # NEW BeautifulSoup approach
    try:
        # BeautifulSoup을 사용해서 더 정확하게 파싱
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # content-container div 찾기
        container_div = soup.find('div', class_='content-container')
        if container_div:
            print(f"\ncontent-container div 발견! 원본 길이: {len(str(container_div))}")
            
            # 불필요한 요소들 제거
            for element in container_div.find_all(['div'], class_=['meta-info', 'wordpress-actions', 'site-badge']):
                print(f"제거하는 요소: {element.name} with class {element.get('class')}")
                element.decompose()
            
            # script 태그 제거
            for script in container_div.find_all('script'):
                print(f"script 태그 제거")
                script.decompose()
            
            # 내용 추출 (HTML 태그 유지)
            extracted = str(container_div)
            
            print(f"\n정리 후 콘텐츠 길이: {len(extracted)}")
            
            # content-container div 태그 자체는 제거
            extracted = re.sub(r'^<div[^>]*class="[^"]*content-container[^"]*"[^>]*>|</div>\s*$', '', extracted, flags=re.MULTILINE)
            
            final_content = extracted.strip()
            
            print(f"\n최종 추출된 콘텐츠 길이: {len(final_content)}")
            print(f"추출된 콘텐츠 미리보기 (처음 500자):")
            print(final_content[:500])
            print(f"\n추출된 콘텐츠 미리보기 (마지막 500자):")
            print(final_content[-500:])
            
            return final_content
        else:
            print("content-container를 찾을 수 없음")
    except Exception as e:
        print(f"BeautifulSoup 파싱 오류: {e}")
        
    return None

if __name__ == "__main__":
    test_content_extraction()