from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.database import get_db
from backend.models.db_models import Task, Member, TaskOutcome
from backend.models.schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskRiskResult,
    AssignTaskRequest, AssignTaskResponse,
    StoreOutcomeRequest, StoreOutcomeResponse,
)
from backend.services.decision_engine import assign_task
from backend.services.memory_orchestrator import store_task_completion
from backend.ml.features import build_task_risk_features
from backend.ml.risk_model import risk_model
from backend.ml.strategy_adapter import strategy_adapter
from backend.agent.llm_client import call_llm
from backend.agent.prompts import RISK_EXPLANATION_APT

router = APIRouter()


@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(
        project_id=task_data.project_id,
        title=task_data.title,
        description=task_data.description,
        category=task_data.category,
        complexity=task_data.complexity,
        assigned_to=task_data.assigned_to if task_data.assigned_to else None,
        status="todo",
        due_date=task_data.due_date,
        is_blocking=task_data.is_blocking,
        created_at=datetime.utcnow(),
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskResponse(
        id=str(task.id), title=task.title, description=task.description,
        category=task.category, complexity=task.complexity,
        assigned_to=str(task.assigned_to) if task.assigned_to else None,
        status=task.status, due_date=task.due_date, is_blocking=task.is_blocking,
        risk_score=task.risk_score, risk_level=task.risk_level,
        confidence=task.confidence, assignment_reason=task.assignment_reason, memory_evidence=task.memory_evidence,
        project_id=str(task.project_id), created_at=task.created_at,
    )


@router.get("/{project_id}", response_model=list[TaskResponse])
async def get_tasks(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.project_id == project_id))
    tasks = result.scalars().all()
    return [
        TaskResponse(
            id=str(t.id), title=t.title, description=t.description,
            category=t.category, complexity=t.complexity,
            assigned_to=str(t.assigned_to) if t.assigned_to else None,
            status=t.status, due_date=t.due_date, is_blocking=t.is_blocking,
            risk_score=t.risk_score, risk_level=t.risk_level,
            confidence=t.confidence, assignment_reason=t.assignment_reason, memory_evidence=t.memory_evidence,
            project_id=str(t.project_id), created_at=t.created_at,
        )
        for t in tasks
    ]


@router.post("/assign-task", response_model=AssignTaskResponse)
async def assign_task_endpoint(req: AssignTaskRequest, db: AsyncSession = Depends(get_db)):
    task_dict = {
        "title": req.task_title, "category": req.task_category,
        "complexity": req.complexity, "deadline": req.deadline,
        "days_remaining": req.days_remaining, "is_blocking": req.is_blocking,
        "project_id": req.project_id,
    }
    result = await assign_task(task_dict, req.candidates, req.memory_enabled)
    
    # Write confidence, risk, and reason back to task DB record
    if req.task_title:
        task_result = await db.execute(
            select(Task).where(
                Task.project_id == req.project_id,
                Task.title == req.task_title,
                Task.status != "done"
            )
        )
        matched_task = task_result.scalar_one_or_none()
        if matched_task:
            matched_task.risk_score = result["risk_score"]
            matched_task.risk_level = result["risk"]
            matched_task.confidence = result.get("confidence")
            matched_task.assignment_reason = result.get("reason", "")
            matched_task.memory_evidence = result.get("memory_evidence", [])[:3]
            await db.commit()

    return AssignTaskResponse(**result)


@router.post("/{task_id}/complete", response_model=StoreOutcomeResponse)
async def complete_task(
    task_id: str, req: StoreOutcomeRequest, db: AsyncSession = Depends(get_db)
):
    # Update task status
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task:
        task.status = "done"
        await db.commit()

    task_dict = {
        "title": req.task_title,
        "category": task.category if task else "general",
        "complexity": task.complexity if task else "medium",
    }
    memories_stored = await store_task_completion(
        req.member, task_dict, req.delay_days, req.blocker_type, req.reason, req.insight
    )

    from backend.ml.ml_engine import record_outcome
    record_outcome(
        member=req.member,
        task={"title": req.task_title,
              "category": task.category if task else "general",
              "complexity": task.complexity if task else "medium"},
        was_delayed=(req.delay_days or 0) > 0,
        delay_days=req.delay_days or 0,
        blocker_type=req.blocker_type or "",
        reason=req.reason or "",
    )

    project_id = str(task.project_id) if task else ""
    new_weights = await strategy_adapter.analyze_and_adapt(project_id, db)
    strategy_changed = new_weights != strategy_adapter.DEFAULT_WEIGHTS

    return StoreOutcomeResponse(
        status="completed",
        memories_stored=memories_stored,
        strategy_changed=strategy_changed,
        new_weights=new_weights,
    )


