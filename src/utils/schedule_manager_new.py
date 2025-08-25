    def get_today_topic_for_manual(self, site: str) -> Dict:
        """데이터베이스에서 오늘의 발행 계획표 주제 가져오기"""
        try:
            today = datetime.now().date()
            weekday = today.weekday()  # 0=월요일, 6=일요일
            
            # 이번주 월요일 날짜 계산 (week_start_date)
            week_start = today - timedelta(days=weekday)
            
            print(f"[SCHEDULE] {site} - 오늘: {today} ({weekday}요일), 주시작: {week_start}")
            
            # DB에서 해당 주, 요일, 사이트의 스케줄 조회
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT specific_topic, topic_category, keywords, target_length
                    FROM publishing_schedule 
                    WHERE week_start_date = %s 
                    AND day_of_week = %s 
                    AND site = %s
                    AND status = 'planned'
                    ORDER BY id DESC
                    LIMIT 1
                """, (week_start, weekday, site))
                
                result = cursor.fetchone()
                
            if result:
                topic, category, keywords_array, length = result
                
                # keywords가 배열로 저장되어 있으면 처리
                if keywords_array and len(keywords_array) > 0:
                    keywords = keywords_array
                else:
                    keywords = []
                
                print(f"[SCHEDULE] {site} DB에서 가져온 주제: {topic} ({category})")
                
                return {
                    'topic': topic,
                    'category': category, 
                    'keywords': keywords,
                    'length': length or 'medium'
                }
            else:
                print(f"[SCHEDULE] {site} DB에 해당 날짜의 계획표 주제 없음 (주시작: {week_start}, 요일: {weekday})")
                
                # DB에 데이터가 없으면 폴백 로직
                return self._get_fallback_topic(site)
                    
        except Exception as e:
            print(f"[SCHEDULE] {site} 계획표 주제 조회 오류: {e}")
            # 오류 시 폴백 로직
            return self._get_fallback_topic(site)
    
    def _get_fallback_topic(self, site: str) -> Dict:
        """DB 조회 실패시 폴백 주제 반환"""
        fallback_topics = {
            'unpre': {"topic": "개발자를 위한 최신 기술 트렌드", "category": "프로그래밍"},
            'untab': {"topic": "부동산 투자 시장 분석", "category": "투자"},
            'skewese': {"topic": "한국사의 중요한 사건들", "category": "역사"},
            'tistory': {"topic": "최신 IT 기술 동향", "category": "기술"}
        }
        
        topic_data = fallback_topics.get(site, fallback_topics['tistory'])
        print(f"[SCHEDULE] {site} 폴백 주제 사용: {topic_data['topic']}")
        
        return {
            'topic': topic_data['topic'],
            'category': topic_data['category'],
            'keywords': [],
            'length': 'medium'
        }