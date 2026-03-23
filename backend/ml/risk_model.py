"""
NEXUS-PM Risk Model — XGBoost classifier for task delay prediction.
"""
import xgboost as xgb
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import os
from sklearn.linear_model import SGDClassifier
from backend.ml.features import FEATURE_COLS


class NexusRiskModel:
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=42,
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def predict_risk(self, features: dict) -> dict:
        # XGBoost prediction
        if not self.is_trained:
            xgb_prob = 0.45  # slightly below MEDIUM so trained model stands out
        else:
            X = np.array([[features.get(c, 0.5) for c in FEATURE_COLS]])
            X_s = self.scaler.transform(X)
            xgb_prob = float(self.model.predict_proba(X_s)[0][1])

        # SGD blending
        sgd_prob = sgd_model.predict(features)
        sgd_weight = sgd_model.blend_weight()

        if sgd_prob is not None and sgd_weight > 0:
            prob = xgb_prob * (1 - sgd_weight) + sgd_prob * sgd_weight
            model_used = f"XGBoost+SGD({sgd_model.n_samples} samples)"
        else:
            prob = xgb_prob
            model_used = "XGBoost" if self.is_trained else "XGBoost(untrained)"

        prob = round(float(prob), 3)
        return {
            "risk_score": prob,
            "risk_level": "HIGH" if prob > 0.65 else "MEDIUM" if prob > 0.35 else "LOW",
            "flag": prob > 0.6,
            "top_factors": self._top_factors(features),
            "untrained": not self.is_trained,
            "model_used": model_used,
            "sgd_samples": sgd_model.n_samples,
        }

    def _top_factors(self, f: dict) -> list:
        factors = []
        if f.get("current_task_load", 0) >= 2:        # lowered from 3
            factors.append("High current workload")
        if f.get("avg_delay_days", 0) > 1.0:           # lowered from 2
            factors.append("History of late delivery")
        if f.get("blocker_frequency", 0) > 0.2:        # lowered from 0.4
            factors.append("Frequent blocker pattern")
        if f.get("days_until_deadline", 7) < 5:        # raised from 3
            factors.append("Tight deadline")
        if f.get("task_type_success", 1) < 0.7:        # raised from 0.5
            factors.append("Low category affinity")
        if f.get("similar_delay_rate", 0) > 0.3:
            factors.append("Similar tasks delayed before")
        return factors[:3] if factors else ["Standard complexity task"]

    def fit(self, X, y):
        X_s = self.scaler.fit_transform(X)
        self.model.fit(X_s, y)
        self.is_trained = True

    def save(self, path="risk_model.joblib"):
        joblib.dump({"model": self.model, "scaler": self.scaler}, path)

    def load(self, path="risk_model.joblib"):
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.is_trained = True

class SGDRiskModel:
    """
    Online learning risk model. Updates on every task completion.
    Runs alongside XGBoost — blended when both have enough samples.
    """
    MIN_SAMPLES = 5     # minimum real samples before predictions are used
    BLEND_THRESHOLD = 20  # samples where SGD takes majority weight

    def __init__(self):
        self.model = SGDClassifier(
            loss="log_loss",
            learning_rate="optimal",
            random_state=42,
            max_iter=1000,
        )
        self.scaler = StandardScaler()
        self.n_samples = 0
        self.classes = np.array([0, 1])
        self._buffer_X = []
        self._buffer_y = []

    def update(self, features: dict, was_delayed: bool) -> None:
        """Call this every time a task is completed. Thread-safe."""
        try:
            x = np.array([[features.get(c, 0.5) for c in FEATURE_COLS]])
            y = np.array([int(was_delayed)])
            self._buffer_X.append(x[0])
            self._buffer_y.append(y[0])
            self.n_samples += 1

            if self.n_samples >= self.MIN_SAMPLES:
                X_arr = np.array(self._buffer_X)
                if self.n_samples == self.MIN_SAMPLES:
                    self.scaler.fit(X_arr)
                X_scaled = self.scaler.transform(X_arr)
                self.model.partial_fit(X_scaled, self._buffer_y,
                                       classes=self.classes)
                self._buffer_X = []
                self._buffer_y = []

            self._save()
        except Exception as e:
            print(f"[SGD] Update warning: {e}")

    def predict(self, features: dict) -> float:
        """Returns delay probability 0-1. Returns None if not ready."""
        try:
            if self.n_samples < self.MIN_SAMPLES:
                return None
            x = np.array([[features.get(c, 0.5) for c in FEATURE_COLS]])
            x_scaled = self.scaler.transform(x)
            prob = float(self.model.predict_proba(x_scaled)[0][1])
            return round(prob, 3)
        except Exception:
            return None

    def blend_weight(self) -> float:
        """How much weight SGD gets in blended prediction (0.0 to 0.6)."""
        if self.n_samples < self.MIN_SAMPLES:
            return 0.0
        if self.n_samples >= self.BLEND_THRESHOLD:
            return 0.6
        return 0.3

    def _save(self):
        try:
            joblib.dump({
                "model": self.model, "scaler": self.scaler,
                "n_samples": self.n_samples,
                "buffer_X": self._buffer_X, "buffer_y": self._buffer_y
            }, "sgd_model.joblib")
        except Exception:
            pass

    def load(self):
        try:
            data = joblib.load("sgd_model.joblib")
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.n_samples = data.get("n_samples", 0)
            self._buffer_X = data.get("buffer_X", [])
            self._buffer_y = data.get("buffer_y", [])
        except Exception:
            pass


sgd_model = SGDRiskModel()
sgd_model.load()

risk_model = NexusRiskModel()
try:
    risk_model.load("risk_model.joblib")
except (FileNotFoundError, Exception):
    pass  # Will use untrained fallback until train.py runs
