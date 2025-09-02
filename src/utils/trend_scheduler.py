#!/usr/bin/env python3
"""
실시간 트렌드 기반 티스토리 주제 자동 업데이트 스케줄러
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.schedule_manager import ScheduleManager
from src.utils.realtime_trends import RealtimeTrends
from datetime import date, timedelta
import logging

class TrendScheduler:
    """실시간 트렌드 기반 스케줄 업데이트"""
    
    def __init__(self):
        self.schedule_manager = ScheduleManager()
        self.trends_collector = RealtimeTrends()
        self.logger = logging.getLogger(__name__)
        
    def update_tistory_with_realtime_trends(self):
        """실시간 트렌드를 바탕으로 티스토리 주제 업데이트"""
        
        print("🚀 실시간 트렌드 기반 티스토리 주제 업데이트 시작")
        print("=" * 60)
        
        try:
            # 실시간 트렌드 수집
            blog_topics = self.trends_collector.get_combined_trends()
            
            if not blog_topics:
                print("⚠️ 트렌드 데이터를 수집할 수 없어 기본값 사용")
                blog_topics = self._get_default_topics()
            
            # 오늘과 내일 날짜 계산
            today = date.today()
            tomorrow = today + timedelta(days=1)
            
            dates_to_update = [today, tomorrow]
            
            conn = self.schedule_manager.db.get_connection()
            
            with conn.cursor() as cursor:
                for target_date in dates_to_update:
                    week_start = target_date - timedelta(days=target_date.weekday())
                    weekday = target_date.weekday()
                    
                    print(f"\n📅 {target_date} 티스토리 주제 업데이트")
                    
                    # tech 카테고리 업데이트
                    tech_topics = blog_topics.get('tech', ['AI 기술 혁신과 미래 전망'])
                    tech_topic = tech_topics[target_date.day % len(tech_topics)]
                    
                    cursor.execute("""
                        UPDATE publishing_schedule
                        SET specific_topic = %s,
                            keywords = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE week_start_date = %s 
                        AND day_of_week = %s 
                        AND site = 'tistory'
                        AND topic_category = 'tech'
                    """, (
                        tech_topic,
                        ['실시간', '트렌드', 'IT', '기술'],
                        week_start, weekday
                    ))
                    
                    print(f"  📱 [tech] {tech_topic}")
                    
                    # social 카테고리 업데이트
                    social_topics = (blog_topics.get('social', []) + 
                                   blog_topics.get('politics', []) +
                                   blog_topics.get('economy', []))
                    
                    if not social_topics:
                        social_topics = ['사회 이슈와 트렌드 분석']
                    
                    social_topic = social_topics[(target_date.day + 3) % len(social_topics)]
                    
                    cursor.execute("""
                        UPDATE publishing_schedule
                        SET specific_topic = %s,
                            keywords = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE week_start_date = %s 
                        AND day_of_week = %s 
                        AND site = 'tistory'
                        AND topic_category = 'social'
                    """, (
                        social_topic,
                        ['사회', '이슈', '정책', '트렌드'],
                        week_start, weekday
                    ))
                    
                    print(f"  🌐 [social] {social_topic}")
            
            conn.commit()
            print(f"\n✅ 실시간 트렌드 기반 티스토리 주제 업데이트 완료!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"트렌드 업데이트 오류: {e}")
            print(f"❌ 업데이트 오류: {e}")
            return False
    
    def _get_default_topics(self) -> dict:
        """트렌드 수집 실패 시 기본 주제"""
        return {
            'tech': [
                'AI 휴머노이드 로봇 상용화 현황',
                '5G vs 6G 통신 기술 비교',
                '메타버스 플랫폼 최신 동향',
                '자율주행차 기술 발전 현황',
                '양자컴퓨터 연구 개발 소식'
            ],
            'social': [
                'MZ세대 라이프스타일 변화',
                '저출산 고령화 사회 대응',
                '부동산 정책 최신 동향',
                '환경보호 정책과 실천',
                '디지털 전환 시대 적응'
            ],
            'politics': [
                '정부 경제 정책 분석',
                '국제 정세와 외교 관계',
                '사회 복지 정책 개선',
                '교육 개혁 추진 현황'
            ],
            'economy': [
                '글로벌 경제 동향 분석',
                '주식 시장 투자 트렌드',
                '암호화폐 규제 정책',
                '스타트업 투자 생태계'
            ]
        }

def test_trend_update():
    """트렌드 업데이트 테스트"""
    
    trend_scheduler = TrendScheduler()
    
    # 실시간 트렌드 업데이트 테스트
    success = trend_scheduler.update_tistory_with_realtime_trends()
    
    if success:
        print("\n🎯 업데이트된 오늘 주제 확인:")
        
        # 오늘 티스토리 주제 확인
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        try:
            conn = trend_scheduler.schedule_manager.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT topic_category, specific_topic
                    FROM publishing_schedule
                    WHERE week_start_date = %s 
                    AND day_of_week = %s 
                    AND site = 'tistory'
                    ORDER BY topic_category
                """, (week_start, today.weekday()))
                
                results = cursor.fetchall()
                
                for category, topic in results:
                    print(f"  📍 [{category}] {topic}")
                    
        except Exception as e:
            print(f"❌ 확인 오류: {e}")

if __name__ == '__main__':
    test_trend_update()