@router.get("/{project_id}/risks", response_model=list[TaskRiskResult])
async def get_task_risks(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Task).where(Task.project_id == project_id, Task.status != "done")
    )
    tasks = result.scalars().all()
    risk_results = []
    for task in tasks:
        assigned = str(task.assigned_to) if task.assigned_to else "unassigned"
        task_dict = {
            "title": task.title, "category": task.category or "general",
            "complexity": task.complexity or "medium",
            "days_remaining": 7, "is_blocking": task.is_blocking,
        }
        feats = build_task_risk_features(task_dict, assigned)
        risk = risk_model.predict_risk(feats)
        explanation = ""
        try:
            explanation = call_llm(RISK_EXPLANATION_APT.format(
                task_title=task.title, member=assigned,
                risk_score=risk["risk_score"], risk_level=risk["risk_level"],
                risk_factors=", ".join(risk["top_factors"]),
                memory_context="See behavioral profile for details.",
            ))
        except Exception:
            explanation = f"Risk level: {risk['risk_level']}"

        risk_results.append(TaskRiskResult(
            task_id=str(task.id), task_title=task.title,
            risk_score=risk["risk_score"], risk_level=risk["risk_level"],
            top_factors=risk["top_factors"], explanation=explanation,
        ))
    return sorted(risk_results, key=lambda x: x.risk_score, reverse=True)
@router.get("/{project_id}/strategy-log")
async def get_strategy_log(project_id: str, db: AsyncSession = Depends(get_db)):
    from backend.models.db_models import StrategyLog
    result = await db.execute(
        select(StrategyLog)
        .where(StrategyLog.project_id == project_id)
        .order_by(StrategyLog.created_at.desc())
    )
    entries = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "trigger_pattern": e.trigger_pattern,
            "failure_rate": e.failure_rate,
            "old_weights": e.old_weights,
            "new_weights": e.new_weights,
            "created_at": str(e.created_at),
        }
        for e in entries
    ]


@router.get("/{project_id}/deadline-reminders")
async def get_deadline_reminders(project_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns overdue + due-soon tasks as structured deadline reminders.
    Used by the frontend NudgeToast and also callable for the demo.
    """
    from datetime import timedelta
    from backend.models.db_models import Nudge

    now = datetime.utcnow()
    soon = now + timedelta(days=2)

    result = await db.execute(
        select(Task).where(
            Task.project_id == project_id,
            Task.status != "done",
            Task.due_date.isnot(None),
        )
    )
    tasks = result.scalars().all()

    reminders = []
    for t in tasks:
        if t.due_date < now:
            severity = "critical"
            label = "OVERDUE"
        elif t.due_date <= soon:
            severity = "warning"
            label = "DUE SOON"
        else:
            continue  # not urgent

        reminders.append({
            "task_id": str(t.id),
            "title": t.title,
            "due_date": str(t.due_date),
            "assigned_to": str(t.assigned_to) if t.assigned_to else None,
            "severity": severity,
            "label": label,
        })

        # Save as Nudge record so it shows in the app
        existing = await db.execute(
            select(Nudge).where(
                Nudge.project_id == project_id,
                Nudge.nudge_type == "deadline_alert",
                Nudge.message.contains(t.title),
                Nudge.was_read == False,
            )
        )
        if not existing.scalar_one_or_none():
            nudge = Nudge(
                project_id=project_id,
                nudge_type="deadline_alert",
                message=f"[{label}] '{t.title}' — due {t.due_date.strftime('%b %d')}",
                severity=severity,
                created_at=now,
            )
            db.add(nudge)

    await db.commit()
    return {"project_id": project_id, "reminders": reminders, "count": len(reminders)}
