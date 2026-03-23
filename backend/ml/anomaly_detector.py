"""
Anomaly Detector — Isolation Forest.
Flags task assignments that are statistical outliers
compared to this team's historical patterns.
contamination=0.1 means ~10% of assignments expected as anomalies.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from backend.ml.features import FEATURE_COLS

# Seed with known good assignments (no anomalies)
SEED_ASSIGNMENTS = np.array([
    # Alice — backend tasks (normal)
    [0.9, 0.0, 0.1, 1, 1.0, 0.9, 0.1, 1.0, 10, 0],
    [0.9, 0.0, 0.1, 2, 1.0, 0.9, 0.1, 0.6, 7,  0],
    # Bob — frontend tasks (normal)
    [0.8, 0.0, 0.1, 1, 1.0, 0.9, 0.1, 0.6, 14, 0],
    [0.8, 0.0, 0.1, 2, 0.9, 0.9, 0.1, 0.3, 10, 0],
    # Priya — devops tasks (normal)
    [1.0, 0.0, 0.0, 1, 1.0, 1.0, 0.0, 0.6, 14, 0],
    [1.0, 0.0, 0.0, 2, 1.0, 1.0, 0.0, 1.0, 7,  0],
    # Raj — testing tasks (normal)
    [0.9, 0.3, 0.1, 1, 0.9, 0.9, 0.2, 0.3, 14, 0],
    # Known anomalies — used to calibrate contamination
    [0.7, 3.0, 0.5, 3, 0.4, 0.2, 0.8, 1.0, 1,  1],  # Bob on backend (mismatch)
    [0.6, 2.0, 0.6, 3, 0.3, 0.1, 0.9, 1.0, 2,  1],  # Alice overloaded
], dtype=float)


class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.15,
            random_state=42,
        )
        self.scaler = StandardScaler()
        self._fitted = False
        self._n_samples = len(SEED_ASSIGNMENTS)
        self._all_samples = list(SEED_ASSIGNMENTS)
        self._fit()

    def _fit(self):
        try:
            X = np.array(self._all_samples)
            X_s = self.scaler.fit_transform(X)
            self.model.fit(X_s)
            self._fitted = True
        except Exception as e:
            print(f"[AnomalyDetector] Fit warning: {e}")

    def score(self, features: dict) -> dict:
        """
        Returns anomaly score for a task assignment.
        is_anomaly=True means statistically unusual for this team.
        anomaly_score: -1 to 1 (lower = more anomalous)
        """
        try:
            if not self._fitted:
                return {"is_anomaly": False, "anomaly_score": 0.0,
                        "message": None}

            x = np.array([[features.get(c, 0.5) for c in FEATURE_COLS]])
            x_s = self.scaler.transform(x)
            prediction = self.model.predict(x_s)[0]   # 1=normal, -1=anomaly
            raw_score = float(self.model.score_samples(x_s)[0])

            is_anomaly = prediction == -1
            normalized = round((raw_score + 0.5) * 2, 3)  # map to 0-1ish

            message = None
            if is_anomaly:
                message = (
                    "This assignment is a statistical outlier "
                    f"based on {self._n_samples} tasks in this team's history. "
                    "Review carefully before confirming."
                )

            return {
                "is_anomaly": is_anomaly,
                "anomaly_score": normalized,
                "raw_score": round(raw_score, 3),
                "message": message,
                "model": f"IsolationForest({self._n_samples} samples)",
            }
        except Exception as e:
            print(f"[AnomalyDetector] Score warning: {e}")
            return {"is_anomaly": False, "anomaly_score": 0.5, "message": None}

    def record(self, features: dict) -> None:
        """Record each real assignment to improve future anomaly detection."""
        try:
            x = [features.get(c, 0.5) for c in FEATURE_COLS]
            self._all_samples.append(x)
            self._n_samples += 1
            if self._n_samples % 5 == 0:
                self._fit()
        except Exception as e:
            print(f"[AnomalyDetector] Record warning: {e}")


anomaly_detector = AnomalyDetector()
