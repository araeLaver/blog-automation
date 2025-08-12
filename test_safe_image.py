#!/usr/bin/env python3
"""
안전한 이미지 생성 테스트
- WordPress 업로드 없이 로컬 이미지 생성만 테스트
"""

from src.utils.safe_image_generator import safe_image_generator
import os

def test_local_image_generation():
    """로컬 이미지 생성 테스트"""
    
    print("=== 안전한 로컬 이미지 생성 테스트 ===")
    
    test_titles = [
        "Python 프로그래밍 기초 가이드",
        "JavaScript 비동기 처리 완벽 이해하기", 
        "데이터베이스 최적화 방법",
        "웹 개발 트렌드 2024",
        "AI와 머신러닝 입문서"
    ]
    
    generated_images = []
    
    for i, title in enumerate(test_titles, 1):
        print(f"\n[테스트 {i}/{len(test_titles)}] 제목: {title}")
        
        try:
            # 로컬 이미지 생성 (외부 요청 없음)
            image_path = safe_image_generator.generate_featured_image(title)
            
            if image_path and os.path.exists(image_path):
                file_size = os.path.getsize(image_path)
                print(f"[OK] 성공: {image_path}")
                print(f"   파일 크기: {file_size:,} bytes")
                generated_images.append(image_path)
            else:
                print(f"[FAIL] 실패: 이미지 생성되지 않음")
                
        except Exception as e:
            print(f"[ERROR] 예외 발생: {e}")
    
    print(f"\n=== 테스트 결과 ===")
    print(f"총 시도: {len(test_titles)}개")
    print(f"성공: {len(generated_images)}개")
    print(f"실패: {len(test_titles) - len(generated_images)}개")
    
    if generated_images:
        print(f"\n생성된 이미지들:")
        for img_path in generated_images:
            print(f"  - {img_path}")
    
    return len(generated_images) == len(test_titles)

if __name__ == "__main__":
    success = test_local_image_generation()
    if success:
        print("\n[SUCCESS] 모든 테스트 통과! 안전하게 이미지 생성 가능")
    else:
        print("\n[WARNING] 일부 테스트 실패. 문제 확인 필요")