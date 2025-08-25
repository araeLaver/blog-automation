-- 8월 남은 기간 발행 계획표 (새 카테고리 적용)
-- 적용 기간: 2025-08-26 ~ 2025-08-31
-- 새로운 듀얼 카테고리 시스템

-- 8월 26일 (화요일)
INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 1, 'unpre', '기술/디지털', 'Python 웹 크롤링 마스터하기', ARRAY['Python', '웹', '크롤링'], 'medium', 'planned', '2025-08-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 1, 'unpre', '교육/자기계발', '개발자 이력서 작성 완벽 가이드', ARRAY['개발자', '이력서', '작성'], 'medium', 'planned', '2025-08-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 1, 'untab', '재정/투자', '월 100만원 배당금 포트폴리오', ARRAY['월', '100만원', '배당금'], 'medium', 'planned', '2025-08-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 1, 'untab', '라이프스타일', '원룸 인테리어 10만원으로 변신', ARRAY['원룸', '인테리어', '10만원으로'], 'medium', 'planned', '2025-08-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 1, 'skewese', '건강/웰니스', '피부 타입별 스킨케어 루틴', ARRAY['피부', '타입별', '스킨케어'], 'medium', 'planned', '2025-08-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 1, 'skewese', '역사/문화', '한국 전쟁 숨겨진 이야기', ARRAY['한국', '전쟁', '숨겨진'], 'medium', 'planned', '2025-08-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 1, 'tistory', '엔터테인먼트', '넷플릭스 숨은 명작 추천', ARRAY['넷플릭스', '숨은', '명작'], 'medium', 'planned', '2025-08-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 1, 'tistory', '트렌드/이슈', 'AI가 바꾸는 일상생활', ARRAY['AI가', '바꾸는', '일상생활'], 'medium', 'planned', '2025-08-26')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

-- 8월 27일 (수요일)
INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 2, 'unpre', '기술/디지털', 'React 18 새로운 기능 완벽 정리', ARRAY['React', '18', '새로운'], 'medium', 'planned', '2025-08-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 2, 'unpre', '교육/자기계발', '코딩테스트 빈출 알고리즘 정리', ARRAY['코딩테스트', '빈출', '알고리즘'], 'medium', 'planned', '2025-08-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 2, 'untab', '재정/투자', '부동산 경매 초보자 가이드', ARRAY['부동산', '경매', '초보자'], 'medium', 'planned', '2025-08-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 2, 'untab', '라이프스타일', '에어프라이어 만능 레시피 30선', ARRAY['에어프라이어', '만능', '레시피'], 'medium', 'planned', '2025-08-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 2, 'skewese', '건강/웰니스', '홈트레이닝 4주 프로그램', ARRAY['홈트레이닝', '4주', '프로그램'], 'medium', 'planned', '2025-08-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 2, 'skewese', '역사/문화', '세종대왕의 리더십 분석', ARRAY['세종대왕의', '리더십', '분석'], 'medium', 'planned', '2025-08-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 2, 'tistory', '엔터테인먼트', '아이돌 서바이벌 프로그램 정리', ARRAY['아이돌', '서바이벌', '프로그램'], 'medium', 'planned', '2025-08-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 2, 'tistory', '트렌드/이슈', '친환경 라이프스타일 실천법', ARRAY['친환경', '라이프스타일', '실천법'], 'medium', 'planned', '2025-08-27')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

-- 8월 28일 (목요일)
INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 3, 'unpre', '기술/디지털', 'VS Code 생산성 200% 높이는 익스텐션', ARRAY['VS', 'Code', '생산성'], 'medium', 'planned', '2025-08-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 3, 'unpre', '교육/자기계발', 'JLPT N2 한 번에 합격하기', ARRAY['JLPT', 'N2', '한'], 'medium', 'planned', '2025-08-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 3, 'untab', '재정/투자', '비트코인 ETF 투자 전략', ARRAY['비트코인', 'ETF', '투자'], 'medium', 'planned', '2025-08-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 3, 'untab', '라이프스타일', '유럽 배낭여행 2주 코스', ARRAY['유럽', '배낭여행', '2주'], 'medium', 'planned', '2025-08-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 3, 'skewese', '건강/웰니스', '단백질 보충제 선택 가이드', ARRAY['단백질', '보충제', '선택'], 'medium', 'planned', '2025-08-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 3, 'skewese', '역사/문화', '임진왜란 7년 전쟁 연대기', ARRAY['임진왜란', '7년', '전쟁'], 'medium', 'planned', '2025-08-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 3, 'tistory', '엔터테인먼트', '웹툰 원작 드라마 성공 비결', ARRAY['웹툰', '원작', '드라마'], 'medium', 'planned', '2025-08-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 3, 'tistory', '트렌드/이슈', '메타버스 플랫폼 비교', ARRAY['메타버스', '플랫폼', '비교'], 'medium', 'planned', '2025-08-28')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

