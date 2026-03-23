from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.schemas import ChatRequest, ChatResponse
from backend.agent.llm_client import call_llm
from backend.agent.prompts import CHAT_APT
from backend.memory.recall import (
    recall_meeting_history,
    recall_project_blockers,
    reflect_on_project,
)
from backend.memory.retain import retain_qa_interaction

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    meeting_mems = recall_meeting_history(req.project_id, req.message, top_k=4)
    blocker_mems = recall_project_blockers(req.project_id, top_k=3)
    all_mems = meeting_mems + blocker_mems
    memory_context = "\n".join(f"- {m}" for m in all_mems) or "No memories yet."

    broad_keywords = [
        "pattern", "summary", "what went wrong", "how is",
        "recommend", "biggest issue", "overview",
    ]
    if any(kw in req.message.lower() for kw in broad_keywords) and req.memory_enabled:
        response = reflect_on_project(req.message, req.project_id)
        answer_type = "reflect"
    else:
        prompt = CHAT_APT.format(memory_context=memory_context, question=req.message)
        response = call_llm(prompt)
        answer_type = "llm"

    retain_qa_interaction(req.project_id, req.message, response)
    return ChatResponse(
        response=response,
        answer_type=answer_type,
        memories_used=len(all_mems),
        memory_snippets=all_mems[:3],
    )
