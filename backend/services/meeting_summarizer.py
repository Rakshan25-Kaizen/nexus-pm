"""
NEXUS-PM Meeting Summarizer — AI-powered meeting transcript analysis.
"""
from backend.agent.llm_client import call_llm_json
from backend.agent.prompts import MEETING_SUMMARY_APT
from backend.services.memory_orchestrator import store_meeting_and_commitments


async def summarize(transcript: str, project_id: str) -> dict:
    prompt = MEETING_SUMMARY_APT.format(transcript=transcript)
    summary = call_llm_json(prompt)
    memories_stored = await store_meeting_and_commitments(project_id, summary)
    summary["memories_stored"] = memories_stored
    return summary
