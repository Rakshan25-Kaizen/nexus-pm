"""
NEXUS-PM Task Scorer — Composite ranking of members for task assignment.
"""
from backend.ml.features import FEATURE_COLS


def composite_rank(llm_result: dict, ml_scores: dict, weights: dict, members: list) -> list:
    scored = []
    for member in members:
        ml = ml_scores.get(member, {"risk_score": 0.5, "risk_level": "MEDIUM"})
        base = 1.0 - ml["risk_score"]
        bonus = 0.0
        if llm_result.get("assigned_to") == member:
            bonus += 0.15
        if llm_result.get("alternative") == member:
            bonus += 0.05
        score = base * weights.get("completion_rate", 0.35) + bonus
        explanation = generate_assignment_explanation(member, {}, ml)
        scored.append(
            {
                "member": member,
                "recommendation_score": round(score, 3),
                "risk_level": ml["risk_level"],
                "risk_score": ml["risk_score"],
                "explanation": explanation,
            }
        )
    return sorted(scored, key=lambda x: x["recommendation_score"], reverse=True)


def generate_assignment_explanation(member: str, features: dict, risk: dict) -> str:
    cr = features.get("completion_rate", 0.7)
    ad = features.get("avg_delay_days", 1.0)
    load = features.get("current_task_load", 1)
    return (
        f"{member} has {cr:.0%} completion rate, {ad:.1f} avg delay days, "
        f"{load} active tasks. Risk: {risk.get('risk_level', 'MEDIUM')}."
    )
