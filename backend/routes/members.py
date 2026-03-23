from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.db_models import Member
from backend.models.schemas import MemberCreate, MemberResponse, BehaviorProfile
from backend.memory.retain import retain_member_skill
from backend.memory.recall import recall_member_history, reflect_member_profile
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=MemberResponse)
async def create_member(member_data: MemberCreate, db: AsyncSession = Depends(get_db)):
    member = Member(
        project_id=member_data.project_id,
        name=member_data.name,
        role=member_data.role,
        skills=member_data.skills,
        created_at=datetime.utcnow(),
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    for skill in member_data.skills:
        retain_member_skill(member.name, skill, "Self-reported at onboarding")
        
    # Update skill affinity model with new member's skills
    try:
        from backend.ml.skill_affinity import skill_affinity
        skill_affinity.update_member(member_data.name, member_data.skills or [])
    except Exception:
        pass

    return MemberResponse(
        id=str(member.id), name=member.name, role=member.role,
        skills=member.skills or [], project_id=str(member.project_id),
        created_at=member.created_at,
    )


@router.get("/{project_id}", response_model=list[MemberResponse])
async def get_members(project_id: str, db: AsyncSession = Depends(get_db)):
    from backend.models.db_models import Task, TaskOutcome
    from sqlalchemy import func

    result = await db.execute(select(Member).where(Member.project_id == project_id))
    members = result.scalars().all()

    # Get active task counts per member in one query
    active_counts_result = await db.execute(
        select(Task.assigned_to, func.count(Task.id).label("cnt"))
        .where(
            Task.project_id == project_id,
            Task.status.in_(["todo", "in_progress"])
        )
        .group_by(Task.assigned_to)
    )
    active_counts = {str(row.assigned_to): row.cnt
                     for row in active_counts_result}

    # Get completion rates from TaskOutcome
    all_outcomes_result = await db.execute(
        select(TaskOutcome).where(
            TaskOutcome.member_id.in_([str(m.id) for m in members])
        )
    )
    all_outcomes = all_outcomes_result.scalars().all()

    outcome_map = {}
    for o in all_outcomes:
        mid = str(o.member_id)
        if mid not in outcome_map:
            outcome_map[mid] = {"total": 0, "on_time": 0, "delays": []}
        outcome_map[mid]["total"] += 1
        if (o.delay_days or 0) == 0:
            outcome_map[mid]["on_time"] += 1
        elif (o.delay_days or 0) > 0:
            outcome_map[mid]["delays"].append(o.delay_days)

    responses = []
    for m in members:
        mid = str(m.id)
        stats = outcome_map.get(mid, {"total": 0, "on_time": 0, "delays": []})
        total = stats["total"]
        on_time = stats["on_time"]
        completion = on_time / total if total > 0 else 1.0
        delays = stats["delays"]
        avg_delay = sum(delays) / len(delays) if delays else 0.0

        responses.append(MemberResponse(
            id=mid,
            name=m.name,
            role=m.role,
            skills=m.skills or [],
            project_id=str(m.project_id),
            created_at=m.created_at,
            active_tasks=active_counts.get(mid, 0),
            completion_rate=round(completion, 2),
            avg_delay_days=round(avg_delay, 1),
        ))

    return responses


@router.get("/{member_id}/behavior", response_model=BehaviorProfile)
async def get_member_behavior(member_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Member).where(Member.id == member_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    memories = recall_member_history(member.name, "general", top_k=10)
    profile = reflect_member_profile(member.name)
    return BehaviorProfile(
        member_id=str(member.id),
        name=member.name,
        memory_count=len(memories),
        raw_memories=memories,
        profile_summary=profile,
        reliability_score=0.7,
    )


@router.get("/{project_id}/forecast")
async def get_workload_forecast(project_id: str, db: AsyncSession = Depends(get_db)):
    """Workload forecast for all team members — next sprint prediction."""
    from backend.ml.workload_forecast import workload_forecaster
    forecasts = workload_forecaster.get_all_forecasts()
    return {
        "forecasts": forecasts,
        "team_overload_risk": workload_forecaster.get_team_overload_risk(),
        "model": "LinearRegression"
    }
