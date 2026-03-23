"""
NEXUS-PM Hindsight Setup Script
Runs: python -m scripts.setup_hindsight

Seeds all 3 Hindsight memory banks with:
  - 8 behavioral memory events
  - 3 meeting transcripts
  - 1 team skills document
  - 3 Mental Models (highest-priority knowledge for reflect())

All via API — no dashboard interaction needed.
Run this ONCE after setup_banks.py has created the banks.
"""

import time
import sys
from hindsight_client import Hindsight
from backend.config import get_settings

settings = get_settings()

client = Hindsight(api_key=settings.hindsight_api_key, base_url=settings.hindsight_base_url)

BANK_MEMBERS  = settings.hindsight_bank_members
BANK_TASKS    = settings.hindsight_bank_tasks
BANK_MEETINGS = settings.hindsight_bank_meetings

RETAIN_PASS = 0
RETAIN_FAIL = 0
MM_PASS = 0
MM_FAIL = 0


def retain(bank, content, context, metadata, label):
    global RETAIN_PASS, RETAIN_FAIL
    try:
        client.retain(
            bank_id=bank,
            content=content,
            context=context,
            metadata=metadata
        )
        print(f"  OK  {label}")
        RETAIN_PASS += 1
    except Exception as e:
        print(f"  ERR {label}: {e}")
        RETAIN_FAIL += 1


def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


# ─────────────────────────────────────────────────────────────
# STEP 1 — SEED 8 BEHAVIORAL MEMORY EVENTS
# ─────────────────────────────────────────────────────────────
section("STEP 1: Seeding behavioral memory events")

retain(
    bank=BANK_TASKS,
    content=(
        "Sprint 1 completed. Alice was assigned 3 concurrent tasks including "
        "two high-complexity items. This caused a 2-day delay on Bob's landing "
        "page task due to upstream dependency bottleneck. Team agreed to cap "
        "high-complexity task assignments at 2 per engineer per sprint."
    ),
    context="Sprint 1 overload pattern detected",
    metadata={"type": "sprint_completed", "pattern": "overload", "sprint": 1},
    label="[1/8] Sprint 1 overload -> tasks-bank"
)

retain(
    bank=BANK_MEMBERS,
    content=(
        "Bob was assigned a backend data processing pipeline in Sprint 2 despite "
        "being a frontend engineer. He struggled with async Python patterns and "
        "PostgreSQL query optimisation. Task slipped 3 days. Decision: backend "
        "data and pipeline tasks should only be assigned to Alice or Priya going forward."
    ),
    context="Bob skill mismatch confirmed Sprint 2",
    metadata={"member": "Bob", "type": "skill_mismatch", "pattern": "skill_mismatch", "sprint": 2},
    label="[2/8] Bob skill mismatch -> members-bank"
)

retain(
    bank=BANK_MEMBERS,
    content=(
        "Alice was overloaded in Sprint 2 for the second consecutive sprint despite "
        "Sprint 1 retrospective agreement. She had auth flow (high complexity), "
        "API tests (medium), and a third task simultaneously. API tests slipped "
        "2 days. Automated workload warnings were requested to prevent recurrence."
    ),
    context="Alice overload repeat incident Sprint 2",
    metadata={"member": "Alice", "type": "overload_repeat", "pattern": "overload", "sprint": 2},
    label="[3/8] Alice overload repeat -> members-bank"
)

retain(
    bank=BANK_TASKS,
    content=(
        "After detecting the overload pattern in sprints 1 and 2, NEXUS updated "
        "its task assignment scoring weights. Current load weight increased from "
        "0.20 to 0.35. Completion rate weight decreased from 0.35 to 0.30. "
        "NEXUS will now prioritise workload balance over raw completion rate "
        "when assigning tasks."
    ),
    context="Strategy adaptation after Sprint 2",
    metadata={"type": "strategy_adaptation", "sprint": 2,
              "old_weights": {"current_load": 0.20, "completion_rate": 0.35},
              "new_weights": {"current_load": 0.35, "completion_rate": 0.30}},
    label="[4/8] Strategy adaptation -> tasks-bank"
)

