"""
더미 콘텐츠 파일 추가
"""
import sqlite3
from datetime import datetime, timedelta
import random
import json
from pathlib import Path

def add_dummy_files():
    """더미 콘텐츠 파일 추가"""
    conn = sqlite3.connect('./data/blog_content.db')
    cursor = conn.cursor()
    
    # 더미 파일 데이터
    sites = ['unpre', 'untab', 'skewese']
    
    wordpress_files = [
        {
            'site': 'unpre',
            'title': 'Python 웹 개발 완벽 가이드',
            'file_path': './data/wordpress_posts/unpre/python_web_guide.html',
            'status': 'draft',
            'tags': json.dumps(['Python', 'Django', 'Flask']),
            'categories': json.dumps(['개발'])
        },
        {
            'site': 'untab',
            'title': '부동산 경매 투자 전략',
            'file_path': './data/wordpress_posts/untab/auction_strategy.html',
            'status': 'published',
            'tags': json.dumps(['부동산', '경매', '투자']),
            'categories': json.dumps(['부동산'])
        },
        {
            'site': 'skewese',
            'title': '조선시대 궁중문화의 이해',
            'file_path': './data/wordpress_posts/skewese/joseon_culture.html',
            'status': 'draft',
            'tags': json.dumps(['조선시대', '궁중문화', '역사']),
            'categories': json.dumps(['한국사'])
        }
    ]
    
    tistory_files = [
        {
            'site': 'tistory',
            'title': '토익 고득점을 위한 5가지 전략',
            'file_path': './data/tistory_posts/toeic_strategy.html',
            'status': 'draft',
            'tags': json.dumps(['토익', 'TOEIC', '영어학습']),
            'categories': json.dumps(['언어학습'])
        },
        {
            'site': 'tistory',
            'title': 'JLPT N2 문법 완전정복',
            'file_path': './data/tistory_posts/jlpt_n2_grammar.html',
            'status': 'draft',
            'tags': json.dumps(['JLPT', 'N2', '일본어']),
            'categories': json.dumps(['언어학습'])
        }
    ]
    
    # WordPress 파일 추가
    for file_data in wordpress_files:
        cursor.execute('''
            INSERT OR IGNORE INTO content_files 
            (site, title, file_path, file_type, word_count, reading_time, status, tags, categories, created_at, file_size)
            VALUES (?, ?, ?, 'wordpress', ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_data['site'],
            file_data['title'],
            file_data['file_path'],
            random.randint(1000, 3000),  # word_count
            random.randint(3, 10),       # reading_time
            file_data['status'],
            file_data['tags'],
            file_data['categories'],
            datetime.now().isoformat(),
            random.randint(10000, 50000) # file_size
        ))
    
    # Tistory 파일 추가
    for file_data in tistory_files:
        cursor.execute('''
            INSERT OR IGNORE INTO content_files 
            (site, title, file_path, file_type, word_count, reading_time, status, tags, categories, created_at, file_size)
            VALUES (?, ?, ?, 'tistory', ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_data['site'],
            file_data['title'],
            file_data['file_path'],
            random.randint(800, 2500),   # word_count
            random.randint(2, 8),        # reading_time
            file_data['status'],
            file_data['tags'],
            file_data['categories'],
            datetime.now().isoformat(),
            random.randint(8000, 40000)  # file_size
        ))
    
    conn.commit()
    conn.close()
    print("더미 콘텐츠 파일이 추가되었습니다!")

if __name__ == "__main__":
    add_dummy_files()