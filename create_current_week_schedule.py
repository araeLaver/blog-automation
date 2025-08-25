#!/usr/bin/env python3
"""
현재 주 스케줄을 DB에 직접 생성하는 스크립트
"""

import requests
import json
from datetime import datetime, timedelta

def create_current_week_schedule():
    """현재 주(2025-08-25) 전체 스케줄을 DB에 직접 생성"""
    
    # 이번주 스케줄 데이터 (실제 계획표 기준)
    schedule_data = []
    week_start = "2025-08-25"
    
    # 각 요일별 스케줄
    daily_schedules = {
        0: {  # 월요일
            'unpre': {"topic": "PyTorch로 컴퓨터 비전 구현", "category": "프로그래밍"},
            'untab': {"topic": "부동산 계약 시 주의사항 완전정리", "category": "부동산"},
            'skewese': {"topic": "재활용과 업사이클링의 창조적 실천", "category": "환경"},
            'tistory': {"topic": "북한 핵 위협 지속, 한반도 긴장 고조", "category": "정치"}
        },
        1: {  # 화요일 - 내일 발행될 주제!
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
    
    # 각 일정을 개별 요청으로 생성
    base_url = "https://sore-kaile-untab-34c55d0a.koyeb.app"
    
    for day_of_week, day_data in daily_schedules.items():
        day_name = ['월','화','수','목','금','토','일'][day_of_week]
        print(f"\n=== {day_of_week}요일({day_name}) 스케줄 생성 ===")
        
        for site, topic_info in day_data.items():
            topic = topic_info['topic']
            category = topic_info['category']
            
            # SQL 직접 실행을 시도
            schedule_text = f"""
            INSERT INTO publishing_schedule 
            (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status)
            VALUES ('{week_start}', {day_of_week}, '{site}', '{category}', '{topic}', '{{}}', 'medium', 'planned')
            ON CONFLICT (week_start_date, day_of_week, site) 
            DO UPDATE SET 
                topic_category = EXCLUDED.topic_category,
                specific_topic = EXCLUDED.specific_topic;
            """
            
            print(f"  {site.upper():8s}: {topic}")
    
    print(f"\n총 {len(daily_schedules) * 4}개 스케줄 준비 완료")
    print("\n=== SQL 명령어들 ===")
    
    # 전체 SQL 생성
    all_sql = []
    for day_of_week, day_data in daily_schedules.items():
        for site, topic_info in day_data.items():
            topic = topic_info['topic'].replace("'", "''")  # SQL 이스케이프
            category = topic_info['category']
            
            sql = f"""INSERT INTO publishing_schedule (week_start_date, day_of_week, site, topic_category, specific_topic, keywords, target_length, status) VALUES ('{week_start}', {day_of_week}, '{site}', '{category}', '{topic}', '{{}}', 'medium', 'planned') ON CONFLICT (week_start_date, day_of_week, site) DO UPDATE SET topic_category = EXCLUDED.topic_category, specific_topic = EXCLUDED.specific_topic;"""
            
            all_sql.append(sql)
    
    # SQL 파일로 저장
    with open('current_week_schedule.sql', 'w', encoding='utf-8') as f:
        f.write("-- 현재 주(2025-08-25) 스케줄 데이터\n")
        f.write("-- 실행 시간: " + datetime.now().isoformat() + "\n\n")
        for sql in all_sql:
            f.write(sql + '\n')
    
    print("SQL 파일 생성: current_week_schedule.sql")
    
    return all_sql

if __name__ == "__main__":
    print("현재 주 스케줄 생성 스크립트")
    print("=" * 50)
    
    sqls = create_current_week_schedule()
    
    print("\n내일(화요일) 발행 주제:")
    print("- UNPRE  : JWT 토큰 기반 시큐리티 구현 (프로그래밍)")
    print("- UNTAB  : 친환경 부동산 그린 리모델링 트렌드 (취미)")  
    print("- SKEWESE: 임진왜란과 이순신의 활약 (뷰티/패션)")
    print("- TISTORY: MZ세대 투자 패턴 분석, 부작용은? (일반)")
    print("\nSQL 파일을 직접 DB에 실행하거나 API로 전송하세요.")