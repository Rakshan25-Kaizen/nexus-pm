import sys
import os
# Ensure the current directory is in sys.path
sys.path.append(os.getcwd())
import uvicorn

if __name__ == "__main__":
    try:
        print(f"Starting uvicorn from {os.getcwd()}")
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, log_level="debug", reload=False)
    except Exception as e:
        print(f"Failed to start: {e}")
