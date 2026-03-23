"""
NEXUS-PM Seed Script — Populates SQLite DB + Hindsight Memory Banks
Run: python -m data.seed
"""
import sys
import os
import asyncio
import json
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ───────────────────────────────────────────────────────────────
# SEED DATA
# ───────────────────────────────────────────────────────────────

PROJECT = {
    "id": "project-1",
    "name": "NEXUS Demo Project",
}

MEMBERS = [
    {"id": "member-1", "name": "Alice", "role": "Backend Engineer",
     "skills": ["Python", "FastAPI", "PostgreSQL", "ML"]},
    {"id": "member-2", "name": "Bob",   "role": "Frontend Engineer",
     "skills": ["React", "TypeScript", "UI/UX", "Tailwind"]},
    {"id": "member-3", "name": "Priya", "role": "Full Stack Engineer",
     "skills": ["Python", "React", "DevOps", "Testing"]},
    {"id": "member-4", "name": "Raj",   "role": "QA Engineer",
     "skills": ["Testing", "Selenium", "Pytest", "Documentation"]},
]

SPRINTS = [
    {"id": "sprint-1", "sprint_number": 1, "name": "Sprint 1 — Foundation",
     "start_date": "2025-02-01", "end_date": "2025-02-14",
     "goal": "Set up core backend infrastructure and REST API", "status": "completed"},
    {"id": "sprint-2", "sprint_number": 2, "name": "Sprint 2 — Integration",
     "start_date": "2025-02-15", "end_date": "2025-02-28",
     "goal": "Connect all services, complete auth, and integration tests", "status": "completed"},
    {"id": "sprint-3", "sprint_number": 3, "name": "Sprint 3 — Quality",
     "start_date": "2025-03-01", "end_date": "2025-03-15",
     "goal": "Performance optimisation, test automation, mobile responsiveness", "status": "completed"},
    {"id": "sprint-4", "sprint_number": 4, "name": "Sprint 4 — Current",
     "start_date": "2025-03-16", "end_date": "2025-03-30",
     "goal": "Ship NEXUS AI memory layer and analytics dashboard", "status": "active"},
]

