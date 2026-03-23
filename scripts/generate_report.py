"""
Generate a project report from demo results.
Run: python -m scripts.generate_report [demo_results.json]
Output: nexus_project_report.html
"""
import httpx, json, sys, asyncio
from datetime import datetime

async def generate():
    demo_file = sys.argv[1] if len(sys.argv) > 1 else "C:/tmp/demo_results_new.json"
    try:
        with open(demo_file) as f:
            demo_results = json.load(f)
        print(f"Loaded demo results from {demo_file}")
    except FileNotFoundError:
        demo_results = None
        print("No demo results file — generating from live data only")

    async with httpx.AsyncClient(timeout=120) as client:
        print("Calling NEXUS report API...")
        r = await client.post(
            "http://localhost:8000/api/agent/report/project-1",
            json={"include_demo_results": demo_results is not None,
                  "demo_results_data": demo_results}
        )
        if r.status_code not in (200, 201):
            print(f"Report API failed: {r.status_code} - {r.text}")
            return

        report = r.json()
        html = build_html_report(report, demo_results)

        filename = f"C:/tmp/nexus_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        with open(filename, "w", encoding='utf-8') as f:
            f.write(html)
        print(f"Report saved: {filename}")
        print("Open in browser: open " + filename)

def build_html_report(report: dict, demo: dict) -> str:
    sections = report.get("sections", {})
    team = sections.get("team_profiles", [])
    sprints = sections.get("sprint_timeline", [])
    risks = sections.get("risk_analysis", [])
    learnings = sections.get("nexus_learnings", {})
    strats = sections.get("strategy_adaptations", [])
    demo_sec = sections.get("demo_results", {})
    narrative = sections.get("narrative", "")
    exec_sum = sections.get("executive_summary", "")

    team_rows = ""
    for m in team:
        rate = m.get("on_time_rate", 0)
        color = "#16A34A" if rate >= 0.85 else "#D97706" if rate >= 0.7 else "#DC2626"
        team_rows += f"""
        <tr>
          <td><strong>{m['name']}</strong></td>
          <td>{m.get('role','')}</td>
          <td>{m.get('tasks_assigned',0)}</td>
          <td style="color:{color};font-weight:bold">{rate:.0%}</td>
          <td>{m.get('avg_delay_days',0):.1f} days</td>
          <td>{"✅ Strong" if rate>=0.85 else "⚠️ Watch" if rate>=0.7 else "🔴 Risk"}</td>
        </tr>"""

    sprint_bars = ""
    for s in sprints:
        total = s.get("tasks_total",1)
        done  = s.get("tasks_done",0)
        pct   = int(done/total*100) if total else 0
        status_color = "#16A34A" if s.get("status")=="completed" else "#2563EB" if s.get("status")=="active" else "#94A3B8"
        sprint_bars += f"""
        <div style="margin-bottom:16px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <strong>{s.get('name','Sprint')}</strong>
            <span style="color:{status_color}">{s.get('status','').upper()}</span>
          </div>
          <div style="background:#E2E8F0;border-radius:6px;height:12px">
            <div style="background:{status_color};width:{pct}%;height:12px;border-radius:6px"></div>
          </div>
          <small style="color:#64748B">{done}/{total} tasks · avg delay {s.get('avg_delay_days',0):.1f}d</small>
        </div>"""

    risk_cards = ""
    for r in [x for x in risks if x.get("risk_level") in ("HIGH","MEDIUM")][:6]:
        color = "#DC2626" if r.get("risk_level")=="HIGH" else "#D97706"
        risk_cards += f"""
        <div style="border:1px solid {color};border-left:5px solid {color};
                    border-radius:8px;padding:14px;margin-bottom:10px;background:#FFF">
          <div style="display:flex;justify-content:space-between">
            <strong>{r.get('task_title','')}</strong>
            <span style="color:{color};font-weight:bold">{r.get('risk_level','')} {r.get('risk_score',0):.2f}</span>
          </div>
          <div style="color:#64748B;font-size:13px;margin-top:4px">
            Assigned: {r.get('assigned_to','?')} · {r.get('category','')}
          </div>
          <div style="margin-top:6px">
            {" · ".join(r.get('top_factors',[])[:3])}
          </div>
        </div>"""

    pattern_cards = ""
    for p in learnings.get("patterns_detected",[])[:4]:
        pattern_cards += f"""
        <div style="border-left:4px solid #2563EB;padding:10px 14px;
                    background:#EFF6FF;margin-bottom:8px;border-radius:0 6px 6px 0;font-size:14px">
          {p[:200]}
        </div>"""

    strat_cards = ""
    for s in strats:
        strat_cards += f"""
        <div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:8px;padding:14px;margin-bottom:10px">
          <strong>⚡ {s.get('trigger_pattern','').replace('_',' ').title()}</strong>
          <span style="color:#D97706;margin-left:8px">{s.get('failure_rate',0):.0%} failure rate triggered adaptation</span>
          <div style="display:flex;gap:16px;margin-top:8px;font-size:13px">
            <div>
              <div style="color:#64748B">BEFORE</div>
              <div>Load: {s.get('old_weights',{}).get('current_load',0):.0%} · Completion: {s.get('old_weights',{}).get('completion_rate',0):.0%}</div>
            </div>
            <div style="font-size:20px">→</div>
            <div>
              <div style="color:#64748B">AFTER</div>
              <div>Load: {s.get('new_weights',{}).get('current_load',0):.0%} · Completion: {s.get('new_weights',{}).get('completion_rate',0):.0%}</div>
            </div>
          </div>
        </div>"""

    demo_section = ""
    if demo_sec:
        changed = demo_sec.get("assignment_changed_by_memory", False)
        mems = demo_sec.get("total_memories_accessed", 0)
        health = demo_sec.get("demo_health","UNKNOWN")
        health_color = "#16A34A" if health=="EXCELLENT" else "#D97706" if health=="GOOD" else "#DC2626"
        qa_html = ""
        for qa in demo_sec.get("chat_qa",[]):
            qa_html += f"""
            <div style="margin-bottom:14px">
              <div style="font-weight:600;color:#1E293B">Q: {qa['q']}</div>
              <div style="color:#475569;margin-top:4px;padding-left:12px;border-left:3px solid #2563EB">{qa['a'][:200]}...</div>
              <div style="font-size:12px;color:#0D9488;margin-top:4px">Used {qa['memories']} memories</div>
            </div>"""
        demo_section = f"""
        <div class="report-card" style="margin-bottom:28px">
          <h2>⚡ Auto Demo Results</h2>
          <div style="display:flex;gap:16px;margin-bottom:16px">
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;padding:12px 18px;text-align:center">
              <div style="font-size:28px;font-weight:bold;color:{health_color}">{health}</div>
              <div style="font-size:12px;color:#64748B">Demo Health</div>
            </div>
            <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:12px 18px;text-align:center">
              <div style="font-size:28px;font-weight:bold;color:#2563EB">{mems}</div>
              <div style="font-size:12px;color:#64748B">Memories Accessed</div>
            </div>
            <div style="background:{'#F0FDF4' if changed else '#FFF7ED'};border:1px solid {'#BBF7D0' if changed else '#FED7AA'};border-radius:8px;padding:12px 18px;text-align:center">
              <div style="font-size:28px;font-weight:bold;color:{'#16A34A' if changed else '#D97706'}">{'YES' if changed else 'NO'}</div>
              <div style="font-size:12px;color:#64748B">Assignment Changed by Memory</div>
            </div>
          </div>
          <h3>Chat Q&A with Memory Evidence</h3>
          {qa_html}
        </div>"""

    generated = report.get("generated_at","")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NEXUS-PM Project Intelligence Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #F8FAFC; color: #1E293B; line-height: 1.6; }}
  .page {{ max-width: 900px; margin: 0 auto; padding: 40px 24px; }}
  .report-header {{ background: linear-gradient(135deg,#1A3A6B,#2563EB);
                    color: white; border-radius: 12px; padding: 36px; margin-bottom: 32px; }}
  .report-header h1 {{ font-size: 28px; margin-bottom: 6px; }}
  .report-header p {{ opacity: 0.8; font-size: 14px; }}
  .report-card {{ background: #FFF; border: 1px solid #E2E8F0;
                  border-radius: 10px; padding: 24px; margin-bottom: 24px; }}
  .report-card h2 {{ font-size: 18px; color: #1A3A6B; margin-bottom: 16px;
                     padding-bottom: 10px; border-bottom: 2px solid #EFF6FF; }}
  .report-card h3 {{ font-size: 15px; color: #475569; margin: 14px 0 8px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  th {{ background: #F1F5F9; padding: 10px 12px; text-align: left;
        font-weight: 600; color: #475569; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #F1F5F9; }}
  .exec-summary {{ background: #EFF6FF; border-left: 5px solid #2563EB;
                   border-radius: 0 8px 8px 0; padding: 16px 20px;
                   font-size: 15px; color: #1E293B; }}
  .narrative {{ font-size: 15px; color: #334155; line-height: 1.8; }}
  .narrative p {{ margin-bottom: 14px; }}
  .footer {{ text-align: center; color: #94A3B8; font-size: 12px;
             margin-top: 40px; padding-top: 20px; border-top: 1px solid #E2E8F0; }}
  .print-btn {{ background: #2563EB; color: white; border: none;
                padding: 10px 20px; border-radius: 6px; cursor: pointer;
                font-size: 14px; float: right; }}
  @media print {{
    .print-btn {{ display: none; }}
    body {{ background: white; }}
    .report-header {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  }}
</style>
</head>
<body>
<div class="page">
  <div class="report-header">
    <button class="print-btn no-print" onclick="window.print()">Download PDF</button>
    <h1>NEXUS-PM Project Intelligence Report</h1>
    <p>Project: NEXUS Demo Project &nbsp;|&nbsp; Generated: {generated[:19].replace('T',' ')} UTC</p>
    <p style="margin-top:8px;font-size:13px;opacity:0.7">
      Powered by Hindsight Memory &nbsp;·&nbsp; {learnings.get('total_memories',0)} memories analyzed
    </p>
  </div>

  <div class="report-card">
    <h2>Executive Summary</h2>
    <div class="exec-summary">{exec_sum or "No summary available — ensure Hindsight memory is seeded."}</div>
  </div>

  <div class="report-card">
    <h2>Team Performance Overview</h2>
    <table>
      <thead><tr><th>Member</th><th>Role</th><th>Tasks</th><th>On-Time Rate</th><th>Avg Delay</th><th>Status</th></tr></thead>
      <tbody>{team_rows or "<tr><td colspan='6' style='color:#94A3B8;text-align:center'>No team data — run seed first</td></tr>"}</tbody>
    </table>
    {_team_highlights(team)}
  </div>

  <div class="report-card">
    <h2>Sprint Timeline</h2>
    {sprint_bars or "<p style='color:#94A3B8'>No sprint data yet.</p>"}
  </div>

  <div class="report-card">
    <h2>What NEXUS Learned</h2>
    <div style="display:flex;gap:16px;margin-bottom:16px">
      <div style="background:#EFF6FF;border-radius:8px;padding:12px 16px;text-align:center">
        <div style="font-size:24px;font-weight:bold;color:#2563EB">{learnings.get('total_memories',0)}</div>
        <div style="font-size:12px;color:#64748B">Total Memories</div>
      </div>
      <div style="background:#F0FDF4;border-radius:8px;padding:12px 16px;text-align:center">
        <div style="font-size:24px;font-weight:bold;color:#16A34A">{len(strats)}</div>
        <div style="font-size:12px;color:#64748B">Strategy Changes</div>
      </div>
      <div style="background:#FFFBEB;border-radius:8px;padding:12px 16px;text-align:center">
        <div style="font-size:24px;font-weight:bold;color:#D97706">{len(learnings.get('patterns_detected',[]))}</div>
        <div style="font-size:12px;color:#64748B">Patterns Detected</div>
      </div>
    </div>
    <h3>Behavioral Patterns Detected</h3>
    {pattern_cards or "<p style='color:#94A3B8'>No patterns detected yet.</p>"}
    <h3>Strategy Adaptations Made</h3>
    {strat_cards or "<p style='color:#94A3B8'>No adaptations yet. NEXUS adapts when failure rate exceeds 40%.</p>"}
  </div>

  <div class="report-card">
    <h2>Current Risk Analysis</h2>
    {risk_cards or "<p style='color:#16A34A'>No HIGH or MEDIUM risk tasks detected.</p>"}
  </div>

  {demo_section}

  <div class="report-card">
    <h2>NEXUS Intelligence Summary</h2>
    <div class="narrative">
      {''.join(f"<p>{{p.strip()}}</p>" for p in narrative.split('\n\n') if p.strip())
        if narrative else "<p style='color:#94A3B8'>Narrative unavailable — ensure memory banks are seeded.</p>"}
    </div>
  </div>

  <div class="footer">
    Generated by NEXUS-PM &nbsp;·&nbsp; Powered by Hindsight Memory (Vectorize) &nbsp;·&nbsp; {generated[:10]}
  </div>
</div>
</body>
</html>"""

def _team_highlights(team):
    html = "<div style='margin-top:14px'>"
    for m in team:
        if m.get("risk_flag"):
            html += f"<div style='background:#FFF7ED;border-left:4px solid #D97706;padding:8px 12px;margin-top:6px;font-size:13px;border-radius:0 6px 6px 0'><strong>{m['name']}:</strong> {m['risk_flag'][:100]}</div>"
        elif m.get("strength"):
            html += f"<div style='background:#F0FDF4;border-left:4px solid #16A34A;padding:8px 12px;margin-top:6px;font-size:13px;border-radius:0 6px 6px 0'><strong>{m['name']}:</strong> {m['strength'][:100]}</div>"
    html += "</div>"
    return html

if __name__ == "__main__":
    asyncio.run(generate())
