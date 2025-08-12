#!/usr/bin/env python3
"""
완전한 자동 발행 테스트 스크립트
"""

import sys
import json
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.generators.content_generator import ContentGenerator
from src.generators.wordpress_content_exporter import WordPressContentExporter
from src.publishers.wordpress_publisher import WordPressPublisher
from src.utils.safe_image_generator import SafeImageGenerator

def test_site_publishing(site: str, topic: str, keywords: list, category: str = "programming"):
    """사이트별 완전한 발행 테스트"""
    print(f"\n=== {site.upper()} 사이트 발행 테스트 시작 ===")
    print(f"주제: {topic}")
    print(f"키워드: {', '.join(keywords)}")
    
    try:
        # 1. 컨텐츠 생성
        print("\n1. 컨텐츠 생성 중...")
        generator = ContentGenerator()
        
        # 사이트 설정 생성
        site_config = {
            'name': f'{site.upper()} Blog',
            'url': f'https://{site}.co.kr',
            'target_audience': get_target_audience(site),
            'categories': [category],
            'content_style': 'professional',
            'tone': 'informative',
            'keywords_focus': keywords
        }
        
        # 컨텐츠 생성 요청
        content_result = generator.generate_content(
            site_config=site_config,
            topic=topic,
            category=category,
            content_length="medium"
        )
        
        if not content_result.get('success'):
            print(f"[FAIL] 컨텐츠 생성 실패: {content_result.get('error')}")
            return False
        
        print(f"[OK] 컨텐츠 생성 완료: {content_result['content']['title']}")
        
        # 2. 이미지 생성
        print("\n2. 이미지 생성 중...")
        image_gen = SafeImageGenerator()
        
        try:
            featured_image = image_gen.generate_featured_image(
                title=content_result['content']['title'],
                width=1200,
                height=630
            )
            images = [{'url': featured_image, 'alt': topic}] if featured_image else []
            print(f"[OK] 이미지 생성 완료: {len(images)}개")
        except Exception as e:
            print(f"[WARN] 이미지 생성 실패 (계속 진행): {e}")
            images = []
        
        # 3. WordPress HTML 생성
        print("\n3. WordPress HTML 생성 중...")
        exporter = WordPressContentExporter()
        
        export_result = exporter.export_to_wordpress(
            content=content_result['content'],
            site=site,
            images=images
        )
        
        if not export_result.get('success'):
            print(f"[FAIL] HTML 생성 실패: {export_result.get('error')}")
            return False
        
        print(f"[OK] HTML 생성 완료: {export_result['file_path']}")
        
        # 4. WordPress 발행
        print("\n4. WordPress 발행 중...")
        wp_publisher = WordPressPublisher(site)
        
        if not wp_publisher.test_connection():
            print(f"[FAIL] WordPress 연결 실패")
            return False
        
        # WordPress 발행 실행
        success, result = wp_publisher.publish_post(
            content=content_result['content'],
            images=images,
            draft=False
        )
        
        if success:
            print(f"[SUCCESS] WordPress 발행 성공!")
            print(f"[URL] 발행 URL: {result}")
            return True
        else:
            print(f"[FAIL] WordPress 발행 실패: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 전체 과정 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_target_audience(site: str) -> str:
    """사이트별 타겟 독자 반환"""
    audiences = {
        'unpre': '개발자, IT 종사자, 프로그래밍 학습자',
        'untab': '부동산 투자자, 경매 참여자, 정책 관심자',
        'skewese': '역사 애호가, 교양 독자, 라이프스타일 관심자'
    }
    return audiences.get(site, '일반 독자')

def main():
    """메인 테스트 실행"""
    print("=== 완전한 자동 발행 테스트 시작 ===")
    
    # 테스트 케이스 정의
    test_cases = [
        {
            'site': 'unpre',
            'topic': 'Python 데이터 분석 라이브러리 완벽 가이드',
            'keywords': ['python', '데이터분석', 'pandas', 'numpy'],
            'category': 'programming'
        },
        {
            'site': 'untab',
            'topic': '2025년 부동산 경매 시장 전망과 투자 전략',
            'keywords': ['부동산경매', '2025년', '투자전략', '시장전망'],
            'category': 'realestate'
        },
        {
            'site': 'skewese',
            'topic': '고대 그리스 철학이 현대에 미치는 영향',
            'keywords': ['고대그리스', '철학', '소크라테스', '플라톤'],
            'category': 'worldhistory'
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        site = test_case['site']
        success = test_site_publishing(
            site=site,
            topic=test_case['topic'],
            keywords=test_case['keywords'],
            category=test_case['category']
        )
        results[site] = success
        
        if success:
            print(f"\n[SUCCESS] {site.upper()} 발행 테스트 성공!")
        else:
            print(f"\n[FAIL] {site.upper()} 발행 테스트 실패!")
        
        # 사이트 간 간격
        if site != test_cases[-1]['site']:
            print("\n" + "="*60)
            time.sleep(2)
    
    # 최종 결과
    print("\n" + "="*60)
    print("=== 최종 테스트 결과 ===")
    
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    for site, success in results.items():
        status = "[OK] 성공" if success else "[FAIL] 실패"
        print(f"{site.upper()}: {status}")
    
    print(f"\n전체 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("[SUCCESS] 모든 사이트 발행 테스트 성공!")
        return True
    else:
        print("[WARN] 일부 사이트에서 문제 발생")
        return False

if __name__ == "__main__":
    main()