TASKS = [
    # Sprint 1
    {"id": "task-1", "title": "Build REST API endpoints", "category": "Backend",
     "complexity": "high", "assigned_to": "member-1", "status": "done",
     "sprint_id": "sprint-1", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.1, "insight": "Clean implementation. Alice delivered on time despite high complexity."},
    {"id": "task-2", "title": "Setup database schema", "category": "Backend",
     "complexity": "medium", "assigned_to": "member-1", "status": "done",
     "sprint_id": "sprint-1", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.1, "insight": "Used async patterns effectively. Schema well-normalised."},
    {"id": "task-3", "title": "Design landing page", "category": "Frontend",
     "complexity": "medium", "assigned_to": "member-2", "status": "done",
     "sprint_id": "sprint-1", "delay_days": 2, "blocker_type": "overload",
     "reason": "Alice had 3 concurrent tasks creating bottleneck for Bob's design reviews",
     "risk_score": 0.45, "insight": "Delayed 2 days due to upstream dependency on Alice."},
    # Sprint 2
    {"id": "task-4", "title": "Implement auth flow", "category": "Backend",
     "complexity": "high", "assigned_to": "member-1", "status": "done",
     "sprint_id": "sprint-2", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.15, "insight": "Solid OAuth2 implementation. Security review passed."},
    {"id": "task-5", "title": "Create dashboard components", "category": "Frontend",
     "complexity": "medium", "assigned_to": "member-2", "status": "done",
     "sprint_id": "sprint-2", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.1, "insight": "Good component architecture. Well-typed components."},
    {"id": "task-6", "title": "Backend data processing pipeline", "category": "Backend",
     "complexity": "high", "assigned_to": "member-2", "status": "done",
     "sprint_id": "sprint-2", "delay_days": 3, "blocker_type": "skill_mismatch",
     "reason": "Bob is frontend-focused, struggled with async Python and DB query optimisation",
     "risk_score": 0.72, "insight": "Delivered 3 days late. Skill mismatch confirmed."},
    {"id": "task-7", "title": "API integration tests", "category": "Testing",
     "complexity": "medium", "assigned_to": "member-1", "status": "done",
     "sprint_id": "sprint-2", "delay_days": 2, "blocker_type": "overload",
     "reason": "Alice had auth flow + API tests simultaneously — pushed over capacity",
     "risk_score": 0.68, "insight": "Alice's second overload incident. Pattern confirmed."},
    # Sprint 3
    {"id": "task-8", "title": "CI/CD pipeline setup", "category": "DevOps",
     "complexity": "medium", "assigned_to": "member-3", "status": "done",
     "sprint_id": "sprint-3", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.1, "insight": "Efficient DevOps. Priya is the go-to for infra tasks."},
    {"id": "task-9", "title": "User acceptance testing", "category": "Testing",
     "complexity": "low", "assigned_to": "member-4", "status": "done",
     "sprint_id": "sprint-3", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.1, "insight": "Thorough test documentation. Found 3 edge-case bugs."},
    {"id": "task-10", "title": "Performance optimisation", "category": "Backend",
     "complexity": "high", "assigned_to": "member-3", "status": "done",
     "sprint_id": "sprint-3", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.12, "insight": "API p95 latency reduced from 420ms to 85ms."},
    {"id": "task-11", "title": "Mobile responsive design", "category": "Frontend",
     "complexity": "medium", "assigned_to": "member-2", "status": "done",
     "sprint_id": "sprint-3", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.1, "insight": "Clean responsive implementation. Bob in his element."},
    {"id": "task-12", "title": "Test automation framework", "category": "Testing",
     "complexity": "high", "assigned_to": "member-4", "status": "done",
     "sprint_id": "sprint-3", "delay_days": 1, "blocker_type": "unclear_requirements",
     "reason": "Test scope changed mid-sprint when product added 2 new flows",
     "risk_score": 0.35, "insight": "1-day delay due to scope change. Process fix, not Raj fix."},
    # Sprint 4 (active)
    {"id": "task-13", "title": "NEXUS memory layer integration", "category": "Backend",
     "complexity": "high", "assigned_to": "member-1", "status": "in_progress",
     "sprint_id": "sprint-4", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.28, "insight": None},
    {"id": "task-14", "title": "Analytics dashboard charts", "category": "Frontend",
     "complexity": "medium", "assigned_to": "member-2", "status": "in_progress",
     "sprint_id": "sprint-4", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.2, "insight": None},
    {"id": "task-15", "title": "Sprint planner AI endpoint", "category": "Backend",
     "complexity": "high", "assigned_to": "member-3", "status": "todo",
     "sprint_id": "sprint-4", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.3, "insight": None},
    {"id": "task-16", "title": "End-to-end test suite for AI", "category": "Testing",
     "complexity": "medium", "assigned_to": "member-4", "status": "todo",
     "sprint_id": "sprint-4", "delay_days": 0, "blocker_type": None, "reason": None,
     "risk_score": 0.22, "insight": None},
]

