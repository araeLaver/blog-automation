"""
Tistory Selenium 기반 자동 발행 모듈 (Open API 대체)
"""

import os
import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from dotenv import load_dotenv

load_dotenv()


class TistorySeleniumPublisher:
    def __init__(self):
        """Selenium 기반 Tistory 발행자 초기화"""
        self.blog_url = "https://untab.tistory.com"
        self.admin_url = "https://untab.tistory.com/manage"
        self.login_url = "https://www.tistory.com/auth/login"
        
        # Tistory 로그인 정보
        self.email = os.getenv("TISTORY_EMAIL")
        self.password = os.getenv("TISTORY_PASSWORD")
        
        if not all([self.email, self.password]):
            raise ValueError("Tistory 로그인 정보가 없습니다")
        
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        try:
            # undetected-chromedriver 사용 (봇 감지 회피)
            options = uc.ChromeOptions()
            
            # 헤드리스 모드 (선택사항)
            # options.add_argument('--headless')
            
            # 기타 옵션
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 사용자 프로필 사용 (로그인 상태 유지)
            user_data_dir = Path("./data/chrome_profile")
            user_data_dir.mkdir(parents=True, exist_ok=True)
            options.add_argument(f'--user-data-dir={user_data_dir}')
            
            # 드라이버 생성
            self.driver = uc.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            print("Chrome 드라이버 설정 완료")
            return True
            
        except Exception as e:
            print(f"드라이버 설정 실패: {e}")
            return False
    
    def login(self) -> bool:
        """Tistory 로그인"""
        try:
            self.driver.get(self.login_url)
            time.sleep(2)
            
            # 이미 로그인되어 있는지 확인
            if "manage" in self.driver.current_url:
                print("이미 로그인되어 있습니다")
                return True
            
            # 카카오 계정으로 로그인 버튼 클릭
            kakao_btn = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn_login.link_kakao_id"))
            )
            kakao_btn.click()
            
            # 카카오 로그인 창으로 전환
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(2)
            
            # 이메일 입력
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "loginId--1"))
            )
            email_input.clear()
            email_input.send_keys(self.email)
            
            # 비밀번호 입력
            password_input = self.driver.find_element(By.ID, "password--2")
            password_input.clear()
            password_input.send_keys(self.password)
            
            # 로그인 버튼 클릭
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn_g.highlight.submit")
            login_btn.click()
            
            # 원래 창으로 돌아오기
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            # 로그인 성공 확인
            time.sleep(3)
            if "tistory.com" in self.driver.current_url:
                print("Tistory 로그인 성공")
                return True
            
            return False
            
        except Exception as e:
            print(f"로그인 실패: {e}")
            return False
    
    def publish_post(self, content: Dict, images: List[Dict] = None, 
                     draft: bool = False) -> Tuple[bool, str]:
        """
        포스트 발행
        
        Args:
            content: 콘텐츠 딕셔너리
            images: 이미지 리스트
            draft: 초안 저장 여부
            
        Returns:
            (성공여부, URL 또는 에러메시지)
        """
        try:
            if not self.driver:
                self.setup_driver()
            
            # 로그인
            if not self.login():
                return False, "로그인 실패"
            
            # 글쓰기 페이지로 이동
            self.driver.get(f"{self.admin_url}/newpost")
            time.sleep(3)
            
            # 제목 입력
            title_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.textarea_tit"))
            )
            title_input.clear()
            title_input.send_keys(content['title'])
            
            # 에디터 모드 변경 (HTML 모드로)
            try:
                html_mode_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn_html")
                html_mode_btn.click()
                time.sleep(1)
            except:
                pass  # 이미 HTML 모드인 경우
            
            # 본문 내용 입력
            # HTML 에디터 찾기
            editor = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.CodeMirror"))
            )
            
            # CodeMirror 에디터에 내용 입력
            code_mirror = self.driver.find_element(By.CSS_SELECTOR, "div.CodeMirror")
            code_mirror.click()
            
            # JavaScript로 직접 내용 설정
            html_content = self._format_content_html(content, images)
            script = f"""
            var editor = document.querySelector('.CodeMirror').CodeMirror;
            editor.setValue(`{html_content}`);
            """
            self.driver.execute_script(script)
            
            # 카테고리 설정
            if content.get('category'):
                try:
                    category_select = self.driver.find_element(By.ID, "category")
                    category_select.click()
                    time.sleep(1)
                    
                    # 카테고리 옵션 선택
                    category_option = self.driver.find_element(
                        By.XPATH, f"//option[contains(text(), '{content['category']}')]"
                    )
                    category_option.click()
                except:
                    pass  # 카테고리가 없는 경우
            
            # 태그 입력
            if content.get('tags'):
                tag_input = self.driver.find_element(By.ID, "tagText")
                for tag in content['tags'][:10]:  # 최대 10개
                    tag_input.send_keys(tag)
                    tag_input.send_keys(",")
                    time.sleep(0.5)
            
            # 공개 설정
            if not draft:
                # 공개 라디오 버튼 선택
                public_radio = self.driver.find_element(By.ID, "open20")
                if not public_radio.is_selected():
                    public_radio.click()
            
            # 발행 버튼 클릭
            if draft:
                # 임시저장 버튼
                save_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn_save")
                save_btn.click()
            else:
                # 발행 버튼
                publish_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn_publish")
                publish_btn.click()
            
            # 발행 확인
            time.sleep(3)
            
            # 발행된 포스트 URL 가져오기
            if "manage/posts" in self.driver.current_url:
                # 방금 발행한 포스트 링크 찾기
                latest_post = self.driver.find_element(
                    By.CSS_SELECTOR, "div.post-item:first-child a.link_post"
                )
                post_url = latest_post.get_attribute("href")
                
                print(f"포스트 발행 성공: {post_url}")
                return True, post_url
            
            return False, "발행 확인 실패"
            
        except Exception as e:
            print(f"포스트 발행 실패: {e}")
            return False, str(e)
        
        finally:
            # 드라이버는 유지 (다음 발행을 위해)
            pass
    
    def _format_content_html(self, content: Dict, images: List[Dict]) -> str:
        """HTML 콘텐츠 포맷팅"""
        html = []
        
        # 서론
        if content.get('introduction'):
            html.append(f"<p>{content['introduction']}</p>")
        
        # 이미지 추가 (있는 경우)
        if images and len(images) > 0:
            # 첫 번째 이미지를 썸네일로
            html.append(f'<p style="text-align: center;">')
            html.append(f'<img src="{images[0]["url"]}" alt="{images[0].get("alt", "")}" />')
            html.append('</p>')
        
        # 본문 섹션들
        for section in content.get('sections', []):
            html.append(f"<h2>{section['heading']}</h2>")
            
            # 단락 처리
            paragraphs = section['content'].split('\n\n')
            for para in paragraphs:
                if para.strip():
                    html.append(f"<p>{para.strip()}</p>")
        
        # 결론
        if content.get('conclusion'):
            html.append(f"<h2>마무리</h2>")
            html.append(f"<p>{content['conclusion']}</p>")
        
        # JavaScript 이스케이프 처리
        html_str = '\n'.join(html)
        html_str = html_str.replace('`', '\\`').replace('${', '\\${')
        
        return html_str
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """이미지 업로드 (에디터 내에서)"""
        try:
            # 이미지 업로드 버튼 클릭
            upload_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn_image")
            upload_btn.click()
            time.sleep(1)
            
            # 파일 선택 input
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(str(Path(image_path).absolute()))
            
            # 업로드 대기
            time.sleep(3)
            
            # 업로드된 이미지 URL 가져오기 (구현 필요)
            return None
            
        except Exception as e:
            print(f"이미지 업로드 실패: {e}")
            return None
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __del__(self):
        """소멸자"""
        self.close()


# 사용 예시
if __name__ == "__main__":
    publisher = TistorySeleniumPublisher()
    
    # 테스트 콘텐츠
    test_content = {
        "title": "Selenium으로 작성한 테스트 포스트",
        "introduction": "이것은 자동화 테스트입니다.",
        "sections": [
            {
                "heading": "첫 번째 섹션",
                "content": "Selenium을 통해 자동으로 작성되었습니다."
            }
        ],
        "conclusion": "테스트 완료",
        "tags": ["테스트", "자동화"],
        "category": "언어"
    }
    
    success, result = publisher.publish_post(test_content)
    print(f"결과: {success}, {result}")
    
    publisher.close()