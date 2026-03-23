"""
NEXUS-PM Model Training
Run: python -m backend.ml.train --mode synthetic
     python -m backend.ml.train --mode memory
"""
import argparse
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from backend.ml.features import FEATURE_COLS
from backend.ml.risk_model import risk_model


def train_synthetic():
    print("NEXUS-PM Risk Model — Synthetic Training")
    print(f"Features: {FEATURE_COLS}")
    print("Generating 300 synthetic training samples...")

    np.random.seed(42)
    n_samples = 300
    X = np.random.rand(n_samples, len(FEATURE_COLS))

    # Assign realistic column ranges
    X[:, 0] = np.random.uniform(0.3, 1.0, n_samples)   # completion_rate
    X[:, 1] = np.random.uniform(0, 5, n_samples)        # avg_delay_days
    X[:, 2] = np.random.uniform(0, 0.8, n_samples)      # blocker_frequency
    X[:, 3] = np.random.randint(0, 5, n_samples)        # current_task_load
    X[:, 4] = np.random.uniform(0.2, 1.0, n_samples)    # recent_velocity
    X[:, 5] = np.random.uniform(0.2, 1.0, n_samples)    # task_type_success
    X[:, 6] = np.random.uniform(0, 0.8, n_samples)      # similar_delay_rate
    X[:, 7] = np.random.choice([0.3, 0.6, 1.0], n_samples)  # task_complexity_score
    X[:, 8] = np.random.randint(1, 14, n_samples)       # days_until_deadline
    X[:, 9] = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])  # is_blocking_others

    # Generate labels based on realistic failure rules
    y = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        prob = 0.20  # base delay probability
        if X[i, 3] >= 3:       # current_task_load >= 3
            prob = max(prob, 0.65)
        if X[i, 5] < 0.4:      # task_type_success < 0.4
            prob = max(prob, 0.70)
        if X[i, 8] < 2:        # days_until_deadline < 2
            prob = max(prob, 0.60)
        if X[i, 0] < 0.5:      # low completion_rate
            prob = max(prob, 0.55)
        y[i] = 1 if np.random.random() < prob else 0

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    risk_model.fit(X_train, y_train)
    risk_model.save("risk_model.joblib")

    train_pred = risk_model.model.predict(risk_model.scaler.transform(X_train))
    test_pred = risk_model.model.predict(risk_model.scaler.transform(X_test))

    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, test_pred)

    print(f"Train accuracy: {train_acc:.2%}")
    print(f"Test accuracy:  {test_acc:.2%}")
    print(f"Delayed samples: {y.sum()}/{n_samples} ({y.mean():.0%})")
    print("Synthetic training complete. Model saved to risk_model.joblib.")

    print("Initializing additional ML models...")

    from backend.ml.skill_affinity import skill_affinity
    print(f"  ✓ Skill affinity model ready "
          f"({len(skill_affinity._member_vectors)} member profiles)")

    from backend.ml.anomaly_detector import anomaly_detector
    print(f"  ✓ Anomaly detector ready "
          f"({anomaly_detector._n_samples} seed samples)")

    from backend.ml.sprint_health import sprint_health
    print(f"  ✓ Sprint health predictor ready "
          f"({sprint_health._n_sprints} sprint samples)")

    from backend.ml.delay_classifier import delay_classifier, TRAINING_DATA
    print(f"  ✓ Delay classifier ready "
          f"({len(TRAINING_DATA)} seed examples)")

    from backend.ml.workload_forecast import workload_forecaster
    print(f"  ✓ Workload forecaster ready "
          f"({len(workload_forecaster._history)} member histories)")

    print("\nAll 6 ML models initialized and ready.")
    print("Run: python -m backend.ml.train --mode synthetic")

def train_memory():
    print("NEXUS-PM Risk Model — Memory-Based Training")
    print("This mode requires at least 20 completed task outcomes in Hindsight.")
    print("Run synthetic mode first: python -m backend.ml.train --mode synthetic")
    print("After seeding real data, re-run with --mode memory.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train NEXUS-PM risk model")
    parser.add_argument(
        "--mode",
        choices=["synthetic", "memory"],
        default="synthetic",
        help="Training mode: synthetic (default) or memory",
    )
    args = parser.parse_args()

    if args.mode == "synthetic":
        train_synthetic()
    else:
        train_memory()
