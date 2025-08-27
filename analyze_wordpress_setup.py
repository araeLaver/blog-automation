#!/usr/bin/env python3
"""
WordPress 사이트 설정 분석 스크립트
- 실제 관리자 로그인 정보 확인
- WordPress REST API 활성화 상태 확인
- Application Password 설정 확인
- 권한 및 설정 문제 진단
"""

import sys
import requests
import base64
from pathlib import Path
import urllib3

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 프로젝트 루트를 시스템 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_wordpress_site(site_name, url, username, password):
    """개별 WordPress 사이트 분석"""
    
    print(f"\n{'='*60}")
    print(f"🔍 {site_name.upper()} 사이트 분석 ({url})")
    print(f"{'='*60}")
    
    analysis_results = {
        'site': site_name,
        'url': url,
        'username': username,
        'issues': [],
        'status': 'unknown'
    }
    
    # 1. 기본 사이트 접속 확인
    print("1. 🌐 기본 사이트 접속 확인...")
    try:
        response = requests.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            print(f"   ✅ 사이트 접속 성공 (상태코드: {response.status_code})")
        else:
            print(f"   ❌ 사이트 접속 실패 (상태코드: {response.status_code})")
            analysis_results['issues'].append(f"사이트 접속 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 사이트 접속 실패: {e}")
        analysis_results['issues'].append(f"사이트 접속 실패: {e}")
        
    # 2. WordPress 확인
    print("2. 📝 WordPress 설치 확인...")
    try:
        wp_login_url = f"{url}/wp-login.php"
        response = requests.get(wp_login_url, timeout=10, verify=False)
        if response.status_code == 200 and 'wordpress' in response.text.lower():
            print(f"   ✅ WordPress 사이트 확인됨")
        else:
            print(f"   ❌ WordPress가 아니거나 접근 불가")
            analysis_results['issues'].append("WordPress 설치 확인 불가")
    except Exception as e:
        print(f"   ❌ WordPress 확인 실패: {e}")
        analysis_results['issues'].append(f"WordPress 확인 실패: {e}")
    
    # 3. REST API 활성화 확인
    print("3. 🔌 WordPress REST API 확인...")
    api_url = f"{url}/wp-json/wp/v2/"
    try:
        response = requests.get(api_url, timeout=10, verify=False)
        if response.status_code == 200:
            print(f"   ✅ REST API 활성화됨")
            api_info = response.json()
            if 'namespace' in api_info:
                print(f"   📊 지원 네임스페이스: {', '.join(api_info.get('namespaces', []))}")
        else:
            print(f"   ❌ REST API 비활성화 또는 접근 불가 (상태코드: {response.status_code})")
            analysis_results['issues'].append(f"REST API 접근 불가: {response.status_code}")
    except Exception as e:
        print(f"   ❌ REST API 확인 실패: {e}")
        analysis_results['issues'].append(f"REST API 확인 실패: {e}")
    
    # 4. 관리자 계정으로 인증 테스트
    print("4. 🔐 관리자 계정 인증 테스트...")
    credentials = f"{username}:{password}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }
    
    try:
        # 포스트 목록 조회로 인증 테스트
        posts_url = f"{url}/wp-json/wp/v2/posts?per_page=1"
        response = requests.get(posts_url, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            print(f"   ✅ 관리자 계정 인증 성공")
            posts_data = response.json()
            print(f"   📊 포스트 수: {len(posts_data)}개 조회 성공")
            analysis_results['status'] = 'success'
        elif response.status_code == 401:
            print(f"   ❌ 인증 실패 - 아이디/비밀번호 오류")
            analysis_results['issues'].append("관리자 계정 인증 실패 - 잘못된 아이디/비밀번호")
            analysis_results['status'] = 'auth_failed'
        elif response.status_code == 403:
            print(f"   ❌ 권한 없음 - Application Password 미설정 또는 권한 부족")
            analysis_results['issues'].append("권한 없음 - Application Password 설정 필요")
            analysis_results['status'] = 'permission_denied'
        else:
            print(f"   ❌ 인증 테스트 실패 (상태코드: {response.status_code})")
            print(f"   📄 응답 내용: {response.text[:200]}")
            analysis_results['issues'].append(f"인증 테스트 실패: {response.status_code}")
            analysis_results['status'] = 'failed'
            
    except Exception as e:
        print(f"   ❌ 인증 테스트 실패: {e}")
        analysis_results['issues'].append(f"인증 테스트 실패: {e}")
        analysis_results['status'] = 'error'
    
    # 5. Application Password 설정 확인
    print("5. 🔑 Application Password 설정 확인...")
    try:
        # 사용자 정보 조회로 Application Password 확인
        users_url = f"{url}/wp-json/wp/v2/users/me"
        response = requests.get(users_url, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ 사용자 정보 조회 성공")
            print(f"   👤 사용자명: {user_data.get('name', 'Unknown')}")
            print(f"   📧 이메일: {user_data.get('email', 'Unknown')}")
            print(f"   🛡️ 역할: {', '.join(user_data.get('roles', []))}")
        else:
            print(f"   ❌ 사용자 정보 조회 실패")
            analysis_results['issues'].append("사용자 정보 조회 실패")
            
    except Exception as e:
        print(f"   ❌ Application Password 확인 실패: {e}")
        analysis_results['issues'].append(f"Application Password 확인 실패: {e}")
    
    return analysis_results

def main():
    """메인 분석 함수"""
    
    print("🔍 WordPress 사이트 설정 분석을 시작합니다...")
    print("현재 하드코딩된 관리자 정보로 실제 접근 가능한지 확인합니다.\n")
    
    # 현재 하드코딩된 WordPress 설정
    wordpress_sites = {
        'unpre': {
            'url': 'https://unpre.co.kr',
            'username': 'unpre',
            'password': 'Kdwyyr1527!'
        },
        'untab': {
            'url': 'https://untab.co.kr', 
            'username': 'untab',
            'password': 'Kdwyyr1527!'
        },
        'skewese': {
            'url': 'https://skewese.com',
            'username': 'skewese', 
            'password': 'Kdwyyr1527!'
        }
    }
    
    results = {}
    
    # 각 사이트 분석
    for site_name, config in wordpress_sites.items():
        results[site_name] = analyze_wordpress_site(
            site_name, 
            config['url'], 
            config['username'], 
            config['password']
        )
    
    # 종합 결과 요약
    print(f"\n{'='*80}")
    print("📊 종합 분석 결과 요약")
    print(f"{'='*80}")
    
    success_count = 0
    
    for site_name, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"\n{status_icon} {site_name.upper()} ({result['url']})")
        print(f"   상태: {result['status']}")
        
        if result['status'] == 'success':
            success_count += 1
            print(f"   🎉 완전히 설정됨 - 실제 발행 가능!")
        else:
            print(f"   ⚠️  문제점:")
            for issue in result['issues']:
                print(f"      - {issue}")
    
    print(f"\n📈 성공률: {success_count}/{len(wordpress_sites)} ({int(success_count/len(wordpress_sites)*100)}%)")
    
    # 권장사항 제시
    print(f"\n🔧 권장 조치사항:")
    
    if success_count == len(wordpress_sites):
        print("✅ 모든 사이트가 정상 설정되어 있습니다!")
        print("   실제 WordPress 사이트로의 자동 발행이 가능합니다.")
    else:
        print("⚠️ 다음 사항들을 확인하세요:")
        print("   1. WordPress 관리자 > 사용자 > 프로필에서 Application Password 생성")
        print("   2. REST API가 플러그인이나 테마에 의해 비활성화되지 않았는지 확인") 
        print("   3. 관리자 계정의 아이디/비밀번호가 정확한지 확인")
        print("   4. 서버 방화벽이나 보안 플러그인이 API 접근을 차단하지 않는지 확인")
    
    return results

if __name__ == "__main__":
    try:
        analysis_results = main()
        
        # 실패한 사이트가 있으면 종료 코드 1
        failed_sites = [site for site, result in analysis_results.items() if result['status'] != 'success']
        if failed_sites:
            print(f"\n❌ {len(failed_sites)}개 사이트에 문제가 있습니다.")
            sys.exit(1)
        else:
            print(f"\n✅ 모든 사이트 분석이 완료되었습니다.")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 분석 중 오류 발생: {e}")
        sys.exit(1)