retain(
    bank=BANK_MEMBERS,
    content=(
        "Priya delivered CI/CD pipeline setup and performance optimisation in "
        "Sprint 3 both on time with zero blockers. API latency reduced from "
        "420ms to 85ms. Priya is the strongest full-stack member and best fit "
        "for DevOps, infra, and backend performance tasks. She consistently "
        "delivers complex tasks without delay."
    ),
    context="Priya strength confirmed Sprint 3",
    metadata={"member": "Priya", "type": "member_strength", "sprint": 3},
    label="[5/8] Priya strength -> members-bank"
)

retain(
    bank=BANK_TASKS,
    content=(
        "Raj's test automation framework task slipped 1 day in Sprint 3 because "
        "product added 2 new user flows mid-sprint. This is a process failure, "
        "not a Raj performance issue. Raj's test documentation is consistently "
        "thorough. Decision: all sprint requirements must be signed off and "
        "locked before kickoff."
    ),
    context="Raj delay process issue Sprint 3",
    metadata={"member": "Raj", "type": "process_risk", "sprint": 3},
    label="[6/8] Raj process risk -> tasks-bank"
)

retain(
    bank=BANK_MEMBERS,
    content=(
        "Bob has delivered all frontend tasks (landing page, dashboard components, "
        "mobile responsive design) on time across 3 sprints. His only delay was "
        "the backend data pipeline — a confirmed skill mismatch. Assigning "
        "backend, data, or DevOps tasks to Bob carries high delay risk based "
        "on observed pattern across two sprints."
    ),
    context="Bob skill boundary confirmed across sprints",
    metadata={"member": "Bob", "type": "member_pattern", "sprint": 3},
    label="[7/8] Bob skill boundary -> members-bank"
)

retain(
    bank=BANK_TASKS,
    content=(
        "Sprint 4 has a critical dependency chain: Priya's sprint planner "
        "endpoint requires Alice's memory layer API to be stable first. "
        "Alice is the only backend engineer and is working on the highest-complexity "
        "task this sprint (8 story points). If Alice encounters delays, Priya "
        "will be blocked and the sprint 4 goal is at risk. Daily check-ins "
        "on Alice's progress are recommended."
    ),
    context="Sprint 4 critical dependency Alice to Priya",
    metadata={"type": "sprint_risk", "pattern": "dependency_risk", "sprint": 4},
    label="[8/8] Sprint 4 dependency risk -> tasks-bank"
)

# ─────────────────────────────────────────────────────────────
# STEP 2 — SEED 3 MEETING TRANSCRIPTS
# ─────────────────────────────────────────────────────────────
section("STEP 2: Seeding meeting transcripts")

retain(
    bank=BANK_MEETINGS,
    content=(
        "Alice: Sprint 1 went well overall. REST API and DB schema shipped clean.\n"
        "Bob: Landing page slipped 2 days. I was waiting on design feedback while Alice was busy.\n"
        "Alice: Yeah I had 3 tasks at the same time for a few days. Felt stretched.\n"
        "Priya: We should cap Alice at 2 high-complexity tasks per sprint.\n"
        "Raj: Test coverage looks good. I'd like earlier access to staging next sprint.\n"
        "Bob: Can we use a proper task limit rule going forward?\n"
        "Alice: Yes. Let's enforce max 2 high-complexity per person."
    ),
    context="Meeting transcript: Sprint 1 Retrospective",
    metadata={"type": "meeting_transcript", "title": "Sprint 1 Retrospective", "sprint": 1},
    label="[1/3] Sprint 1 retro transcript -> meetings-bank"
)

retain(
    bank=BANK_MEETINGS,
    content=(
        "Bob: I struggled with the data pipeline. Async Python patterns were harder than expected. Slipped 3 days.\n"
        "Priya: We flagged this in kickoff. Backend data work should go to Alice or me going forward.\n"
        "Alice: I also slipped on API tests. I had too much on again.\n"
        "Raj: The overload cap is not being enforced. Alice had 3 tasks again.\n"
        "Priya: We need an automated warning when someone hits their task limit.\n"
        "Alice: Agree. The rule exists but nobody checked.\n"
        "Bob: I will stick to frontend. Lesson learned."
    ),
    context="Meeting transcript: Sprint 2 Retrospective",
    metadata={"type": "meeting_transcript", "title": "Sprint 2 Retrospective", "sprint": 2},
    label="[2/3] Sprint 2 retro transcript -> meetings-bank"
)

