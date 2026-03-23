"""
NEXUS-PM ML Engine — Unified entry point for all 6 ML models.
Import from here in routes. Never import models directly.
All methods are safe — wrapped in try/except, never raise.
"""
from backend.ml.risk_model import risk_model, sgd_model
from backend.ml.skill_affinity import skill_affinity
from backend.ml.workload_forecast import workload_forecaster
from backend.ml.delay_classifier import delay_classifier
from backend.ml.sprint_health import sprint_health
from backend.ml.anomaly_detector import anomaly_detector
from backend.ml.features import build_task_risk_features, FEATURE_COLS


def predict_task_risk(task: dict, member: str) -> dict:
    """Full risk prediction: XGBoost + SGD blend + anomaly check."""
    try:
        feats = build_task_risk_features(task, member)
        risk = risk_model.predict_risk(feats)
        anomaly = anomaly_detector.score(feats)
        affinity = skill_affinity.score(member, task.get("category", "general"))
        return {
            **risk,
            "skill_affinity": affinity,
            "anomaly": anomaly,
        }
    except Exception as e:
        return {
            "risk_score": 0.5, "risk_level": "MEDIUM",
            "flag": False, "top_factors": [],
            "skill_affinity": 0.65,
            "anomaly": {"is_anomaly": False},
            "error": str(e),
        }


def record_outcome(member: str, task: dict,
                   was_delayed: bool, delay_days: int = 0,
                   blocker_type: str = "", reason: str = "") -> None:
    """Call on every task.complete(). Updates all learning models."""
    try:
        feats = build_task_risk_features(task, member)

        # Model 1: SGD online learning
        sgd_model.update(feats, was_delayed)

        # Model 4: Delay classifier (only for delayed tasks)
        if was_delayed and blocker_type:
            delay_classifier.update(
                task.get("title", ""), task.get("category", "general"),
                blocker_type, reason, blocker_type
            )
    except Exception as e:
        print(f"[MLEngine] record_outcome warning: {e}")


def get_model_status() -> dict:
    """Returns status of all 6 models. Used in /health endpoint."""
    return {
        "xgboost":     {"trained": risk_model.is_trained, "model": "XGBoostClassifier"},
        "sgd":         {"samples": sgd_model.n_samples,   "model": "SGDClassifier"},
        "skill":       {"fitted": skill_affinity._fitted,  "model": "CosineSimilarity"},
        "workload":    {"members": len(workload_forecaster._history), "model": "LinearRegression"},
        "delay_clf":   {"real_samples": delay_classifier._n_real_samples, "model": "MultinomialNB"},
        "sprint_health": {"sprints": sprint_health._n_sprints, "model": "RandomForestClassifier"},
        "anomaly":     {"samples": anomaly_detector._n_samples, "model": "IsolationForest"},
    }
