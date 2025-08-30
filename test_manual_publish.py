#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트 스크립트: 수정된 수동 발행 시스템 검증
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('src')

from utils.monthly_schedule_manager import MonthlyScheduleManager
from generators.content_generator import ContentGenerator
from config.sites_config import SITE_CONFIGS
from datetime import datetime

def test_manual_publish():
    """수동 발행 시스템 테스트"""
    print("=== 수동 발행 시스템 테스트 시작 ===")
    
    # 1. 스케줄 매니저 초기화
    schedule_manager = MonthlyScheduleManager()
    content_generator = ContentGenerator()
    
    today = datetime.now().date()
    print(f"오늘 날짜: {today}")
    
    # 2. UNPRE 사이트에 대해 오늘의 주제 확인
    site = "unpre"
    topics_result = schedule_manager.get_today_dual_topics(site)
    
    if not topics_result:
        print(f"[ERROR] {site}: 오늘({today}) 예정된 주제가 없습니다")
        return False
    
    primary_topic, secondary_topic = topics_result
    print(f"[TOPICS] {site}: {today} 예정 주제 조회 완료")
    print(f"  - Primary: {primary_topic['category']} - {primary_topic['topic']}")
    if secondary_topic:
        print(f"  - Secondary: {secondary_topic['category']} - {secondary_topic['topic']}")
    
    # 3. Primary 주제로 콘텐츠 생성 테스트
    if primary_topic:
        site_config = SITE_CONFIGS.get(site)
        
        print(f"\n[CONTENT] {site}: 콘텐츠 생성 시작 - '{primary_topic['topic']}'")
        print(f"Parameters:")
        print(f"  - site_config: {site_config['name']}")
        print(f"  - topic: {primary_topic['topic']}")  
        print(f"  - category: {primary_topic['category']}")
        print(f"  - existing_posts: None")
        print(f"  - content_length: 'medium'")
        
        try:
            # 수정된 파라미터 순서로 호출
            content_result = content_generator.generate_content(
                site_config, 
                primary_topic['topic'], 
                primary_topic['category'], 
                None,  # existing_posts
                'medium'  # content_length
            )
            
            if content_result and 'title' in content_result:
                print(f"[SUCCESS] 생성된 제목: {content_result['title']}")
                print(f"[MATCH] 계획된 주제: {primary_topic['topic']}")
                
                # 제목이 주제와 관련 있는지 간단 확인
                if any(word in content_result['title'] for word in primary_topic['topic'].split()[:2]):
                    print("SUCCESS: 제목이 계획된 주제와 일치합니다!")
                    return True
                else:
                    print("FAIL: 제목이 계획된 주제와 일치하지 않습니다!")
                    return False
            else:
                print("[ERROR] 콘텐츠 생성 실패")
                return False
                
        except Exception as e:
            print(f"[ERROR] 콘텐츠 생성 오류: {e}")
            return False
    
    return False

if __name__ == "__main__":
    success = test_manual_publish()
    if success:
        print("\nSUCCESS: 수동 발행 시스템이 올바르게 작동합니다!")
    else:
        print("\nFAIL: 수동 발행 시스템에 문제가 있습니다.")