retain(
    bank=BANK_MEETINGS,
    content=(
        "Priya: Sprint 4 is the AI sprint. NEXUS memory layer, analytics, sprint planner.\n"
        "Alice: Memory layer is high complexity. One task only for me this sprint.\n"
        "Bob: Analytics charts are mine. Recharts should be straightforward.\n"
        "Priya: I will take the sprint planner endpoint once Alice has the memory API stable.\n"
        "Raj: I will write E2E tests once the AI flows are testable. Can we lock requirements this time?\n"
        "Priya: Yes. All specs signed off before sprint starts.\n"
        "Alice: NEXUS is going to be really useful once memory works. Let us make it count."
    ),
    context="Meeting transcript: Sprint 4 Kickoff",
    metadata={"type": "meeting_transcript", "title": "Sprint 4 Kickoff", "sprint": 4},
    label="[3/3] Sprint 4 kickoff transcript -> meetings-bank"
)

# ─────────────────────────────────────────────────────────────
# STEP 3 — ADD TEAM SKILLS DOCUMENT
# ─────────────────────────────────────────────────────────────
section("STEP 3: Adding team skills document")

skills_doc = """
NEXUS Demo Project — Team Skills and Capacity Reference

Alice Chen — Backend Engineer
  Skills: Python, FastAPI, PostgreSQL, SQLAlchemy, ML, XGBoost
  Capacity: Maximum 2 concurrent high-complexity tasks
  Strengths: Backend APIs, database design, ML pipelines, auth flows
  Risk flag: Overloaded in Sprint 1 and Sprint 2 when given 3 or more tasks simultaneously.
             Third concurrent task consistently causes 2-day slippage.

Bob Kumar — Frontend Engineer
  Skills: React, TypeScript, Tailwind CSS, UI/UX design, Recharts, responsive design
  Capacity: 3 tasks standard
  Strengths: All frontend tasks. Consistently delivers on time across all sprints.
  Risk flag: HIGH RISK on backend, data pipeline, DevOps tasks.
             Confirmed 3-day delay on backend pipeline Sprint 2 (skill mismatch).
             Do not assign backend or data tasks to Bob.

Priya Sharma — Full Stack Engineer
  Skills: Python, React, DevOps, GitHub Actions, Redis, Testing, performance tuning
  Capacity: 3 tasks standard
  Strengths: DevOps, infra, backend performance, full stack delivery.
             Top performer Sprint 3: API latency 420ms to 85ms.
  Risk flag: Sprint 4 is blocked on Alice. Monitor Alice progress daily.

Raj Patel — QA Engineer
  Skills: Selenium, Pytest, Documentation, Test Automation, UAT
  Capacity: 4 tasks (testing tasks are lower complexity)
  Strengths: Thorough test documentation, consistent defect detection.
             Found 3 edge-case bugs in Sprint 3 UAT that would have reached production.
  Risk flag: Mid-sprint scope changes cause delays. Not a performance issue.
             Lock all test scope requirements before sprint kickoff.
"""

retain(
    bank=BANK_MEMBERS,
    content=skills_doc,
    context="Team skills matrix and capacity reference document",
    metadata={"type": "team_reference", "document": "skills_matrix"},
    label="Team skills document -> members-bank"
)

# ─────────────────────────────────────────────────────────────
# STEP 4 — CREATE 3 MENTAL MODELS
# ─────────────────────────────────────────────────────────────
# Mental models are checked FIRST by reflect() before any search.
# They run reflect() internally so memories must be indexed first.
# Wait before creating them.
# ─────────────────────────────────────────────────────────────
section("STEP 4: Creating mental models (waiting 30s for indexing...)")

print("  Waiting 30 seconds for Hindsight to index memories...")
for i in range(6):
    time.sleep(5)
    print(f"  {(i+1)*5}s...")

mental_models = [
    {
        "name":         "Backend task assignment rule",
        "source_query": "Who should be assigned backend and data pipeline tasks, and why? Include specific sprint evidence.",
        "bank":         BANK_MEMBERS,
        "tags":         ["assignment", "backend", "skill-routing", "Bob", "Alice", "Priya"]
    },
    {
        "name":         "Alice workload policy",
        "source_query": "What is Alice's workload capacity limit, what happens when she exceeds it, and how many times has this occurred?",
        "bank":         BANK_MEMBERS,
        "tags":         ["alice", "workload", "capacity", "overload", "policy"]
    },
    {
        "name":         "Team failure patterns across sprints",
        "source_query": "What recurring failure patterns has this team shown across Sprints 1, 2, and 3? Include the pattern name, who it affects, and how many times it occurred.",
        "bank":         BANK_TASKS,
        "tags":         ["patterns", "failures", "risk", "retrospective", "overload", "skill_mismatch"]
    },
]

