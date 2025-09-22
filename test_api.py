import requests
response = requests.get('http://localhost:5000/api/weekly-plan/current')
print(f'Status: {response.status_code}')
result = response.json()
print(f'Success: {result.get("success")}')
data = result.get('data', {})
print(f'Week: {data.get("week_start")} ~ {data.get("week_end")}')
print(f'Days: {len(data.get("days", []))}')
print(f'Revenue: ${data.get("total_expected_revenue", 0)}')
if data.get("days"):
    print(f'Today (Monday): {data["days"][0]["sites"]["tistory"]["title"]}')