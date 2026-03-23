"""
Workload Forecast Model — predicts member task load for next sprint.
Uses Linear Regression on historical task load per member per sprint.
Returns predicted load + overload risk flag.
"""
import numpy as np
from sklearn.linear_model import LinearRegression

# Historical load data — populated from DB task outcomes
# Format: {member: [sprint1_load, sprint2_load, sprint3_load, ...]}
DEFAULT_HISTORY = {
    "Alice": [3, 3, 2, 1],   # Sprint 1-4 task counts
    "Bob":   [2, 3, 2, 1],
    "Priya": [2, 2, 2, 1],
    "Raj":   [1, 1, 2, 1],
}

CAPACITY = {
    "Alice": 2,   # safe max for Alice (confirmed by pattern)
    "Bob":   3,
    "Priya": 3,
    "Raj":   4,
}
DEFAULT_CAPACITY = 3


class WorkloadForecaster:
    def __init__(self):
        self._models = {}
        self._history = dict(DEFAULT_HISTORY)
        self._fit_all()

    def _fit_all(self):
        for member, loads in self._history.items():
            self._fit_member(member, loads)

    def _fit_member(self, member: str, loads: list):
        try:
            if len(loads) < 2:
                return
            X = np.array(range(len(loads))).reshape(-1, 1)
            y = np.array(loads, dtype=float)
            model = LinearRegression()
            model.fit(X, y)
            self._models[member] = model
        except Exception as e:
            print(f"[WorkloadForecast] Fit warning for {member}: {e}")

    def predict_next_sprint(self, member: str) -> dict:
        """
        Predicts task load for next sprint.
        Returns: predicted_load, overload_risk, capacity, trend
        """
        try:
            history = self._history.get(member, [DEFAULT_CAPACITY])
            cap = CAPACITY.get(member, DEFAULT_CAPACITY)

            if member not in self._models or len(history) < 2:
                predicted = float(np.mean(history)) if history else cap
            else:
                next_sprint_idx = len(history)
                predicted = float(
                    self._models[member].predict([[next_sprint_idx]])[0]
                )

            predicted = max(0, round(predicted, 1))
            overload_risk = predicted >= cap
            overload_prob = min(1.0, max(0.0, predicted / cap))

            trend = "stable"
            if len(history) >= 2:
                if history[-1] > history[-2]:
                    trend = "increasing"
                elif history[-1] < history[-2]:
                    trend = "decreasing"

            return {
                "member": member,
                "predicted_load": predicted,
                "capacity": cap,
                "overload_risk": overload_risk,
                "overload_probability": round(overload_prob, 2),
                "trend": trend,
                "history": history,
                "warning": (
                    f"{member} predicted at {predicted:.1f} tasks — "
                    f"at or above safe capacity ({cap})"
                ) if overload_risk else None,
            }
        except Exception as e:
            print(f"[WorkloadForecast] Predict warning: {e}")
            return {
                "member": member, "predicted_load": DEFAULT_CAPACITY,
                "capacity": CAPACITY.get(member, DEFAULT_CAPACITY),
                "overload_risk": False, "overload_probability": 0.5,
                "trend": "unknown", "history": [],  "warning": None,
            }

    def update(self, member: str, sprint_load: int) -> None:
        """Call after each sprint completion with actual task count."""
        try:
            if member not in self._history:
                self._history[member] = []
            self._history[member].append(sprint_load)
            self._fit_member(member, self._history[member])
        except Exception as e:
            print(f"[WorkloadForecast] Update warning: {e}")

    def get_all_forecasts(self) -> list:
        """Returns forecast for all known members."""
        return [
            self.predict_next_sprint(m)
            for m in self._history
        ]

    def get_team_overload_risk(self) -> float:
        """Returns 0-1 overall team overload risk for next sprint."""
        try:
            forecasts = self.get_all_forecasts()
            if not forecasts:
                return 0.3
            risks = [f["overload_probability"] for f in forecasts]
            return round(sum(risks) / len(risks), 2)
        except Exception:
            return 0.3


workload_forecaster = WorkloadForecaster()
