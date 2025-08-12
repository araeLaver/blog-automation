"""
더미 데이터 추가 스크립트
"""
import sqlite3
from datetime import datetime, timedelta
import random
import hashlib

def setup_dummy_data():
    """더미 데이터 설정"""
    conn = sqlite3.connect('./data/blog_content.db')
    cursor = conn.cursor()
    
    # 더미 포스트 데이터 추가
    sites = ['unpre', 'untab', 'skewese']
    categories = {
        'unpre': ['개발', 'IT', '언어학습'],
        'untab': ['부동산', '경매', '정책/제도'],
        'skewese': ['세계사', '한국사', '라이프']
    }
    
    titles = {
        'unpre': [
            'Python 프로그래밍 기초',
            'JavaScript ES6 문법 정리',
            'React Hook 사용법',
            '토익 고득점 전략',
            'JLPT N2 문법 정리'
        ],
        'untab': [
            '부동산 투자 가이드',
            '경매 낙찰 전략',
            '임대수익률 계산법',
            '재개발 투자 포인트',
            '부동산 세금 절세'
        ],
        'skewese': [
            '고구려 역사 탐구',
            '조선시대 문화사',
            '세계사 주요 사건',
            '한국사능력검정시험 대비',
            '역사 속 인물 이야기'
        ]
    }
    
    # 지난 30일간의 더미 데이터 생성
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        posts_count = random.randint(1, 4)  # 하루에 1-4개 포스트
        
        for _ in range(posts_count):
            site = random.choice(sites)
            category = random.choice(categories[site])
            title = f"{random.choice(titles[site])} - {date.strftime('%m월%d일')}"
            title_hash = hashlib.md5(title.encode()).hexdigest()
            
            cursor.execute('''
                INSERT OR IGNORE INTO content_history (site, title, title_hash, category, url, published_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                site,
                title,
                title_hash,
                category,
                f"https://{site}.co.kr/posts/{random.randint(1000, 9999)}",
                date.strftime('%Y-%m-%d %H:%M:%S'),
                'published'
            ))
    
    conn.commit()
    conn.close()
    print("더미 데이터가 성공적으로 추가되었습니다!")

if __name__ == "__main__":
    setup_dummy_data()