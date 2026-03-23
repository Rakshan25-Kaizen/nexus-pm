"""Quick Hindsight connection and seed check. Run: python -m scripts.check_hindsight"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.memory.hindsight_client import client, BANK_MEMBERS, BANK_TASKS, BANK_MEETINGS

def check():
    print("Checking Hindsight connection...")
    banks = [
        (BANK_MEMBERS,  "members-bank"),
        (BANK_TASKS,    "tasks-bank"),
        (BANK_MEETINGS, "meetings-bank"),
    ]
    all_ok = True
    for bank_id, label in banks:
        try:
            result = client.recall(
                bank_id=bank_id,
                query="Alice team member performance",
                budget="low",
                max_tokens=512
            )
            count = len(result.results)
            if count > 0:
                print(f"  OK  {label}: {count} memories found")
            else:
                print(f"  EMPTY  {label}: 0 memories — run: make seed")
                all_ok = False
        except Exception as e:
            print(f"  ERR  {label}: {e}")
            all_ok = False

    if all_ok:
        print("\nHindsight is seeded and working.")
    else:
        print("\nRun: make seed   or   python -m scripts.setup_hindsight")

if __name__ == "__main__":
    check()
