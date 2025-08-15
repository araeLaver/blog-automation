"""
AI 기반 콘텐츠 생성 모듈
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import anthropic
from dotenv import load_dotenv

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
                        category: str, existing_posts: List[str] = None, content_length: str = 'medium') -> Dict:
        """메인 콘텐츠 생성 함수"""
        
        # 프롬프트 생성
        prompt = self._create_prompt(site_config, topic, category, existing_posts, content_length)
        
        # Claude API로 콘텐츠 생성
        content = self._generate_with_claude(prompt)
        
        # 콘텐츠 파싱 및 구조화
        structured_content = self._parse_content(content)
        
        # SEO 최적화
        optimized_content = self._optimize_for_seo(structured_content, site_config)
        
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
        
        # 섹션 템플릿 생성
        sections_template = []
        for i in range(settings['sections']):
            sections_template.append(f'''        {{
            "heading": "{i+1}번째 핵심 내용의 제목",
            "content": "{settings['section_length']}의 설명. 반드시 다음 형식을 포함하세요:\\n\\n- 문단 나누기: 2-3줄마다 줄바꿈\\n- 구분선: ---를 사용해서 하위 주제 구분\\n- 표 활용: 비교나 정리가 필요한 부분은 HTML 표로 작성\\n- 목록: 중요 포인트는 - 기호로 목록화\\n- 강조: **굵은 글씨**로 핵심 키워드 강조\\n\\n실용적인 정보와 예시를 포함하되, 읽기 쉽게 포맷팅하세요."
        }}''')
        
        sections_json = ',\n'.join(sections_template)
        
        prompt = f"""🎯 전문가급 블로그 콘텐츠 작성 미션 🎯

📝 **작성 주제**: {topic}
🏢 **블로그**: {site_config['name']}
👥 **타겟 독자**: {site_config['target_audience']}
📊 **카테고리**: {category}
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
    "conclusion": "핵심 내용 요약과 독자에게 도움이 되는 마무리 ({settings['conclusion_length']})",
    "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"],
    "keywords": ["키워드1", "키워드2", "키워드3"]
}}

🎯 **가독성 향상 필수 요구사항**:
- 위 JSON 형식 외에는 아무것도 출력하지 마세요
- 모든 내용은 한국어로 작성하세요
- 각 섹션은 {settings['section_length']}로 충분히 상세하게 작성하세요

📋 **컨텐츠 포맷팅 규칙**:
1. **문단 구분**: 2-3문장마다 \\n\\n로 줄바꿈
2. **섹션 구분**: 하위 주제 사이에 --- 구분선 사용
3. **표 활용**: 비교/정리 필요시 HTML 테이블 사용
   예: <table><tr><th>항목</th><th>설명</th></tr><tr><td>내용1</td><td>설명1</td></tr></table>
4. **목록화**: 중요 포인트는 - 또는 1. 2. 3. 형태로 목록
5. **강조**: **굵은 글씨**로 핵심 키워드 강조
6. **코드**: 필요시 ```언어\\n코드\\n``` 형태로 작성
"""
        
        if existing_posts:
            prompt += f"\n\n[최근 발행 포스트 (중복 방지)]\n"
            for post in existing_posts[:5]:
                prompt += f"- {post}\n"
        
        return prompt
    
    def _generate_with_claude(self, prompt: str) -> str:
        """Claude API로 콘텐츠 생성"""
        try:
            # 시스템 메시지 - 고품질 콘텐츠 생성을 위한 상세 가이드
            system_message = """🚀 당신은 전문 블로그 콘텐츠 크리에이터입니다 🚀

**핵심 미션**: 독자가 실제로 도움받을 수 있는 고품질, 실용적인 한국어 블로그 콘텐츠 생성

**콘텐츠 품질 기준 (매우 중요!):**

📚 **전문성**: 
- 해당 분야의 전문가 수준의 깊이 있는 내용
- 최신 트렌드와 실무 경험이 반영된 인사이트
- 단순한 정보 나열이 아닌 실용적 가이드

💡 **실용성**:
- 독자가 바로 적용할 수 있는 구체적인 방법론
- 단계별 실행 가이드 제공
- 실제 사례와 예시를 풍부하게 포함

🎯 **가독성**:
- 명확한 구조와 논리적 흐름
- 적절한 소제목과 문단 구분
- 핵심 포인트는 굵게 강조

**절대적 요구사항:**
✅ 오직 유효한 JSON 형식으로만 응답
✅ 모든 내용은 한국어로 작성
✅ 각 섹션당 최소 300-500자의 상세한 내용
✅ 실제 도움이 되는 구체적 정보 포함
✅ 전문적이면서도 이해하기 쉬운 설명

❌ 절대 하지 말 것:
❌ JSON 외의 다른 텍스트 출력 금지
❌ 피상적이거나 일반적인 내용 금지
❌ 단순 번역체나 어색한 문장 금지
❌ 빈약한 내용이나 짧은 설명 금지"""
            
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
                print(f"Retry Response starts with: {result[:100]}...")
            
            return result
        except Exception as e:
            print(f"Claude API 오류: {e}")
            raise
    
    def _parse_content(self, content: str) -> Dict:
        """생성된 콘텐츠 파싱"""
        try:
            print(f"Parsing content: {content[:500]}...")
            
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
            
            parsed_content = json.loads(content)
            print(f"Successfully parsed JSON: {list(parsed_content.keys())}")
            
            # 콘텐츠 검증
            return self._validate_content(parsed_content)
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            print(f"파싱 시도한 내용: {content[:500]}...")
            # JSON 파싱 실패시 기본 구조로 변환
            return self._fallback_parse(original_content)
    
    def _validate_content(self, content: Dict) -> Dict:
        """생성된 콘텐츠 검증 및 필터링"""
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
                "heading": "마무리",
                "content": "배운 내용을 정리하고 다음 단계로 나아가는 방법을 제시합니다. 지속적인 학습과 개선의 중요성을 강조합니다."
            }
        ]
        
        return {
            "title": title,
            "meta_description": "실용적인 개발 기술과 베스트 프랙티스를 다루는 가이드입니다.",
            "introduction": introduction,
            "sections": sections,
            "conclusion": "이상으로 핵심 내용을 알아보았습니다. 지속적인 학습과 실전 적용을 통해 더 나은 개발자가 되시길 바랍니다.",
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