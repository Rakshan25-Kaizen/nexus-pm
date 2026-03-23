import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import useNexusStore from '../../store/useNexusStore';
import { generateReport, getQuickReport } from '../../api/client';
import AgentAvatar from '../Agent/AgentAvatar';
import { Download, FileText, CheckCircle, AlertTriangle, XCircle, ArrowRight } from 'lucide-react';

export default function ReportPage() {
  const { projectId } = useNexusStore();
  const [searchParams] = useSearchParams();
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loadingStep, setLoadingStep] = useState(0);

  const isDemoMode = searchParams.get('demo') === 'true';
  const projectName = "NEXUS Demo Project";

  const loadingSteps = [
    "Reading team behavioral memory...",
    "Analyzing sprint performance...",
    "Scoring task risks...",
    "Generating strategic insights...",
    "Writing your report..."
  ];

  useEffect(() => {
    let interval;
    if (isLoading) {
      interval = setInterval(() => {
        setLoadingStep(s => (s < loadingSteps.length - 1 ? s + 1 : s));
      }, 600);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleGenerateReport = async () => {
    setIsLoading(true);
    setLoadingStep(0);
    setError(null);
    setReport(null);
    try {
      const data = await generateReport(projectId, {
        include_demo_results: isDemoMode,
        demo_file: isDemoMode ? 'demo_results.json' : null
      });
      setReport(data);
    } catch (e) {
      console.error(e);
      setError("Failed to generate report. Ensure backend is running and data is seeded.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh]">
        <AgentAvatar size={80} state="thinking" />
        <h2 className="text-xl font-semibold mt-6 mb-2">NEXUS is analyzing your project...</h2>
        <div className="text-gray-400 h-6 transition-all duration-300">
          {loadingSteps[loadingStep]}
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="max-w-3xl mx-auto flex flex-col items-center justify-center py-20">
        <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mb-6">
          <FileText size={40} className="text-accent" />
        </div>
        <h1 className="text-3xl font-bold mb-4">Project Intelligence Report</h1>
        <p className="text-gray-400 text-center mb-8 max-w-lg">
          Generate a comprehensive AI-powered report analyzing team behavior, sprint velocity, strategic changes, and hidden risks based on Hindsight memory.
        </p>
        <button
          onClick={handleGenerateReport}
          className="bg-accent hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors"
        >
          <FileText size={20} />
          Generate Report
        </button>
        {error && <div className="text-red-400 mt-6 bg-red-400/10 p-4 rounded-lg">{error}</div>}
      </div>
    );
  }

  const { sections, generated_at } = report;
  const team = sections.team_profiles || [];
  const sprints = sections.sprint_timeline || [];
  const learnings = sections.nexus_learnings || {};
  const risks = sections.risk_analysis || [];
  const strats = sections.strategy_adaptations || [];
  const demo = sections.demo_results;
  const narrative = sections.narrative;
  const exec_summary = sections.executive_summary;

  return (
    <>
      <style>{`
        @media print {
          .no-print { display: none !important; }
          body { background: white !important; color: black !important; }
          .report-card { break-inside: avoid; }
        }
      `}</style>
      
      <div className="max-w-[900px] mx-auto bg-[#F8FAFC] text-[#1E293B] min-h-screen p-8 rounded-xl relative shadow-[0_0_40px_rgba(0,0,0,0.3)] no-print">
        
        {/* HEADER SECTION */}
        <div className="bg-gradient-to-br from-[#1A3A6B] to-[#2563EB] text-white rounded-xl p-8 mb-8 relative report-card">
          <button 
            onClick={() => window.print()} 
            className="no-print absolute top-6 right-6 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors text-white text-sm"
          >
            <Download size={16} /> Download PDF
          </button>
          
          <div className="text-blue-300 text-xs font-bold tracking-widest mb-2 uppercase">NEXUS AI Project Manager</div>
          <h1 className="text-3xl font-bold mb-2">Project Intelligence Report</h1>
          <p className="text-blue-200 text-sm">
            Project: {projectName} &nbsp;|&nbsp; Generated: {new Date(generated_at).toLocaleString()}
          </p>
          <p className="text-blue-300 text-xs mt-3 opacity-80 flex items-center gap-1.5">
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4"><path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 100-16 8 8 0 000 16zm1-8h4v2h-6V7h2v5z"/></svg>
            Powered by Hindsight Memory · {learnings.total_memories || 0} memories analyzed
          </p>
        </div>

        {/* SECTION 1: Executive Summary */}
        <div className="bg-white border border-[#E2E8F0] rounded-xl p-6 mb-6 report-card shadow-sm">
          <h2 className="text-[#1A3A6B] text-lg font-bold mb-4 pb-2 border-b-2 border-[#EFF6FF]">Executive Summary</h2>
          <div className="bg-[#EFF6FF] border-l-4 border-[#2563EB] rounded-r-lg p-4 text-[#1E293B] font-medium leading-relaxed">
            {exec_summary || "No summary available."}
          </div>
        </div>

        {/* SECTION 2: Team Performance Overview */}
        <div className="bg-white border border-[#E2E8F0] rounded-xl p-6 mb-6 report-card shadow-sm">
          <h2 className="text-[#1A3A6B] text-lg font-bold mb-4 pb-2 border-b-2 border-[#EFF6FF]">Team Performance Overview</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-[#F1F5F9] text-[#475569]">
                <tr>
                  <th className="p-3 font-semibold rounded-tl-lg">Member</th>
                  <th className="p-3 font-semibold">Role</th>
                  <th className="p-3 font-semibold">Tasks Completed</th>
                  <th className="p-3 font-semibold">On-Time Rate</th>
                  <th className="p-3 font-semibold">Avg Delay</th>
                  <th className="p-3 font-semibold rounded-tr-lg">Status</th>
                </tr>
              </thead>
              <tbody>
                {team.map((m, i) => {
                  const rate = m.on_time_rate || 0;
                  const colorClass = rate >= 0.85 ? 'text-[#16A34A]' : rate >= 0.7 ? 'text-[#D97706]' : 'text-[#DC2626]';
                  return (
                    <tr key={i} className="border-b border-[#F1F5F9]">
                      <td className="p-3 font-bold">{m.name}</td>
                      <td className="p-3 text-[#475569]">{m.role}</td>
                      <td className="p-3">{m.tasks_completed}/{m.tasks_assigned}</td>
                      <td className={`p-3 font-bold ${colorClass}`}>{(rate * 100).toFixed(0)}%</td>
                      <td className="p-3">{m.avg_delay_days.toFixed(1)} days</td>
                      <td className="p-3 font-medium flex items-center gap-1.5">
                        {rate >= 0.85 ? <><CheckCircle size={14} className="text-green-600"/> Strong</> :
                         rate >= 0.7 ? <><AlertTriangle size={14} className="text-amber-600"/> Watch</> :
                         <><AlertTriangle size={14} className="text-red-600"/> Risk</>}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          <div className="mt-4 space-y-2">
            {team.map((m, i) => (
              m.risk_flag ? (
                <div key={i} className="bg-[#FFF7ED] border-l-4 border-[#D97706] p-3 text-sm rounded-r-lg flex items-start gap-2">
                  <span className="font-bold min-w-16">{m.name}:</span> {m.risk_flag}
                </div>
              ) : m.strength ? (
                <div key={`s-${i}`} className="bg-[#F0FDF4] border-l-4 border-[#16A34A] p-3 text-sm rounded-r-lg flex items-start gap-2">
                  <span className="font-bold min-w-16">{m.name}:</span> {m.strength}
                </div>
              ) : null
            ))}
          </div>
        </div>

        {/* SECTION 3: Sprint Timeline */}
        <div className="bg-white border border-[#E2E8F0] rounded-xl p-6 mb-6 report-card shadow-sm">
          <h2 className="text-[#1A3A6B] text-lg font-bold mb-4 pb-2 border-b-2 border-[#EFF6FF]">Sprint Timeline</h2>
          <div className="space-y-4">
            {sprints.map((s, i) => {
              const total = s.tasks_total || 1;
              const pct = (s.tasks_done / total) * 100;
              const isDone = s.status === 'completed';
              const color = isDone ? '#16A34A' : s.status === 'active' ? '#2563EB' : '#94A3B8';
              return (
                <div key={i}>
                  <div className="flex justify-between text-sm font-semibold mb-1">
                    <span>{s.name}</span>
                    <span style={{ color }}>{s.status.toUpperCase()}</span>
                  </div>
                  <div className="bg-[#E2E8F0] h-3 rounded-full overflow-hidden w-full">
                    <div style={{ width: `${pct}%`, backgroundColor: color }} className="h-full rounded-full transition-all duration-500"/>
                  </div>
                  <div className="text-xs text-[#64748B] mt-1 flex justify-between">
                    <span>{s.tasks_done}/{total} tasks generated</span>
                    {s.avg_delay > 0 && <span className="text-[#D97706] font-medium">Avg delay: {s.avg_delay.toFixed(1)}d</span>}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* SECTION 4: NEXUS Learnings */}
        <div className="bg-white border border-[#E2E8F0] rounded-xl p-6 mb-6 report-card shadow-sm">
          <h2 className="text-[#1A3A6B] text-lg font-bold mb-4 pb-2 border-b-2 border-[#EFF6FF]">What NEXUS Learned</h2>
          
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-[#EFF6FF] rounded-lg p-4 text-center border border-[#BFDBFE]">
              <div className="text-3xl font-bold text-[#2563EB]">{learnings.total_memories || 0}</div>
              <div className="text-xs text-[#64748B] font-medium uppercase mt-1">Total Memories</div>
            </div>
            <div className="bg-[#F0FDF4] rounded-lg p-4 text-center border border-[#BBF7D0]">
              <div className="text-3xl font-bold text-[#16A34A]">{strats.length}</div>
              <div className="text-xs text-[#64748B] font-medium uppercase mt-1">Strategy Changes</div>
            </div>
            <div className="bg-[#FFFBEB] rounded-lg p-4 text-center border border-[#FDE68A]">
              <div className="text-3xl font-bold text-[#D97706]">{(learnings.patterns_detected || []).length}</div>
              <div className="text-xs text-[#64748B] font-medium uppercase mt-1">Patterns Detected</div>
            </div>
          </div>

          {(learnings.patterns_detected && learnings.patterns_detected.length > 0) ? (
            <div className="mb-6">
              <h3 className="text-sm font-bold text-[#475569] uppercase tracking-wider mb-3">Behavioral Patterns</h3>
              <div className="space-y-2">
                {learnings.patterns_detected.slice(0, 4).map((p, i) => (
                  <div key={i} className="bg-[#EFF6FF] border-l-4 border-[#2563EB] p-3 text-sm rounded-r-lg">{p}</div>
                ))}
              </div>
            </div>
          ) : null}

          {(strats && strats.length > 0) ? (
            <div>
              <h3 className="text-sm font-bold text-[#475569] uppercase tracking-wider mb-3">Strategy Adaptations Made</h3>
              <div className="space-y-3">
                {strats.map((s, i) => (
                  <div key={i} className="bg-[#FFFBEB] border border-[#FCD34D] rounded-lg p-4">
                    <div className="font-bold text-[#D97706] flex items-center gap-2 mb-2">
                      <AlertTriangle size={16}/> {s.trigger_pattern.replace(/_/g, ' ').toUpperCase()}
                    </div>
                    <div className="text-xs text-[#92400E] mb-3 bg-[#FEF3C7] inline-block px-2 py-1 rounded">
                      {(s.failure_rate * 100).toFixed(0)}% failure rate triggered adaptation
                    </div>
                    
                    <div className="flex items-center gap-6 justify-center bg-white p-3 rounded border border-[#FDE68A]">
                      <div className="text-center">
                        <div className="text-[10px] font-bold text-[#94A3B8] tracking-widest uppercase mb-1">Old Weights</div>
                        <div className="text-xs"><span className="font-medium">Load:</span> {((s.old_weights?.current_load || 0) * 100).toFixed(0)}%</div>
                        <div className="text-xs"><span className="font-medium">Completion:</span> {((s.old_weights?.completion_rate || 0) * 100).toFixed(0)}%</div>
                      </div>
                      <ArrowRight size={20} className="text-[#94A3B8]"/>
                      <div className="text-center">
                        <div className="text-[10px] font-bold text-[#94A3B8] tracking-widest uppercase mb-1">New Weights</div>
                        <div className="text-xs"><span className="font-medium">Load:</span> {((s.new_weights?.current_load || 0) * 100).toFixed(0)}%</div>
                        <div className="text-xs"><span className="font-medium">Completion:</span> {((s.new_weights?.completion_rate || 0) * 100).toFixed(0)}%</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>

        {/* SECTION 5: Current Risk Analysis */}
        <div className="bg-white border border-[#E2E8F0] rounded-xl p-6 mb-6 report-card shadow-sm">
          <h2 className="text-[#1A3A6B] text-lg font-bold mb-4 pb-2 border-b-2 border-[#EFF6FF]">Active Risk Analysis (XGBoost)</h2>
          {risks.filter(r => r.risk_level === 'HIGH' || r.risk_level === 'MEDIUM').length === 0 ? (
            <div className="text-green-600 bg-green-50 p-4 rounded-lg font-medium flex items-center gap-2">
              <CheckCircle size={18}/> No HIGH or MEDIUM risk tasks detected. TEAM IS ON TRACK.
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {risks.filter(r => r.risk_level === 'HIGH' || r.risk_level === 'MEDIUM').slice(0, 6).map((r, i) => {
                const colorHex = r.risk_level === 'HIGH' ? '#DC2626' : '#D97706';
                const bgHex = r.risk_level === 'HIGH' ? '#FEF2F2' : '#FFFBEB';
                return (
                  <div key={i} className="border rounded-lg p-4" style={{ borderColor: colorHex, borderLeftWidth: '4px', backgroundColor: bgHex }}>
                    <div className="flex justify-between items-start mb-2">
                      <div className="font-semibold text-sm mr-2">{r.task_title}</div>
                      <div className="font-black text-sm whitespace-nowrap" style={{ color: colorHex }}>{r.risk_score.toFixed(2)}</div>
                    </div>
                    <div className="text-xs font-medium text-[#475569] mb-2 border-b pb-2 border-black/5">
                      Assigned: {r.assigned_to} &middot; {r.category}
                    </div>
                    <div className="text-xs text-[#64748B] leading-tight">
                      <strong>Key factors: </strong>
                      {r.top_factors.slice(0, 3).join(', ')}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* SECTION 6: Demo Section */}
        {demo && (
          <div className="bg-white border border-[#E2E8F0] rounded-xl p-6 mb-6 report-card shadow-sm">
            <h2 className="text-[#1A3A6B] text-lg font-bold mb-4 pb-2 border-b-2 border-[#EFF6FF]">⚡ Auto Demo Verification Results</h2>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-[#F0FDF4] border border-[#BBF7D0] rounded-lg p-4 text-center">
                <div className={`text-2xl font-bold ${demo.demo_health === 'EXCELLENT' ? 'text-green-600' : 'text-amber-600'}`}>
                  {demo.demo_health}
                </div>
                <div className="text-xs text-[#64748B] mt-1">Demo Health</div>
              </div>
              <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-[#2563EB]">{demo.total_memories_accessed}</div>
                <div className="text-xs text-[#64748B] mt-1">Memories Accessed</div>
              </div>
              <div className={`${demo.assignment_changed_by_memory ? 'bg-[#F0FDF4] border-[#BBF7D0]' : 'bg-[#FFF7ED] border-[#FED7AA]'} border rounded-lg p-4 text-center`}>
                <div className={`text-2xl font-bold ${demo.assignment_changed_by_memory ? 'text-green-600' : 'text-amber-600'}`}>
                  {demo.assignment_changed_by_memory ? 'YES' : 'NO'}
                </div>
                <div className="text-xs text-[#64748B] mt-1">Assignment Shifted by Evidence</div>
              </div>
            </div>
            
            <h3 className="text-sm font-bold text-[#475569] uppercase tracking-wider mb-4 border-t pt-4">Memory Chat Interrogations</h3>
            <div className="space-y-4">
              {(demo.chat_qa || []).map((qa, i) => (
                <div key={i} className="bg-[#F8FAFC] border border-[#E2E8F0] p-4 rounded-lg">
                  <div className="font-bold text-sm mb-2 text-[#1E293B]">Q: {qa.q}</div>
                  <div className="text-sm text-[#475569] border-l-2 border-[#2563EB] pl-3 py-1 mb-2 leading-relaxed">
                    {qa.a.substring(0, 300)}...
                  </div>
                  <div className="text-xs font-semibold text-[#0D9488] bg-[#F0FDFA] inline-block px-2 py-1 rounded">
                    Anchored securely using {qa.memories} memories
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SECTION 7: Narrative */}
        <div className="bg-white border border-[#E2E8F0] rounded-xl p-6 mb-8 report-card shadow-sm">
          <h2 className="text-[#1A3A6B] text-lg font-bold mb-4 pb-2 border-b-2 border-[#EFF6FF]">NEXUS Intelligence Analyst Summary</h2>
          <div className="prose prose-sm text-[#334155] max-w-none text-justify leading-[1.8] font-serif">
            {narrative ? narrative.split('\n\n').map((p, i) => <p key={i} className="mb-4 text-[15px]">{p}</p>) : 
              <span className="italic">No conclusive intelligence assembled yet. Complete more sprints or supply more meetings data into memory.</span>}
          </div>
        </div>

        {/* FOOTER */}
        <div className="text-center text-[#94A3B8] text-xs pt-4 border-t border-[#E2E8F0] mb-8 pb-8 no-print">
          Generated entirely by NEXUS-PM &middot; Accelerated utilizing Vectorize Hindsight Cloud &middot; {new Date(generated_at).toISOString().split('T')[0]}
        </div>
      </div>
    </>
  );
}
