-- 2025년 9월 발행 계획표
-- 생성일시: 2025-08-25T20:24:49.648828
-- 총 240개 포스팅 (일 8개 x 30일)

INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 0, 'unpre', '기술/디지털', 
'ChatGPT API 활용 실전 가이드', ARRAY['ChatGPT', 'API', '활용'], 'medium', 'planned', '2025-09-01')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 0, 'unpre', '교육/자기계발', 
'토익 900점 3개월 완성 로드맵', ARRAY['토익', '900점', '3개월'], 'medium', 'planned', '2025-09-01')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 0, 'untab', '재정/투자', 
'2025년 주목할 성장주 TOP 10', ARRAY['2025년', '주목할', '성장주'], 'medium', 'planned', '2025-09-01')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 0, 'untab', '라이프스타일', 
'제주도 한달살기 완벽 가이드', ARRAY['제주도', '한달살기', '완벽'], 'medium', 'planned', '2025-09-01')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 0, 'skewese', '건강/웰니스', 
'간헐적 단식 16:8 완벽 가이드', ARRAY['간헐적', '단식', '16:8'], 'medium', 'planned', '2025-09-01')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 0, 'skewese', '역사/문화', 
'조선시대 왕들의 일상생활', ARRAY['조선시대', '왕들의', '일상생활'], 'medium', 'planned', '2025-09-01')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 0, 'tistory', '엔터테인먼트', 
'2025년 기대작 K-드라마 라인업', ARRAY['2025년', '기대작', 'K-드라마'], 'medium', 'planned', '2025-09-01')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 0, 'tistory', '트렌드/이슈', 
'MZ세대 소비 트렌드 2025', ARRAY['MZ세대', '소비', '트렌드'], 'medium', 'planned', '2025-09-01')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 1, 'unpre', '기술/디지털', 
'Python 웹 크롤링 마스터하기', ARRAY['Python', '웹', '크롤링'], 'medium', 'planned', '2025-09-02')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 1, 'unpre', '교육/자기계발', 
'개발자 이력서 작성 완벽 가이드', ARRAY['개발자', '이력서', '작성'], 'medium', 'planned', '2025-09-02')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 1, 'untab', '재정/투자', 
'월 100만원 배당금 포트폴리오', ARRAY['월', '100만원', '배당금'], 'medium', 'planned', '2025-09-02')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 1, 'untab', '라이프스타일', 
'원룸 인테리어 10만원으로 변신', ARRAY['원룸', '인테리어', '10만원으로'], 'medium', 'planned', '2025-09-02')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 1, 'skewese', '건강/웰니스', 
'피부 타입별 스킨케어 루틴', ARRAY['피부', '타입별', '스킨케어'], 'medium', 'planned', '2025-09-02')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 1, 'skewese', '역사/문화', 
'한국 전쟁 숨겨진 이야기', ARRAY['한국', '전쟁', '숨겨진'], 'medium', 'planned', '2025-09-02')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 1, 'tistory', '엔터테인먼트', 
'넷플릭스 숨은 명작 추천', ARRAY['넷플릭스', '숨은', '명작'], 'medium', 'planned', '2025-09-02')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 1, 'tistory', '트렌드/이슈', 
'AI가 바꾸는 일상생활', ARRAY['AI가', '바꾸는', '일상생활'], 'medium', 'planned', '2025-09-02')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 2, 'unpre', '기술/디지털', 
'React 18 새로운 기능 완벽 정리', ARRAY['React', '18', '새로운'], 'medium', 'planned', '2025-09-03')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 2, 'unpre', '교육/자기계발', 
'코딩테스트 빈출 알고리즘 정리', ARRAY['코딩테스트', '빈출', '알고리즘'], 'medium', 'planned', '2025-09-03')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 2, 'untab', '재정/투자', 
'부동산 경매 초보자 가이드', ARRAY['부동산', '경매', '초보자'], 'medium', 'planned', '2025-09-03')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 2, 'untab', '라이프스타일', 
'에어프라이어 만능 레시피 30선', ARRAY['에어프라이어', '만능', '레시피'], 'medium', 'planned', '2025-09-03')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 2, 'skewese', '건강/웰니스', 
'홈트레이닝 4주 프로그램', ARRAY['홈트레이닝', '4주', '프로그램'], 'medium', 'planned', '2025-09-03')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 2, 'skewese', '역사/문화', 
'세종대왕의 리더십 분석', ARRAY['세종대왕의', '리더십', '분석'], 'medium', 'planned', '2025-09-03')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 2, 'tistory', '엔터테인먼트', 
'아이돌 서바이벌 프로그램 정리', ARRAY['아이돌', '서바이벌', '프로그램'], 'medium', 'planned', '2025-09-03')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 2, 'tistory', '트렌드/이슈', 
'친환경 라이프스타일 실천법', ARRAY['친환경', '라이프스타일', '실천법'], 'medium', 'planned', '2025-09-03')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 3, 'unpre', '기술/디지털', 
'VS Code 생산성 200% 높이는 익스텐션', ARRAY['VS', 'Code', '생산성'], 'medium', 'planned', '2025-09-04')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 3, 'unpre', '교육/자기계발', 
'JLPT N2 한 번에 합격하기', ARRAY['JLPT', 'N2', '한'], 'medium', 'planned', '2025-09-04')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 3, 'untab', '재정/투자', 
'비트코인 ETF 투자 전략', ARRAY['비트코인', 'ETF', '투자'], 'medium', 'planned', '2025-09-04')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 3, 'untab', '라이프스타일', 
'유럽 배낭여행 2주 코스', ARRAY['유럽', '배낭여행', '2주'], 'medium', 'planned', '2025-09-04')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 3, 'skewese', '건강/웰니스', 
'단백질 보충제 선택 가이드', ARRAY['단백질', '보충제', '선택'], 'medium', 'planned', '2025-09-04')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 3, 'skewese', '역사/문화', 
'임진왜란 7년 전쟁 연대기', ARRAY['임진왜란', '7년', '전쟁'], 'medium', 'planned', '2025-09-04')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 3, 'tistory', '엔터테인먼트', 
'웹툰 원작 드라마 성공 비결', ARRAY['웹툰', '원작', '드라마'], 'medium', 'planned', '2025-09-04')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 3, 'tistory', '트렌드/이슈', 
'메타버스 플랫폼 비교', ARRAY['메타버스', '플랫폼', '비교'], 'medium', 'planned', '2025-09-04')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 4, 'unpre', '기술/디지털', 
'Docker로 개발환경 통일하기', ARRAY['Docker로', '개발환경', '통일하기'], 'medium', 'planned', '2025-09-05')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 4, 'unpre', '교육/자기계발', 
'기술 면접 단골 질문 100선', ARRAY['기술', '면접', '단골'], 'medium', 'planned', '2025-09-05')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 4, 'untab', '재정/투자', 
'ISA 계좌 200% 활용법', ARRAY['ISA', '계좌', '200%'], 'medium', 'planned', '2025-09-05')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 4, 'untab', '라이프스타일', 
'미니멀 라이프 시작하기', ARRAY['미니멀', '라이프', '시작하기'], 'medium', 'planned', '2025-09-05')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 4, 'skewese', '건강/웰니스', 
'수면의 질 높이는 10가지 방법', ARRAY['수면의', '질', '높이는'], 'medium', 'planned', '2025-09-05')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 4, 'skewese', '역사/문화', 
'고구려 광개토대왕 정복사', ARRAY['고구려', '광개토대왕', '정복사'], 'medium', 'planned', '2025-09-05')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 4, 'tistory', '엔터테인먼트', 
'K-POP 4세대 그룹 분석', ARRAY['K-POP', '4세대', '그룹'], 'medium', 'planned', '2025-09-05')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 4, 'tistory', '트렌드/이슈', 
'Z세대 신조어 사전', ARRAY['Z세대', '신조어', '사전'], 'medium', 'planned', '2025-09-05')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 5, 'unpre', '기술/디지털', 
'Git 브랜치 전략 실무 가이드', ARRAY['Git', '브랜치', '전략'], 'medium', 'planned', '2025-09-06')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 5, 'unpre', '교육/자기계발', 
'영어 회화 스피킹 연습법', ARRAY['영어', '회화', '스피킹'], 'medium', 'planned', '2025-09-06')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 5, 'untab', '재정/투자', 
'미국 주식 세금 절약 팁', ARRAY['미국', '주식', '세금'], 'medium', 'planned', '2025-09-06')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 5, 'untab', '라이프스타일', 
'홈카페 분위기 만들기', ARRAY['홈카페', '분위기', '만들기'], 'medium', 'planned', '2025-09-06')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 5, 'skewese', '건강/웰니스', 
'글루텐프리 다이어트 효과', ARRAY['글루텐프리', '다이어트', '효과'], 'medium', 'planned', '2025-09-06')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 5, 'skewese', '역사/문화', 
'신라 화랑도 정신과 문화', ARRAY['신라', '화랑도', '정신과'], 'medium', 'planned', '2025-09-06')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 5, 'tistory', '엔터테인먼트', 
'OTT 플랫폼별 특징 비교', ARRAY['OTT', '플랫폼별', '특징'], 'medium', 'planned', '2025-09-06')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 5, 'tistory', '트렌드/이슈', 
'리셀 시장 인기 아이템', ARRAY['리셀', '시장', '인기'], 'medium', 'planned', '2025-09-06')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 6, 'unpre', '기술/디지털', 
'AWS Lambda 서버리스 입문', ARRAY['AWS', 'Lambda', '서버리스'], 'medium', 'planned', '2025-09-07')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 6, 'unpre', '교육/자기계발', 
'개발자 포트폴리오 만들기', ARRAY['개발자', '포트폴리오', '만들기'], 'medium', 'planned', '2025-09-07')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 6, 'untab', '재정/투자', 
'리츠(REITs) 투자 완벽 가이드', ARRAY['리츠(REITs)', '투자', '완벽'], 'medium', 'planned', '2025-09-07')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 6, 'untab', '라이프스타일', 
'캠핑 초보자 장비 리스트', ARRAY['캠핑', '초보자', '장비'], 'medium', 'planned', '2025-09-07')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 6, 'skewese', '건강/웰니스', 
'요가 초보자 기본 자세', ARRAY['요가', '초보자', '기본'], 'medium', 'planned', '2025-09-07')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 6, 'skewese', '역사/문화', 
'백제 문화재의 아름다움', ARRAY['백제', '문화재의', '아름다움'], 'medium', 'planned', '2025-09-07')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 6, 'tistory', '엔터테인먼트', 
'한국 영화 역대 흥행 TOP 20', ARRAY['한국', '영화', '역대'], 'medium', 'planned', '2025-09-07')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-01', 6, 'tistory', '트렌드/이슈', 
'숏폼 콘텐츠 제작 팁', ARRAY['숏폼', '콘텐츠', '제작'], 'medium', 'planned', '2025-09-07')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 0, 'unpre', '기술/디지털', 
'TypeScript 타입 시스템 완벽 이해', ARRAY['TypeScript', '타입', '시스템'], 'medium', 'planned', '2025-09-08')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 0, 'unpre', '교육/자기계발', 
'효과적인 코드 리뷰 방법', ARRAY['효과적인', '코드', '리뷰'], 'medium', 'planned', '2025-09-08')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 0, 'untab', '재정/투자', 
'금 투자 vs 달러 투자 비교', ARRAY['금', '투자', 'vs'], 'medium', 'planned', '2025-09-08')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 0, 'untab', '라이프스타일', 
'반려식물 키우기 입문', ARRAY['반려식물', '키우기', '입문'], 'medium', 'planned', '2025-09-08')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 0, 'skewese', '건강/웰니스', 
'비타민 D 부족 증상과 해결법', ARRAY['비타민', 'D', '부족'], 'medium', 'planned', '2025-09-08')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 0, 'skewese', '역사/문화', 
'일제강점기 독립운동가들', ARRAY['일제강점기', '독립운동가들'], 'medium', 'planned', '2025-09-08')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 0, 'tistory', '엔터테인먼트', 
'예능 프로그램 시청률 분석', ARRAY['예능', '프로그램', '시청률'], 'medium', 'planned', '2025-09-08')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 0, 'tistory', '트렌드/이슈', 
'NFT 아트 투자 가이드', ARRAY['NFT', '아트', '투자'], 'medium', 'planned', '2025-09-08')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 1, 'unpre', '기술/디지털', 
'Next.js 14 App Router 실전', ARRAY['Next.js', '14', 'App'], 'medium', 'planned', '2025-09-09')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 1, 'unpre', '교육/자기계발', 
'토익 스피킹 레벨7 공략법', ARRAY['토익', '스피킹', '레벨7'], 'medium', 'planned', '2025-09-09')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 1, 'untab', '재정/투자', 
'P2P 투자 리스크 관리법', ARRAY['P2P', '투자', '리스크'], 'medium', 'planned', '2025-09-09')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 1, 'untab', '라이프스타일', 
'혼밥 맛집 전국 지도', ARRAY['혼밥', '맛집', '전국'], 'medium', 'planned', '2025-09-09')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 1, 'skewese', '건강/웰니스', 
'MBTI별 운동법 추천', ARRAY['MBTI별', '운동법', '추천'], 'medium', 'planned', '2025-09-09')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 1, 'skewese', '역사/문화', 
'한국 전통 건축의 과학', ARRAY['한국', '전통', '건축의'], 'medium', 'planned', '2025-09-09')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 1, 'tistory', '엔터테인먼트', 
'인기 유튜버 콘텐츠 전략', ARRAY['인기', '유튜버', '콘텐츠'], 'medium', 'planned', '2025-09-09')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 1, 'tistory', '트렌드/이슈', 
'온라인 커뮤니티 문화', ARRAY['온라인', '커뮤니티', '문화'], 'medium', 'planned', '2025-09-09')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 2, 'unpre', '기술/디지털', 
'PostgreSQL vs MySQL 성능 비교', ARRAY['PostgreSQL', 'vs', 'MySQL'], 'medium', 'planned', '2025-09-10')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 2, 'unpre', '교육/자기계발', 
'일본어 한자 효율적으로 외우기', ARRAY['일본어', '한자', '효율적으로'], 'medium', 'planned', '2025-09-10')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 2, 'untab', '재정/투자', 
'연금저축펀드 선택 가이드', ARRAY['연금저축펀드', '선택', '가이드'], 'medium', 'planned', '2025-09-10')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 2, 'untab', '라이프스타일', 
'북유럽 스타일 홈 데코', ARRAY['북유럽', '스타일', '홈'], 'medium', 'planned', '2025-09-10')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 2, 'skewese', '건강/웰니스', 
'저탄고지 식단 일주일 메뉴', ARRAY['저탄고지', '식단', '일주일'], 'medium', 'planned', '2025-09-10')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 2, 'skewese', '역사/문화', 
'조선 후기 실학자들', ARRAY['조선', '후기', '실학자들'], 'medium', 'planned', '2025-09-10')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 2, 'tistory', '엔터테인먼트', 
'게임 스트리머 수익 구조', ARRAY['게임', '스트리머', '수익'], 'medium', 'planned', '2025-09-10')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 2, 'tistory', '트렌드/이슈', 
'틱톡 챌린지 모음', ARRAY['틱톡', '챌린지', '모음'], 'medium', 'planned', '2025-09-10')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 3, 'unpre', '기술/디지털', 
'Redis 캐싱 전략 구현하기', ARRAY['Redis', '캐싱', '전략'], 'medium', 'planned', '2025-09-11')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 3, 'unpre', '교육/자기계발', 
'개발자 연봉 협상 전략', ARRAY['개발자', '연봉', '협상'], 'medium', 'planned', '2025-09-11')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 3, 'untab', '재정/투자', 
'해외 부동산 투자 입문', ARRAY['해외', '부동산', '투자'], 'medium', 'planned', '2025-09-11')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 3, 'untab', '라이프스타일', 
'일본 료칸 여행 추천', ARRAY['일본', '료칸', '여행'], 'medium', 'planned', '2025-09-11')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 3, 'skewese', '건강/웰니스', 
'필라테스 vs 요가 비교', ARRAY['필라테스', 'vs', '요가'], 'medium', 'planned', '2025-09-11')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 3, 'skewese', '역사/문화', 
'궁궐 건축물의 숨은 의미', ARRAY['궁궐', '건축물의', '숨은'], 'medium', 'planned', '2025-09-11')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 3, 'tistory', '엔터테인먼트', 
'디즈니플러스 추천작', ARRAY['디즈니플러스', '추천작'], 'medium', 'planned', '2025-09-11')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 3, 'tistory', '트렌드/이슈', 
'ESG 경영 우수 기업', ARRAY['ESG', '경영', '우수'], 'medium', 'planned', '2025-09-11')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 4, 'unpre', '기술/디지털', 
'GraphQL API 설계 베스트 프랙티스', ARRAY['GraphQL', 'API', '설계'], 'medium', 'planned', '2025-09-12')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 4, 'unpre', '교육/자기계발', 
'온라인 강의 플랫폼 비교', ARRAY['온라인', '강의', '플랫폼'], 'medium', 'planned', '2025-09-12')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 4, 'untab', '재정/투자', 
'공모주 청약 전략', ARRAY['공모주', '청약', '전략'], 'medium', 'planned', '2025-09-12')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 4, 'untab', '라이프스타일', 
'와인 입문자 가이드', ARRAY['와인', '입문자', '가이드'], 'medium', 'planned', '2025-09-12')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 4, 'skewese', '건강/웰니스', 
'콜라겐 영양제 효과 분석', ARRAY['콜라겐', '영양제', '효과'], 'medium', 'planned', '2025-09-12')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 4, 'skewese', '역사/문화', 
'한국 전통 음식의 역사', ARRAY['한국', '전통', '음식의'], 'medium', 'planned', '2025-09-12')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 4, 'tistory', '엔터테인먼트', 
'음원차트 역주행 곡들', ARRAY['음원차트', '역주행', '곡들'], 'medium', 'planned', '2025-09-12')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 4, 'tistory', '트렌드/이슈', 
'구독 경제 서비스 정리', ARRAY['구독', '경제', '서비스'], 'medium', 'planned', '2025-09-12')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 5, 'unpre', '기술/디지털', 
'Kubernetes 입문자 가이드', ARRAY['Kubernetes', '입문자', '가이드'], 'medium', 'planned', '2025-09-13')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 5, 'unpre', '교육/자기계발', 
'시간 관리 앱 추천 TOP 10', ARRAY['시간', '관리', '앱'], 'medium', 'planned', '2025-09-13')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 5, 'untab', '재정/투자', 
'ETF vs 펀드 수익률 비교', ARRAY['ETF', 'vs', '펀드'], 'medium', 'planned', '2025-09-13')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 5, 'untab', '라이프스타일', 
'홈베이킹 필수 도구', ARRAY['홈베이킹', '필수', '도구'], 'medium', 'planned', '2025-09-13')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 5, 'skewese', '건강/웰니스', 
'스트레스 관리 명상법', ARRAY['스트레스', '관리', '명상법'], 'medium', 'planned', '2025-09-13')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 5, 'skewese', '역사/문화', 
'전통 혼례 문화 이야기', ARRAY['전통', '혼례', '문화'], 'medium', 'planned', '2025-09-13')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 5, 'tistory', '엔터테인먼트', 
'배우 필모그래피 분석', ARRAY['배우', '필모그래피', '분석'], 'medium', 'planned', '2025-09-13')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 5, 'tistory', '트렌드/이슈', 
'언택트 서비스 트렌드', ARRAY['언택트', '서비스', '트렌드'], 'medium', 'planned', '2025-09-13')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 6, 'unpre', '기술/디지털', 
'CI/CD 파이프라인 구축하기', ARRAY['CI/CD', '파이프라인', '구축하기'], 'medium', 'planned', '2025-09-14')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 6, 'unpre', '교육/자기계발', 
'노션으로 업무 효율 높이기', ARRAY['노션으로', '업무', '효율'], 'medium', 'planned', '2025-09-14')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 6, 'untab', '재정/투자', 
'부동산 분양권 투자법', ARRAY['부동산', '분양권', '투자법'], 'medium', 'planned', '2025-09-14')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 6, 'untab', '라이프스타일', 
'부산 로컬 맛집 투어', ARRAY['부산', '로컬', '맛집'], 'medium', 'planned', '2025-09-14')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 6, 'skewese', '건강/웰니스', 
'체지방 감량 과학적 방법', ARRAY['체지방', '감량', '과학적'], 'medium', 'planned', '2025-09-14')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 6, 'skewese', '역사/문화', 
'한글 창제 비하인드 스토리', ARRAY['한글', '창제', '비하인드'], 'medium', 'planned', '2025-09-14')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 6, 'tistory', '엔터테인먼트', 
'독립영화 추천 리스트', ARRAY['독립영화', '추천', '리스트'], 'medium', 'planned', '2025-09-14')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-08', 6, 'tistory', '트렌드/이슈', 
'뉴트로 감성 아이템', ARRAY['뉴트로', '감성', '아이템'], 'medium', 'planned', '2025-09-14')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 0, 'unpre', '기술/디지털', 
'마이크로서비스 아키텍처 설계', ARRAY['마이크로서비스', '아키텍처', '설계'], 'medium', 'planned', '2025-09-15')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 0, 'unpre', '교육/자기계발', 
'개발자 커리어 로드맵', ARRAY['개발자', '커리어', '로드맵'], 'medium', 'planned', '2025-09-15')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 0, 'untab', '재정/투자', 
'암호화폐 스테이킹 수익', ARRAY['암호화폐', '스테이킹', '수익'], 'medium', 'planned', '2025-09-15')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 0, 'untab', '라이프스타일', 
'스마트홈 구축 가이드', ARRAY['스마트홈', '구축', '가이드'], 'medium', 'planned', '2025-09-15')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 0, 'skewese', '건강/웰니스', 
'근육량 늘리는 식단', ARRAY['근육량', '늘리는', '식단'], 'medium', 'planned', '2025-09-15')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 0, 'skewese', '역사/문화', 
'고려 청자의 제작 비법', ARRAY['고려', '청자의', '제작'], 'medium', 'planned', '2025-09-15')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 0, 'tistory', '엔터테인먼트', 
'뮤지컬 공연 정보', ARRAY['뮤지컬', '공연', '정보'], 'medium', 'planned', '2025-09-15')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 0, 'tistory', '트렌드/이슈', 
'비건 뷰티 브랜드', ARRAY['비건', '뷰티', '브랜드'], 'medium', 'planned', '2025-09-15')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 1, 'unpre', '기술/디지털', 
'WebSocket 실시간 통신 구현', ARRAY['WebSocket', '실시간', '통신'], 'medium', 'planned', '2025-09-16')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 1, 'unpre', '교육/자기계발', 
'비즈니스 영어 이메일 템플릿', ARRAY['비즈니스', '영어', '이메일'], 'medium', 'planned', '2025-09-16')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 1, 'untab', '재정/투자', 
'채권 투자 기초 지식', ARRAY['채권', '투자', '기초'], 'medium', 'planned', '2025-09-16')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 1, 'untab', '라이프스타일', 
'향수 선택하는 법', ARRAY['향수', '선택하는', '법'], 'medium', 'planned', '2025-09-16')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 1, 'skewese', '건강/웰니스', 
'피부 미백 홈케어 방법', ARRAY['피부', '미백', '홈케어'], 'medium', 'planned', '2025-09-16')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 1, 'skewese', '역사/문화', 
'전통 놀이 문화 탐구', ARRAY['전통', '놀이', '문화'], 'medium', 'planned', '2025-09-16')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 1, 'tistory', '엔터테인먼트', 
'팟캐스트 인기 채널', ARRAY['팟캐스트', '인기', '채널'], 'medium', 'planned', '2025-09-16')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 1, 'tistory', '트렌드/이슈', 
'제로웨이스트 실천법', ARRAY['제로웨이스트', '실천법'], 'medium', 'planned', '2025-09-16')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 2, 'unpre', '기술/디지털', 
'JWT 인증 시스템 만들기', ARRAY['JWT', '인증', '시스템'], 'medium', 'planned', '2025-09-17')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 2, 'unpre', '교육/자기계발', 
'프로그래밍 독학 가이드', ARRAY['프로그래밍', '독학', '가이드'], 'medium', 'planned', '2025-09-17')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 2, 'untab', '재정/투자', 
'원자재 투자 타이밍', ARRAY['원자재', '투자', '타이밍'], 'medium', 'planned', '2025-09-17')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 2, 'untab', '라이프스타일', 
'커피 홈로스팅 입문', ARRAY['커피', '홈로스팅', '입문'], 'medium', 'planned', '2025-09-17')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 2, 'skewese', '건강/웰니스', 
'탈모 예방 두피 관리법', ARRAY['탈모', '예방', '두피'], 'medium', 'planned', '2025-09-17')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 2, 'skewese', '역사/문화', 
'한국 불교 문화재 순례', ARRAY['한국', '불교', '문화재'], 'medium', 'planned', '2025-09-17')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 2, 'tistory', '엔터테인먼트', 
'트위치 vs 유튜브 비교', ARRAY['트위치', 'vs', '유튜브'], 'medium', 'planned', '2025-09-17')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 2, 'tistory', '트렌드/이슈', 
'디지털 노마드 라이프', ARRAY['디지털', '노마드', '라이프'], 'medium', 'planned', '2025-09-17')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 3, 'unpre', '기술/디지털', 
'SEO 최적화 체크리스트', ARRAY['SEO', '최적화', '체크리스트'], 'medium', 'planned', '2025-09-18')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 3, 'unpre', '교육/자기계발', 
'IT 자격증 우선순위 정리', ARRAY['IT', '자격증', '우선순위'], 'medium', 'planned', '2025-09-18')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 3, 'untab', '재정/투자', 
'부업으로 월 300만원 벌기', ARRAY['부업으로', '월', '300만원'], 'medium', 'planned', '2025-09-18')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 3, 'untab', '라이프스타일', 
'전국 글램핑 명소', ARRAY['전국', '글램핑', '명소'], 'medium', 'planned', '2025-09-18')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 3, 'skewese', '건강/웰니스', 
'눈 건강 지키는 습관', ARRAY['눈', '건강', '지키는'], 'medium', 'planned', '2025-09-18')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 3, 'skewese', '역사/문화', 
'조선시대 과거제도 분석', ARRAY['조선시대', '과거제도', '분석'], 'medium', 'planned', '2025-09-18')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 3, 'tistory', '엔터테인먼트', 
'웹드라마 제작 트렌드', ARRAY['웹드라마', '제작', '트렌드'], 'medium', 'planned', '2025-09-18')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 3, 'tistory', '트렌드/이슈', 
'공유경제 서비스 활용', ARRAY['공유경제', '서비스', '활용'], 'medium', 'planned', '2025-09-18')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 4, 'unpre', '기술/디지털', 
'웹 성능 최적화 기법', ARRAY['웹', '성능', '최적화'], 'medium', 'planned', '2025-09-19')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 4, 'unpre', '교육/자기계발', 
'개발자 번아웃 극복법', ARRAY['개발자', '번아웃', '극복법'], 'medium', 'planned', '2025-09-19')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 4, 'untab', '재정/투자', 
'프리랜서 세금 절약법', ARRAY['프리랜서', '세금', '절약법'], 'medium', 'planned', '2025-09-19')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 4, 'untab', '라이프스타일', 
'혼자 떠나는 국내 여행', ARRAY['혼자', '떠나는', '국내'], 'medium', 'planned', '2025-09-19')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 4, 'skewese', '건강/웰니스', 
'장 건강 프로바이오틱스', ARRAY['장', '건강', '프로바이오틱스'], 'medium', 'planned', '2025-09-19')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 4, 'skewese', '역사/문화', 
'전통 의학 한의학 이야기', ARRAY['전통', '의학', '한의학'], 'medium', 'planned', '2025-09-19')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 4, 'tistory', '엔터테인먼트', 
'버라이어티쇼 비하인드', ARRAY['버라이어티쇼', '비하인드'], 'medium', 'planned', '2025-09-19')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 4, 'tistory', '트렌드/이슈', 
'인플루언서 마케팅 분석', ARRAY['인플루언서', '마케팅', '분석'], 'medium', 'planned', '2025-09-19')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 5, 'unpre', '기술/디지털', 
'모바일 반응형 디자인 팁', ARRAY['모바일', '반응형', '디자인'], 'medium', 'planned', '2025-09-20')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 5, 'unpre', '교육/자기계발', 
'효과적인 스터디 그룹 운영', ARRAY['효과적인', '스터디', '그룹'], 'medium', 'planned', '2025-09-20')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 5, 'untab', '재정/투자', 
'소액 투자 앱 비교', ARRAY['소액', '투자', '앱'], 'medium', 'planned', '2025-09-20')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 5, 'untab', '라이프스타일', 
'수납 정리 노하우', ARRAY['수납', '정리', '노하우'], 'medium', 'planned', '2025-09-20')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 5, 'skewese', '건강/웰니스', 
'디톡스 주스 레시피', ARRAY['디톡스', '주스', '레시피'], 'medium', 'planned', '2025-09-20')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 5, 'skewese', '역사/문화', 
'한국 전통 음악 이해하기', ARRAY['한국', '전통', '음악'], 'medium', 'planned', '2025-09-20')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 5, 'tistory', '엔터테인먼트', 
'연예인 SNS 마케팅', ARRAY['연예인', 'SNS', '마케팅'], 'medium', 'planned', '2025-09-20')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 5, 'tistory', '트렌드/이슈', 
'숏츠/릴스 알고리즘', ARRAY['숏츠/릴스', '알고리즘'], 'medium', 'planned', '2025-09-20')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 6, 'unpre', '기술/디지털', 
'AI 코딩 어시스턴트 비교', ARRAY['AI', '코딩', '어시스턴트'], 'medium', 'planned', '2025-09-21')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 6, 'unpre', '교육/자기계발', 
'해외 취업 준비 체크리스트', ARRAY['해외', '취업', '준비'], 'medium', 'planned', '2025-09-21')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 6, 'untab', '재정/투자', 
'경제 지표 읽는 법', ARRAY['경제', '지표', '읽는'], 'medium', 'planned', '2025-09-21')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 6, 'untab', '라이프스타일', 
'계절별 옷장 정리법', ARRAY['계절별', '옷장', '정리법'], 'medium', 'planned', '2025-09-21')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 6, 'skewese', '건강/웰니스', 
'폼롤러 사용법 완벽 정리', ARRAY['폼롤러', '사용법', '완벽'], 'medium', 'planned', '2025-09-21')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 6, 'skewese', '역사/문화', 
'민속 신앙과 무속 문화', ARRAY['민속', '신앙과', '무속'], 'medium', 'planned', '2025-09-21')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 6, 'tistory', '엔터테인먼트', 
'콘서트 티켓팅 꿀팁', ARRAY['콘서트', '티켓팅', '꿀팁'], 'medium', 'planned', '2025-09-21')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-15', 6, 'tistory', '트렌드/이슈', 
'가상 인플루언서 등장', ARRAY['가상', '인플루언서', '등장'], 'medium', 'planned', '2025-09-21')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 0, 'unpre', '기술/디지털', 
'오픈소스 기여 시작하기', ARRAY['오픈소스', '기여', '시작하기'], 'medium', 'planned', '2025-09-22')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 0, 'unpre', '교육/자기계발', 
'프리랜서 개발자 시작하기', ARRAY['프리랜서', '개발자', '시작하기'], 'medium', 'planned', '2025-09-22')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 0, 'untab', '재정/투자', 
'환율 변동 투자 전략', ARRAY['환율', '변동', '투자'], 'medium', 'planned', '2025-09-22')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 0, 'untab', '라이프스타일', 
'홈트레이닝 공간 만들기', ARRAY['홈트레이닝', '공간', '만들기'], 'medium', 'planned', '2025-09-22')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 0, 'skewese', '건강/웰니스', 
'얼굴 붓기 빼는 마사지', ARRAY['얼굴', '붓기', '빼는'], 'medium', 'planned', '2025-09-22')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 0, 'skewese', '역사/문화', 
'전통 공예 기법 소개', ARRAY['전통', '공예', '기법'], 'medium', 'planned', '2025-09-22')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 0, 'tistory', '엔터테인먼트', 
'방송 제작 비하인드', ARRAY['방송', '제작', '비하인드'], 'medium', 'planned', '2025-09-22')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 0, 'tistory', '트렌드/이슈', 
'업사이클링 브랜드', ARRAY['업사이클링', '브랜드'], 'medium', 'planned', '2025-09-22')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 1, 'unpre', '기술/디지털', 
'테스트 주도 개발(TDD) 실전', ARRAY['테스트', '주도', '개발(TDD)'], 'medium', 'planned', '2025-09-23')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 1, 'unpre', '교육/자기계발', 
'개발 블로그 운영 팁', ARRAY['개발', '블로그', '운영'], 'medium', 'planned', '2025-09-23')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 1, 'untab', '재정/투자', 
'노후 자금 계획 세우기', ARRAY['노후', '자금', '계획'], 'medium', 'planned', '2025-09-23')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 1, 'untab', '라이프스타일', 
'베란다 텃밭 가꾸기', ARRAY['베란다', '텃밭', '가꾸기'], 'medium', 'planned', '2025-09-23')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 1, 'skewese', '건강/웰니스', 
'체형별 운동 루틴', ARRAY['체형별', '운동', '루틴'], 'medium', 'planned', '2025-09-23')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 1, 'skewese', '역사/문화', 
'한국사 미스터리 사건들', ARRAY['한국사', '미스터리', '사건들'], 'medium', 'planned', '2025-09-23')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 1, 'tistory', '엔터테인먼트', 
'예능 레전드 장면들', ARRAY['예능', '레전드', '장면들'], 'medium', 'planned', '2025-09-23')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 1, 'tistory', '트렌드/이슈', 
'펫코노미 시장 분석', ARRAY['펫코노미', '시장', '분석'], 'medium', 'planned', '2025-09-23')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 2, 'unpre', '기술/디지털', 
'클린 코드 작성법', ARRAY['클린', '코드', '작성법'], 'medium', 'planned', '2025-09-24')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 2, 'unpre', '교육/자기계발', 
'오픈소스 포트폴리오 만들기', ARRAY['오픈소스', '포트폴리오', '만들기'], 'medium', 'planned', '2025-09-24')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 2, 'untab', '재정/투자', 
'신용등급 올리는 방법', ARRAY['신용등급', '올리는', '방법'], 'medium', 'planned', '2025-09-24')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 2, 'untab', '라이프스타일', 
'명품 가방 관리법', ARRAY['명품', '가방', '관리법'], 'medium', 'planned', '2025-09-24')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 2, 'skewese', '건강/웰니스', 
'면역력 높이는 음식', ARRAY['면역력', '높이는', '음식'], 'medium', 'planned', '2025-09-24')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 2, 'skewese', '역사/문화', 
'근대화 과정의 빛과 그림자', ARRAY['근대화', '과정의', '빛과'], 'medium', 'planned', '2025-09-24')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 2, 'tistory', '엔터테인먼트', 
'아이돌 덕질 입문 가이드', ARRAY['아이돌', '덕질', '입문'], 'medium', 'planned', '2025-09-24')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 2, 'tistory', '트렌드/이슈', 
'홈코노미 트렌드', ARRAY['홈코노미', '트렌드'], 'medium', 'planned', '2025-09-24')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 3, 'unpre', '기술/디지털', 
'디자인 패턴 실무 적용', ARRAY['디자인', '패턴', '실무'], 'medium', 'planned', '2025-09-25')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 3, 'unpre', '교육/자기계발', 
'코딩 부트캠프 선택 가이드', ARRAY['코딩', '부트캠프', '선택'], 'medium', 'planned', '2025-09-25')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 3, 'untab', '재정/투자', 
'대출 이자 줄이는 팁', ARRAY['대출', '이자', '줄이는'], 'medium', 'planned', '2025-09-25')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 3, 'untab', '라이프스타일', 
'에코백 DIY 아이디어', ARRAY['에코백', 'DIY', '아이디어'], 'medium', 'planned', '2025-09-25')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 3, 'skewese', '건강/웰니스', 
'생리통 완화 요가', ARRAY['생리통', '완화', '요가'], 'medium', 'planned', '2025-09-25')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 3, 'skewese', '역사/문화', 
'한국 성씨의 기원', ARRAY['한국', '성씨의', '기원'], 'medium', 'planned', '2025-09-25')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 3, 'tistory', '엔터테인먼트', 
'영화제 수상작 분석', ARRAY['영화제', '수상작', '분석'], 'medium', 'planned', '2025-09-25')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 3, 'tistory', '트렌드/이슈', 
'리빙포인트 인테리어', ARRAY['리빙포인트', '인테리어'], 'medium', 'planned', '2025-09-25')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 4, 'unpre', '기술/디지털', 
'API 문서화 자동화', ARRAY['API', '문서화', '자동화'], 'medium', 'planned', '2025-09-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 4, 'unpre', '교육/자기계발', 
'개발자 네트워킹 방법', ARRAY['개발자', '네트워킹', '방법'], 'medium', 'planned', '2025-09-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 4, 'untab', '재정/투자', 
'청약통장 활용 전략', ARRAY['청약통장', '활용', '전략'], 'medium', 'planned', '2025-09-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 4, 'untab', '라이프스타일', 
'강아지와 함께 가는 여행지', ARRAY['강아지와', '함께', '가는'], 'medium', 'planned', '2025-09-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 4, 'skewese', '건강/웰니스', 
'금연 성공 전략', ARRAY['금연', '성공', '전략'], 'medium', 'planned', '2025-09-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 4, 'skewese', '역사/문화', 
'전통 명절의 유래', ARRAY['전통', '명절의', '유래'], 'medium', 'planned', '2025-09-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 4, 'tistory', '엔터테인먼트', 
'한류 콘텐츠 해외 반응', ARRAY['한류', '콘텐츠', '해외'], 'medium', 'planned', '2025-09-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 4, 'tistory', '트렌드/이슈', 
'K-뷰티 글로벌 트렌드', ARRAY['K-뷰티', '글로벌', '트렌드'], 'medium', 'planned', '2025-09-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 5, 'unpre', '기술/디지털', 
'보안 취약점 점검 가이드', ARRAY['보안', '취약점', '점검'], 'medium', 'planned', '2025-09-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 5, 'unpre', '교육/자기계발', 
'기술 서적 추천 리스트', ARRAY['기술', '서적', '추천'], 'medium', 'planned', '2025-09-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 5, 'untab', '재정/투자', 
'재테크 자동화 시스템', ARRAY['재테크', '자동화', '시스템'], 'medium', 'planned', '2025-09-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 5, 'untab', '라이프스타일', 
'홈파티 준비 체크리스트', ARRAY['홈파티', '준비', '체크리스트'], 'medium', 'planned', '2025-09-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 5, 'skewese', '건강/웰니스', 
'알레르기 관리법', ARRAY['알레르기', '관리법'], 'medium', 'planned', '2025-09-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 5, 'skewese', '역사/문화', 
'한국 고대사 논쟁점들', ARRAY['한국', '고대사', '논쟁점들'], 'medium', 'planned', '2025-09-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 5, 'tistory', '엔터테인먼트', 
'리얼리티쇼 인기 비결', ARRAY['리얼리티쇼', '인기', '비결'], 'medium', 'planned', '2025-09-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 5, 'tistory', '트렌드/이슈', 
'스트리트 패션 분석', ARRAY['스트리트', '패션', '분석'], 'medium', 'planned', '2025-09-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 6, 'unpre', '기술/디지털', 
'데이터베이스 인덱싱 전략', ARRAY['데이터베이스', '인덱싱', '전략'], 'medium', 'planned', '2025-09-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 6, 'unpre', '교육/자기계발', 
'온라인 코딩 교육 사이트 비교', ARRAY['온라인', '코딩', '교육'], 'medium', 'planned', '2025-09-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 6, 'untab', '재정/투자', 
'투자 손실 세금 공제', ARRAY['투자', '손실', '세금'], 'medium', 'planned', '2025-09-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 6, 'untab', '라이프스타일', 
'독서 공간 꾸미기', ARRAY['독서', '공간', '꾸미기'], 'medium', 'planned', '2025-09-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 6, 'skewese', '건강/웰니스', 
'치아 미백 홈케어', ARRAY['치아', '미백', '홈케어'], 'medium', 'planned', '2025-09-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 6, 'skewese', '역사/문화', 
'문화재 복원 이야기', ARRAY['문화재', '복원', '이야기'], 'medium', 'planned', '2025-09-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 6, 'tistory', '엔터테인먼트', 
'음악 방송 1위 예측', ARRAY['음악', '방송', '1위'], 'medium', 'planned', '2025-09-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-22', 6, 'tistory', '트렌드/이슈', 
'미닝아웃 소비 문화', ARRAY['미닝아웃', '소비', '문화'], 'medium', 'planned', '2025-09-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 0, 'unpre', '기술/디지털', 
'로그 관리 시스템 구축', ARRAY['로그', '관리', '시스템'], 'medium', 'planned', '2025-09-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 0, 'unpre', '교육/자기계발', 
'개발자 건강 관리법', ARRAY['개발자', '건강', '관리법'], 'medium', 'planned', '2025-09-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 0, 'untab', '재정/투자', 
'부동산 세금 완벽 정리', ARRAY['부동산', '세금', '완벽'], 'medium', 'planned', '2025-09-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 0, 'untab', '라이프스타일', 
'향초 브랜드 추천', ARRAY['향초', '브랜드', '추천'], 'medium', 'planned', '2025-09-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 0, 'skewese', '건강/웰니스', 
'자세 교정 스트레칭', ARRAY['자세', '교정', '스트레칭'], 'medium', 'planned', '2025-09-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 0, 'skewese', '역사/문화', 
'전통 시장의 역사', ARRAY['전통', '시장의', '역사'], 'medium', 'planned', '2025-09-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 0, 'tistory', '엔터테인먼트', 
'드라마 OST 명곡들', ARRAY['드라마', 'OST', '명곡들'], 'medium', 'planned', '2025-09-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 0, 'tistory', '트렌드/이슈', 
'크라우드펀딩 성공 사례', ARRAY['크라우드펀딩', '성공', '사례'], 'medium', 'planned', '2025-09-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 1, 'unpre', '기술/디지털', 
'모니터링 대시보드 만들기', ARRAY['모니터링', '대시보드', '만들기'], 'medium', 'planned', '2025-09-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 1, 'unpre', '교육/자기계발', 
'재택근무 생산성 향상법', ARRAY['재택근무', '생산성', '향상법'], 'medium', 'planned', '2025-09-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 1, 'untab', '재정/투자', 
'파이어족 되는 방법', ARRAY['파이어족', '되는', '방법'], 'medium', 'planned', '2025-09-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 1, 'untab', '라이프스타일', 
'차박 여행 준비물', ARRAY['차박', '여행', '준비물'], 'medium', 'planned', '2025-09-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 1, 'skewese', '건강/웰니스', 
'항산화 음식 리스트', ARRAY['항산화', '음식', '리스트'], 'medium', 'planned', '2025-09-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 1, 'skewese', '역사/문화', 
'한국 영토 변천사', ARRAY['한국', '영토', '변천사'], 'medium', 'planned', '2025-09-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 1, 'tistory', '엔터테인먼트', 
'예능 유행어 정리', ARRAY['예능', '유행어', '정리'], 'medium', 'planned', '2025-09-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
INSERT INTO unble.publishing_schedule 
(week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-09-29', 1, 'tistory', '트렌드/이슈', 
'소셜미디어 알고리즘 변화', ARRAY['소셜미디어', '알고리즘', '변화'], 'medium', 'planned', '2025-09-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) 
DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, 
scheduled_date = EXCLUDED.scheduled_date, updated_at = CURRENT_TIMESTAMP;