-- 8월 29일 (금요일)
INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 4, 'unpre', '기술/디지털', 'Docker로 개발환경 통일하기', ARRAY['Docker로', '개발환경', '통일하기'], 'medium', 'planned', '2025-08-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 4, 'unpre', '교육/자기계발', '기술 면접 단골 질문 100선', ARRAY['기술', '면접', '단골'], 'medium', 'planned', '2025-08-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 4, 'untab', '재정/투자', 'ISA 계좌 200% 활용법', ARRAY['ISA', '계좌', '200%'], 'medium', 'planned', '2025-08-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 4, 'untab', '라이프스타일', '미니멀 라이프 시작하기', ARRAY['미니멀', '라이프', '시작하기'], 'medium', 'planned', '2025-08-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 4, 'skewese', '건강/웰니스', '수면의 질 높이는 10가지 방법', ARRAY['수면의', '질', '높이는'], 'medium', 'planned', '2025-08-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 4, 'skewese', '역사/문화', '고구려 광개토대왕 정복사', ARRAY['고구려', '광개토대왕', '정복사'], 'medium', 'planned', '2025-08-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 4, 'tistory', '엔터테인먼트', 'K-POP 4세대 그룹 분석', ARRAY['K-POP', '4세대', '그룹'], 'medium', 'planned', '2025-08-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 4, 'tistory', '트렌드/이슈', 'Z세대 신조어 사전', ARRAY['Z세대', '신조어', '사전'], 'medium', 'planned', '2025-08-29')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

-- 8월 30일 (토요일)
INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 5, 'unpre', '기술/디지털', 'Git 브랜치 전략 실무 가이드', ARRAY['Git', '브랜치', '전략'], 'medium', 'planned', '2025-08-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 5, 'unpre', '교육/자기계발', '영어 회화 스피킹 연습법', ARRAY['영어', '회화', '스피킹'], 'medium', 'planned', '2025-08-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 5, 'untab', '재정/투자', '미국 주식 세금 절약 팁', ARRAY['미국', '주식', '세금'], 'medium', 'planned', '2025-08-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 5, 'untab', '라이프스타일', '홈카페 분위기 만들기', ARRAY['홈카페', '분위기', '만들기'], 'medium', 'planned', '2025-08-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 5, 'skewese', '건강/웰니스', '글루텐프리 다이어트 효과', ARRAY['글루텐프리', '다이어트', '효과'], 'medium', 'planned', '2025-08-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 5, 'skewese', '역사/문화', '신라 화랑도 정신과 문화', ARRAY['신라', '화랑도', '정신과'], 'medium', 'planned', '2025-08-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 5, 'tistory', '엔터테인먼트', 'OTT 플랫폼별 특징 비교', ARRAY['OTT', '플랫폼별', '특징'], 'medium', 'planned', '2025-08-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 5, 'tistory', '트렌드/이슈', '리셀 시장 인기 아이템', ARRAY['리셀', '시장', '인기'], 'medium', 'planned', '2025-08-30')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

-- 8월 31일 (일요일)
INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 6, 'unpre', '기술/디지털', 'AWS Lambda 서버리스 입문', ARRAY['AWS', 'Lambda', '서버리스'], 'medium', 'planned', '2025-08-31')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 6, 'unpre', '교육/자기계발', '개발자 포트폴리오 만들기', ARRAY['개발자', '포트폴리오', '만들기'], 'medium', 'planned', '2025-08-31')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 6, 'untab', '재정/투자', '리츠(REITs) 투자 완벽 가이드', ARRAY['리츠(REITs)', '투자', '완벽'], 'medium', 'planned', '2025-08-31')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 6, 'untab', '라이프스타일', '캠핑 초보자 장비 리스트', ARRAY['캠핑', '초보자', '장비'], 'medium', 'planned', '2025-08-31')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 6, 'skewese', '건강/웰니스', '요가 초보자 기본 자세', ARRAY['요가', '초보자', '기본'], 'medium', 'planned', '2025-08-31')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 6, 'skewese', '역사/문화', '백제 문화재의 아름다움', ARRAY['백제', '문화재의', '아름다움'], 'medium', 'planned', '2025-08-31')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 6, 'tistory', '엔터테인먼트', '한국 영화 역대 흥행 TOP 20', ARRAY['한국', '영화', '역대'], 'medium', 'planned', '2025-08-31')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;

INSERT INTO unble.publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status, scheduled_date) 
VALUES ('2025-08-25', 6, 'tistory', '트렌드/이슈', '숏폼 콘텐츠 제작 팁', ARRAY['숏폼', '콘텐츠', '제작'], 'medium', 'planned', '2025-08-31')
ON CONFLICT (week_start_date, day_of_week, site, topic_category) DO UPDATE SET specific_topic = EXCLUDED.specific_topic, keywords = EXCLUDED.keywords, updated_at = CURRENT_TIMESTAMP;