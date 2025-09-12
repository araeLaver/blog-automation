"""
AI 기반 콘텐츠 생성 모듈
"""

import os
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import anthropic
from dotenv import load_dotenv
from src.utils.api_tracker import api_tracker

load_dotenv()


class ContentGenerator:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        print(f"API Key loaded: {api_key[:20] if api_key else 'None'}...")  # 디버그용
        
        if not api_key or api_key.startswith("sk-ant-api03-your-actual"):
            raise ValueError("실제 Claude API 키가 설정되지 않았습니다. .env 파일의 ANTHROPIC_API_KEY를 확인하세요.")
        
        # Koyeb 환경에서 proxies 파라미터 문제 해결
        # 모든 프록시 관련 환경변수 백업 및 임시 제거
        proxy_env_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
                         'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']
        old_proxy_values = {}
        
        for var in proxy_env_vars:
            if var in os.environ:
                old_proxy_values[var] = os.environ.pop(var)
        
        try:
            # proxies 매개변수를 명시적으로 None으로 설정하여 클라이언트 초기화
            try:
                # 최신 버전 anthropic 라이브러리 호환
                self.anthropic_client = anthropic.Anthropic(
                    api_key=api_key,
                    proxies=None  # 명시적으로 None 설정
                )
            except TypeError:
                # 구버전 anthropic 라이브러리 호환 (proxies 파라미터 없음)
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                
        except Exception as e:
            print(f"Anthropic 클라이언트 초기화 오류: {e}")
            raise
        finally:
            # 환경변수 복원
            for var, value in old_proxy_values.items():
                os.environ[var] = value
    
    def generate_content(self, site_config: Dict, topic: str, 
                        category: str, existing_posts: List[str] = None, content_length: str = 'medium', site_key: str = None) -> Dict:
        """메인 콘텐츠 생성 함수"""
        
        # 프롬프트 생성
        prompt = self._create_prompt(site_config, topic, category, existing_posts, content_length)
        
        # Claude API로 콘텐츠 생성 (사이트 정보 전달)
        content = self._generate_with_claude(prompt, site_key)
        
        # 콘텐츠 파싱 및 구조화
        structured_content = self._parse_content(content)
        
        # SEO 최적화
        optimized_content = self._optimize_for_seo(structured_content, site_config)
        
        # 최종 Unicode 안전성 검사 (Windows CP949 호환성 보장)
        # UTF-8 사용으로 변경 - cp949 호환성 체크 제거
        # optimized_content = self._ensure_cp949_compatibility(optimized_content)
        
        return optimized_content
    
    def _create_prompt(self, site_config: Dict, topic: str, 
                       category: str, existing_posts: List[str] = None, content_length: str = 'medium') -> str:
        """AI 프롬프트 생성"""
        
        # 콘텐츠 길이별 설정
        length_settings = {
            'short': {
                'sections': 2,
                'section_length': '200-300자',
                'introduction_length': '150자 정도',
                'conclusion_length': '150자',
                'total_guide': '1,500-2,000자 분량'
            },
            'medium': {
                'sections': 3,
                'section_length': '300-500자',
                'introduction_length': '200자 정도',
                'conclusion_length': '200자',
                'total_guide': '2,500-3,500자 분량'
            },
            'long': {
                'sections': 4,
                'section_length': '400-600자',
                'introduction_length': '250자 정도',
                'conclusion_length': '250자',
                'total_guide': '4,000-5,500자 분량'
            },
            'very_long': {
                'sections': 5,
                'section_length': '500-700자',
                'introduction_length': '300자 정도',
                'conclusion_length': '300자',
                'total_guide': '6,000-8,000자 분량'
            }
        }
        
        settings = length_settings.get(content_length, length_settings['medium'])
        
        # 섹션 템플릿 생성 - 주제별 맞춤 구조
        section_topics = [
            f"{topic}의 핵심 개념과 특징",
            f"{topic}의 구체적 활용 방법",  
            f"{topic} 관련 주의사항과 팁",
            f"{topic}의 실제 사례와 예시",
            f"{topic}의 기대 효과와 미래 전망"
        ]
        
        sections_template = []
        for i in range(settings['sections']):
            section_topic = section_topics[i] if i < len(section_topics) else f"{i+1}번째 핵심 내용"
            sections_template.append(f'''        {{
            "heading": "{section_topic}에 대한 구체적이고 매력적인 제목",
            "content": "{settings['section_length']}의 상세한 설명. 반드시 다음 형식을 포함하세요:\\n\\n[핀] **구조화된 내용 요구사항:**\\n\\n1. **도입 문장**: 이 섹션의 중요성 설명 (2-3문장)\\n\\n2. **핵심 내용**: \\n   - 주요 포인트 3-5개를 목록이나 표 형태로 정리\\n   - 각 포인트마다 **굵은 글씨**로 키워드 강조\\n   - 비교/정리 필요시 HTML 표 활용\\n\\n3. **실용 정보**: \\n   - 구체적인 예시나 수치 제시\\n   - 단계별 가이드나 체크리스트\\n   - 코드나 도구 예시 (필요시)\\n\\n4. **주의사항**: [주의] 텍스트와 함께 중요한 주의점 안내\\n\\n5. **마무리**: 이 섹션의 핵심 포인트 요약 (2-3문장)\\n\\n반드시 실용적이고 전문적인 내용으로 작성하세요."
        }}''')
        
        sections_json = ',\n'.join(sections_template)
        
        prompt = f"""TOPIC: {topic}

Write a comprehensive blog post about "{topic}" ONLY.

Title must be about: {topic}
Content must be about: {topic}
Do not write about general topics or other subjects.

Blog: {site_config['name']}
Audience: {site_config['target_audience']}
Category: {category}
📏 **분량**: {settings['total_guide']}

🔥 **품질 요구사항 (매우 중요!)** 🔥

**1. 전문성과 깊이**:
- 해당 분야 전문가 수준의 인사이트 제공
- 최신 트렌드와 실제 경험이 반영된 내용
- 표면적 설명이 아닌 심층적 분석과 가이드

**2. 실용성과 가치**:
- 독자가 즉시 활용할 수 있는 구체적 방법론
- 단계별 실행 가이드와 체크리스트
- 실제 사례, 예시, 데이터가 풍부하게 포함
- 문제 해결에 직접적으로 도움되는 내용

**3. 콘텐츠 구성과 가독성**:
- 논리적이고 체계적인 정보 구조
- 각 섹션은 {settings['section_length']}로 상세하고 알찬 내용
- **굵은 글씨**로 핵심 키워드 강조
- 비교표, 체크리스트, 코드 예제 적극 활용

**4. SEO와 검색 최적화**:
- 자연스러우면서도 검색에 최적화된 제목
- 독자가 클릭하고 싶어하는 매력적인 제목 구성
- 핵심 키워드가 자연스럽게 포함된 내용

[핵심 작성 주제]
{topic}

[블로그 정보]
- 카테고리: {category}
- 타겟 독자: {site_config['target_audience']}
- 작성 스타일: {site_config['content_style']}
- 콘텐츠 길이: {settings['total_guide']}

[작성 요구사항]
반드시 아래 JSON 형식으로만 응답하세요. 다른 형식은 허용되지 않습니다.

{{
    "title": "{topic}에 대한 매력적인 한국어 제목 (30-60자)",
    "meta_description": "검색 결과에 표시될 120-160자 설명",
    "introduction": "독자의 관심을 끄는 {settings['introduction_length']}의 서론. 주제의 중요성과 이 글에서 다룰 내용 소개",
    "sections": [
{sections_json}
    ],
    "additional_content": "주제와 관련된 추가 유용한 정보나 심화 내용 ({settings['conclusion_length']})",
    "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"],
    "keywords": ["키워드1", "키워드2", "키워드3"]
}}

**가독성 향상 필수 요구사항**:
- 위 JSON 형식 외에는 아무것도 출력하지 마세요
- 모든 내용은 한국어로 작성하세요
- 각 섹션은 {settings['section_length']}로 충분히 상세하게 작성하세요
- 절대 이모지나 유니코드 특수문자를 사용하지 마세요
- **목록 작성 시 절대 준수사항**: 각 항목마다 반드시 새 줄에 작성 (- 항목은 각각 \\n으로 구분)

**컨텐츠 포맷팅 규칙**:
1. **문단 구분**: 2-3문장마다 \\n\\n로 줄바꿈
2. **섹션 구분**: 하위 주제 사이에 --- 구분선 사용  
3. **표 활용**: 비교/정리 필요시 HTML 테이블 사용
   예: <table><tr><th>항목</th><th>설명</th></tr><tr><td>내용1</td><td>설명1</td></tr></table>
4. **목록화**: 중요 포인트는 목록 형태로 작성 (각 항목마다 반드시 새 줄에 작성)
   - 각 항목은 반드시 새 줄에 작성: 
     - 첫 번째 항목\\n
     - 두 번째 항목\\n
     - 세 번째 항목\\n
   - 절대 "- 항목1 - 항목2 - 항목3" 형태로 한 줄에 이어쓰지 않기
5. **강조**: 핵심 키워드는 **굵은글씨**로 자연스럽게 강조
6. **코드**: 필요시 ```언어\\n코드\\n``` 형태로 작성
7. **아이콘**: 핵심 정보에 [핀], [팁], [주의], [타겟] 등 대괄호 텍스트 사용
8. **숫자와 데이터**: 퍼센트, 금액, 날짜 등은 명확하게 표기
9. **박스 강조**: 중요한 정보는 박스 형태나 인용문으로 강조
"""
        
        if existing_posts:
            prompt += f"\n\n[최근 발행 포스트 (중복 방지)]\n"
            for post in existing_posts[:5]:
                prompt += f"- {post}\n"
        
        return prompt
    
    def _generate_with_claude(self, prompt: str, site_key: str = None) -> str:
        """Claude API로 콘텐츠 생성"""
        try:
            # 시스템 메시지 - 고품질 콘텐츠 생성을 위한 상세 가이드
            system_message = """당신은 전문 블로그 콘텐츠 크리에이터입니다.

**핵심 미션**: 독자가 실제로 도움받을 수 있는 고품질, 실용적인 한국어 블로그 콘텐츠 생성

**콘텐츠 품질 기준 (매우 중요!):**

**전문성**: 
- 해당 분야의 전문가 수준의 깊이 있는 내용
- 최신 트렌드와 실무 경험이 반영된 인사이트
- 단순한 정보 나열이 아닌 실용적 가이드

[중요] **실용성**:
- 독자가 바로 적용할 수 있는 구체적인 방법론
- 단계별 실행 가이드 제공
- 실제 사례와 예시를 풍부하게 포함

[핵심] **가독성**:
- 명확한 구조와 논리적 흐름
- 적절한 소제목과 문단 구분
- 핵심 포인트는 굵게 강조

**절대적 요구사항:**
[필수] 오직 유효한 JSON 형식으로만 응답
[필수] 모든 내용은 한국어로 작성
[필수] 각 섹션당 최소 300-500자의 상세한 내용
[필수] 실제 도움이 되는 구체적 정보 포함
[필수] 전문적이면서도 이해하기 쉬운 설명
[필수] 목록 작성 시 각 항목은 반드시 새 줄에 작성 (- 항목은 각각 \\n으로 구분)
[필수] 절대 "- 항목1 - 항목2" 형태로 한 줄에 이어쓰지 않기
[필수] 절대 이모지나 유니코드 특수문자 사용하지 말 것

[금지] 절대 하지 말 것:
[금지] JSON 외의 다른 텍스트 출력 금지
[금지] 피상적이거나 일반적인 내용 금지
[금지] 단순 번역체나 어색한 문장 금지
[금지] 빈약한 내용이나 짧은 설명 금지
[금지] 목록을 한 줄에 나열하는 것 절대 금지 (- 항목1 - 항목2 형태 금지)
[금지] 이모지, 특수문자, 유니코드 기호 사용 절대 금지"""
            
            # 입력 토큰 추정 (시스템 메시지 + 사용자 메시지)
            input_text = system_message + prompt
            estimated_input_tokens = len(input_text) // 3  # 대략적 추정
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,  # 더 긴 고품질 콘텐츠를 위해 증가
                temperature=0.8,  # 창의성 증가
                system=system_message,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            
            # 즉시 CP949 호환성 처리 - API 응답 직후
            # UTF-8 사용으로 변경 - cp949 클리닝 제거
            # result = self._aggressive_cp949_clean(result)
            
            # 추가 CP949 호환성 처리 - 문자 단위로 검사 및 변환
            # UTF-8 사용으로 변경 - cp949 호환성 체크 제거
            # result = self._ensure_cp949_compatibility(result)
            
            # 실제 토큰 사용량 (Claude API 응답에서 가져오기)
            actual_input_tokens = response.usage.input_tokens
            actual_output_tokens = response.usage.output_tokens
            
            # API 사용량 추적
            api_tracker.track_usage(
                service="claude",
                model="claude-3-5-sonnet-20241022",
                input_tokens=actual_input_tokens,
                output_tokens=actual_output_tokens,
                site=site_key,
                purpose="content_generation",
                success=True,
                endpoint="messages"
            )
            
            # 디버깅: API 응답 로그
            print(f"Claude API Response Length: {len(result)}")
            print(f"Response starts with: {result[:200]}...")
            print(f"Response ends with: ...{result[-200:]}")
            print(f"Full response: {result}")
            
            # 응답이 코드로 시작하는 경우 처리
            if result.strip().startswith(('const', 'function', 'import', 'jsx', 'python', 'async', 'def')):
                print("Warning: Claude returned code instead of JSON. Regenerating...")
                # 재시도 with stronger prompt
                retry_prompt = f"""**절대적 요구사항**: 
                오직 JSON 형식으로만 응답하세요. 코드를 작성하지 마세요.
                블로그 글 제목과 내용을 JSON으로 작성하세요.
                
                다시 한번 요청: {prompt}"""
                
                # 재시도 입력 토큰 추정
                retry_input_text = system_message + retry_prompt
                retry_estimated_input_tokens = len(retry_input_text) // 3
                
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=0.7,
                    system=system_message,
                    messages=[
                        {"role": "user", "content": retry_prompt}
                    ]
                )
                result = response.content[0].text
                
                # 재시도 API 사용량 추적
                api_tracker.track_usage(
                    service="claude",
                    model="claude-3-5-sonnet-20241022",
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    site=site_key,
                    purpose="content_generation_retry",
                    success=True,
                    endpoint="messages"
                )
                
                print(f"Retry Response starts with: {result[:100]}...")
            
            return result
        except Exception as e:
            # 실패한 API 호출 추적
            api_tracker.track_usage(
                service="claude",
                model="claude-3-5-sonnet-20241022",
                input_tokens=estimated_input_tokens if 'estimated_input_tokens' in locals() else 0,
                output_tokens=0,
                site=site_key,
                purpose="content_generation",
                success=False,
                error_message=str(e),
                endpoint="messages"
            )
            print(f"Claude API 오류: {e}")
            raise
    
    def _parse_content(self, content: str) -> Dict:
        """생성된 콘텐츠 파싱"""
        try:
            print(f"Parsing content: {content[:500]}...")
            
            # CP949 호환성 처리
            # UTF-8 사용으로 변경 - cp949 호환성 체크 제거
            # content = self._ensure_cp949_compatibility(content)
            
            # JSON 추출 (마크다운 코드 블록 제거)
            original_content = content
            
            # 먼저 순수 JSON인지 확인
            if content.strip().startswith("{") and content.strip().endswith("}"):
                print("Content appears to be pure JSON")
            elif "```json" in content:
                content = content.split("```json")[1].split("```")[0]
                print("Extracted from ```json blocks")
            elif "```" in content and content.count("```") >= 2:
                # 실제 JSON 블록만 추출
                parts = content.split("```")
                for i, part in enumerate(parts):
                    if part.strip().startswith("{") and part.strip().endswith("}"):
                        content = part
                        print("Extracted JSON block from ``` blocks")
                        break
                else:
                    # JSON 블록을 찾지 못한 경우, 첫 번째와 마지막 ```를 제거
                    if len(parts) >= 3:
                        content = parts[1]
                        print("Used first ``` block")
            
            # JSON이 아닌 다른 텍스트가 앞뒤에 있는 경우 추출
            if not content.strip().startswith("{"):
                # 첫 번째 { 찾기
                start_idx = content.find("{")
                if start_idx != -1:
                    # 마지막 } 찾기
                    end_idx = content.rfind("}")
                    if end_idx != -1 and end_idx > start_idx:
                        content = content[start_idx:end_idx+1]
                        print("Extracted JSON from mixed content")
            
            print(f"Cleaned content for JSON parsing: {content[:300]}...")
            
            # 특수 문자 정리 (인코딩 오류 방지)
            print("Applying unicode sanitization...")
            content = self._sanitize_unicode_for_json(content)
            print("Unicode sanitization completed.")
            
            # 강력한 CP949 정리 적용 (JSON 파싱 전)
            # UTF-8 사용으로 변경 - cp949 클리닝 제거
            # content = self._aggressive_cp949_clean(content)
            print("CP949 cleaning applied before JSON parsing.")
            
            parsed_content = json.loads(content)
            print(f"Successfully parsed JSON: {list(parsed_content.keys())}")
            
            # 강제 CP949 호환성 변환
            def force_utf8_safe(obj):
                if isinstance(obj, dict):
                    return {k: force_utf8_safe(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [force_utf8_safe(item) for item in obj]
                elif isinstance(obj, str):
                    # UTF-8로 그대로 반환
                    return obj
                else:
                    return obj
            
            parsed_content = force_utf8_safe(parsed_content)
            print("CP949 호환성 변환 적용 완료")
            
            # 콘텐츠 검증
            return self._validate_content(parsed_content)
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            print(f"파싱 시도한 내용: {content[:500]}...")
            # JSON 파싱 실패시 기본 구조로 변환
            return self._fallback_parse(original_content)
    
    def _validate_content(self, content: Dict) -> Dict:
        """생성된 콘텐츠 검증 및 필터링"""
        import datetime
        current_year = datetime.datetime.now().year
        
        # 연도 수정 (2024년 → 현재 연도)
        for key in ['title', 'meta_description', 'introduction', 'additional_content']:
            if key in content and content[key]:
                content[key] = re.sub(r'2024년', f'{current_year}년', content[key])
                content[key] = re.sub(r'\[2024년\]', f'[{current_year}년]', content[key])
        
        # 섹션 내용도 연도 수정
        if 'sections' in content and isinstance(content['sections'], list):
            for section in content['sections']:
                if isinstance(section, dict):
                    for key in ['heading', 'content']:
                        if key in section and section[key]:
                            section[key] = re.sub(r'2024년', f'{current_year}년', section[key])
                            section[key] = re.sub(r'\[2024년\]', f'[{current_year}년]', section[key])
        
        # 제목 검증
        title = content.get('title', '')
        
        # 코드가 섞인 제목 감지 및 수정
        code_indicators = ['jsx', 'const', 'element', 'function', 'import', 'async', 'await', 
                          'def', 'class', '{', '}', '<', '>', '()', '=>', '\n']
        if any(indicator in title.lower() for indicator in code_indicators):
            # 주제 기반으로 새 제목 생성
            topic_keywords = ['Python', 'JavaScript', 'React', 'Node', 'async', 'API', 'Database']
            matched_keyword = next((kw for kw in topic_keywords if kw.lower() in title.lower()), '프로그래밍')
            content['title'] = f"{matched_keyword} 완벽 가이드: 실전 예제와 베스트 프랙티스"
        
        # 제목이 너무 짧거나 이상한 경우
        if len(title.strip()) < 10 or title.count('\n') > 0:
            content['title'] = "프로그래밍 실전 가이드: 개발자를 위한 핵심 기술"
        
        # 섹션 검증
        sections = content.get('sections', [])
        valid_sections = []
        for section in sections:
            if isinstance(section, dict) and 'heading' in section and 'content' in section:
                # 섹션 내용이 코드만인 경우 설명 추가
                if section['content'].strip().startswith(('const', 'function', 'import', '<', '{', 'jsx')):
                    section['content'] = f"이 섹션에서는 다음과 같은 내용을 다룹니다:\n\n{section['content']}"
                valid_sections.append(section)
        
        content['sections'] = valid_sections
        
        return content
    
    def _fallback_parse(self, content: str) -> Dict:
        """JSON 파싱 실패시 대체 파싱"""
        import re
        
        print(f"Fallback parsing activated for content: {content[:200]}...")
        
        # 제목 추출 시도
        title = "실용적인 개발 가이드"
        title_match = re.search(r'#\s*(.+)|제목[:：]\s*(.+)', content)
        if title_match:
            title = title_match.group(1) or title_match.group(2)
            title = title.strip()
        
        # 코드로 시작하는 경우 제목 생성
        if content.strip().startswith(('const', 'function', 'import', '<', '{', 'jsx', 'python', 'async')):
            title = "개발자를 위한 실전 기술 가이드"
        
        # 내용 추출 시도
        lines = content.split('\n')
        non_code_lines = [line.strip() for line in lines 
                         if line.strip() and not line.strip().startswith(('const', 'function', 'import', '<', '{', '}', '//', '#', 'jsx'))]
        
        # 실제 내용 생성
        introduction = "이 글에서는 실용적인 개발 기술과 베스트 프랙티스를 다룹니다."
        if non_code_lines:
            introduction = ' '.join(non_code_lines[:3]) or introduction
            
        sections = [
            {
                "heading": "기본 개념",
                "content": "핵심 개념과 원리를 이해하는 것이 중요합니다. 기본기를 탄탄히 하고 실무에 적용할 수 있는 방법을 알아보겠습니다."
            },
            {
                "heading": "실전 적용",
                "content": "이론을 실제 프로젝트에 적용하는 방법을 알아봅니다. 효율적인 개발을 위한 팁과 노하우를 공유합니다."
            },
            {
                "heading": "심화 학습",
                "content": "더 깊이 있는 학습을 위한 리소스와 실무에서 활용할 수 있는 고급 기법들을 소개합니다."
            }
        ]
        
        return {
            "title": title,
            "meta_description": "실용적인 개발 기술과 베스트 프랙티스를 다루는 가이드입니다.",
            "introduction": introduction,
            "sections": sections,
            "additional_content": "관련 기술들과 함께 활용하면 더욱 효과적인 결과를 얻을 수 있습니다. 실무 프로젝트에서 이런 접근 방식들이 어떻게 적용되는지 살펴보세요.",
            "tags": ["개발", "프로그래밍", "기술", "가이드", "실전"],
            "keywords": ["개발", "프로그래밍", "기술"]
        }
    
    def _optimize_for_seo(self, content: Dict, site_config: Dict) -> Dict:
        """SEO 최적화"""
        # 제목 최적화
        if len(content['title']) < 30:
            content['title'] = f"{content['title']} - {site_config['name']}"
        
        # 키워드 밀도 조정
        main_keywords = site_config.get('keywords_focus', [])
        for keyword in main_keywords[:3]:
            # 각 섹션에 키워드 자연스럽게 추가
            for section in content['sections']:
                if keyword.lower() not in section['content'].lower():
                    section['content'] = self._insert_keyword(
                        section['content'], keyword
                    )
        
        # 내부 링크 추가 준비 (실제 URL은 발행시 추가)
        content['internal_links'] = []
        
        # 구조화된 데이터 추가
        content['structured_data'] = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": content['title'],
            "description": content['meta_description'],
            "datePublished": datetime.now().isoformat(),
            "author": {
                "@type": "Organization",
                "name": site_config['name']
            }
        }
        
        return content
    
    def _insert_keyword(self, text: str, keyword: str) -> str:
        """텍스트에 키워드 자연스럽게 삽입"""
        # 간단한 구현 - 실제로는 더 정교한 NLP 필요
        sentences = text.split('.')
        if len(sentences) > 2:
            # 중간 문장에 키워드 추가
            mid = len(sentences) // 2
            sentences[mid] = f"{sentences[mid]}. 이와 관련하여 {keyword}도 중요한 요소입니다"
        
        return '.'.join(sentences)
    
    def generate_title_variations(self, base_title: str, count: int = 5) -> List[str]:
        """제목 변형 생성 (A/B 테스트용)"""
        prompt = f"""
다음 제목의 변형을 {count}개 만들어주세요.
원본 제목: {base_title}

요구사항:
- SEO 최적화
- 클릭률을 높일 수 있는 매력적인 표현
- 30-60자 길이
- 각각 다른 접근 방식 사용

JSON 배열 형식으로 출력:
["제목1", "제목2", ...]
"""
        
        response = self._generate_with_claude(prompt)
        try:
            return json.loads(response)
        except:
            return [base_title]
    
    def improve_content(self, original_content: str, feedback: str) -> str:
        """기존 콘텐츠 개선"""
        prompt = f"""
다음 콘텐츠를 피드백에 따라 개선해주세요.

[원본 콘텐츠]
{original_content}

[개선 요청사항]
{feedback}

개선된 콘텐츠를 출력해주세요.
"""
        
        return self._generate_with_claude(prompt)
    
    def _sanitize_unicode_for_json(self, content: str) -> str:
        """JSON 파싱 전 유니코드 특수 문자 정리"""
        import re
        
        # 문제가 되는 유니코드 이모지 및 특수 문자를 안전한 텍스트로 변환
        replacements = {
            '⚠️': '[주의]',
            '⚠': '[주의]',
            '✅': '[확인]',
            '❌': '[오류]',
            '⭐': '[중요]',
            '🔥': '[핫]',
            '💡': '[팁]',
            '📌': '[포인트]',
            '🚀': '[시작]',
            '⏰': '[시간]',
            '💰': '[가격]',
            '📈': '[상승]',
            '📉': '[하락]',
            '👍': '[좋음]',
            '👎': '[나쁨]',
            '🎯': '[목표]',
            '📊': '[차트]',
            '🔍': '[검색]',
            '📝': '[작성]',
            '🎨': '[디자인]',
            '🛠': '[도구]',
            '⚡': '[빠름]',
            '🌟': '[별점]'
        }
        
        for emoji, replacement in replacements.items():
            content = content.replace(emoji, replacement)
        
        # CP949에서 인코딩할 수 없는 문자들을 안전하게 제거/변환
        try:
            # 먼저 CP949로 인코딩해보고 오류가 있으면 해당 문자 제거
            content.encode('cp949')
            print(f"Content is CP949 safe: {len(content)} chars")
        except UnicodeEncodeError as e:
            print(f"UnicodeEncodeError detected: {e}")
            # CP949로 인코딩할 수 없는 문자들을 ignore하여 제거
            content = content.encode('cp949', errors='ignore').decode('cp949')
            print(f"CP949 problematic chars removed: {len(content)} chars remaining")
        
        print(f"Unicode sanitized content preview: {content[:200]}...")
        return content
    
    def _aggressive_cp949_clean(self, text: str) -> str:
        """API 응답 직후 강력한 CP949 호환성 처리 - 완전한 Unicode 제거"""
        import re
        
        # 1단계: 모든 이모지와 특수 유니코드 문자를 텍스트로 변환
        # 이모지 매핑 (모든 가능한 이모지 처리)
        emoji_replacements = {
            # 경고 및 체크 마크
            '⚠': '[주의]', '⚠️': '[주의]',
            '✅': '[완료]', '❌': '[실패]', '❗': '[중요]', '❓': '[질문]',
            '⭐': '[별점]', '⭐️': '[별점]', '🌟': '[별점]',
            
            # 사무용품 및 문서
            '📌': '[중요]', '📍': '[위치]', '📋': '[목록]', '📊': '[차트]',
            '📈': '[상승]', '📉': '[하락]', '📝': '[메모]', '📄': '[문서]',
            '📑': '[페이지]', '📚': '[도서]', '📖': '[독서]', '📓': '[노트]',
            '📒': '[장부]', '📘': '[서적]', '📙': '[가이드]', '📗': '[안내서]',
            '📕': '[교재]', '📔': '[수첩]', '📅': '[일정]', '📆': '[달력]',
            
            # 기술 및 도구
            '🔍': '[검색]', '🔎': '[검색]', '🔧': '[도구]', '🔨': '[해머]',
            '⚙': '[설정]', '⚙️': '[설정]', '🖥': '[컴퓨터]', '💻': '[노트북]',
            '📱': '[스마트폰]', '⌨': '[키보드]', '⌨️': '[키보드]', '🖱': '[마우스]',
            '🔌': '[연결]', '🔋': '[배터리]', '💾': '[저장]', '💿': '[디스크]',
            
            # 방향 및 화살표
            '🎯': '[목표]', '🎪': '[이벤트]', '🎨': '[디자인]', '🎭': '[연극]',
            '🚀': '[시작]', '🛰': '[위성]', '🛸': '[UFO]', '✈': '[비행기]',
            '✈️': '[비행기]', '🚁': '[헬기]', '🚂': '[기차]', '🚗': '[자동차]',
            
            # 감정 및 제스처
            '👍': '[좋음]', '👎': '[나쁨]', '👌': '[완벽]', '✋': '[정지]',
            '✌': '[평화]', '✌️': '[평화]', '👏': '[박수]', '🙏': '[감사]',
            '💪': '[힘]', '🤝': '[악수]', '👥': '[사람들]', '👤': '[사용자]',
            
            # 돈과 비즈니스
            '💰': '[돈]', '💵': '[달러]', '💴': '[엔]', '💶': '[유로]',
            '💷': '[파운드]', '💳': '[카드]', '💸': '[지출]', '📈': '[성장]',
            '📊': '[분석]', '📉': '[감소]', '💹': '[주식]', '💼': '[비즈니스]',
            
            # 시간 및 날씨
            '⏰': '[알람]', '⏱': '[스톱워치]', '⏲': '[타이머]', '🕐': '[1시]',
            '🕑': '[2시]', '🕒': '[3시]', '🕓': '[4시]', '🕔': '[5시]',
            '🕕': '[6시]', '🕖': '[7시]', '🕗': '[8시]', '🕘': '[9시]',
            '🕙': '[10시]', '🕚': '[11시]', '🕛': '[12시]',
            '☀': '[태양]', '☀️': '[태양]', '🌙': '[달]', '⭐': '[별]',
            '🌈': '[무지개]', '☔': '[비]', '⛅': '[구름]', '❄': '[눈]',
            '❄️': '[눈]', '🌨': '[눈]', '🌨️': '[눈]',
            
            # 음식
            '🍎': '[사과]', '🍊': '[오렌지]', '🍌': '[바나나]', '🍓': '[딸기]',
            '🍕': '[피자]', '🍔': '[햄버거]', '🍟': '[감자튀김]', '🍳': '[계란]',
            '☕': '[커피]', '☕️': '[커피]', '🍵': '[차]', '🍺': '[맥주]',
            '🍷': '[와인]', '🥂': '[샴페인]', '🍴': '[식기]', '🥄': '[숟가락]',
        }
        
        # 이모지 교체
        cleaned_text = text
        for emoji, replacement in emoji_replacements.items():
            cleaned_text = cleaned_text.replace(emoji, replacement)
        
        # 2단계: 남은 모든 비-CP949 문자를 안전한 문자로 교체
        safe_chars = []
        replaced_count = 0
        
        for char in cleaned_text:
            try:
                char.encode('cp949')
                safe_chars.append(char)
            except UnicodeEncodeError:
                # 일반적인 특수 문자 처리
                char_code = ord(char)
                if char_code == 0x2026:  # …
                    safe_chars.append('...')
                elif char_code == 0x2013:  # –
                    safe_chars.append('-')
                elif char_code == 0x2014:  # —
                    safe_chars.append('-')
                elif char_code == 0x201c:  # "
                    safe_chars.append('"')
                elif char_code == 0x201d:  # "
                    safe_chars.append('"')
                elif char_code == 0x2018:  # '
                    safe_chars.append("'")
                elif char_code == 0x2019:  # '
                    safe_chars.append("'")
                elif char_code == 0x2022:  # •
                    safe_chars.append('*')
                elif char_code == 0x00b7:  # ·
                    safe_chars.append('*')
                elif char_code == 0x2192:  # →
                    safe_chars.append('->')
                elif char_code == 0x2190:  # ←
                    safe_chars.append('<-')
                elif char_code == 0x00d7:  # ×
                    safe_chars.append('x')
                elif char_code == 0x00f7:  # ÷
                    safe_chars.append('/')
                else:
                    # 모든 기타 비-CP949 문자는 공백으로 교체 (? 대신)
                    safe_chars.append(' ')
                    
                replaced_count += 1
        
        result = ''.join(safe_chars)
        
        # 3단계: 연속된 공백을 하나로 줄이기
        result = re.sub(r'\s+', ' ', result)
        
        # 4단계: 최종 CP949 검증
        try:
            result.encode('cp949')
            if replaced_count > 0:
                print(f"[CP949_CLEAN] Replaced {replaced_count} problematic Unicode characters")
            return result.strip()
        except UnicodeEncodeError as e:
            # 매우 극단적인 경우 - ASCII만 남기기
            print(f"[CP949_CLEAN] Critical error, applying ASCII-only fallback: {e}")
            final_result = ''.join(c if ord(c) < 128 else ' ' for c in result)
            final_result = re.sub(r'\s+', ' ', final_result)
            return final_result.strip()
    
    def _ensure_cp949_compatibility(self, content: Dict) -> Dict:
        """Windows CP949 호환성을 위한 최종 Unicode 안전성 검사"""
        print("[CP949_CHECK] Starting final Unicode compatibility check...")
        
        def sanitize_text(text):
            """개별 텍스트 문자열의 CP949 호환성 보장"""
            if not isinstance(text, str):
                return text
            
            import re
            print(f"[CP949_DEBUG] Processing: {text[:100]}...")
            
            # 1단계: 개별 문자별로 CP949 호환성 검사 및 제거
            safe_chars = []
            replaced_chars = []
            for char in text:
                try:
                    char.encode('cp949')
                    safe_chars.append(char)
                except UnicodeEncodeError:
                    # CP949로 인코딩할 수 없는 문자는 제거하거나 대체
                    char_code = ord(char)
                    replacement = f'[{char_code}]'  # 기본값
                    replaced_chars.append(f"{char}(U+{char_code:04X})")
                    
                    if char_code == 0x26A0:  # ⚠
                        replacement = '[주의]'
                    elif char_code == 0x2705:  # ✅
                        replacement = '[성공]'
                    elif char_code == 0x274C:  # ❌
                        replacement = '[실패]'
                    elif char_code == 0x1F4CC:  # 📌
                        replacement = '[핀]'
                    elif char_code == 0x1F4CA:  # 📊
                        replacement = '[리포트]'
                    elif char_code == 0x1F3AF:  # 🎯
                        replacement = '[타겟]'
                    elif char_code == 0x1F4DD:  # 📝
                        replacement = '[작성]'
                    elif char_code == 0x1F50C:  # 🔌
                        replacement = '[연결]'
                    elif char_code == 0x1F4C5:  # 📅
                        replacement = '[일정]'
                    elif char_code == 0x1F4CB:  # 📋
                        replacement = '[목록]'
                    elif 0x1F600 <= char_code <= 0x1F64F:  # 이모티콘 범위
                        replacement = '[이모지]'
                    elif 0x1F300 <= char_code <= 0x1F5FF:  # 기호 및 그림문자
                        replacement = '[기호]'
                    elif 0x1F680 <= char_code <= 0x1F6FF:  # 교통 및 지도 기호
                        replacement = '[기호]'
                    elif 0x2600 <= char_code <= 0x26FF:  # 기타 기호
                        replacement = '[기호]'
                    # 기타 모든 문제 문자들은 제거
                    else:
                        replacement = ''
                    
                    safe_chars.append(replacement)
            
            result = ''.join(safe_chars)
            
            # 디버깅: 변경된 문자들 출력
            if replaced_chars:
                print(f"[CP949_DEBUG] Replaced chars: {replaced_chars}")
                print(f"[CP949_DEBUG] Original: {text[:100]}...")
                print(f"[CP949_DEBUG] Result: {result[:100]}...")
            
            # 2단계: 최종 CP949 검증
            try:
                result.encode('cp949')
                return result
            except UnicodeEncodeError:
                # 여전히 문제가 있으면 강제로 안전하게 변환
                final_safe = result.encode('cp949', errors='ignore').decode('cp949')
                print(f"[CP949_DEBUG] Final fallback applied: {text[:30]}... -> {final_safe[:30]}...")
                return final_safe
        
        def sanitize_content_recursive(obj):
            """재귀적으로 모든 문자열 콘텐츠 정리"""
            if isinstance(obj, dict):
                return {key: sanitize_content_recursive(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_content_recursive(item) for item in obj]
            elif isinstance(obj, str):
                return sanitize_text(obj)
            else:
                return obj
        
        try:
            sanitized_content = sanitize_content_recursive(content)
            print("[CP949_CHECK] Content sanitization completed successfully.")
            return sanitized_content
        except Exception as e:
            print(f"[CP949_CHECK] Error during sanitization: {e}")
            # 에러 발생 시 원본 반환
            return content