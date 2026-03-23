import sys
import os
import traceback

root = r"c:\Users\Rakshan25\OneDrive\AI Agent [Nexus}\Nexus AI Agent"
sys.path.insert(0, root)
os.chdir(root)

async def test_logic():
    print("Simulating Sprint Planning Logic...")
    try:
        from backend.services import sprint_planner
        from backend.ml.sprint_health import sprint_health
        from backend.ml.risk_model import risk_model
        from backend.ml.features import build_task_risk_features
        from backend.ml.workload_forecast import workload_forecaster
        
        project_id = "test-proj"
        available_tasks = [
            {"id": "1", "title": "Backend Refactor", "category": "Backend", "complexity": "high"},
            {"id": "2", "title": "Frontend UI", "category": "Frontend", "complexity": "medium"}
        ]
        available_members = ["Alice", "Bob"]
        
        print("Calling generate_plan...")
        plan = await sprint_planner.generate_plan(project_id, available_tasks, available_members)
        print(f"Plan generated: {plan.keys()}")
        
        print("Predicting health...")
        all_risks = []
        for task in available_tasks:
            for member in available_members:
                feats = build_task_risk_features(
                    {"title": task.get("title",""), "category": task.get("category","general"),
                     "complexity": task.get("complexity","medium"),
                     "is_blocking": False, "days_remaining": 14},
                    member
                )
                r = risk_model.predict_risk(feats)
                all_risks.append(r["risk_score"])
        
        forecasts = workload_forecaster.get_all_forecasts()
        at_cap = sum(1 for f in forecasts if f["overload_risk"])
        
        sprint_feats = {
            "total_tasks": len(available_tasks),
            "high_complexity_count": 1,
            "avg_member_load": 1.0,
            "team_avg_risk_score": sum(all_risks) / max(len(all_risks), 1),
            "has_blocking_tasks": 0,
            "days_in_sprint": 14,
            "members_at_capacity": at_cap,
            "prior_sprint_success_rate": 0.8,
        }
        health = sprint_health.predict(sprint_feats)
        print(f"Health: {health}")
        
        print("Test SUCCESS")
        
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_logic())