for i, mm in enumerate(mental_models):
    try:
        result = client.create_mental_model(
            bank_id=mm["bank"],
            name=mm["name"],
            source_query=mm["source_query"],
            tags=mm["tags"]
        )
        print(f"  OK  [{i+1}/3] '{mm['name']}'")
        op_id = getattr(result, "operation_id", None)
        print(f"       operation_id: {op_id if op_id is not None else '(pending)'}")
        MM_PASS += 1
    except Exception as e:
        print(f"  ERR [{i+1}/3] '{mm['name']}': {e}")
        MM_FAIL += 1

# ─────────────────────────────────────────────────────────────
# STEP 5 — VERIFICATION TESTS
# ─────────────────────────────────────────────────────────────
section("STEP 5: Verification tests")

print("\nWaiting 10 more seconds for mental models to complete...")
time.sleep(10)

test_results = []

verification_queries = [
    {
        "bank":    BANK_MEMBERS,
        "query":   "Who should handle backend tasks?",
        "must_contain": ["Alice", "Priya", "Bob"],
        "should_mention": ["mismatch", "frontend", "Sprint 2", "delay"]
    },
    {
        "bank":    BANK_MEMBERS,
        "query":   "What is Alice's workload history?",
        "must_contain": ["Alice"],
        "should_mention": ["overload", "Sprint 1", "Sprint 2", "2 tasks", "3 tasks"]
    },
    {
        "bank":    BANK_TASKS,
        "query":   "What patterns of failure has this team shown?",
        "must_contain": ["overload", "mismatch"],
        "should_mention": ["Alice", "Bob", "Raj", "pattern"]
    },
]

for i, test in enumerate(verification_queries):
    print(f"\n  Test {i+1}: '{test['query']}'")
    try:
        answer = client.reflect(
            bank_id=test["bank"],
            query=test["query"],
            budget="mid"
        )
        text = answer.text
        print(f"  Answer: {text[:200]}{'...' if len(text)>200 else ''}")

        # Check if answer is grounded
        grounded = any(word.lower() in text.lower() for word in test["should_mention"])
        has_names = all(name in text for name in test["must_contain"])

        if grounded and has_names:
            print(f"  PASS — answer is specific and memory-grounded")
            test_results.append(True)
        else:
            print(f"  WARN — answer may be generic (missing: {[w for w in test['should_mention'] if w.lower() not in text.lower()]})")
            test_results.append(False)

    except Exception as e:
        print(f"  FAIL — reflect() error: {e}")
        test_results.append(False)

# ─────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────
section("SETUP COMPLETE — Summary")

tests_passed = sum(test_results)
tests_total  = len(test_results)

retain_ok = RETAIN_FAIL == 0
mm_ok = MM_FAIL == 0
verify_ok = tests_passed == tests_total
all_ok = retain_ok and mm_ok and verify_ok

print(f"""
  Memory items retained:   {RETAIN_PASS} (8 behavioral + 3 meetings + 1 team skills doc)
  Mental models created:   {MM_PASS}/3 (check dashboard Mental Models tab)
  Retain operations:       {RETAIN_PASS} passed / {RETAIN_FAIL} failed
  Verification tests:      {tests_passed}/{tests_total} passed

  Overall status: {'ALL GOOD - NEXUS is ready' if all_ok else 'ISSUES FOUND - see errors above'}

  Next steps:
    1. Open ui.hindsight.vectorize.io
       - World Facts tab: should show 30+ memories
       - Mental Models tab: should show 3 models
       - Graph view: should show entity nodes (Alice, Bob, Priya, Raj)
       - Observations tab: auto-populates within 2 minutes

    2. Test NEXUS in your app:
       Go to /agent and ask:
         "Who should handle backend tasks?"
         "What is Alice's workload history?"
         "What patterns has our team shown?"
       All 3 should give specific, evidence-based answers.

    3. If World Facts still shows 0 after this script:
       Check your .env — HINDSIGHT_API_KEY and bank IDs must match exactly.
       Run: python -m backend.memory.setup_banks
       Then re-run: python -m scripts.setup_hindsight
""")

if not all_ok:
    sys.exit(1)
