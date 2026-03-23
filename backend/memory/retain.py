"""
NEXUS-PM Memory Retain Functions
All functions wrapped in try/except — NEVER raise, only print warning.
"""
from backend.memory.hindsight_client import client, BANK_MEETINGS, BANK_MEMBERS, BANK_TASKS


def retain_meeting_summary(project_id: str, summary: dict) -> None:
    try:
        date = summary.get("date", "unknown")
        participants = ", ".join(summary.get("participants", []))
        decisions = "; ".join(
            d.get("decision", "") for d in summary.get("decisions", [])
        )
        action_items = "; ".join(
            f"{a.get('assigned_to', '?')}: {a.get('task', '?')}"
            for a in summary.get("action_items", [])
        )
        blockers = "; ".join(
            b.get("description", "") for b in summary.get("blockers", [])
        )
        content = (
            f"Meeting on {date}. Participants: {participants}. "
            f"Decisions: {decisions}. "
            f"Action items: {action_items}. "
            f"Blockers: {blockers}."
        )
        client.retain(
            bank_id=BANK_MEETINGS,
            content=content,
            context=f"Project {project_id} meeting summary",
            metadata={"type": "meeting_summary", "project_id": project_id},
        )
    except Exception as e:
        print(f"[NEXUS Memory] Warning: Failed to retain meeting summary: {e}")


def retain_member_task_completion(
    member: str, task: dict, completed_on_time: bool, delay_days: int = 0, blocker: str = ""
) -> None:
    try:
        title = task.get("title", "unknown task")
        category = task.get("category", "general")
        complexity = task.get("complexity", "medium")
        outcome = "on time" if completed_on_time else f"{delay_days} days late"
        content = (
            f"{member} executed '{title}' (type:{category}, complexity:{complexity}). "
            f"Outcome: {outcome}. Blocker: {blocker or 'none'}."
        )
        client.retain(
            bank_id=BANK_MEMBERS,
            content=content,
            context=f"{member} task execution record",
            metadata={
                "member": member,
                "type": "task_execution",
                "completed_on_time": str(completed_on_time),
                "delay_days": str(delay_days),
            },
        )
    except Exception as e:
        print(f"[NEXUS Memory] Warning: Failed to retain member task completion: {e}")


def retain_task_outcome(task: dict, assigned_to: str, outcome: dict) -> None:
    try:
        title = task.get("title", "unknown")
        category = task.get("category", "general")
        complexity = task.get("complexity", "medium")
        delayed = outcome.get("delayed", False)
        delay_days = outcome.get("delay_days", 0)
        reason = outcome.get("reason", "none")
        insight = outcome.get("insight", "none")
        content = (
            f"{assigned_to} completed '{title}' ({category}, {complexity}). "
            f"Delayed: {delayed}. Delay days: {delay_days}. "
            f"Reason: {reason}. Insight: {insight}."
        )
        client.retain(
            bank_id=BANK_TASKS,
            content=content,
            context=f"Task outcome for {title}",
            metadata={
                "type": "task_outcome",
                "category": category,
                "delayed": str(delayed),
                "delay_days": str(delay_days),
                "assigned_to": assigned_to,
            },
        )
    except Exception as e:
        print(f"[NEXUS Memory] Warning: Failed to retain task outcome: {e}")


def retain_blocker_event(
    project_id: str, blocker_type: str, resolution_hours: float, resolved_by: str
) -> None:
    try:
        content = (
            f"Project {project_id} hit blocker: {blocker_type}. "
            f"Resolved in {resolution_hours:.1f}h by {resolved_by}."
        )
        client.retain(
            bank_id=BANK_TASKS,
            content=content,
            context=f"Blocker event in project {project_id}",
            metadata={"type": "blocker_event", "project_id": project_id, "blocker_type": blocker_type},
        )
    except Exception as e:
        print(f"[NEXUS Memory] Warning: Failed to retain blocker event: {e}")


def retain_strategy_change(
    project_id: str, pattern: str, failure_rate: float, old_weights: dict, new_weights: dict
) -> None:
    try:
        content = (
            f"Strategy adapted for {project_id}: {pattern} detected. "
            f"Failure rate: {failure_rate:.0%}. New weights: {new_weights}."
        )
        client.retain(
            bank_id=BANK_TASKS,
            content=content,
            context=f"Strategy adaptation for project {project_id}",
            metadata={"type": "strategy_adaptation", "project_id": project_id, "pattern": pattern},
        )
    except Exception as e:
        print(f"[NEXUS Memory] Warning: Failed to retain strategy change: {e}")


def retain_member_skill(member: str, skill: str, evidence: str) -> None:
    try:
        content = f"{member} demonstrated skill in {skill}. Evidence: {evidence}"
        client.retain(
            bank_id=BANK_MEMBERS,
            content=content,
            context=f"{member} skill observation",
            metadata={"member": member, "skill": skill, "type": "skill_observation"},
        )
    except Exception as e:
        print(f"[NEXUS Memory] Warning: Failed to retain member skill: {e}")


def retain_qa_interaction(project_id: str, question: str, answer: str) -> None:
    try:
        content = f"Team asked: '{question}'. NEXUS answered: '{answer[:300]}'"
        client.retain(
            bank_id=BANK_MEETINGS,
            content=content,
            context=f"Chat interaction in project {project_id}",
            metadata={"type": "chat_interaction", "project_id": project_id},
        )
    except Exception as e:
        print(f"[NEXUS Memory] Warning: Failed to retain QA interaction: {e}")


def retain_sprint_plan(project_id: str, sprint_number: int, assignments_summary: str) -> None:
    try:
        content = f"Sprint {sprint_number} planned for {project_id}: {assignments_summary}"
        client.retain(
            bank_id=BANK_TASKS,
            content=content,
            context=f"Sprint plan for project {project_id}",
            metadata={"type": "sprint_plan", "project_id": project_id, "sprint_number": str(sprint_number)},
        )
    except Exception as e:
        print(f"[NEXUS Memory] Warning: Failed to retain sprint plan: {e}")
