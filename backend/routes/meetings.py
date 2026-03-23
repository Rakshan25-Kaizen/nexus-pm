from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.schemas import MeetingTranscriptRequest, MeetingSummaryResponse
from backend.services import meeting_summarizer
from backend.memory.recall import recall_meeting_history

router = APIRouter()


@router.post("/summarize", response_model=MeetingSummaryResponse)
async def summarize_meeting(
    req: MeetingTranscriptRequest, db: AsyncSession = Depends(get_db)
):
    summary = await meeting_summarizer.summarize(req.transcript, req.project_id)
    return MeetingSummaryResponse(**summary)


@router.get("/{project_id}")
async def get_meetings(project_id: str, db: AsyncSession = Depends(get_db)):
    memories = recall_meeting_history(project_id, "recent meetings decisions")
    return {"project_id": project_id, "memories": memories, "count": len(memories)}
