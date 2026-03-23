import sys
import os

root = r"C:\Users\Rakshan25\OneDrive\AI Agent [Nexus}\Nexus AI Agent"
sys.path.insert(0, root)
os.chdir(root)

try:
    from backend.ml.train import train_synthetic
    train_synthetic()
    print("====== SYNTHETIC TRAINING SUCCESS ======")
except Exception as e:
    import traceback
    traceback.print_exc()
