#!/usr/bin/env python3
"""
WordPress 텍스트 전용 고속 발행 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.publishers.wordpress_publisher import WordPressPublisher
import time

def test_text_only_publishing():
    print("=" * 60)
    print("WordPress 텍스트 전용 고속 발행 테스트")
    print("=" * 60)
    
    # 테스트 콘텐츠
    test_content = {
        'title': '🚀 텍스트 전용 고속 발행 테스트',
        'content': '''
        <h2>텍스트 전용 고속 발행 테스트</h2>
        <p>이 포스트는 WordPress 고속 텍스트 발행 모드를 테스트하기 위해 생성되었습니다.</p>
        
        <h3>주요 특징</h3>
        <ul>
            <li>이미지 업로드 완전 스킵</li>
            <li>카테고리/태그 간소화</li>
            <li>연결 타임아웃 단축 (20초)</li>
            <li>재시도 횟수 최소화</li>
        </ul>
        
        <h3>예상 개선사항</h3>
        <p><strong>발행 시간: 20분 → 5분 이내</strong></p>
        
        <p><em>테스트 시각: {}</em></p>
        '''.format(time.strftime("%Y-%m-%d %H:%M:%S")),
        'meta_description': '텍스트 전용 고속 발행 모드 테스트',
        'categories': ['테스트'],
        'tags': ['고속발행', '테스트'],
        'keywords': ['텍스트', '고속', '발행', '테스트']
    }
    
    # 테스트할 사이트
    test_sites = ['unpre', 'untab', 'skewese']
    
    for site in test_sites:
        print(f"\n📌 {site.upper()} 사이트 텍스트 전용 발행 테스트")
        print("-" * 50)
        
        try:
            publisher = WordPressPublisher(site)
            
            # 연결 테스트
            if not publisher.test_connection():
                print(f"❌ {site} 연결 실패")
                continue
            
            print(f"✅ {site} 연결 성공")
            
            # 시작 시간 기록
            start_time = time.time()
            print(f"⏰ 발행 시작: {time.strftime('%H:%M:%S')}")
            
            # 텍스트 전용 발행 (text_only=True)
            success, result = publisher.publish_post(
                content=test_content,
                images=None,  # 이미지 없음
                draft=True,   # 초안으로 발행 (공개 안됨)
                text_only=True  # 텍스트 전용 모드
            )
            
            # 종료 시간 기록
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏰ 발행 완료: {time.strftime('%H:%M:%S')}")
            print(f"🕐 소요 시간: {duration:.1f}초")
            
            if success:
                print(f"🎉 {site} 텍스트 전용 발행 성공!")
                print(f"🔗 URL: {result}")
                print(f"⚡ 목표 달성: {duration:.1f}초 < 300초 (5분)")
            else:
                print(f"❌ {site} 발행 실패: {result}")
                
        except Exception as e:
            print(f"❌ {site} 테스트 중 오류: {str(e)}")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_text_only_publishing()