"""
빠른 시작 가이드 - 시스템 설정 및 테스트
"""

import os
from pathlib import Path
from src.utils.logger import log_info, log_error

def check_environment():
    """환경변수 설정 상태 확인"""
    print("🔍 환경변수 설정 상태 확인...")
    
    required_vars = {
        "ANTHROPIC_API_KEY": "Claude API 키",
        "OPENAI_API_KEY": "OpenAI API 키", 
        "UNPRE_URL": "unpre.co.kr URL",
        "UNPRE_USERNAME": "unpre 관리자 아이디",
        "UNPRE_PASSWORD": "unpre 앱 패스워드"
    }
    
    missing = []
    configured = []
    
    for var, description in required_vars.items():
        value = os.getenv(var, "").strip()
        if not value or "여기에_" in value:
            missing.append(f"❌ {var}: {description}")
        else:
            configured.append(f"✅ {var}: 설정됨")
    
    print("\n📋 설정 상태:")
    for item in configured:
        print(item)
    
    if missing:
        print("\n⚠️  누락된 설정:")
        for item in missing:
            print(item)
        print(f"\n💡 .env 파일을 열어서 위 항목들을 설정해주세요.")
        return False
    
    print("\n🎉 모든 필수 설정이 완료되었습니다!")
    return True

def show_wordpress_setup_guide():
    """WordPress 앱 패스워드 설정 가이드"""
    print("\n" + "="*60)
    print("📚 WordPress 앱 패스워드 생성 가이드")
    print("="*60)
    
    steps = [
        "1. unpre.co.kr 관리자 페이지 로그인",
        "2. 사용자 → 프로필 메뉴 클릭",
        "3. 아래로 스크롤하여 '애플리케이션 패스워드' 섹션 찾기",
        "4. '새 애플리케이션 패스워드' 이름에 'Blog Automation' 입력",
        "5. '새 애플리케이션 패스워드 추가' 버튼 클릭",
        "6. 생성된 패스워드를 복사하여 .env 파일의 UNPRE_PASSWORD에 입력",
        "7. untab.co.kr, skewese.com도 동일한 과정 반복"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n⚠️  중요: 일반 로그인 패스워드가 아닌 '앱 패스워드'를 사용해야 합니다!")

def show_api_key_guide():
    """API 키 발급 가이드"""
    print("\n" + "="*60)
    print("🔑 API 키 발급 가이드")
    print("="*60)
    
    print("\n1. Claude API (Anthropic):")
    print("   - https://console.anthropic.com 접속")
    print("   - 계정 생성 후 API Keys 메뉴")
    print("   - 새 키 생성하여 ANTHROPIC_API_KEY에 입력")
    
    print("\n2. OpenAI API:")
    print("   - https://platform.openai.com 접속")
    print("   - API Keys 메뉴에서 새 키 생성")
    print("   - OPENAI_API_KEY에 입력")
    
    print("\n💰 비용 예상:")
    print("   - Claude: 월 약 2-5만원 (사용량에 따라)")
    print("   - OpenAI: 백업용이므로 거의 무료")

def test_system():
    """시스템 간단 테스트"""
    print("\n🧪 시스템 테스트 실행...")
    
    try:
        # 데이터베이스 테스트
        from src.utils.database import ContentDatabase
        db = ContentDatabase()
        print("✅ 데이터베이스 초기화 성공")
        
        # 설정 파일 로드 테스트
        from config.sites_config import SITE_CONFIGS
        print(f"✅ 사이트 설정 로드 성공 ({len(SITE_CONFIGS)}개 사이트)")
        
        return True
        
    except Exception as e:
        print(f"❌ 시스템 테스트 실패: {e}")
        return False

def main():
    """메인 실행"""
    print("🚀 블로그 자동화 시스템 빠른 시작 가이드")
    print("="*60)
    
    # .env 파일 존재 확인
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env 파일이 없습니다. .env.example을 복사하여 .env 파일을 만들어주세요.")
        return
    
    # 환경변수 로드
    from dotenv import load_dotenv
    load_dotenv()
    
    # 환경변수 확인
    if not check_environment():
        show_api_key_guide()
        show_wordpress_setup_guide()
        return
    
    # 시스템 테스트
    if not test_system():
        return
    
    print("\n" + "="*60)
    print("🎯 다음 단계:")
    print("="*60)
    print("1. python main.py test      # 모든 API 연결 테스트")
    print("2. python main.py setup     # 초기 데이터 설정")
    print("3. python main.py post unpre # 테스트 포스트 1개 생성")
    print("4. python main.py schedule   # 자동 스케줄러 시작")
    
    print("\n🔥 준비 완료! 이제 자동으로 블로그가 운영됩니다.")

if __name__ == "__main__":
    main()