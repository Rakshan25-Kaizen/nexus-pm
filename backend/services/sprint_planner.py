"""
NEXUS-PM Sprint Planner — AI-powered sprint planning with memory context.
"""
from backend.agent.llm_client import call_llm_json
from backend.agent.prompts import SPRINT_PLAN_APT
from backend.memory.recall import (
    recall_member_history,
    recall_recent_outcomes,
    recall_project_blockers,
)
from backend.memory.retain import retain_sprint_plan


async def generate_plan(
    project_id: str, available_tasks: list, members: list
) -> dict:
    member_histories = []
    for m in members:
        h = recall_member_history(m, "general", top_k=3)
        member_histories.append(f"{m}: {'; '.join(h[:2]) if h else 'no history'}")

    velocity = recall_recent_outcomes(project_id, days=30)
    blockers = recall_project_blockers(project_id, top_k=3)
    memory_context = "\n".join(member_histories + velocity[:3] + blockers[:2])

    tasks_list = "\n".join(
        f"- id:{t.get('id', '?')} title:{t.get('title', '?')} cat:{t.get('category', '?')}"
        for t in available_tasks
    )
    # Build member list with roles and skill constraints
    MEMBER_ROLES = {
        "Alice":  ("Backend Engineer",   ["Backend", "ML"],             2),
        "Bob":    ("Frontend Engineer",  ["Frontend", "Design"],        3),
        "Priya":  ("Full Stack Engineer", ["Backend", "Frontend", "DevOps", "Testing"], 3),
        "Raj":    ("QA Engineer",        ["Testing", "General"],        4),
    }

    # Filter candidates for each task based on hard role categories
    tasks_with_candidates = []
    for t in available_tasks:
        cat = t.get('category', 'General')
        candidates = [
            m for m in members
            if cat in MEMBER_ROLES.get(m, (m, ["General"], 3))[1]
        ]
        # Fallback to everyone if cat is General or nobody found
        if not candidates or cat == 'General':
            candidates = members
            
        tasks_with_candidates.append(
            f"- id:{t.get('id', '?')} title:{t.get('title', '?')} cat:{cat} | CANDIDATES: {', '.join(candidates)}"
        )

    tasks_list = "\n".join(tasks_with_candidates)
    
    member_lines = []
    for m in members:
        role, allowed_cats, cap = MEMBER_ROLES.get(m, (m, ["General"], 3))
        member_lines.append(
            f"- {m} ({role}) | Capacity: {cap} tasks | Skills: {', '.join(allowed_cats)}"
        )
    members_list = "\n".join(member_lines)

    # Add hard constraint preamble to memory context
    constraint_block = """
HARD ASSIGNMENT RULES — NEVER VIOLATE THESE:
1. Bob is a Frontend Engineer. ONLY assign Frontend or Design tasks to Bob. No exceptions.
2. Raj is a QA Engineer. ONLY assign Testing or General tasks to Raj. No exceptions.
3. Alice is a Backend Engineer. Max 1 high-complexity task per sprint.
4. If a task has "CANDIDATES" listed, you MUST choose from that list only.

"""
    prompt = SPRINT_PLAN_APT.format(
        tasks_list=tasks_list,
        members_list=members_list,
        memory_context=constraint_block + (memory_context or "No prior sprint data."),
    )
    plan = call_llm_json(prompt)

    # Hallucination guard
    for a in plan.get("assignments", []):
        if a.get("assigned_to") not in members and members:
            a["assigned_to"] = members[0]

    sprint_summary = ", ".join(
        f"{a['assigned_to']}:{a['task_id']}" for a in plan.get("assignments", [])
    )
    retain_sprint_plan(project_id, plan.get("sprint_name", "?"), sprint_summary)
    plan["memories_used"] = len(member_histories) + len(velocity[:3]) + len(blockers[:2])
    plan["memory_evidence"] = member_histories[:6] + velocity[:2]
    return plan


async def analyze_sprint_health(project_id: str, sprint_id: str) -> dict:
    return {
        "sprint_id": sprint_id,
        "status": "healthy",
        "note": "Full health analysis available after sprint completion",
    }
