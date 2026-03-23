"""
NEXUS-PM Feature Engineering
Builds feature vectors from Hindsight memory for ML risk prediction.
"""
import re
from backend.memory.recall import recall_member_history, recall_recent_performance, recall_similar_tasks

FEATURE_COLS = [
    "completion_rate",
    "avg_delay_days",
    "blocker_frequency",
    "current_task_load",
    "recent_velocity",
    "task_type_success",
    "similar_delay_rate",
    "task_complexity_score",
    "days_until_deadline",
    "is_blocking_others",
]


def build_member_features(member: str, task_category: str) -> dict:
    memories = recall_member_history(member, task_category) + recall_recent_performance(
        member, task_category
    )

    if len(memories) == 0:
        return {
            "completion_rate": 0.70,
            "avg_delay_days": 1.0,
            "blocker_frequency": 0.20,
            "current_task_load": 1,
            "recent_velocity": 1.0,
            "task_type_success": 0.65,
            "fallback_used": True,
            "confidence": "LOW",
        }

    total = len(memories)
    on_time_count = sum(1 for m in memories if "on time" in m.lower())
    completion_rate = on_time_count / total if total > 0 else 0.70

    delay_numbers = []
    for m in memories:
        nums = re.findall(r"(\d+)\s*days?\s*late", m.lower())
        delay_numbers.extend(int(n) for n in nums)
    avg_delay_days = sum(delay_numbers) / len(delay_numbers) if delay_numbers else 1.0

    blocked_count = sum(1 for m in memories if "blocked" in m.lower())
    blocker_frequency = blocked_count / total if total > 0 else 0.20

    recent_velocity = min(sum(1 for m in memories[:7] if m), 5) / 5.0 if memories else 1.0

    from backend.ml.skill_affinity import skill_affinity
    task_type_success = skill_affinity.score(member, task_category)

    return {
        "completion_rate": round(completion_rate, 3),
        "avg_delay_days": round(avg_delay_days, 2),
        "blocker_frequency": round(blocker_frequency, 3),
        "current_task_load": 1,
        "recent_velocity": round(recent_velocity, 3),
        "task_type_success": round(task_type_success, 3),
        "fallback_used": False,
        "confidence": "HIGH",
    }


def build_task_risk_features(task: dict, member: str) -> dict:
    member_feats = build_member_features(member, task.get("category", "general"))
    similar = recall_similar_tasks(task.get("title", ""), task.get("category", ""))
    similar_delay_rate = (
        sum(1 for s in similar if "delay" in s.lower()) / max(len(similar), 1)
    )

    complexity_map = {"low": 0.3, "medium": 0.6, "high": 1.0}
    task_complexity_score = complexity_map.get(task.get("complexity", "medium"), 0.6)

    days_remaining = task.get("days_remaining", 7)
    days_until_deadline = max(days_remaining, 0)
    is_blocking_others = float(task.get("is_blocking", False))

    return {
        **member_feats,
        "skill_affinity_score": member_feats.get("task_type_success", 0.65),
        "similar_delay_rate": round(similar_delay_rate, 3),
        "task_complexity_score": task_complexity_score,
        "days_until_deadline": days_until_deadline,
        "is_blocking_others": is_blocking_others,
    }


def compute_weighted_reliability(member: str, category: str) -> float:
    memories = recall_member_history(member, category)
    if not memories:
        return 0.5
    scores = []
    for i, mem in enumerate(memories):
        weight = max(0.5, 1.0 - i * 0.05)
        is_success = "on time" in mem.lower() or "completed" in mem.lower()
        scores.append((1.0 if is_success else 0.0) * weight)
    return sum(scores) / len(scores)