MEMORY_EVENTS = [
    {"bank": "tasks", "title": "Sprint 1 completed — overload pattern detected",
     "type": "sprint_completed",
     "text": "Sprint 1 completed. Alice was assigned 3 concurrent tasks including two high-complexity items. This caused a 2-day delay on Bob's landing page task due to upstream dependency bottleneck. Team agreed to cap high-complexity task assignments at 2 per engineer per sprint.",
     "metadata": {"type": "sprint_completed", "severity": "warning"}},
    {"bank": "members", "title": "Bob struggled with backend data pipeline",
     "type": "skill_mismatch",
     "text": "Bob was assigned a backend data processing pipeline in Sprint 2 despite being a frontend engineer. He struggled with async Python patterns and PostgreSQL query optimisation. Task slipped 3 days. Decision: backend data and pipeline tasks should only be assigned to Alice or Priya going forward.",
     "metadata": {"type": "skill_mismatch", "severity": "high"}},
    {"bank": "members", "title": "Alice overloaded again — second incident",
     "type": "overload_repeat",
     "text": "Alice was overloaded in Sprint 2 for the second consecutive sprint despite Sprint 1 retrospective agreement. She had auth flow (high complexity), API tests (medium), and a third task simultaneously. API tests slipped 2 days. Automated workload warnings were requested to prevent recurrence.",
     "metadata": {"type": "overload_repeat", "severity": "high"}},
    {"bank": "tasks", "title": "NEXUS assignment strategy updated",
     "type": "strategy_adaptation",
     "text": "After detecting the overload pattern in sprints 1 and 2, NEXUS updated its task assignment scoring weights. Current load weight increased from 0.20 to 0.35. Completion rate weight decreased from 0.35 to 0.30. NEXUS will now be more conservative about assigning tasks to members who are already loaded, even if they have high completion rates.",
     "metadata": {"type": "strategy_adaptation", "severity": "info"}},
    {"bank": "members", "title": "Priya confirmed as best fit for DevOps",
     "type": "member_strength",
     "text": "Priya delivered CI/CD pipeline setup and performance optimisation in Sprint 3 both on time with zero blockers. API latency reduced from 420ms to 85ms. Priya is the strongest full-stack member and best fit for DevOps, infra, and backend performance tasks. She consistently delivers complex tasks without delay.",
     "metadata": {"type": "member_strength", "severity": "info"}},
    {"bank": "tasks", "title": "Raj delayed by mid-sprint requirement change",
     "type": "process_risk",
     "text": "Raj's test automation framework task slipped 1 day in Sprint 3 because product added 2 new user flows mid-sprint. This is a process failure, not a Raj performance issue. Raj's test documentation is consistently thorough. Decision: all sprint requirements must be signed off and locked before kickoff.",
     "metadata": {"type": "process_risk", "severity": "warning"}},
    {"bank": "members", "title": "Bob strong on frontend — high risk on backend",
     "type": "member_pattern",
     "text": "Bob has delivered all frontend tasks (landing page, dashboard components, mobile responsive design) on time. His only delay was the backend data pipeline — a confirmed skill mismatch. Assigning backend, data, or DevOps tasks to Bob carries high delay risk based on observed pattern across two sprints.",
     "metadata": {"type": "member_pattern", "severity": "info"}},
    {"bank": "tasks", "title": "Sprint 4 critical dependency — Priya blocked on Alice",
     "type": "sprint_risk",
     "text": "Sprint 4 has a critical dependency chain: Priya's sprint planner endpoint requires Alice's memory layer API to be stable first. Alice is the only backend engineer and is working on the highest-complexity task this sprint (8 story points). If Alice encounters delays, Priya will be blocked and the sprint 4 goal is at risk. Daily check-ins on Alice's progress are recommended.",
     "metadata": {"type": "sprint_risk", "severity": "warning"}},
]

MEETING_TRANSCRIPTS = [
    {"title": "Sprint 1 Retrospective", "sprint_id": "sprint-1",
     "transcript": "Alice: Sprint 1 went well overall. REST API and DB schema shipped clean. Bob: Landing page slipped 2 days — I was waiting on design feedback while Alice was busy. Alice: Yeah I had 3 tasks at the same time for a few days. Felt stretched. Priya: We should cap Alice at 2 high-complexity tasks per sprint. She's our only backend person. Raj: Test coverage looks good. I'd like earlier access to staging next sprint. Bob: Can we use a proper task limit rule going forward? Alice: Yes. Let's enforce max 2 high-complexity per person.",
     "summary": "Sprint 1 delivered core backend on time. Alice hit overload with 3 concurrent tasks causing 2-day delay. Team agreed to cap high-complexity task assignments at 2 per person per sprint.",
     "attendees": ["Alice", "Bob", "Priya", "Raj"], "date": "2025-02-14"},
    {"title": "Sprint 2 Retrospective", "sprint_id": "sprint-2",
     "transcript": "Bob: I struggled with the data pipeline. Async Python patterns were harder than expected. Slipped 3 days. Priya: We flagged this in kickoff. Backend data work should go to Alice or me going forward. Alice: I also slipped on API tests — I had too much on again. Raj: The overload cap is not being enforced. Alice had 3 tasks again. Priya: We need an automated warning when someone hits their task limit. Alice: Agree. The rule exists but nobody checked. Bob: I will stick to frontend. Lesson learned.",
     "summary": "Two incidents: Bob delayed 3 days on backend pipeline (skill mismatch), Alice overloaded again despite sprint 1 agreement.",
     "attendees": ["Alice", "Bob", "Priya", "Raj"], "date": "2025-02-28"},
    {"title": "Sprint 4 Kickoff", "sprint_id": "sprint-4",
     "transcript": "Priya: Sprint 4 is the AI sprint — NEXUS memory layer, analytics, sprint planner. Alice: Memory layer is high complexity. One task only for me this sprint. Bob: Analytics charts are mine. Recharts should be straightforward. Priya: I will take the sprint planner endpoint once Alice has the memory API stable. Raj: I will write E2E tests once the AI flows are testable. Can we lock requirements this time? Priya: Yes — all specs signed off before sprint starts. Alice: NEXUS is going to be really useful once memory works.",
     "summary": "Sprint 4 is the AI feature sprint. Alice on memory layer (single task). Priya on sprint planner (after Alice). Requirements locked.",
     "attendees": ["Alice", "Bob", "Priya", "Raj"], "date": "2025-03-16"},
]

