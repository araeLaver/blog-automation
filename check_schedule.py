from datetime import date
from src.utils.schedule_manager import schedule_manager

conn = schedule_manager.db.get_connection()
cursor = conn.cursor()

# 오늘은 2025년 9월 2일 (화요일)
today = date(2025, 9, 2)
week_start = date(2025, 9, 1)  # 월요일
day_of_week = 1  # 화요일

print(f"Checking schedule for {today} (Tuesday)")
print(f"Week start: {week_start}, Day of week: {day_of_week}")

# 화요일 스케줄 확인
cursor.execute("""
    SELECT site, topic_category, specific_topic, status 
    FROM publishing_schedule 
    WHERE week_start_date = %s AND day_of_week = %s
    ORDER BY site, topic_category
""", (week_start, day_of_week))

results = cursor.fetchall()
print(f"\nFound {len(results)} schedules for Tuesday:")
for r in results:
    print(f"  - {r[0]}: [{r[1]}] {r[2]} (status: {r[3]})")

# 9월 전체 스케줄 확인
cursor.execute("""
    SELECT COUNT(*), COUNT(DISTINCT week_start_date + (day_of_week * INTERVAL '1 day'))
    FROM publishing_schedule
    WHERE week_start_date + (day_of_week * INTERVAL '1 day') >= '2025-09-01'
    AND week_start_date + (day_of_week * INTERVAL '1 day') < '2025-10-01'
""")
total, days = cursor.fetchone()
print(f"\nSeptember schedule summary:")
print(f"  Total entries: {total}")
print(f"  Days with schedule: {days}")

conn.close()