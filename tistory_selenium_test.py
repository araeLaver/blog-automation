"""
Tistory Selenium 자동화 테스트
"""

import os
from dotenv import load_dotenv
from src.publishers.tistory_selenium_publisher import TistorySeleniumPublisher

load_dotenv()

def test_tistory_selenium():
    """Selenium으로 Tistory 포스트 발행 테스트"""
    
    # 환경변수 확인
    email = os.getenv("TISTORY_EMAIL")
    password = os.getenv("TISTORY_PASSWORD")
    
    if not email or "카카오계정" in email:
        print("❌ Tistory 로그인 정보를 .env 파일에 설정하세요:")
        print("   TISTORY_EMAIL=실제_카카오_이메일")
        print("   TISTORY_PASSWORD=실제_카카오_비밀번호")
        return
    
    print("🚀 Tistory Selenium 테스트 시작...")
    
    # 발행자 생성
    publisher = TistorySeleniumPublisher()
    
    # 테스트 콘텐츠
    test_content = {
        "title": "자동화 테스트 - 토익 파트5 공략법",
        "introduction": "토익 파트5는 문법과 어휘를 평가하는 중요한 섹션입니다.",
        "sections": [
            {
                "heading": "1. 품사 문제 접근법",
                "content": "빈칸 앞뒤의 품사를 파악하는 것이 핵심입니다. 명사 자리에는 명사가, 형용사 자리에는 형용사가 와야 합니다."
            },
            {
                "heading": "2. 시제 문제 해결법", 
                "content": "문장의 시간 표현을 찾아보세요. yesterday, tomorrow, since 등의 단어가 힌트가 됩니다."
            },
            {
                "heading": "3. 전치사 선택 요령",
                "content": "동사와 함께 쓰이는 전치사는 암기가 필수입니다. depend on, consist of 등을 외워두세요."
            }
        ],
        "conclusion": "파트5는 충분한 연습으로 고득점이 가능한 영역입니다. 매일 20문제씩 꾸준히 풀어보세요.",
        "tags": ["토익", "파트5", "문법", "어휘", "토익공부법"],
        "category": "언어"
    }
    
    # 발행 시도
    success, result = publisher.publish_post(test_content, draft=True)  # 임시저장으로 테스트
    
    if success:
        print(f"✅ 발행 성공! URL: {result}")
    else:
        print(f"❌ 발행 실패: {result}")
    
    # 드라이버 종료
    publisher.close()
    print("테스트 완료")


if __name__ == "__main__":
    test_tistory_selenium()