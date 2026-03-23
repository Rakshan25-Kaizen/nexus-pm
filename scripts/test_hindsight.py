"""
Quick test: python -m scripts.test_hindsight
Tests all 3 banks with a single reflect() call each.
Shows whether memory is seeded and working.
"""

from hindsight_client import Hindsight
from backend.config import get_settings

settings = get_settings()
client   = Hindsight(api_key=settings.hindsight_api_key, base_url=settings.hindsight_base_url)

tests = [
    (settings.hindsight_bank_members,  "Who should handle backend tasks?"),
    (settings.hindsight_bank_members,  "What is Alice's workload history?"),
    (settings.hindsight_bank_tasks,    "What are the main risk patterns for this team?"),
    (settings.hindsight_bank_meetings, "What decisions were made in Sprint 2?"),
]

print("Testing Hindsight memory banks...\n")

for bank, query in tests:
    print(f"Bank: {bank}")
    print(f"Q: {query}")
    try:
        answer = client.reflect(bank_id=bank, query=query, budget="low")
        text   = answer.text
        tl = text.lower()
        is_generic = len(text) < 80 or any(
            p in tl
            for p in (
                "no memory",
                "haven't seen",
                "don't have enough information",
                "not available in the",
                "cannot find any information",
                "i cannot find",
                "i'm sorry, but i don't have",
            )
        )
        status = "WARN - generic answer, run setup_hindsight.py" if is_generic else "PASS - memory-grounded"
        print(f"A: {text[:150]}{'...' if len(text)>150 else ''}")
        print(f"Status: {status}\n")
    except Exception as e:
        print(f"ERROR: {e}\n")
