from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database import get_db
from backend.models.db_models import AgentInteraction, Nudge
from backend.models.schemas import (
    AgentInteractionResponse, NudgeResponse, AgentStatusResponse,
    OnboardingRequest, OnboardingResponse,
    BeforeAfterRequest, BeforeAfterResponse, BeforeAfterDecision,
)
from backend.agent.nexus_agent import nexus_agent
from backend.agent.llm_client import call_llm, call_llm_json
from backend.agent.prompts import MEMBER_ONBOARD_APT, BEFORE_AFTER_APT
from backend.services.nudge_engine import nudge_engine
from backend.services.decision_engine import assign_task
from backend.websocket.manager import manager
from backend.memory.recall import recall_meeting_history
from backend.memory.retain import retain_member_skill
from backend.config import get_settings
from backend.services.digest_service import generate_morning_digest

router = APIRouter()
settings = get_settings()


@router.get("/digest/{project_id}")
async def get_digest(project_id: str, db: AsyncSession = Depends(get_db)):
    digest = await generate_morning_digest(project_id, db)
    from datetime import datetime
    return {"digest": digest, "generated_at": datetime.utcnow().isoformat()}


@router.post("/digest/{project_id}/send")
async def send_digest(project_id: str, db: AsyncSession = Depends(get_db)):
    from backend.services.delivery_service import deliver_digest
    digest = await generate_morning_digest(project_id, db)
    delivery = await deliver_digest(
        project_id=project_id,
        digest_text=digest,
        project_name="NEXUS Demo Project"
    )
    from datetime import datetime
    return {
        "digest": digest,
        "delivered_via": delivery,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/greet/{project_id}")
async def greet(project_id: str):
    message = await nexus_agent.greet(project_id)
    return {"message": message}


@router.post("/chat", response_model=AgentInteractionResponse)
async def agent_chat(req: dict, db: AsyncSession = Depends(get_db)):
    message = req.get("message", "")
    project_id = req.get("project_id", "")
    memory_enabled = req.get("memory_enabled", True)
    return await nexus_agent.answer(message, project_id, memory_enabled)


@router.get("/nudges/{project_id}", response_model=list[NudgeResponse])
async def get_nudges(project_id: str, db: AsyncSession = Depends(get_db)):
    nudges = await nudge_engine.get_active_nudges(project_id, db)
    return [
        NudgeResponse(
            id=str(n.id), nudge_type=n.nudge_type, message=n.message,
            target_member=n.target_member,
            task_id=str(n.task_id) if n.task_id else None,
            severity=n.severity, was_read=n.was_read, created_at=n.created_at,
        )
        for n in nudges
    ]


@router.post("/nudges/{nudge_id}/read")
async def mark_nudge_read(nudge_id: str, db: AsyncSession = Depends(get_db)):
    await nudge_engine.mark_read(nudge_id, db)
    return {"status": "read"}


@router.get("/status/{project_id}", response_model=AgentStatusResponse)
async def get_agent_status(project_id: str, db: AsyncSession = Depends(get_db)):
    interaction_count = await db.execute(
        select(func.count(AgentInteraction.id)).where(
            AgentInteraction.project_id == project_id
        )
    )
    nudge_count = await db.execute(
        select(func.count(Nudge.id)).where(
            Nudge.project_id == project_id, Nudge.was_read == False
        )
    )
    return AgentStatusResponse(
        agent_name=settings.nexus_agent_name,
        persona=settings.nexus_agent_persona,
        memory_bank_counts={"meetings": 0, "members": 0, "tasks": 0},
        total_interactions=interaction_count.scalar() or 0,
        active_nudges=nudge_count.scalar() or 0,
        last_active="now",
        is_learning=True,
    )


@router.post("/before-after", response_model=BeforeAfterResponse)
async def before_after(req: BeforeAfterRequest, db: AsyncSession = Depends(get_db)):
    task_dict = {
        "title": req.task_title, "category": req.task_category,
        "complexity": req.complexity, "deadline": req.deadline,
        "project_id": req.project_id, "days_remaining": 7,
        "is_blocking": False,
    }
    without = await assign_task(task_dict, req.candidates, memory_enabled=False)
    with_mem = await assign_task(task_dict, req.candidates, memory_enabled=True)
    evidence = with_mem.get("memory_evidence", [])
    prompt = BEFORE_AFTER_APT.format(
        without_decision=str(without),
        with_decision=str(with_mem),
        memory_evidence="\n".join(evidence),
    )
    diff_summary = call_llm(prompt)
    impact = abs(with_mem["confidence"] - without["confidence"])
    return BeforeAfterResponse(
        without_memory=BeforeAfterDecision(
            assigned_to=without["assigned_to"],
            reason=without["reason"],
            confidence=without["confidence"],
            risk_level=without["risk"],
        ),
        with_memory=BeforeAfterDecision(
            assigned_to=with_mem["assigned_to"],
            reason=with_mem["reason"],
            confidence=with_mem["confidence"],
            risk_level=with_mem["risk"],
            memory_evidence=evidence,
        ),
        difference_summary=diff_summary,
        memory_impact_score=round(impact, 3),
    )


@router.post("/explain/{task_id}")
async def explain_task(
    task_id: str,
    project_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    explanation = await nexus_agent.explain_decision(task_id, project_id)
    return {"explanation": explanation}


@router.post("/onboard", response_model=OnboardingResponse)
async def onboard_member(req: OnboardingRequest, db: AsyncSession = Depends(get_db)):
    team_context_mems = recall_meeting_history(
        req.project_id, "team skills needs blockers", top_k=4
    )
    team_context = "\n".join(team_context_mems) or "No team context yet."
    prompt = MEMBER_ONBOARD_APT.format(
        member_name=req.member_name,
        role=req.role,
        skills=", ".join(req.skills),
        background_notes=req.background_notes or "None provided.",
        team_context=team_context,
    )
    result = call_llm_json(prompt)
    for skill in req.skills:
        retain_member_skill(req.member_name, skill, "Provided at onboarding")
    return OnboardingResponse(
        member_id="pending-creation",
        welcome_message=result.get("welcome_message", "Welcome to the team!"),
        initial_tasks_suggested=result.get("suggested_tasks", []),
        skill_gaps_detected=result.get("skill_gaps", []),
        memories_created=len(req.skills) + 1,
    )


from pydantic import BaseModel
from typing import Optional

class ReportRequest(BaseModel):
    include_demo_results: bool = False
    demo_file: Optional[str] = None
    demo_results_data: Optional[dict] = None

@router.post("/report/{project_id}")
async def get_project_report(project_id: str, req: ReportRequest, db: AsyncSession = Depends(get_db)):
    from backend.services.report_service import generate_project_report
    demo_data = req.demo_results_data
    if req.include_demo_results and req.demo_file and not demo_data:
        import json
        try:
            with open(req.demo_file) as f:
                demo_data = json.load(f)
        except Exception as e:
            print(f"Error loading demo file: {e}")
    report = await generate_project_report(project_id, db, demo_results=demo_data)
    return report

@router.get("/report/{project_id}/quick")
async def get_quick_report(project_id: str, db: AsyncSession = Depends(get_db)):
    from backend.memory.recall import reflect_on_project
    from backend.models.db_models import Task, Member
    from backend.ml.features import build_task_risk_features
    from backend.ml.risk_model import risk_model
    from datetime import datetime

    exec_sum = reflect_on_project("3-sentence project summary", project_id)
    
    tasks_result = await db.execute(select(Task).where(Task.project_id == project_id))
    all_tasks = tasks_result.scalars().all()
    open_tasks = [t for t in all_tasks if t.status not in ("done","blocked")]
    
    members_result = await db.execute(select(Member).where(Member.project_id == project_id))
    members = members_result.scalars().all()

    high = []
    for t in open_tasks:
        assigned_name = next((m.name for m in members if str(m.id)==str(t.assigned_to)), "unassigned")
        feats = build_task_risk_features({"title":t.title,"category":t.category,
            "complexity":t.complexity,"is_blocking":t.is_blocking,"days_remaining":7}, assigned_name)
        risk = risk_model.predict_risk(feats)
        if risk["risk_level"] == "HIGH":
            high.append({
                "task_title": t.title,
                "assigned_to": assigned_name,
                "risk_score": risk["risk_score"]
            })
            
    return {
        "executive_summary": exec_sum,
        "high_risk_count": len(high),
        "high_risk_tasks": high[:3],
        "generated_at": datetime.utcnow().isoformat()
    }
@router.get("/memory-stats/{project_id}")
async def get_memory_stats(project_id: str):
    """Returns real memory counts from Hindsight banks."""
    from backend.memory.hindsight_client import client, BANK_MEETINGS, BANK_MEMBERS, BANK_TASKS
    stats = {"meetings": 0, "members": 0, "tasks": 0}
    try:
        for bank_key, bank_id in [
            ("meetings", BANK_MEETINGS),
            ("members", BANK_MEMBERS),
            ("tasks", BANK_TASKS)
        ]:
            result = client.recall(
                bank_id=bank_id,
                query="team project member task",
                budget="low",
                max_tokens=100
            )
            stats[bank_key] = len(result.results)
    except Exception as e:
        print(f"[MemoryStats] Warning: {e}")
    return {
        "banks": stats,
        "total": sum(stats.values()),
        "project_id": project_id
    }