STRATEGY_ADAPTATION = {
    "project_id": "project-1",
    "trigger_pattern": "overload_pattern",
    "failure_rate": 0.50,
    "old_weights": {"completion_rate": 0.35, "delay_history": 0.25, "recent_velocity": 0.20, "current_load": 0.20},
    "new_weights": {"completion_rate": 0.30, "delay_history": 0.20, "recent_velocity": 0.15, "current_load": 0.35},
}

NUDGES = [
    {"project_id": "project-1", "nudge_type": "overload_warning",
     "message": "Alice has 1 active high-complexity task (memory layer — 8 points). Based on sprint history, assigning another task now risks delay. Last two overload incidents led to 2-day slips.",
     "target_member": "Alice", "severity": "warning"},
    {"project_id": "project-1", "nudge_type": "skill_mismatch_prevention",
     "message": "Sprint planner endpoint is a backend Python task. Only Alice or Priya should be assigned — Bob has a confirmed pattern of delays on backend tasks.",
     "target_member": None, "severity": "info"},
    {"project_id": "project-1", "nudge_type": "dependency_alert",
     "message": "Priya's sprint planner task is blocked on Alice's memory layer API. Alice is 3 days into a high-complexity task. Check progress today.",
     "target_member": "Priya", "severity": "warning"},
]


# ───────────────────────────────────────────────────────────────
# MAIN SEED FUNCTION
# ───────────────────────────────────────────────────────────────

