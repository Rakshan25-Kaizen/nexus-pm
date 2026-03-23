import requests
import sys

try:
    print("Testing NEXUS-PM Agent API directly...")
    res = requests.get('http://localhost:8000/api/agent/digest/project-1')
    if res.ok:
        data = res.json()
        print("\nSUCCESS! The LLM successfully digested the memory context.")
        print(f"Groq API Response:\n----------------\n{data.get('digest')}\n----------------")
    else:
        print(f"Backend API failed: {res.status_code}\n{res.text}")
except Exception as e:
    print(f"Failed to connect to backend: {e}")
    sys.exit(1)
