"""
NEXUS-PM Digest Service — Generates morning digests using memory + DB state.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.db_models import Sprint, Task, Member
from backend.agent.llm_client import call_llm
from backend.agent.prompts import MORNING_DIGEST_APT
from backend.memory.recall import (
    recall_meeting_history,
    recall_recent_outcomes,
    recall_project_blockers,
)
from backend.memory.retain import retain_qa_interaction


async def generate_morning_digest(project_id: str, db: AsyncSession) -> str:
    """Generate a NEXUS morning digest using memory + DB state."""

    # 1. Get active sprint status
    sprint_result = await db.execute(
        select(Sprint).where(Sprint.project_id == project_id, Sprint.status == "active")
    )
    sprint = sprint_result.scalar_one_or_none()

    # 2. Get task counts
    tasks_result = await db.execute(
        select(Task).where(Task.project_id == project_id)
    )
    all_tasks = tasks_result.scalars().all()
    todo_count = sum(1 for t in all_tasks if t.status == "todo")
    in_progress = sum(1 for t in all_tasks if t.status == "in_progress")
    done_count = sum(1 for t in all_tasks if t.status == "done")
    blocked_count = sum(1 for t in all_tasks if t.status == "blocked")

    sprint_status = (
        f"Sprint: {sprint.name if sprint else 'No active sprint'}. "
        f"Tasks: {todo_count} todo, {in_progress} in progress, {done_count} done, {blocked_count} blocked."
    )

    # 3. Get team workload
    members_result = await db.execute(
        select(Member).where(Member.project_id == project_id)
    )
    members = members_result.scalars().all()
    workload_lines = []
    for m in members:
        active = sum(
            1 for t in all_tasks
            if str(t.assigned_to) == str(m.id) and t.status == "in_progress"
        )
        workload_lines.append(f"{m.name}: {active} active tasks")
    team_workload = "\n".join(workload_lines) or "No members yet."

    # 4. Recall memory context
    try:
        meeting_mems = recall_meeting_history(project_id, "recent activity risks blockers", top_k=4)
        blocker_mems = recall_project_blockers(project_id, top_k=3)
        outcome_mems = recall_recent_outcomes(project_id, days=7)
        memory_context = "\n".join(meeting_mems + outcome_mems[:2]) or "No recent memory."
        active_blockers = "\n".join(blocker_mems) or "No active blockers recorded."
    except Exception as e:
        print(f"[Digest] Warning: Memory recall failed: {e}")
        memory_context = "Memory recall unavailable."
        active_blockers = "Unable to check blockers."

    # 5. Generate digest via LLM
    prompt = MORNING_DIGEST_APT.format(
        sprint_status=sprint_status,
        team_workload=team_workload,
        memory_context=memory_context,
        active_blockers=active_blockers,
    )
    try:
        digest = call_llm(prompt)
    except Exception as e:
        print(f"[Digest] LLM generation failed: {e}")
        digest = "NEXUS Morning Brief (Fallback): The LLM connection is currently unavailable. " \
                 f"{sprint_status} {team_workload}"

    # 6. Store digest as memory event
    try:
        retain_qa_interaction(project_id, "morning_digest", digest)
    except Exception:
        pass

    return digest
