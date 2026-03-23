import sys
import os

root = r"c:\Users\Rakshan25\OneDrive\AI Agent [Nexus}\Nexus AI Agent"
sys.path.insert(0, root)
os.chdir(root)

def test_models():
    print("Starting ML Model Tests...")
    try:
        from backend.ml.ml_engine import (
            risk_model, skill_affinity, delay_classifier,
            anomaly_detector, workload_forecaster, sprint_health
        )
        
        # 1. Skill Affinity
        score = skill_affinity.score("Alice", "Backend")
        print(f"[OK] Skill Affinity: {score}")
        
        # 2. Delay Classifier
        res = delay_classifier.classify("Server down", "Backend")
        print(f"[OK] Delay Classifier: {res['cause']}")
        
        # 3. Risk Model
        risk = risk_model.predict_risk({"skill_affinity_score": 0.8, "high_complexity_flag": 0, "is_blocking_flag": 0, "days_remaining": 7})
        print(f"[OK] Risk Model: {risk['risk_level']}")
        
        # 4. Anomaly Detector
        feats = {"skill_affinity_score": 0.8, "high_complexity_flag": 0, "is_blocking_flag": 0, "days_remaining": 7}
        anom = anomaly_detector.score(feats)
        print(f"[OK] Anomaly Detector: {anom['is_anomaly']}")
        
        # 5. Workload Forecaster
        wf = workload_forecaster.predict_next_sprint("Bob")
        print(f"[OK] Workload Forecast: {wf['predicted_load']}")
        
        # 6. Sprint Health
        sh = sprint_health.predict({"team_avg_risk_score": 0.2, "total_tasks": 5, "members_at_capacity": 0, "avg_member_load": 1.5, "high_complexity_count": 1, "has_blocking_tasks": 0, "days_in_sprint": 14, "prior_sprint_success_rate": 0.8})
        print(f"[OK] Sprint Health: {sh['health_label']}")
        
        print("\nALL MODELS RESPONDING CORRECTLY")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_models()
