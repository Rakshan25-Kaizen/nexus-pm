"""
NEXUS-PM Strategy Adapter — Dynamically adjusts assignment weights based on failure patterns.
"""
from backend.memory.recall import recall_recent_outcomes
from backend.memory.retain import retain_strategy_change


class StrategyAdapter:
    DEFAULT_WEIGHTS = {
        "completion_rate": 0.35,
        "delay_history": 0.25,
        "recent_velocity": 0.20,
        "current_load": 0.20,
    }

    ADAPTATION_RULES = {
        "overload_pattern": {
            "completion_rate": 0.30,
            "delay_history": 0.20,
            "recent_velocity": 0.15,
            "current_load": 0.35,
        },
        "skill_mismatch": {
            "completion_rate": 0.25,
            "delay_history": 0.20,
            "recent_velocity": 0.25,
            "current_load": 0.30,
        },
        "deadline_pressure": {
            "completion_rate": 0.25,
            "delay_history": 0.30,
            "recent_velocity": 0.30,
            "current_load": 0.15,
        },
    }
    MIN_OUTCOMES = 5

    def get_current_weights(self, project_id: str) -> dict:
        try:
            outcomes = recall_recent_outcomes(project_id, days=14)
            for o in outcomes:
                if "strategy_adaptation" in o or "Strategy adapted" in o:
                    for rule_name, weights in self.ADAPTATION_RULES.items():
                        if rule_name.replace("_", " ") in o.lower() or rule_name in o:
                            return weights
        except Exception:
            pass
        return self.DEFAULT_WEIGHTS

    async def analyze_and_adapt(self, project_id: str, db) -> dict:
        try:
            outcomes = recall_recent_outcomes(project_id, days=14)
            if len(outcomes) < self.MIN_OUTCOMES:
                return self.DEFAULT_WEIGHTS
            failure_rate = self._compute_failure_rate(outcomes)
            if failure_rate <= 0.4:
                return self.DEFAULT_WEIGHTS
            pattern = self._detect_dominant_pattern(outcomes)
            if not pattern:
                return self.DEFAULT_WEIGHTS
            new_weights = self.ADAPTATION_RULES[pattern]
            retain_strategy_change(
                project_id, pattern, failure_rate, self.DEFAULT_WEIGHTS, new_weights
            )
            from backend.models.db_models import StrategyLog
            from datetime import datetime

            log = StrategyLog(
                project_id=project_id,
                trigger_pattern=pattern,
                failure_rate=failure_rate,
                old_weights=self.DEFAULT_WEIGHTS,
                new_weights=new_weights,
                created_at=datetime.utcnow(),
            )
            db.add(log)
            await db.commit()
            return new_weights
        except Exception as e:
            print(f"StrategyAdapter error: {e}")
            return self.DEFAULT_WEIGHTS

    def _compute_failure_rate(self, outcomes: list) -> float:
        if not outcomes:
            return 0.0
        delayed = sum(
            1 for o in outcomes if "delayed" in o.lower() or "failed" in o.lower()
        )
        return delayed / len(outcomes)

    def _detect_dominant_pattern(self, outcomes: list) -> str | None:
        try:
            from backend.ml.delay_classifier import delay_classifier
            if not outcomes:
                return None
            failures = [o for o in outcomes
                       if "delayed" in o.lower() or "failed" in o.lower()]
            if not failures:
                return None

            # Use NB classifier on each failure string
            cause_counts = {}
            for text in failures:
                result = delay_classifier.classify(
                    task_title=text, category="general",
                    blocker_type="", reason=text
                )
                cause = result.get("cause", "unknown")
                cause_counts[cause] = cause_counts.get(cause, 0) + 1

            if not cause_counts:
                return None

            top_cause = max(cause_counts, key=cause_counts.get)
            top_count = cause_counts[top_cause]
            if top_count / len(failures) < 0.4:
                return None

            # Map NB cause → strategy adapter pattern name
            cause_to_pattern = {
                "overload": "overload_pattern",
                "skill_mismatch": "skill_mismatch",
                "process_failure": "deadline_pressure",
                "external_dependency": "deadline_pressure",
                "unclear_requirements": "deadline_pressure",
            }
            return cause_to_pattern.get(top_cause)

        except Exception as e:
            print(f"[StrategyAdapter] NB pattern detection warning: {e}")
            # Fallback to original keyword matching
            return self._detect_dominant_pattern_keywords(outcomes)

    def _detect_dominant_pattern_keywords(self, outcomes: list) -> str | None:
        if not outcomes:
            return None
        failures = [
            o for o in outcomes if "delayed" in o.lower() or "failed" in o.lower()
        ]
        if not failures:
            return None
        n = len(failures)
        overload = sum(
            1
            for o in failures
            if "overload" in o.lower() or "too many tasks" in o.lower()
        )
        mismatch = sum(
            1
            for o in failures
            if "skill" in o.lower() or "wrong type" in o.lower()
        )
        deadline = sum(
            1
            for o in failures
            if "deadline" in o.lower() or "tight" in o.lower()
        )
        if overload / n > 0.5:
            return "overload_pattern"
        if mismatch / n > 0.4:
            return "skill_mismatch"
        if deadline / n > 0.4:
            return "deadline_pressure"
        return None


strategy_adapter = StrategyAdapter()
