"""
PostgreSQL에 더미 데이터 추가
"""
import json
from datetime import datetime, timedelta
import random
from src.utils.postgresql_database import PostgreSQLDatabase

def add_postgresql_data():
    """PostgreSQL에 더미 데이터 추가"""
    try:
        db = PostgreSQLDatabase()
        print("PostgreSQL connection successful")
        
        # 더미 콘텐츠 히스토리 추가
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
            posts_count = random.randint(1, 3)  # 하루에 1-3개 포스트
            
            for _ in range(posts_count):
                site = random.choice(sites)
                category = random.choice(categories[site])
                title = f"{random.choice(titles[site])} - {date.strftime('%m월%d일')}"
                
                db.add_content(
                    site=site,
                    title=title,
                    category=category,
                    keywords=[f"{category}", f"{site}", "자동생성"],
                    content=f"이것은 {title}에 대한 자동 생성된 콘텐츠입니다.",
                    url=f"https://{site}.co.kr/posts/{random.randint(1000, 9999)}",
                    word_count=random.randint(1000, 3000),
                    reading_time=random.randint(3, 10)
                )
        
        print("Content history data added successfully")
        
        # 더미 콘텐츠 파일 추가
        wordpress_files = [
            {
                'site': 'unpre',
                'title': 'Python 웹 개발 완벽 가이드',
                'file_path': './data/wordpress_posts/unpre/python_web_guide.html',
                'status': 'draft',
                'tags': ['Python', 'Django', 'Flask'],
                'categories': ['개발']
            },
            {
                'site': 'untab',
                'title': '부동산 경매 투자 전략',
                'file_path': './data/wordpress_posts/untab/auction_strategy.html',
                'status': 'published',
                'tags': ['부동산', '경매', '투자'],
                'categories': ['부동산']
            },
            {
                'site': 'skewese',
                'title': '조선시대 궁중문화의 이해',
                'file_path': './data/wordpress_posts/skewese/joseon_culture.html',
                'status': 'draft',
                'tags': ['조선시대', '궁중문화', '역사'],
                'categories': ['한국사']
            }
        ]
        
        tistory_files = [
            {
                'site': 'tistory',
                'title': '토익 고득점을 위한 5가지 전략',
                'file_path': './data/tistory_posts/toeic_strategy.html',
                'status': 'draft',
                'tags': ['토익', 'TOEIC', '영어학습'],
                'categories': ['언어학습']
            },
            {
                'site': 'tistory',
                'title': 'JLPT N2 문법 완전정복',
                'file_path': './data/tistory_posts/jlpt_n2_grammar.html',
                'status': 'draft',
                'tags': ['JLPT', 'N2', '일본어'],
                'categories': ['언어학습']
            }
        ]
        
        # WordPress 파일 추가
        for file_data in wordpress_files:
            db.add_content_file(
                site=file_data['site'],
                title=file_data['title'],
                file_path=file_data['file_path'],
                file_type='wordpress',
                metadata={
                    'word_count': random.randint(1000, 3000),
                    'reading_time': random.randint(3, 10),
                    'status': file_data['status'],
                    'tags': file_data['tags'],
                    'categories': file_data['categories'],
                    'file_size': random.randint(10000, 50000)
                }
            )
        
        # Tistory 파일 추가
        for file_data in tistory_files:
            db.add_content_file(
                site=file_data['site'],
                title=file_data['title'],
                file_path=file_data['file_path'],
                file_type='tistory',
                metadata={
                    'word_count': random.randint(800, 2500),
                    'reading_time': random.randint(2, 8),
                    'status': file_data['status'],
                    'tags': file_data['tags'],
                    'categories': file_data['categories'],
                    'file_size': random.randint(8000, 40000)
                }
            )
        
        print("Content files data added successfully")
        
        # 주제 풀 데이터 추가
        for site, topic_list in titles.items():
            topics_data = []
            for i, topic in enumerate(topic_list):
                for category in categories[site]:
                    topics_data.append({
                        'topic': f"{topic} - {category}",
                        'category': category,
                        'priority': random.randint(1, 10),
                        'used': random.choice([True, False]),
                        'difficulty_level': random.randint(1, 5),
                        'estimated_length': random.randint(1500, 3000),
                        'target_keywords': [topic, category, site]
                    })
            
            db.add_topics_bulk(site, topics_data)
        
        print("Topic pool data added successfully")
        
        # 시스템 로그 추가
        for i in range(10):
            db.add_system_log(
                level=random.choice(['INFO', 'WARNING', 'ERROR']),
                component=random.choice(['content_generator', 'wordpress_publisher', 'web_dashboard']),
                message=f"테스트 로그 메시지 {i+1}",
                details={'test': True, 'index': i+1},
                site=random.choice(sites)
            )
        
        print("System logs data added successfully")
        
        print("\nPostgreSQL dummy data added successfully!")
        print("Now you can check the dashboard with data at http://localhost:5000")
        
    except Exception as e:
        print(f"Data addition error: {e}")

if __name__ == "__main__":
    add_postgresql_data()