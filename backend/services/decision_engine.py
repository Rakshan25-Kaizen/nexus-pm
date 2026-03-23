"""
NEXUS-PM Decision Engine — Full 5-step task assignment pipeline.
"""
from backend.agent.llm_client import call_llm_json
from backend.agent.prompts import TASK_ASSIGNMENT_APT
from backend.memory.recall import recall_member_history, recall_similar_tasks
from backend.ml.features import build_task_risk_features
from backend.ml.risk_model import risk_model
from backend.ml.task_scorer import composite_rank
from backend.ml.strategy_adapter import strategy_adapter


async def assign_task(task: dict, members: list, memory_enabled: bool = True) -> dict:
    # STEP 3: Memory Recall
    if memory_enabled:
        memory_contexts = {}
        for member in members:
            history = recall_member_history(member, task.get("category", "general"))
            sim = recall_similar_tasks(task.get("title", ""), task.get("category", ""))
            memory_contexts[member] = history + sim
    else:
        memory_contexts = {m: ["Memory disabled — using default logic"] for m in members}

    # STEP 4: Decision Generation
    retrieved_memories = "\n".join(
        f"{m}: {chr(10).join(mems[:3])}" for m, mems in memory_contexts.items()
    )
    ml_scores = {
        m: risk_model.predict_risk(build_task_risk_features(task, m)) for m in members
    }
    ml_risk_str = "\n".join(
        f"{m}: {v['risk_level']} ({v['risk_score']})" for m, v in ml_scores.items()
    )
    weights = strategy_adapter.get_current_weights(task.get("project_id", ""))
    members_list_str = "\n".join(f"- {m}" for m in members)

    prompt = TASK_ASSIGNMENT_APT.format(
        task_title=task.get("title", ""),
        task_category=task.get("category", ""),
        complexity=task.get("complexity", "medium"),
        deadline=task.get("deadline", "TBD"),
        days_remaining=task.get("days_remaining", 7),
        is_blocking=task.get("is_blocking", False),
        members_list=members_list_str,
        retrieved_memories=retrieved_memories or "No memory yet.",
        ml_risk_scores=ml_risk_str,
        strategy_weights=str(weights),
    )
    llm_result = call_llm_json(prompt)
    if llm_result.get("assigned_to") not in members:
        llm_result["assigned_to"] = members[0]  # hallucination guard

    # Anomaly detection
    try:
        from backend.ml.anomaly_detector import anomaly_detector
        top_member = llm_result.get("assigned_to", members[0])
        top_feats = build_task_risk_features(task, top_member)
        anomaly = anomaly_detector.score(top_feats)
        anomaly_detector.record(top_feats)
    except Exception:
        anomaly = {"is_anomaly": False, "anomaly_score": 0.5, "message": None}

    # STEP 5: Composite Ranking
    ranked = composite_rank(llm_result, ml_scores, weights, members)
    total_memories = sum(len(v) for v in memory_contexts.values())

    return {
        "assigned_to": ranked[0]["member"],
        "risk": ranked[0]["risk_level"],
        "risk_score": ranked[0]["risk_score"],
        "confidence": float(llm_result.get("confidence", 0.75)),
        "reason": llm_result.get("reason", ""),
        "memory_evidence": memory_contexts.get(ranked[0]["member"], [])[:3],
        "warnings": llm_result.get("warnings", []),
        "alternative": llm_result.get("alternative"),
        "strategy_weights": weights,
        "all_scores": ranked,
        "acts_trace": [
            "PERCEIVE",
            f"RECALL:{total_memories}",
            "REASON",
            "ADAPT",
            "LEARN",
        ],
        "anomaly": anomaly,
        "memory_enabled": memory_enabled,
    }
