from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.database import get_db
from backend.models.db_models import Sprint
from backend.models.schemas import (
    SprintPlanRequest, SprintPlanResponse, SprintResponse,
)
from backend.services import sprint_planner

router = APIRouter()


@router.post("/plan", response_model=SprintPlanResponse)
async def create_sprint_plan(req: SprintPlanRequest, db: AsyncSession = Depends(get_db)):
    plan = await sprint_planner.generate_plan(
        req.project_id, req.available_tasks, req.available_members
    )

    # Predict sprint health
    try:
        from backend.ml.sprint_health import sprint_health
        from backend.ml.risk_model import risk_model
        from backend.ml.features import build_task_risk_features
        from backend.ml.workload_forecast import workload_forecaster

        all_risks = []
        # Enrich assignments from LLM with real ML scores
        for assignment in plan.get("assignments", []):
            t_id = assignment.get("task_id")
            m_name = assignment.get("assigned_to")
            
            # Find the actual task object from req.available_tasks
            task_obj = next((t for t in req.available_tasks if str(t.get("id")) == str(t_id)), None)
            if task_obj and m_name:
                feats = build_task_risk_features(
                    {"title": task_obj.get("title",""), "category": task_obj.get("category","general"),
                     "complexity": task_obj.get("complexity","medium"),
                     "is_blocking": False, "days_remaining": 14},
                    m_name
                )
                r = risk_model.predict_risk(feats)
                assignment["risk_score"] = float(r["risk_score"])
                assignment["risk"] = str(r["risk_level"])
                assignment["confidence"] = float(max(0.01, 1.0 - r["risk_score"])) # Ensure > 0 for UI check
                all_risks.append(float(r["risk_score"]))
            else:
                assignment["risk"] = "MEDIUM"
                assignment["confidence"] = 0.5
                all_risks.append(0.5)

        forecasts = workload_forecaster.get_all_forecasts()
        at_cap = sum(1 for f in forecasts if f["overload_risk"])

        sprint_feats = {
            "total_tasks": len(req.available_tasks),
            "high_complexity_count": sum(
                1 for t in req.available_tasks
                if t.get("complexity") == "high"
            ),
            "avg_member_load": len(req.available_tasks) / max(len(req.available_members), 1),
            "team_avg_risk_score": sum(all_risks) / max(len(all_risks), 1),
            "has_blocking_tasks": 0,
            "days_in_sprint": 14,
            "members_at_capacity": at_cap,
            "prior_sprint_success_rate": 0.8,
        }
        health = sprint_health.predict(sprint_feats)
        plan["sprint_health"] = health
    except Exception as e:
        import traceback
        print(f"[SprintHealth] Error in prediction loop:")
        traceback.print_exc()
        plan["sprint_health"] = None

    # Only create a DB record if sprint_number <= 4 (real sprints)
    # Sprint planner generates plans freely — only confirmed sprints are saved
    from sqlalchemy import select as sa_select
    existing = await db.execute(
        sa_select(Sprint).where(
            Sprint.project_id == req.project_id,
            Sprint.sprint_number == req.sprint_number
        )
    )
    existing_sprint = existing.scalar_one_or_none()

    sprint_id = ""
    if existing_sprint:
        # Update the existing sprint's AI plan instead of creating new
        existing_sprint.ai_plan = plan
        await db.commit()
        sprint_id = str(existing_sprint.id)
    elif req.sprint_number <= 4:
        # Only persist real sprint numbers
        sprint = Sprint(
            project_id=req.project_id,
            sprint_number=req.sprint_number,
            name=plan.get("sprint_name", f"Sprint {req.sprint_number}"),
            ai_plan=plan,
            status="planning",
            created_at=datetime.utcnow(),
        )
        db.add(sprint)
        await db.commit()
        await db.refresh(sprint)
        sprint_id = str(sprint.id)
    # else: sprint_number > 4 = demo planning, don't persist

    return SprintPlanResponse(
        sprint_id=sprint_id,
        recommended_tasks=plan.get("assignments", []),
        assigned_members={},
        risk_summary=plan.get("risk_summary", ""),
        reasoning="",
        memories_used=plan.get("memories_used", 0),
        capacity_warnings=plan.get("capacity_warnings", []),
        sprint_health=plan.get("sprint_health"),
    )


@router.get("/{project_id}", response_model=list[SprintResponse])
async def get_sprints(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Sprint).where(Sprint.project_id == project_id)
    )
    sprints = result.scalars().all()
    return [
        SprintResponse(
            id=str(s.id), project_id=str(s.project_id),
            sprint_number=s.sprint_number, name=s.name,
            start_date=s.start_date, end_date=s.end_date,
            goal=s.goal, status=s.status, ai_plan=s.ai_plan,
            created_at=s.created_at,
        )
        for s in sprints
    ]


@router.get("/{sprint_id}/health")
async def get_sprint_health(sprint_id: str, db: AsyncSession = Depends(get_db)):
    return await sprint_planner.analyze_sprint_health("", sprint_id)
