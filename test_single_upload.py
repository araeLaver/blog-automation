#!/usr/bin/env python3
"""
단일 이미지 WordPress 업로드 테스트
- 로컬에서 생성된 1개 이미지만 테스트
- 안전장치 적용
"""

from src.utils.safe_image_generator import safe_image_generator
from src.publishers.wordpress_publisher import WordPressPublisher
import os
import time

def test_single_wordpress_upload():
    """단일 이미지 WordPress 업로드 테스트 (매우 안전)"""
    
    print("=== 단일 이미지 WordPress 업로드 테스트 ===")
    
    try:
        # 1. 로컬 이미지 생성
        test_title = "테스트 이미지 업로드"
        print(f"1단계: 로컬 이미지 생성 중... ({test_title})")
        
        image_path = safe_image_generator.generate_featured_image(test_title)
        if not image_path or not os.path.exists(image_path):
            print("[FAIL] 로컬 이미지 생성 실패")
            return False
        
        file_size = os.path.getsize(image_path)
        print(f"[OK] 로컬 이미지 생성 완료: {file_size:,} bytes")
        
        # 2. WordPress 연결 테스트
        print("2단계: WordPress 연결 테스트...")
        wp_publisher = WordPressPublisher('unpre')
        
        if not wp_publisher.test_connection():
            print("[FAIL] WordPress 연결 실패")
            return False
        
        print("[OK] WordPress 연결 성공")
        
        # 3. 안전한 단일 이미지 업로드
        print("3단계: 단일 이미지 업로드 중...")
        
        # 안전한 이미지 객체 생성
        safe_image = {
            'url': image_path,  # 로컬 파일 경로
            'type': 'thumbnail',
            'alt': test_title
        }
        
        # 업로드 (내부 안전장치 적용)
        media_id = wp_publisher._upload_media(safe_image)
        
        if media_id:
            print(f"[SUCCESS] 이미지 업로드 성공! Media ID: {media_id}")
            
            # 4. 업로드된 이미지 정보 확인
            print("4단계: 업로드된 이미지 확인...")
            # WordPress 미디어 라이브러리에서 확인 가능
            
            return True
        else:
            print("[FAIL] 이미지 업로드 실패")
            return False
            
    except Exception as e:
        print(f"[ERROR] 테스트 중 예외 발생: {e}")
        return False
    
    finally:
        # 5. 임시 파일 정리
        try:
            if 'image_path' in locals() and image_path and os.path.exists(image_path):
                os.remove(image_path)
                print("[CLEANUP] 임시 이미지 파일 삭제 완료")
        except:
            pass

if __name__ == "__main__":
    print("경고: 이 테스트는 실제 WordPress 사이트에 이미지를 업로드합니다.")
    print("계속하시겠습니까? (y/N): ", end="")
    
    # 자동으로 진행 (테스트용)
    response = 'y'  # input().lower()
    
    if response == 'y':
        success = test_single_wordpress_upload()
        if success:
            print("\n[SUCCESS] 단일 이미지 업로드 테스트 성공!")
            print("다음 단계로 진행 가능합니다.")
        else:
            print("\n[WARNING] 테스트 실패. 문제 확인 후 재시도 필요")
    else:
        print("테스트 취소됨")