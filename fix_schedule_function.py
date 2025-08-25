#!/usr/bin/env python3
"""
get_today_topic_for_manual 함수를 완전히 계획표 기반으로 교체
"""

new_function = '''    def get_today_topic_for_manual(self, site: str) -> Dict:
        """계획표 주제만 사용 (수동발행용)"""
        try:
            today = datetime.now().date()
            weekday = today.weekday()  # 0=월요일, 6=일요일
            
            # 계획표 주제 정의
            schedule_plan = {
                0: {  # 월요일
                    'unpre': {"topic": "Redis 캐싱 전략과 성능 튜닝", "category": "프로그래밍"},
                    'untab': {"topic": "리츠(REITs) 투자의 장단점", "category": "취미"}, 
                    'skewese': {"topic": "한글의 과학적 원리와 우수성", "category": "뷰티/패션"},
                    'tistory': {"topic": "재건축 규제 완화, 시장 변화 예상", "category": "일반"}
                },
                1: {  # 화요일
                    'unpre': {"topic": "Docker 컨테이너 운영 실무", "category": "프로그래밍"},
                    'untab': {"topic": "친환경 부동산 그린 리모델링 트렌드", "category": "투자"}, 
                    'skewese': {"topic": "4.19혁명과 민주주의 발전", "category": "역사"},
                    'tistory': {"topic": "2025년 ChatGPT-5와 차세대 AI 혁신", "category": "기술"}
                },
                2: {  # 수요일  
                    'unpre': {"topic": "React Hook 고급 활용법", "category": "프로그래밍"},
                    'untab': {"topic": "고령화 사회와 실버타운 투자", "category": "투자"},
                    'skewese': {"topic": "임진왜란과 이순신의 활약", "category": "역사"}, 
                    'tistory': {"topic": "MZ세대 투자 패턴 분석, 부작용은?", "category": "투자"}
                },
                3: {  # 목요일
                    'unpre': {"topic": "Python 데이터 분석 마스터", "category": "프로그래밍"},
                    'untab': {"topic": "인플레이션 시대의 투자 가이드", "category": "투자"},
                    'skewese': {"topic": "한국 전통 건축의 아름다움과 과학", "category": "역사"},
                    'tistory': {"topic": "인플레이션 재부상? 2025년 전망", "category": "경제"}
                },
                4: {  # 금요일
                    'unpre': {"topic": "TypeScript 고급 타입 시스템", "category": "프로그래밍"},
                    'untab': {"topic": "공모주 투자 전략 분석", "category": "투자"},
                    'skewese': {"topic": "정조의 개혁 정치와 화성 건설", "category": "역사"},
                    'tistory': {"topic": "2026 월드컵 공동개최, 한국 축구 재도약", "category": "스포츠"}
                },
                5: {  # 토요일
                    'unpre': {"topic": "GraphQL API 설계와 최적화", "category": "프로그래밍"},
                    'untab': {"topic": "메타버스 부동산 투자", "category": "투자"},
                    'skewese': {"topic": "고구려의 영토 확장과 광개토대왕", "category": "역사"},
                    'tistory': {"topic": "K-문화 글로벌 확산 현황", "category": "문화"}
                },
                6: {  # 일요일
                    'unpre': {"topic": "Kubernetes 클러스터 관리", "category": "프로그래밍"},
                    'untab': {"topic": "ESG 투자의 미래 전망", "category": "투자"},
                    'skewese': {"topic": "조선 후기 실학사상의 발전", "category": "역사"},
                    'tistory': {"topic": "전기차 배터리 기술 혁신과 미래", "category": "기술"}
                }
            }
            
            if weekday in schedule_plan and site in schedule_plan[weekday]:
                topic_data = schedule_plan[weekday][site]
                print(f"[SCHEDULE] {site} 계획표 주제: {topic_data['topic']}")
                return {
                    'topic': topic_data['topic'],
                    'category': topic_data['category'],
                    'keywords': [],
                    'length': 'medium'
                }
            
            print(f"[SCHEDULE] {site} 계획표에 해당 요일 주제 없음")
            return None
                    
        except Exception as e:
            print(f"[SCHEDULE] 계획표 주제 조회 오류: {e}")
            return None'''

# 함수 시작 라인과 끝 라인 찾기
with open('/Users/down/Dev/D/auto/blog-automation/src/utils/schedule_manager.py', 'r') as f:
    lines = f.readlines()

# 함수 시작과 끝 찾기
start_line = None
end_line = None

for i, line in enumerate(lines):
    if 'def get_today_topic_for_manual(self, site: str) -> Dict:' in line:
        start_line = i
        break

if start_line is not None:
    # 함수 끝 찾기 (들여쓰기가 같은 레벨의 다음 함수 또는 클래스까지)
    indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
    
    for i in range(start_line + 1, len(lines)):
        current_line = lines[i].strip()
        if current_line and not current_line.startswith('#'):
            current_indent = len(lines[i]) - len(lines[i].lstrip())
            if current_indent <= indent_level:
                end_line = i
                break
    
    if end_line is None:
        end_line = len(lines)

print(f"함수 위치: {start_line + 1}행 ~ {end_line}행")
print(f"교체할 라인 수: {end_line - start_line}")