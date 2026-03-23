"""
NEXUS Agent — Core AI agent personality and proactive engine.
"""
from datetime import datetime
from uuid import uuid4

from backend.agent.llm_client import call_llm
from backend.agent.prompts import NEXUS_GREETING_APT, CHAT_APT, NEXUS_NUDGE_APT
from backend.memory.recall import (
    recall_meeting_history,
    recall_recent_outcomes,
    recall_project_blockers,
)
from backend.memory.retain import retain_qa_interaction
from backend.models.schemas import AgentInteractionResponse


class NexusAgent:
    PERSONA = (
        "You are NEXUS, an AI project manager with a distinct personality. "
        "You are: direct and honest (never vague), analytically sharp (cite data), "
        "occasionally dry and witty (but professional), proactively helpful "
        "(notice problems before users ask), and memory-driven (always reference "
        "specific past events, never speak in generalities). "
        "Speak in first person. Call team members by name. "
        "Never say 'I don't have access to' — either recall it or say 'I haven't seen that yet.' "
        "State confidence level with recommendations. "
        "Use phrases like 'Based on what I remember...' or 'Last time this happened...'"
    )

    async def greet(self, project_id: str) -> str:
        mems1 = recall_meeting_history(project_id, "recent activity decisions", top_k=4)
        mems2 = recall_recent_outcomes(project_id, days=7)
        mems3 = recall_project_blockers(project_id, top_k=3)
        memory_context = "\n".join(mems1 + mems2 + mems3)
        if not memory_context:
            memory_context = "No activity recorded yet."
        prompt = NEXUS_GREETING_APT.format(memory_context=memory_context)
        return call_llm(prompt)

    async def answer(
        self, message: str, project_id: str, memory_enabled: bool = True
    ) -> AgentInteractionResponse:
        all_mems = []
        if memory_enabled:
            meeting_mems = recall_meeting_history(project_id, message, top_k=4)
            blocker_mems = recall_project_blockers(project_id, top_k=3)
            all_mems = meeting_mems + blocker_mems
            memory_context = "\n".join(all_mems) if all_mems else "No memory yet."
        else:
            memory_context = "Memory disabled."

        prompt = CHAT_APT.format(memory_context=memory_context, question=message)
        response_text = call_llm(prompt, system=self.PERSONA)
        retain_qa_interaction(project_id, message, response_text)

        return AgentInteractionResponse(
            id=str(uuid4()),
            interaction_type="conversation",
            user_message=message,
            agent_message=response_text,
            context=None,
            memories_used=len(all_mems),
            was_proactive=False,
            created_at=datetime.utcnow(),
        )

    async def proactive_check(self, project_id: str, db) -> list[str]:
        nudges = []
        try:
            from sqlalchemy import select, func
            from backend.models.db_models import Task, Member

            # Check overloaded members (3+ active tasks)
            result = await db.execute(
                select(Member.name, func.count(Task.id).label("cnt"))
                .join(Task, Task.assigned_to == Member.id)
                .where(Task.project_id == project_id, Task.status != "done")
                .group_by(Member.name)
                .having(func.count(Task.id) >= 3)
            )
            overloaded = result.all()
            for row in overloaded:
                nudge_msg = call_llm(
                    NEXUS_NUDGE_APT.format(
                        nudge_type="overload_warning",
                        context=f"{row[0]} has {row[1]} active tasks",
                    )
                )
                nudges.append(nudge_msg)

            # Check past-due tasks
            result = await db.execute(
                select(Task)
                .where(
                    Task.project_id == project_id,
                    Task.status != "done",
                    Task.due_date < datetime.utcnow(),
                    Task.due_date.isnot(None),
                )
            )
            overdue_tasks = result.scalars().all()
            for task in overdue_tasks[:3]:
                nudge_msg = call_llm(
                    NEXUS_NUDGE_APT.format(
                        nudge_type="deadline_alert",
                        context=f"Task '{task.title}' is past due",
                    )
                )
                nudges.append(nudge_msg)

            # Check failure rate from memory
            outcomes = recall_recent_outcomes(project_id, days=14)
            if outcomes:
                delayed = sum(1 for o in outcomes if "delayed" in o.lower() or "failed" in o.lower())
                failure_rate = delayed / len(outcomes)
                if failure_rate > 0.4:
                    nudge_msg = call_llm(
                        NEXUS_NUDGE_APT.format(
                            nudge_type="pattern_alert",
                            context=f"Failure rate at {failure_rate:.0%} over last 14 days",
                        )
                    )
                    nudges.append(nudge_msg)

        except Exception as e:
            print(f"[NEXUS Agent] Proactive check error: {e}")

        return nudges[:5]

    async def explain_decision(self, task_id: str, project_id: str) -> str:
        mems = recall_meeting_history(project_id, f"task {task_id} assignment decision", top_k=3)
        memory_context = "\n".join(mems) if mems else "No decision memory found."
        prompt = (
            f"Explain why the assignment decision was made for task {task_id}.\n\n"
            f"Memory context:\n{memory_context}\n\n"
            f"Be specific and cite evidence. 2-3 sentences."
        )
        return call_llm(prompt, system=self.PERSONA)


nexus_agent = NexusAgent()
