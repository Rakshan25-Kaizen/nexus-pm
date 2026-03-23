"""
NEXUS-PM Memory Banks Setup
Run: python -m backend.memory.setup_banks
"""
from backend.memory.hindsight_client import client


def setup_banks():
    banks = [
        {
            "bank_id": "meetings-bank",
            "name": "Meeting Intelligence",
            "mission": (
                "I store summaries of team meetings, key decisions, action items, and blockers. "
                "I help recall what was decided, who committed to what, and whether past "
                "decisions led to good outcomes."
            ),
            "disposition": {"skepticism": 3, "literalism": 4, "empathy": 2},
        },
        {
            "bank_id": "members-bank",
            "name": "Team Behavioral Profiles",
            "mission": (
                "I track each team member's behavioral patterns over time — task history, "
                "skills, failures, workload, reliability scores, and performance trends. "
                "I help make smarter task assignments and flag overload or skill mismatches."
            ),
            "disposition": {"skepticism": 2, "literalism": 3, "empathy": 4},
        },
        {
            "bank_id": "tasks-bank",
            "name": "Task Risk History",
            "mission": (
                "I store all task outcomes, delay reasons, blocker events, and strategy "
                "adaptations. I help identify risk patterns and predict which tasks are "
                "likely to be delayed based on this team's specific history."
            ),
            "disposition": {"skepticism": 4, "literalism": 4, "empathy": 2},
        },
    ]

    created = 0
    for bank in banks:
        try:
            client.banks.create(
                bank_id=bank["bank_id"],
                name=bank["name"],
                mission=bank["mission"],
                disposition=bank["disposition"],
            )
            print(f"✓ Created bank: {bank['bank_id']}")
            created += 1
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "conflict" in error_msg:
                print(f"○ Bank already exists: {bank['bank_id']}")
            else:
                print(f"✗ Failed to create {bank['bank_id']}: {e}")

    print(f"\nSetup complete. {created} banks created, {3 - created} already existed.")


if __name__ == "__main__":
    setup_banks()
