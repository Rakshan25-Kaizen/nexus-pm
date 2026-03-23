import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from backend.ml.train import train_synthetic
        train_synthetic()
        with open("trace.txt", "w") as f:
            f.write("SUCCESS")
    except Exception as e:
        with open("trace.txt", "w") as f:
            traceback.print_exc(file=f)
