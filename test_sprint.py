import requests
import json

url = "http://localhost:8000/api/sprint/plan"
data = {
    "project_id": "test-project",
    "sprint_number": 1,
    "available_members": ["Alice", "Bob"],
    "available_tasks": [
        {"id": "1", "title": "Fix bug", "category": "Backend", "complexity": "high"}
    ]
}

try:
    print(f"Sending request to {url}...")
    r = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {r.status_code}")
    print("Response Body:")
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print(r.text)
except Exception as e:
    print(f"Error: {e}")
