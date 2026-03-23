"""
Sprint Health Predictor — Random Forest classifier.
Predicts probability of sprint on-time completion at kickoff.
8 sprint-level features. Trained on seed sprint data.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

SPRINT_FEATURE_COLS = [
    "total_tasks",
    "high_complexity_count",
    "avg_member_load",
    "team_avg_risk_score",
    "has_blocking_tasks",
    "days_in_sprint",
    "members_at_capacity",
    "prior_sprint_success_rate",
]

# Seed training data from known sprint outcomes
# [total, high_complex, avg_load, avg_risk, blocking, days, at_cap, prior_success]
SEED_X = np.array([
    [3, 2, 1.0, 0.20, 0, 14, 0, 0.80],  # Sprint 1 — delivered with minor delay
    [4, 2, 1.5, 0.35, 0, 14, 1, 0.80],  # Sprint 2 — had delays
    [5, 1, 1.25, 0.18, 0, 14, 0, 0.75], # Sprint 3 — clean delivery
], dtype=float)
SEED_Y = np.array([1, 0, 1])  # 1=on track, 0=delayed


class SprintHealthPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=50, max_depth=4,
            random_state=42, class_weight="balanced"
        )
        self.scaler = StandardScaler()
        self._fitted = False
        self._n_sprints = 0
        self._train_seed()

    def _train_seed(self):
        try:
            X_s = self.scaler.fit_transform(SEED_X)
            self.model.fit(X_s, SEED_Y)
            self._fitted = True
            self._n_sprints = len(SEED_Y)
        except Exception as e:
            print(f"[SprintHealth] Seed train warning: {e}")

    def predict(self, sprint_features: dict) -> dict:
        """
        Predict sprint health from kickoff features.
        Returns: on_track_probability, health_label, risk_factors
        """
        try:
            if not self._fitted:
                return {
                    "on_track_probability": 0.7,
                    "health_label": "Unknown",
                    "health_emoji": "?",
                    "risk_factors": [],
                    "model": "SprintHealth(untrained)"
                }

            x = np.array([[
                sprint_features.get(c, 0.0)
                for c in SPRINT_FEATURE_COLS
            ]])
            x_s = self.scaler.transform(x)
            prob = float(self.model.predict_proba(x_s)[0][1])

            label = (
                "On track" if prob >= 0.75
                else "At risk" if prob >= 0.50
                else "Critical"
            )
            emoji = "✅" if prob >= 0.75 else "⚠️" if prob >= 0.50 else "🔴"

            # Feature importance-based risk factors
            factors = []
            f = sprint_features
            if f.get("members_at_capacity", 0) > 0:
                factors.append("Member at workload capacity")
            if f.get("high_complexity_count", 0) >= 2:
                factors.append("Multiple high-complexity tasks")
            if f.get("team_avg_risk_score", 0) > 0.4:
                factors.append("Elevated team risk score")
            if f.get("has_blocking_tasks", 0) == 1:
                factors.append("Blocking dependency present")

            return {
                "on_track_probability": round(prob, 2),
                "health_label": label,
                "health_emoji": emoji,
                "risk_factors": factors[:3],
                "model": f"RandomForest({self._n_sprints} sprints trained)",
            }
        except Exception as e:
            print(f"[SprintHealth] Predict warning: {e}")
            return {
                "on_track_probability": 0.7,
                "health_label": "Unknown",
                "health_emoji": "?",
                "risk_factors": [], "model": "fallback"
            }

    def update(self, features: dict, was_on_track: bool) -> None:
        """Update with actual sprint outcome."""
        try:
            x = np.array([[features.get(c, 0.0) for c in SPRINT_FEATURE_COLS]])
            new_X = np.vstack([SEED_X, x])
            new_y = np.append(SEED_Y, int(was_on_track))
            X_s = self.scaler.fit_transform(new_X)
            self.model.fit(X_s, new_y)
            self._n_sprints += 1
        except Exception as e:
            print(f"[SprintHealth] Update warning: {e}")


sprint_health = SprintHealthPredictor()
