"""
NEXUS-PM Memory Recall Functions
All wrapped in try/except returning [] or "" on failure.
"""
from backend.memory.hindsight_client import client, BANK_MEETINGS, BANK_MEMBERS, BANK_TASKS


def recall_member_history(member: str, category: str, top_k: int = 8) -> list[str]:
    try:
        query = f"{member} {category} task execution history delayed on_time failures skill"
        results = client.recall(bank_id=BANK_MEMBERS, query=query, budget="mid", max_tokens=4096)
        return [r.text for r in results.results[:top_k]]
    except Exception as e:
        print(f"[NEXUS Recall] Warning: recall_member_history failed: {e}")
        return []


def recall_similar_tasks(task_title: str, category: str, top_k: int = 5) -> list[str]:
    try:
        query = f"{task_title} {category} delay outcome completed on_time failure blocker"
        results = client.recall(bank_id=BANK_TASKS, query=query, budget="mid")
        return [r.text for r in results.results[:top_k]]
    except Exception as e:
        print(f"[NEXUS Recall] Warning: recall_similar_tasks failed: {e}")
        return []


def recall_recent_outcomes(project_id: str, days: int = 14) -> list[str]:
    try:
        query = f"recent task outcomes failures delays project {project_id} last {days} days"
        results = client.recall(bank_id=BANK_TASKS, query=query, budget="high")
        return [r.text for r in results.results]
    except Exception as e:
        print(f"[NEXUS Recall] Warning: recall_recent_outcomes failed: {e}")
        return []


def recall_meeting_history(project_id: str, query_text: str, top_k: int = 6) -> list[str]:
    try:
        query = f"{query_text} project {project_id}"
        results = client.recall(bank_id=BANK_MEETINGS, query=query, budget="mid")
        return [r.text for r in results.results[:top_k]]
    except Exception as e:
        print(f"[NEXUS Recall] Warning: recall_meeting_history failed: {e}")
        return []


def recall_project_blockers(project_id: str, top_k: int = 8) -> list[str]:
    try:
        query = f"blockers problems patterns project {project_id}"
        results = client.recall(bank_id=BANK_TASKS, query=query, budget="high")
        return [r.text for r in results.results[:top_k]]
    except Exception as e:
        print(f"[NEXUS Recall] Warning: recall_project_blockers failed: {e}")
        return []


def recall_member_skills(member: str, task_category: str, top_k: int = 5) -> list[str]:
    try:
        query = f"{member} skills experience {task_category} performance"
        results = client.recall(bank_id=BANK_MEMBERS, query=query, budget="mid")
        return [r.text for r in results.results[:top_k]]
    except Exception as e:
        print(f"[NEXUS Recall] Warning: recall_member_skills failed: {e}")
        return []


def recall_recent_performance(member: str, category: str, top_k: int = 6) -> list[str]:
    try:
        query = f"{member} recent performance last 30 days {category}"
        results = client.recall(bank_id=BANK_MEMBERS, query=query, budget="mid")
        return [r.text for r in results.results[:top_k]]
    except Exception as e:
        print(f"[NEXUS Recall] Warning: recall_recent_performance failed: {e}")
        return []


def reflect_member_profile(member: str) -> str:
    try:
        query = f"Summarize {member}'s work patterns, strengths, and risk factors"
        answer = client.reflect(bank_id=BANK_MEMBERS, query=query, budget="mid")
        return answer.text
    except Exception as e:
        print(f"[NEXUS Recall] Warning: reflect_member_profile failed: {e}")
        return ""


def reflect_on_project(query_text: str, project_id: str) -> str:
    try:
        query = f"{query_text} project {project_id}"
        answer = client.reflect(bank_id=BANK_MEETINGS, query=query, budget="mid")
        return answer.text
    except Exception as e:
        print(f"[NEXUS Recall] Warning: reflect_on_project failed: {e}")
        return ""
