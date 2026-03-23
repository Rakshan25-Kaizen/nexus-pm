import requests
print("Testing DB route /api/tasks...")
try:
    r = requests.get("http://localhost:8000/api/tasks/project-1", timeout=3)
    print("DB OK:", r.status_code, len(r.text))
except Exception as e:
    print("DB HUNG:", str(e))

print("\nTesting status route...")
try:
    r = requests.get("http://localhost:8000/api/agent/status/project-1", timeout=3)
    print("STATUS OK:", r.status_code, len(r.text))
except Exception as e:
    print("STATUS HUNG:", str(e))
