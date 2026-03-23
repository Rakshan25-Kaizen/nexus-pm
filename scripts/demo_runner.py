"""
NEXUS-PM Auto Demo Runner
Run: python -m scripts.demo_runner
Requires: API running at localhost:8000 + Hindsight seeded
Output: demo_results_new.json + printed report
"""

import httpx, json, time, asyncio
from datetime import datetime

BASE = "http://localhost:8000"
PROJECT_ID = "project-1"
RESULTS = {
    "demo_run_at": datetime.now().isoformat(),
    "project_id": PROJECT_ID,
    "steps": [],
    "summary": {},
    "errors": []
}

def log(icon, msg): print(f"  {icon}  {msg}")
def step_start(n, name): print(f"\n{'='*55}\nSTEP {n}: {name}\n{'='*55}")

async def run_demo():
    async with httpx.AsyncClient(timeout=60) as client:

        # STEP 1: Health check
        step_start(1, "API Health Check")
        r = await client.get(f"{BASE}/health")
        data = r.json()
        log("OK", f"API: {data.get('app')} | Memory: {data.get('memory')} | LLM: {data.get('llm')}")
        RESULTS["steps"].append({"step": 1, "name": "health_check", "result": data, "status": "pass"})

        # STEP 2: Agent greeting
        step_start(2, "NEXUS Agent Greeting (Memory-Aware)")
        t0 = time.time()
        r = await client.get(f"{BASE}/api/agent/greet/{PROJECT_ID}")
        elapsed = round(time.time() - t0, 2)
        greeting = r.json().get("message", "")
        log("NEXUS", greeting)
        log("TIME", f"{elapsed}s")
        RESULTS["steps"].append({
            "step": 2, "name": "agent_greeting",
            "result": {"greeting": greeting, "response_time_s": elapsed},
            "status": "pass" if greeting else "fail"
        })

        # STEP 3: Morning digest
        step_start(3, "Morning Digest Generation")
        t0 = time.time()
        r = await client.get(f"{BASE}/api/agent/digest/{PROJECT_ID}")
        elapsed = round(time.time() - t0, 2)
        digest_data = r.json()
        digest = digest_data.get("digest", "")
        log("DIGEST", digest[:200] + "..." if len(digest) > 200 else digest)
        log("TIME", f"{elapsed}s")
        RESULTS["steps"].append({
            "step": 3, "name": "morning_digest",
            "result": {"digest": digest, "generated_at": digest_data.get("generated_at"), "response_time_s": elapsed},
            "status": "pass" if len(digest) > 50 else "warn"
        })

        # STEP 4: Memory chat — 4 key questions
        step_start(4, "Memory-Powered Chat (4 Questions)")
        questions = [
            "Who should handle backend tasks and why?",
            "What is Alice's performance history?",
            "What are the risks in our current sprint?",
            "What patterns of failure has our team shown?"
        ]
        chat_results = []
        for i, q in enumerate(questions):
            t0 = time.time()
            r = await client.post(f"{BASE}/api/agent/chat",
                json={"message": q, "project_id": PROJECT_ID, "memory_enabled": True})
            elapsed = round(time.time() - t0, 2)
            resp = r.json()
            answer = resp.get("response", "")
            mems = resp.get("memories_used", 0)
            snippets = resp.get("memory_snippets", [])
            log(f"Q{i+1}", q)
            log("A", answer[:180] + "..." if len(answer) > 180 else answer)
            log("MEM", f"Used {mems} memories | Time: {elapsed}s")
            chat_results.append({
                "question": q,
                "answer": answer,
                "memories_used": mems,
                "memory_snippets": snippets,
                "response_time_s": elapsed,
                "grounded": mems > 0
            })
        RESULTS["steps"].append({
            "step": 4, "name": "memory_chat",
            "result": {"conversations": chat_results},
            "status": "pass" if all(c["grounded"] for c in chat_results) else "warn"
        })

        # STEP 5: Task assignment — WITH and WITHOUT memory (before/after)
        step_start(5, "Task Assignment — Before/After Memory Comparison")
        task_payload = {
            "task_title": "Backend data processing pipeline",
            "task_category": "Backend",
            "complexity": "high",
            "deadline": "2025-04-01",
            "days_remaining": 10,
            "is_blocking": False,
            "project_id": PROJECT_ID,
            "candidates": ["Alice", "Bob", "Priya", "Raj"]
        }
        # Without memory
        t0 = time.time()
        payload_no_mem = {**task_payload, "memory_enabled": False}
        r_no = await client.post(f"{BASE}/api/assign-task", json=payload_no_mem)
        t_no = round(time.time() - t0, 2)
        res_no = r_no.json()

        # With memory
        t0 = time.time()
        payload_mem = {**task_payload, "memory_enabled": True}
        r_mem = await client.post(f"{BASE}/api/assign-task", json=payload_mem)
        t_mem = round(time.time() - t0, 2)
        res_mem = r_mem.json()

        log("WITHOUT MEMORY", f"Assigned to: {res_no.get('assigned_to')} | Confidence: {res_no.get('confidence',0):.0%} | Risk: {res_no.get('risk')}")
        log("WITH MEMORY",    f"Assigned to: {res_mem.get('assigned_to')} | Confidence: {res_mem.get('confidence',0):.0%} | Risk: {res_mem.get('risk')}")
        log("REASON", res_mem.get('reason','')[:150])
        log("EVIDENCE", f"Memory snippets: {len(res_mem.get('memory_evidence',[]))}")
        assignment_changed = res_no.get("assigned_to") != res_mem.get("assigned_to")
        log("IMPACT", f"Assignment changed by memory: {'YES' if assignment_changed else 'NO'}")

        RESULTS["steps"].append({
            "step": 5, "name": "task_assignment_comparison",
            "result": {
                "task": task_payload["task_title"],
                "without_memory": {
                    "assigned_to": res_no.get("assigned_to"),
                    "confidence": res_no.get("confidence"),
                    "risk": res_no.get("risk"),
                    "reason": res_no.get("reason")
                },
                "with_memory": {
                    "assigned_to": res_mem.get("assigned_to"),
                    "confidence": res_mem.get("confidence"),
                    "risk": res_mem.get("risk"),
                    "reason": res_mem.get("reason"),
                    "memory_evidence": res_mem.get("memory_evidence", []),
                    "acts_trace": res_mem.get("acts_trace", [])
                },
                "assignment_changed_by_memory": assignment_changed,
                "confidence_delta": round((res_mem.get("confidence",0) - res_no.get("confidence",0)), 3)
            },
            "status": "pass"
        })

        # STEP 6: Risk scoring for all tasks
        step_start(6, "XGBoost Risk Scoring — All Active Tasks")
        t0 = time.time()
        r = await client.get(f"{BASE}/api/tasks/{PROJECT_ID}/risks")
        elapsed = round(time.time() - t0, 2)
        risks = r.json() if r.status_code == 200 else []
        high_risk = [t for t in risks if t.get("risk_level") == "HIGH"]
        med_risk  = [t for t in risks if t.get("risk_level") == "MEDIUM"]
        low_risk  = [t for t in risks if t.get("risk_level") == "LOW"]
        log("SCORED", f"{len(risks)} tasks scored in {elapsed}s")
        log("HIGH RISK", f"{len(high_risk)} tasks")
        log("MEDIUM",    f"{len(med_risk)} tasks")
        log("LOW RISK",  f"{len(low_risk)} tasks")
        for t in high_risk:
            log("ALERT", f"{t.get('task_title','?')}: {t.get('risk_score',0):.2f} — {', '.join(t.get('top_factors',[]))}")
        RESULTS["steps"].append({
            "step": 6, "name": "risk_scoring",
            "result": {
                "total_scored": len(risks),
                "high_risk": high_risk,
                "medium_risk": med_risk,
                "low_risk": low_risk,
                "response_time_s": elapsed
            },
            "status": "pass" if risks else "warn"
        })

        # STEP 7: Sprint plan generation
        step_start(7, "AI Sprint Plan Generation (Memory-Powered)")
        t0 = time.time()
        sprint_payload = {
            "project_id": PROJECT_ID,
            "sprint_number": 5,
            "available_members": ["Alice", "Bob", "Priya", "Raj"],
            "available_tasks": [
                {"id": "t-a", "title": "Deploy NEXUS to production", "category": "DevOps", "complexity": "high"},
                {"id": "t-b", "title": "Build user onboarding flow", "category": "Frontend", "complexity": "medium"},
                {"id": "t-c", "title": "Database query optimisation", "category": "Backend", "complexity": "high"},
                {"id": "t-d", "title": "Write API documentation",    "category": "Backend", "complexity": "low"},
                {"id": "t-e", "title": "Cross-browser testing",      "category": "Testing",  "complexity": "medium"}
            ],
            "velocity_target": 5
        }
        r = await client.post(f"{BASE}/api/sprint/plan", json=sprint_payload)
        elapsed = round(time.time() - t0, 2)
        plan = r.json() if r.status_code in (200,201) else {}
        assignments = plan.get("recommended_tasks", plan.get("assignments", []))
        warnings = plan.get("capacity_warnings", [])
        mem_used = plan.get("memories_used", 0)
        log("PLAN", plan.get("sprint_name", "Sprint 5"))
        log("MEMORIES", f"Used {mem_used} memories to generate plan")
        for a in assignments:
            log("ASSIGN", f"{a.get('assigned_to','?')} <- {a.get('task_id','?')} [{a.get('risk','?')}]")
        for w in warnings:
            log("WARN", w)
        RESULTS["steps"].append({
            "step": 7, "name": "sprint_plan",
            "result": {
                "sprint_name": plan.get("sprint_name", "Sprint 5"),
                "assignments": assignments,
                "capacity_warnings": warnings,
                "risk_summary": plan.get("risk_summary", ""),
                "memories_used": mem_used,
                "response_time_s": elapsed
            },
            "status": "pass" if assignments else "warn"
        })

        # STEP 8: Meeting summarizer
        step_start(8, "Meeting Transcript Summarization + Memory Storage")
        transcript = """Alice: We need to decide on the production deployment approach for NEXUS.
Priya: I suggest we use Railway for backend and Vercel for frontend. Zero config.
Bob: Works for me. I can handle the Vercel setup — it's in my wheelhouse.
Alice: I'll own the Railway setup and environment variables.
Raj: I want to run the full E2E suite before we push to production. Can we make that mandatory?
Priya: Yes — add it as a required check in the CI pipeline. Alice can you add that gate?
Alice: Done. Let's plan to deploy by end of this week. Raj, can you have tests ready by Wednesday?
Raj: Wednesday is tight but doable if the environment is stable.
Priya: Alice, Raj needs the staging URL by Tuesday then.
Alice: I'll have it up by Tuesday morning."""
        t0 = time.time()
        r = await client.post(f"{BASE}/api/meetings/summarize",
            json={"transcript": transcript, "project_id": PROJECT_ID})
        elapsed = round(time.time() - t0, 2)
        summary = r.json() if r.status_code == 200 else {}
        log("DECISIONS", str(len(summary.get("decisions",[]))))
        log("ACTION ITEMS", str(len(summary.get("action_items",[]))))
        log("MEMORIES STORED", str(summary.get("memories_stored",0)))
        log("TIME", f"{elapsed}s")
        RESULTS["steps"].append({
            "step": 8, "name": "meeting_summarizer",
            "result": {
                "decisions": summary.get("decisions", []),
                "action_items": summary.get("action_items", []),
                "blockers": summary.get("blockers", []),
                "behavioral_insights": summary.get("behavioral_insights", []),
                "summary": summary.get("summary", ""),
                "memories_stored": summary.get("memories_stored", 0),
                "response_time_s": elapsed
            },
            "status": "pass" if summary.get("memories_stored",0) > 0 else "warn"
        })

        # STEP 9: Member behavior profile
        step_start(9, "Member Behavioral Profile via reflect()")
        t0 = time.time()
        members_r = await client.get(f"{BASE}/api/members/{PROJECT_ID}")
        members_list = members_r.json() if members_r.status_code == 200 else []
        profiles = []
        for m in members_list[:2]:  # Profile first 2 members for speed
            r = await client.get(f"{BASE}/api/members/{m['id']}/behavior")
            profile = r.json() if r.status_code == 200 else {}
            log(m["name"], profile.get("profile_summary","")[:120] + "...")
            profiles.append({
                "member": m["name"],
                "role": m.get("role",""),
                "memory_count": profile.get("memory_count",0),
                "profile_summary": profile.get("profile_summary",""),
                "reliability_score": profile.get("reliability_score",0)
            })
        elapsed = round(time.time() - t0, 2)
        RESULTS["steps"].append({
            "step": 9, "name": "behavioral_profiles",
            "result": {"profiles": profiles, "response_time_s": elapsed},
            "status": "pass" if profiles else "warn"
        })

        # STEP 10: Agent status
        step_start(10, "NEXUS Agent Status")
        r = await client.get(f"{BASE}/api/agent/status/{PROJECT_ID}")
        status = r.json() if r.status_code == 200 else {}
        log("AGENT", status.get("agent_name","NEXUS"))
        log("INTERACTIONS", str(status.get("total_interactions",0)))
        log("ACTIVE NUDGES", str(status.get("active_nudges",0)))
        log("LEARNING", str(status.get("is_learning",True)))
        RESULTS["steps"].append({
            "step": 10, "name": "agent_status",
            "result": status,
            "status": "pass"
        })

        # SUMMARY
        total_steps = len(RESULTS["steps"])
        passed = sum(1 for s in RESULTS["steps"] if s["status"] == "pass")
        warned = sum(1 for s in RESULTS["steps"] if s["status"] == "warn")
        failed = sum(1 for s in RESULTS["steps"] if s["status"] == "fail")
        total_mems = sum(
            c.get("memories_used",0)
            for s in RESULTS["steps"] if s["name"]=="memory_chat"
            for c in s["result"].get("conversations",[])
        )
        RESULTS["summary"] = {
            "total_steps": total_steps,
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "total_memories_accessed": total_mems,
            "assignment_changed_by_memory": RESULTS["steps"][4]["result"].get("assignment_changed_by_memory",False),
            "meeting_memories_stored": RESULTS["steps"][7]["result"].get("memories_stored",0),
            "sprint_plan_generated": bool(RESULTS["steps"][6]["result"].get("assignments")),
            "demo_health": "EXCELLENT" if failed==0 and warned<=1 else "GOOD" if failed==0 else "NEEDS ATTENTION"
        }

        print(f"""
{'='*55}
DEMO COMPLETE
{'='*55}
  Steps:    {passed} passed / {warned} warned / {failed} failed
  Memories: {total_mems} accessed across all chat queries
  Health:   {RESULTS['summary']['demo_health']}
  Output:   demo_results_new.json
{'='*55}
""")

        with open("C:/tmp/demo_results_new.json","w") as f:
            json.dump(RESULTS, f, indent=2, default=str)
        print("  Saved: C:/tmp/demo_results_new.json")
        print("  Run report generator: python -m scripts.generate_report C:/tmp/demo_results_new.json")

if __name__ == "__main__":
    asyncio.run(run_demo())