async def run_seed():
    print("🌱 NEXUS-PM seed starting...\n")

    # Import after path setup
    from backend.database import async_session, init_db
    from backend.models.db_models import (
        Project, Member, Task, TaskOutcome, Sprint,
        StrategyLog, Nudge, AgentInteraction,
    )
    from backend.memory.hindsight_client import client, BANK_MEETINGS, BANK_MEMBERS, BANK_TASKS

    BANK_MAP = {"tasks": BANK_TASKS, "members": BANK_MEMBERS, "meetings": BANK_MEETINGS}

    # Initialize DB tables
    await init_db()
    print("  ✓ Database tables created")

    async with async_session() as db:
        # 1. Project
        existing = await db.get(Project, "project-1")
        if existing:
            print("  ⚠ Project already exists — clearing old data...")
            # Delete in reverse dependency order
            from sqlalchemy import delete
            await db.execute(delete(TaskOutcome))
            await db.execute(delete(AgentInteraction))
            await db.execute(delete(Nudge))
            await db.execute(delete(StrategyLog))
            await db.execute(delete(Task))
            await db.execute(delete(Sprint))
            await db.execute(delete(Member))
            await db.execute(delete(Project))
            await db.commit()
            print("  ✓ Old data cleared")

        project = Project(id=PROJECT["id"], name=PROJECT["name"])
        db.add(project)
        await db.commit()
        print(f"  ✓ Project: {PROJECT['name']}")

        # 2. Members
        for i, m in enumerate(MEMBERS, 1):
            member = Member(id=m["id"], project_id="project-1", name=m["name"], role=m["role"])
            member.skills = m["skills"]
            db.add(member)
            print(f"  Creating member {i}/{len(MEMBERS)}: {m['name']}...")
        await db.commit()
        print(f"  ✓ Members: {len(MEMBERS)}")

        # 3. Sprints
        for s in SPRINTS:
            sprint = Sprint(
                id=s["id"], project_id="project-1", sprint_number=s["sprint_number"],
                name=s["name"], start_date=datetime.strptime(s["start_date"], "%Y-%m-%d"),
                end_date=datetime.strptime(s["end_date"], "%Y-%m-%d"),
                goal=s["goal"], status=s["status"],
            )
            db.add(sprint)
        await db.commit()
        print(f"  ✓ Sprints: {len(SPRINTS)}")

        # 4. Tasks + TaskOutcomes for completed tasks
        outcomes_created = 0
        for i, t in enumerate(TASKS, 1):
            task = Task(
                id=t["id"], project_id="project-1", title=t["title"],
                category=t["category"], complexity=t["complexity"],
                assigned_to=t["assigned_to"], status=t["status"],
                risk_score=t.get("risk_score"), is_blocking=False,
            )
            db.add(task)

            # Create outcome for completed tasks
            if t["status"] == "done":
                outcome = TaskOutcome(
                    task_id=t["id"], member_id=t["assigned_to"],
                    completed_at=datetime.utcnow(),
                    delay_days=t.get("delay_days", 0),
                    blocker_type=t.get("blocker_type"),
                    reason=t.get("reason"),
                    insight=t.get("insight"),
                )
                db.add(outcome)
                outcomes_created += 1

        await db.commit()
        print(f"  ✓ Tasks: {len(TASKS)} ({outcomes_created} with outcomes)")

        # 5. Strategy adaptation
        strategy = StrategyLog(
            project_id="project-1",
            trigger_pattern=STRATEGY_ADAPTATION["trigger_pattern"],
            failure_rate=STRATEGY_ADAPTATION["failure_rate"],
            old_weights=STRATEGY_ADAPTATION["old_weights"],
            new_weights=STRATEGY_ADAPTATION["new_weights"],
        )
        db.add(strategy)
        await db.commit()
        print("  ✓ Strategy adaptations: 1")

        # 6. Nudges
        for n in NUDGES:
            nudge = Nudge(
                project_id=n["project_id"], nudge_type=n["nudge_type"],
                message=n["message"], target_member=n["target_member"],
                severity=n["severity"],
            )
            db.add(nudge)
        await db.commit()
        print(f"  ✓ Nudges: {len(NUDGES)}")

    # ───────────────────────────────────────────────────────
    # HINDSIGHT MEMORY SEEDING
    # ───────────────────────────────────────────────────────
    print("\n📡 Seeding Hindsight memory banks...")

    mem_success = 0
    mem_fail = 0

    # 7. Memory events → Hindsight
    for i, event in enumerate(MEMORY_EVENTS, 1):
        bank = BANK_MAP[event["bank"]]
        try:
            client.retain(
                bank_id=bank,
                content=event["text"],
                context=event["title"],
                metadata={k: str(v) for k, v in event["metadata"].items()},
            )
            print(f"  ✓ Memory {i}/{len(MEMORY_EVENTS)}: {event['title'][:60]}...")
            mem_success += 1
        except Exception as e:
            print(f"  ⚠ Memory {i}/{len(MEMORY_EVENTS)} FAILED: {e}")
            mem_fail += 1

    # 8. Meeting transcripts → Hindsight
    for i, meeting in enumerate(MEETING_TRANSCRIPTS, 1):
        try:
            client.retain(
                bank_id=BANK_MEETINGS,
                content=meeting["transcript"],
                context=f"Meeting transcript: {meeting['title']}",
                metadata={"type": "meeting_transcript", "sprint_id": meeting["sprint_id"]},
            )
            print(f"  ✓ Meeting {i}/{len(MEETING_TRANSCRIPTS)}: {meeting['title']}")
            mem_success += 1
        except Exception as e:
            print(f"  ⚠ Meeting {i}/{len(MEETING_TRANSCRIPTS)} FAILED: {e}")
            mem_fail += 1

    # ───────────────────────────────────────────────────────
    # SUMMARY
    # ───────────────────────────────────────────────────────
    total_memories = len(MEMORY_EVENTS) + len(MEETING_TRANSCRIPTS)
    print(f"\n{'='*60}")
    print("Seed complete.")
    print(f"  SQLite:     {len(MEMBERS)} members, {len(SPRINTS)} sprints, {len(TASKS)} tasks,")
    print(f"              {len(MEETING_TRANSCRIPTS)} meetings, 1 strategy, {len(NUDGES)} nudges")
    print(f"  Hindsight:  {mem_success}/{total_memories} memories retained ({mem_fail} failed)")
    print(f"{'='*60}")
    print('NEXUS is ready. Try asking: "Who should handle backend tasks?"')


if __name__ == "__main__":
    asyncio.run(run_seed())
