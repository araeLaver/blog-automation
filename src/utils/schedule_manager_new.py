    def get_today_topic_for_manual(self, site: str) -> Dict:
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
                    'unpre': {"topic": "JWT 토큰 기반 시큐리티 구현", "category": "프로그래밍"},
                    'untab': {"topic": "친환경 부동산 그린 리모델링 트렌드", "category": "취미"}, 
                    'skewese': {"topic": "임진왜란과 이순신의 활약", "category": "뷰티/패션"},
                    'tistory': {"topic": "MZ세대 투자 패턴 분석, 부작용은?", "category": "일반"}
                },
                2: {  # 수요일  
                    'unpre': {"topic": "React Hook 고급 활용법", "category": "프로그래밍"},
                    'untab': {"topic": "고령화 사회와 실버타운 투자", "category": "투자"},
                    'skewese': {"topic": "조선시대 과거제도와 교육", "category": "역사"}, 
                    'tistory': {"topic": "전기차 시장 현황과 미래 전망", "category": "기술"}
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
            return None