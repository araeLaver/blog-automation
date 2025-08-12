"""
Tistory 이메일 발행 모듈 - 이메일로 포스트 발행
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import Dict, List, Tuple
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class TistoryEmailPublisher:
    def __init__(self):
        """이메일 발행 초기화"""
        # Tistory 이메일 발행 주소 (관리 페이지에서 확인)
        self.tistory_email = os.getenv("TISTORY_PUBLISH_EMAIL", "untab.포스트키@tistory.com")
        
        # 발신 이메일 설정
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")  # 앱 패스워드 사용
        
        if not all([self.sender_email, self.sender_password]):
            raise ValueError("이메일 발송 정보가 없습니다")
    
    def publish_post(self, content: Dict, images: List[Dict] = None) -> Tuple[bool, str]:
        """
        이메일로 포스트 발행
        
        Tistory 이메일 발행 형식:
        - 제목: 메일 제목이 포스트 제목
        - 본문: HTML 형식 지원
        - 첨부 이미지: 본문에 자동 삽입
        """
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart('related')
            msg['From'] = self.sender_email
            msg['To'] = self.tistory_email
            msg['Subject'] = content['title']
            
            # HTML 본문 생성
            html_content = self._create_html_content(content, images)
            
            # HTML 파트 추가
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 이미지 첨부 (있는 경우)
            if images:
                for i, img in enumerate(images[:3]):  # 최대 3개
                    if img.get('url', '').startswith('http'):
                        continue  # 외부 URL은 스킵
                    
                    img_path = Path(img['url'])
                    if img_path.exists():
                        with open(img_path, 'rb') as f:
                            img_data = f.read()
                            img_mime = MIMEImage(img_data)
                            img_mime.add_header('Content-ID', f'<image{i}>')
                            msg.attach(img_mime)
            
            # 태그 추가 (본문 끝에)
            if content.get('tags'):
                tags_text = f"\n\n태그: {', '.join(content['tags'])}"
                # 태그는 본문 끝에 텍스트로 추가
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"이메일 발행 성공: {content['title']}")
            return True, f"이메일로 발행됨: {self.tistory_email}"
            
        except Exception as e:
            print(f"이메일 발행 실패: {e}")
            return False, str(e)
    
    def _create_html_content(self, content: Dict, images: List[Dict]) -> str:
        """HTML 콘텐츠 생성"""
        html = []
        
        # 스타일 추가
        html.append("""
        <html>
        <body style="font-family: 'Malgun Gothic', sans-serif; line-height: 1.8; max-width: 800px; margin: 0 auto; padding: 20px;">
        """)
        
        # 서론
        if content.get('introduction'):
            html.append(f"<p>{content['introduction']}</p>")
        
        # 첫 번째 이미지 (인라인)
        if images and len(images) > 0:
            html.append('<p style="text-align: center;">')
            html.append('<img src="cid:image0" style="max-width: 100%; height: auto;" />')
            html.append('</p>')
        
        # 본문 섹션들
        for i, section in enumerate(content.get('sections', [])):
            html.append(f"<h2 style='color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px;'>{section['heading']}</h2>")
            
            # 단락 처리
            paragraphs = section['content'].split('\n\n')
            for para in paragraphs:
                if para.strip():
                    html.append(f"<p>{para.strip()}</p>")
            
            # 중간 이미지 삽입
            if images and i == 0 and len(images) > 1:
                html.append('<p style="text-align: center;">')
                html.append('<img src="cid:image1" style="max-width: 100%; height: auto;" />')
                html.append('</p>')
        
        # 결론
        if content.get('conclusion'):
            html.append(f"<h2 style='color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px;'>마무리</h2>")
            html.append(f"<p>{content['conclusion']}</p>")
        
        # 태그
        if content.get('tags'):
            html.append(f"<p style='margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666;'>")
            html.append(f"태그: {', '.join(content['tags'])}")
            html.append("</p>")
        
        html.append("</body></html>")
        
        return '\n'.join(html)


# 사용 예시
if __name__ == "__main__":
    publisher = TistoryEmailPublisher()
    
    test_content = {
        "title": "이메일로 발행하는 테스트 포스트",
        "introduction": "이메일 발행 기능 테스트입니다.",
        "sections": [
            {
                "heading": "이메일 발행의 장점",
                "content": "API 없이도 자동 발행이 가능합니다."
            }
        ],
        "conclusion": "이메일 발행 완료",
        "tags": ["이메일", "자동화"]
    }
    
    success, result = publisher.publish_post(test_content)
    print(f"결과: {success}, {result}")