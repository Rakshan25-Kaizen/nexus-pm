"""
NEXUS-PM Memory Orchestrator — Coordinates memory storage across banks.
"""
from backend.memory.retain import (
    retain_member_task_completion,
    retain_task_outcome,
    retain_meeting_summary,
    retain_member_skill,
)


async def store_task_completion(
    member: str, task: dict, delay_days: int, blocker: str, reason: str, insight: str
) -> int:
    completed_on_time = delay_days == 0
    retain_member_task_completion(member, task, completed_on_time, delay_days, blocker)
    retain_task_outcome(
        task,
        member,
        {
            "delayed": not completed_on_time,
            "delay_days": delay_days,
            "blockers": blocker,
            "reason": reason,
            "insight": insight,
        },
    )
    return 2


async def store_meeting_and_commitments(project_id: str, summary: dict) -> int:
    retain_meeting_summary(project_id, summary)
    count = 1
    for item in summary.get("action_items", []):
        retain_member_task_completion(
            item.get("assigned_to", "unknown"),
            {"title": item.get("task", ""), "category": "general", "complexity": "medium"},
            False,
            0,
            "",
        )
        count += 1
    for insight in summary.get("behavioral_insights", []):
        retain_member_skill(project_id, "team_insight", insight)
        count += 1
    return count
