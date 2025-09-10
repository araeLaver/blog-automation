#!/usr/bin/env python3
"""
키워드 리서치 자동화 스케줄러
매일 정기적으로 인기 키워드를 수집하여 저장
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import schedule

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.keyword_research import keyword_researcher

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/keyword_scheduler.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class KeywordScheduler:
    """키워드 수집 스케줄러"""
    
    def __init__(self):
        self.data_dir = Path("data/keywords")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 카테고리별 수집 설정
        self.categories = [
            '기술/IT', '투자/경제', '건강/의료', '교육/학습',
            '생활/라이프', '여행/관광', '패션/뷰티', '연예/문화'
        ]
        
    def collect_daily_keywords(self):
        """일일 키워드 수집"""
        try:
            logger.info("=== 일일 키워드 수집 시작 ===")
            
            all_keywords = []
            today = datetime.now().strftime('%Y-%m-%d')
            
            for category in self.categories:
                try:
                    logger.info(f"{category} 카테고리 키워드 수집 중...")
                    
                    # 카테고리별 키워드 리서치 (50개씩)
                    keywords = keyword_researcher.research_high_volume_keywords(
                        category=category, 
                        limit=50
                    )
                    
                    category_data = []
                    for kw in keywords:
                        kw_dict = {
                            'keyword': kw.keyword,
                            'search_volume': kw.search_volume,
                            'trend_score': kw.trend_score,
                            'competition': kw.competition,
                            'category': kw.category,
                            'search_intent': kw.search_intent,
                            'difficulty': kw.difficulty,
                            'opportunity_score': kw.opportunity_score,
                            'related_keywords': kw.related_keywords,
                            'collected_date': today,
                            'timestamp': kw.timestamp.isoformat()
                        }
                        category_data.append(kw_dict)
                    
                    all_keywords.extend(category_data)
                    logger.info(f"[완료] {category}: {len(category_data)}개 키워드 수집 완료")
                    
                    # 카테고리별 파일 저장
                    category_file = self.data_dir / f"{category.replace('/', '_')}_{today}.json"
                    with open(category_file, 'w', encoding='utf-8') as f:
                        json.dump(category_data, f, ensure_ascii=False, indent=2)
                    
                    # 수집 간격 (API 제한 방지)
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"[실패] {category} 카테고리 수집 실패: {e}")
                    continue
            
            # 전체 키워드 파일 저장
            all_keywords_file = self.data_dir / f"all_keywords_{today}.json"
            with open(all_keywords_file, 'w', encoding='utf-8') as f:
                json.dump(all_keywords, f, ensure_ascii=False, indent=2)
            
            # 고기회 키워드 별도 저장
            high_opportunity_keywords = [
                kw for kw in all_keywords 
                if kw['opportunity_score'] >= 30  # 기회점수 30 이상
            ]
            high_opportunity_keywords.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            high_opp_file = self.data_dir / f"high_opportunity_{today}.json"
            with open(high_opp_file, 'w', encoding='utf-8') as f:
                json.dump(high_opportunity_keywords, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[성공] 일일 키워드 수집 완료!")
            logger.info(f"총 키워드: {len(all_keywords)}개")
            logger.info(f"고기회 키워드: {len(high_opportunity_keywords)}개")
            logger.info(f"저장 위치: {self.data_dir}")
            
            return {
                'success': True,
                'total_keywords': len(all_keywords),
                'high_opportunity_keywords': len(high_opportunity_keywords),
                'categories_collected': len(self.categories),
                'date': today
            }
            
        except Exception as e:
            logger.error(f"[실패] 일일 키워드 수집 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_blog_keyword_report(self):
        """블로그 작성을 위한 키워드 리포트 생성"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            high_opp_file = self.data_dir / f"high_opportunity_{today}.json"
            
            if not high_opp_file.exists():
                logger.warning("[경고] 오늘의 고기회 키워드 파일을 찾을 수 없습니다.")
                return
            
            with open(high_opp_file, 'r', encoding='utf-8') as f:
                keywords = json.load(f)
            
            # 카테고리별 상위 키워드 정리
            report = {
                'generated_date': today,
                'total_keywords': len(keywords),
                'categories': {}
            }
            
            for category in self.categories:
                category_keywords = [
                    kw for kw in keywords 
                    if kw['category'] == category
                ][:10]  # 카테고리별 상위 10개
                
                if category_keywords:
                    report['categories'][category] = {
                        'count': len(category_keywords),
                        'keywords': [
                            {
                                'keyword': kw['keyword'],
                                'search_volume': kw['search_volume'],
                                'opportunity_score': kw['opportunity_score'],
                                'search_intent': kw['search_intent'],
                                'related_keywords': kw['related_keywords'][:5]
                            }
                            for kw in category_keywords
                        ]
                    }
            
            # 블로그 키워드 리포트 저장
            report_file = self.data_dir / f"blog_keyword_report_{today}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            # 간단한 텍스트 리포트도 생성
            self._generate_text_report(report, today)
            
            logger.info(f"[완료] 블로그 키워드 리포트 생성 완료: {report_file}")
            
        except Exception as e:
            logger.error(f"[실패] 블로그 키워드 리포트 생성 실패: {e}")
    
    def _generate_text_report(self, report, date):
        """사람이 읽기 쉬운 텍스트 리포트 생성"""
        try:
            report_text = f"""
# 블로그 키워드 추천 리포트 ({date})

총 {report['total_keywords']}개의 고기회 키워드를 분석했습니다.

## 카테고리별 추천 키워드

"""
            
            for category, data in report['categories'].items():
                if data['keywords']:
                    report_text += f"\n### {category} ({data['count']}개 키워드)\n\n"
                    
                    for i, kw in enumerate(data['keywords'][:5], 1):
                        report_text += f"{i}. **{kw['keyword']}**\n"
                        report_text += f"   - 검색량: {kw['search_volume']:,}회/월\n"
                        report_text += f"   - 기회점수: {kw['opportunity_score']}\n"
                        report_text += f"   - 검색의도: {kw['search_intent']}\n"
                        report_text += f"   - 관련키워드: {', '.join(kw['related_keywords'])}\n\n"
            
            report_text += f"""
## 블로그 작성 팁

1. **고기회 점수**가 높은 키워드를 우선 선택하세요
2. **Informational** 키워드는 가이드/팁 형태의 글로 작성
3. **Commercial** 키워드는 제품 리뷰/비교 글로 작성
4. 관련 키워드들을 본문에 자연스럽게 포함하세요

---
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            text_file = self.data_dir / f"blog_keywords_{date}.md"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            logger.info(f"[완료] 텍스트 리포트 생성: {text_file}")
            
        except Exception as e:
            logger.error(f"[실패] 텍스트 리포트 생성 실패: {e}")
    
    def cleanup_old_files(self, days_to_keep=7):
        """오래된 키워드 파일 정리"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for file in self.data_dir.glob("*.json"):
                if file.stat().st_mtime < cutoff_date.timestamp():
                    file.unlink()
                    deleted_count += 1
            
            logger.info(f"[정리] {deleted_count}개의 오래된 파일을 정리했습니다.")
            
        except Exception as e:
            logger.error(f"[실패] 파일 정리 실패: {e}")
    
    def run_scheduler(self):
        """스케줄러 실행"""
        logger.info("키워드 수집 스케줄러 시작")
        
        # 스케줄 등록
        schedule.every().day.at("09:00").do(self.collect_daily_keywords)
        schedule.every().day.at("09:30").do(self.generate_blog_keyword_report)
        schedule.every().day.at("23:59").do(self.cleanup_old_files)
        
        # 즉시 한 번 실행
        logger.info("초기 키워드 수집 실행...")
        self.collect_daily_keywords()
        self.generate_blog_keyword_report()
        
        # 스케줄러 실행
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

def main():
    """메인 함수"""
    try:
        scheduler = KeywordScheduler()
        scheduler.run_scheduler()
    except KeyboardInterrupt:
        logger.info("[중단] 사용자에 의해 스케줄러가 중단되었습니다.")
    except Exception as e:
        logger.error(f"[실패] 스케줄러 실행 오류: {e}")

if __name__ == "__main__":
    main()