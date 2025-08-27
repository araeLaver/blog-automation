#!/bin/bash

# 자동발행 시스템 시작 스크립트

echo "🚀 PostgreSQL 기반 자동발행 시스템 시작"
echo "======================================"

# .env 파일 존재 확인
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다!"
    echo "   .env.example을 복사하여 .env 파일을 만들고 API 키를 설정하세요."
    exit 1
fi

# ANTHROPIC_API_KEY 확인
if ! grep -q "ANTHROPIC_API_KEY.*=" .env || grep -q "ANTHROPIC_API_KEY=your_anthropic_api_key_here" .env; then
    echo "❌ ANTHROPIC_API_KEY가 설정되지 않았습니다!"
    echo "   .env 파일에서 실제 Claude API 키를 설정하세요."
    exit 1
fi

# 로그 디렉토리 생성
mkdir -p ./data/logs

echo "✅ 환경 설정 확인 완료"
echo ""

# 스케줄 확인
echo "📅 오늘 발행 예정 확인 중..."
python3 -c "
import sys
from pathlib import Path
project_root = Path('.')
sys.path.insert(0, str(project_root))

from src.utils.postgresql_database import PostgreSQLDatabase
from datetime import datetime

try:
    today = datetime.now()
    db = PostgreSQLDatabase()
    conn = db.get_connection()
    
    sites = ['untab', 'unpre', 'skewese', 'tistory']
    total_topics = 0
    
    for site in sites:
        with conn.cursor() as cursor:
            cursor.execute(f'''
                SELECT COUNT(*)
                FROM {db.schema}.monthly_publishing_schedule
                WHERE site = %s AND year = %s AND month = %s AND day = %s
                AND status = 'pending'
            ''', (site, today.year, today.month, today.day))
            
            count = cursor.fetchone()[0]
            total_topics += count
            
            if count > 0:
                print(f'✅ {site.upper()}: {count}개 주제 발행 예정')
            else:
                print(f'⚪ {site.upper()}: 오늘 발행 예정 없음')
    
    if total_topics > 0:
        print(f'\\n📊 총 {total_topics}개 주제가 오늘 자동발행될 예정입니다.')
    else:
        print('\\n📊 오늘은 발행 예정된 주제가 없습니다.')
        
except Exception as e:
    print(f'❌ 스케줄 확인 오류: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "스케줄 확인 실패"
    exit 1
fi

echo ""
echo "🕐 자동발행 시간표:"
echo "   - 새벽 03:00에 모든 사이트 순차 발행"
echo "   - 순서: UNTAB → UNPRE → SKEWESE → TISTORY"
echo "   - 사이트 간 5분 간격"
echo ""

# 실행 방법 선택
echo "실행 방법을 선택하세요:"
echo "1) 포그라운드 실행 (터미널에서 직접 확인)"
echo "2) 백그라운드 실행 (nohup으로 백그라운드 실행)"
echo "3) 테스트 실행 (특정 사이트 즉시 실행)"
echo ""
read -p "선택 (1-3): " choice

case $choice in
    1)
        echo "🔄 포그라운드에서 자동발행 시스템 시작..."
        python3 daily_auto_publisher.py
        ;;
    2)
        echo "🔄 백그라운드에서 자동발행 시스템 시작..."
        nohup python3 daily_auto_publisher.py > ./data/logs/nohup.log 2>&1 &
        echo "백그라운드 프로세스 PID: $!"
        echo "로그 확인: tail -f ./data/logs/nohup.log"
        echo "프로세스 종료: kill $!"
        ;;
    3)
        echo "테스트할 사이트를 선택하세요:"
        echo "1) untab   2) unpre   3) skewese   4) tistory"
        read -p "선택 (1-4): " site_choice
        
        case $site_choice in
            1) site="untab" ;;
            2) site="unpre" ;;
            3) site="skewese" ;;
            4) site="tistory" ;;
            *) echo "잘못된 선택"; exit 1 ;;
        esac
        
        echo "🧪 $site 사이트 테스트 실행..."
        python3 daily_auto_publisher.py --test $site
        ;;
    *)
        echo "잘못된 선택입니다."
        exit 1
        ;;
esac