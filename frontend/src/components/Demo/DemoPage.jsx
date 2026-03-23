import React, { useState, useEffect, useCallback, useMemo } from 'react';
import useNexusStore from '../../store/useNexusStore';
import {
  getTasks,
  getTaskRisks,
  getMembers,
  getAgentStatus,
  getDigest,
  assignTask,
  agentChat,
  agentGreet,
  summarizeMeeting,
  createSprint,
  beforeAfter,
} from '../../api/client';
import AgentAvatar from '../Agent/AgentAvatar';
import DemoScene from './DemoScene';
import ACTsStepper from './ACTsStepper';
import BeforeAfterLive from './BeforeAfterLive';
import RiskChart from '../Analytics/RiskChart';
import WorkloadGauge from '../Analytics/WorkloadGauge';
import StrategyLog from '../Analytics/StrategyLog';
import MemoryTimeline from '../Analytics/MemoryTimeline';
import SummaryView from '../Meetings/SummaryView';
import SprintCard from '../Sprint/SprintCard';

const TABS = [
  'Dashboard',
  'Agent',
  'Task Assignment',
  'Meetings',
  'Sprint Planner',
  'Analytics',
  'Memory Timeline',
  'Before/After',
];

const MEETING_SAMPLE = `Alice: Memory layer is high complexity. One task only for me this sprint.
Bob: Analytics charts are mine. Recharts should be straightforward.
Priya: I will take the sprint planner endpoint once Alice has the memory API stable.
Raj: Can we lock requirements this time? Mid-sprint changes cost us last sprint.
Priya: Yes — all specs signed off before sprint starts.
Alice: NEXUS is going to be really useful once memory works.`;

const QUICK_CHIPS = [
  'Who should handle backend tasks?',
  "What is Alice's history?",
  'What are our team risk patterns?',
  'What did we decide in Sprint 2?',
];

const SPRINT_STAGES = [
  'Recalling past sprint performance...',
  'Analyzing team capacity...',
  'Optimizing task assignments...',
  'Generating sprint plan...',
];

export default function DemoPage() {
  const { projectId, memoryEnabled, members, tasks, setTasks, setRisks, setMembers, currentRisks, strategyLog, memoryTimeline, totalMemoryEvents, incrementMemoryEvents, setLastMemorySnippets } =
    useNexusStore();

  const [tab, setTab] = useState(0);
  const [dashLoading, setDashLoading] = useState(false);
  const [dashError, setDashError] = useState(null);
  const [digestText, setDigestText] = useState('');
  const [digestTime, setDigestTime] = useState('');
  const [agentStatus, setAgentStatus] = useState(null);

  const [agentMessages, setAgentMessages] = useState([]);
  const [agentInput, setAgentInput] = useState('');
  const [agentTyping, setAgentTyping] = useState(false);
  const [lastEvidence, setLastEvidence] = useState([]);

  const [taskPick, setTaskPick] = useState('');
  const [assignLoading, setAssignLoading] = useState(false);
  const [assignError, setAssignError] = useState(null);
  const [assignResult, setAssignResult] = useState(null);
  const [actStep, setActStep] = useState(0);

  const [meetingText, setMeetingText] = useState(MEETING_SAMPLE);
  const [meetLoading, setMeetLoading] = useState(false);
  const [meetError, setMeetError] = useState(null);
  const [meetSummary, setMeetSummary] = useState(null);

  const [sprintSelected, setSprintSelected] = useState({});
  const [sprintLoading, setSprintLoading] = useState(false);
  const [sprintStage, setSprintStage] = useState(-1);
  const [sprintPlan, setSprintPlan] = useState(null);
  const [sprintError, setSprintError] = useState(null);

  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  const [memCountDisplay, setMemCountDisplay] = useState(0);
  const [memStatus, setMemStatus] = useState(null);

  const [baLoading, setBaLoading] = useState(false);
  const [baResult, setBaResult] = useState(null);

  const DEMO_FALLBACK_TASK = useMemo(
    () => ({
      id: 'demo-fallback-task',
      title: 'Backend data processing pipeline',
      category: 'Backend',
      complexity: 'high',
      status: 'todo',
      due_date: '',
      is_blocking: false,
    }),
    []
  );

  const openTasks = useMemo(() => {
    const o = tasks.filter((t) => t.status !== 'done');
    if (o.length > 0) return o;
    return [DEMO_FALLBACK_TASK];
  }, [tasks, DEMO_FALLBACK_TASK]);

  const selectedTaskObj = useMemo(
    () => openTasks.find((t) => t.id === taskPick) || openTasks[0],
    [openTasks, taskPick]
  );

  const loadCore = useCallback(async () => {
    const [t, r, m] = await Promise.all([
      getTasks(projectId),
      getTaskRisks(projectId),
      getMembers(projectId),
    ]);
    setTasks(t);
    setRisks(r);
    setMembers(m);
  }, [projectId, setTasks, setRisks, setMembers]);

  useEffect(() => {
    loadCore().catch(() => {});
  }, [loadCore]);

  useEffect(() => {
    if (tab !== 0) return;
    let cancelled = false;
    (async () => {
      setDashLoading(true);
      setDashError(null);
      try {
        await loadCore();
        const [d, st] = await Promise.all([
          getDigest(projectId).catch(() => ({ digest: '', generated_at: '' })),
          getAgentStatus(projectId),
        ]);
        if (cancelled) return;
        setDigestText(d.digest || '');
        setDigestTime(d.generated_at ? new Date(d.generated_at).toLocaleString() : '');
        setAgentStatus(st);
      } catch (e) {
        if (!cancelled) setDashError(e?.message || 'load failed');
      } finally {
        if (!cancelled) setDashLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [tab, projectId, loadCore]);

  useEffect(() => {
    if (tab !== 1) return;
    setAgentTyping(true);
    agentGreet(projectId)
      .then((data) => {
        setAgentMessages([{ role: 'nexus', content: data.message, memories_used: 0 }]);
      })
      .catch(() => {
        setAgentMessages([
          { role: 'nexus', content: 'Hi — connect the backend for a live greeting.', memories_used: 0 },
        ]);
      })
      .finally(() => setAgentTyping(false));
  }, [tab, projectId]);

  useEffect(() => {
    if (actStep < 1 || actStep > 5) return;
    const id = setTimeout(() => {
      setActStep((s) => (s < 5 ? s + 1 : 6));
    }, 800);
    return () => clearTimeout(id);
  }, [actStep]);

  useEffect(() => {
    if (tab !== 6) return;
    getAgentStatus(projectId).then(setMemStatus).catch(() => {});
    setMemCountDisplay(0);
    const target = Math.max(totalMemoryEvents || 0, 1);
    let n = 0;
    const t = setInterval(() => {
      n += 1;
      setMemCountDisplay((v) => {
        const step = Math.max(1, Math.ceil(target / 24));
        return Math.min(v + step, target);
      });
      if (n >= 24) clearInterval(t);
    }, 45);
    return () => clearInterval(t);
  }, [tab, projectId, totalMemoryEvents]);

  useEffect(() => {
    if (tab !== 5) return;
    setAnalyticsLoading(true);
    getTaskRisks(projectId)
      .then(setRisks)
      .catch(() => {})
      .finally(() => setAnalyticsLoading(false));
  }, [tab, projectId, setRisks]);

  useEffect(() => {
    if (tab !== 4) return;
    loadCore().catch(() => {});
  }, [tab, loadCore]);

  useEffect(() => {
    if (tab !== 4) return;
    const open = tasks.filter((t) => t.status !== 'done');
    const source = open.length ? open : [DEMO_FALLBACK_TASK];
    setSprintSelected((prev) => {
      const next = { ...prev };
      source.forEach((t) => {
        if (next[t.id] === undefined) next[t.id] = true;
      });
      return next;
    });
  }, [tab, tasks, DEMO_FALLBACK_TASK]);

  const riskBreakdown = useMemo(() => {
    const lvl = (r) => String(r.risk_level || '').toUpperCase();
    const h = currentRisks.filter((r) => lvl(r) === 'HIGH').length;
    const m = currentRisks.filter((r) => lvl(r) === 'MEDIUM').length;
    const l = currentRisks.filter((r) => lvl(r) === 'LOW').length;
    return { h, m, l };
  }, [currentRisks]);

  const handleAssign = async () => {
    if (!selectedTaskObj || !members.length) return;
    setAssignError(null);
    setAssignResult(null);
    setActStep(0);
    setAssignLoading(true);
    try {
      const res = await assignTask({
        task_title: selectedTaskObj.title,
        task_category: selectedTaskObj.category || 'General',
        complexity: selectedTaskObj.complexity || 'medium',
        deadline: selectedTaskObj.due_date || '',
        days_remaining: 7,
        is_blocking: !!selectedTaskObj.is_blocking,
        project_id: projectId,
        candidates: members.map((m) => m.name),
        memory_enabled: true,
      });
      const trace = res.acts_trace || [];
      const recallLine = trace.find((x) => String(x).startsWith('RECALL:')) || 'RECALL:0';
      const n = parseInt(String(recallLine).split(':')[1], 10) || 0;
      setAssignResult({ ...res, _memories_found: n });
      setActStep(1);
    } catch (e) {
      setAssignError(e?.message || 'assign failed');
    }
    setAssignLoading(false);
  };

  const handleSendAgent = async (text) => {
    const msg = text || agentInput;
    if (!msg.trim()) return;
    setAgentInput('');
    setAgentMessages((m) => [...m, { role: 'user', content: msg }]);
    setAgentTyping(true);
    try {
      const data = await agentChat({ message: msg, project_id: projectId, memory_enabled: memoryEnabled });
      const snippets = data.memory_snippets || data.context?.memory_snippets || [];
      setLastMemorySnippets(snippets);
      setLastEvidence(
        snippets.length
          ? snippets
          : data.memories_used > 0
          ? [`Hindsight recall used ${data.memories_used} memory match(es) for this answer.`]
          : []
      );
      setAgentMessages((m) => [
        ...m,
        { role: 'nexus', content: data.agent_message, memories_used: data.memories_used || 0 },
      ]);
      incrementMemoryEvents(data.memories_used || 0);
    } catch {
      setAgentMessages((m) => [
        ...m,
        { role: 'nexus', content: 'Connection error. Is the backend running?', memories_used: 0 },
      ]);
      setLastEvidence([]);
    }
    setAgentTyping(false);
  };

  const handleSummarizeMeeting = async () => {
    setMeetLoading(true);
    setMeetError(null);
    setMeetSummary(null);
    try {
      const data = await summarizeMeeting({ transcript: meetingText, project_id: projectId });
      setMeetSummary(data);
    } catch (e) {
      setMeetError(e?.message || 'failed');
    }
    setMeetLoading(false);
  };

  const handleSprintPlan = async () => {
    setSprintError(null);
    setSprintPlan(null);
    setSprintLoading(true);
    setSprintStage(0);
    for (let i = 0; i < SPRINT_STAGES.length; i++) {
      setSprintStage(i);
      await new Promise((r) => setTimeout(r, 600));
    }
    try {
      const selectedTasks = openTasks
        .filter((t) => sprintSelected[t.id])
        .map((t) => (t.id ? { id: t.id, title: t.title, category: t.category, complexity: t.complexity } : t));
      const data = await createSprint({
        project_id: projectId,
        sprint_number: 5,
        available_members: members.map((m) => m.name),
        available_tasks: selectedTasks,
        velocity_target: 5,
      });
      setSprintPlan(data);
      useNexusStore.getState().addSprintPlan(data);
    } catch (e) {
      setSprintError(e?.message || 'failed');
    }
    setSprintLoading(false);
    setSprintStage(-1);
  };

  const handleBeforeAfter = async (payload) => {
    setBaResult(null);
    setBaLoading(true);
    try {
      const data = await beforeAfter({ ...payload, project_id: projectId });
      setBaResult(data);
    } catch {
      setBaResult(null);
    }
    setBaLoading(false);
  };

  const actData = assignResult
    ? {
        task_title: selectedTaskObj?.title || 'Task',
        task_category: selectedTaskObj?.category || 'General',
        complexity: selectedTaskObj?.complexity || 'medium',
        memories_found: assignResult._memories_found ?? 0,
        strategy_weights: assignResult.strategy_weights || {},
      }
    : {};

  const scores = assignResult?.all_scores || [];

  return (
    <div className="min-h-[calc(100vh-6rem)] text-white">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">NEXUS-PM Strategic Intelligence</h1>
        <p className="text-[#0D9488] text-sm mt-1 font-medium">
          Live Intelligence — All actions utilize real-time Hindsight memory, Groq processing, and XGBoost risk evaluation.
        </p>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {TABS.map((label, i) => (
          <button
            key={label}
            type="button"
            onClick={() => setTab(i)}
            className={`rounded-full px-4 py-2 text-sm font-medium transition ${
              tab === i ? 'bg-[#2563EB] text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-gray-800 bg-[#0A1628] p-6">
        {tab === 0 && (
          <DemoScene
            title="Dashboard"
            subtitle="Live task snapshot, digest, and team"
            isLoading={dashLoading}
            error={dashError}
          >
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-4">
                <p className="text-xs text-gray-500">Total Tasks</p>
                <p className="text-2xl font-bold">{tasks.length}</p>
              </div>
              <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-4">
                <p className="text-xs text-gray-500">High Risk</p>
                <p className="text-2xl font-bold text-red-400">{riskBreakdown.h}</p>
              </div>
              <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-4">
                <p className="text-xs text-gray-500">Memory Events</p>
                <p className="text-2xl font-bold text-teal-400">{totalMemoryEvents}</p>
              </div>
              <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-4">
                <p className="text-xs text-gray-500">Strategy Adaptations</p>
                <p className="text-2xl font-bold text-amber-400">{strategyLog.length}</p>
              </div>
            </div>

            <div className="rounded-xl border border-gray-800 bg-gray-900/40 p-4 mb-6 relative">
              <span className="absolute top-3 right-3 text-[11px] px-2 py-0.5 rounded text-white" style={{ background: '#0D9488' }}>
                Powered by Hindsight
              </span>
              <h3 className="text-sm font-semibold mb-2">Morning Brief</h3>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{digestText || '—'}</p>
              <p className="text-xs text-gray-500 mt-2">{digestTime}</p>
            </div>

            <div>
              <h3 className="text-sm font-semibold mb-3">Team</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {members.map((m) => (
                  <div key={m.id} className="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-900/50 p-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#2563EB]/30 text-sm font-bold">
                      {m.name
                        .split(' ')
                        .map((x) => x[0])
                        .join('')
                        .slice(0, 2)}
                    </div>
                    <div>
                      <p className="font-medium">{m.name}</p>
                      <p className="text-xs text-gray-500">{m.role || 'Member'}</p>
                      <p className="text-xs text-gray-500">{m.active_tasks ?? 0} active tasks</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </DemoScene>
        )}

        {tab === 1 && (
          <DemoScene title="Talk to NEXUS" subtitle="Agent chat with memory evidence" isLoading={false} error={null}>
            <div className="flex gap-4 h-[420px]">
              <div className="w-44 flex-shrink-0 flex flex-col items-center">
                <AgentAvatar size={56} state={agentTyping ? 'thinking' : 'idle'} />
                <p className="text-xs text-gray-500 mt-2 text-center">Memory events: {totalMemoryEvents}</p>
              </div>
              <div className="flex-1 flex flex-col min-w-0 border border-gray-800 rounded-xl bg-gray-900/30">
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {agentMessages.map((m, i) => (
                    <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div
                        className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${
                          m.role === 'user' ? 'bg-[#2563EB] text-white' : 'bg-gray-800 text-gray-200'
                        }`}
                      >
                        <p>{m.content}</p>
                        {m.role === 'nexus' && (m.memories_used || 0) > 0 && (
                          <span
                            className="mt-1 inline-block text-[11px] px-2 py-0.5 rounded text-white"
                            style={{ background: '#0D9488' }}
                          >
                            Used {m.memories_used} memories
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                  {agentTyping && (
                    <div className="flex justify-start">
                      <AgentAvatar size={32} state="thinking" />
                    </div>
                  )}
                </div>
                <div className="px-3 pb-2 flex flex-wrap gap-2">
                  {QUICK_CHIPS.map((c) => (
                    <button
                      key={c}
                      type="button"
                      onClick={() => handleSendAgent(c)}
                      className="text-xs px-3 py-1 rounded-full bg-gray-800 hover:bg-gray-700 text-gray-300"
                    >
                      {c}
                    </button>
                  ))}
                </div>
                <div className="p-3 border-t border-gray-800 flex gap-2">
                  <textarea
                    value={agentInput}
                    onChange={(e) => setAgentInput(e.target.value)}
                    className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm min-h-[44px]"
                    placeholder="Ask NEXUS..."
                    onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendAgent())}
                  />
                  <button
                    type="button"
                    onClick={() => handleSendAgent()}
                    className="px-4 py-2 rounded-lg bg-[#2563EB] text-sm font-medium"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
            <div className="mt-4 rounded-lg border border-gray-800 bg-gray-900/40 p-4">
              <h4 className="text-xs font-semibold text-gray-400 mb-2">Memory evidence</h4>
              {lastEvidence.length === 0 ? (
                <p className="text-xs text-gray-500">Evidence snippets appear after a response with memory recall.</p>
              ) : (
                lastEvidence.map((s, i) => (
                  <div
                    key={i}
                    className="mb-2 text-sm italic text-gray-300"
                    style={{ borderLeft: '2px solid #2563EB', padding: '8px 12px', fontSize: 13 }}
                  >
                    {s}
                  </div>
                ))
              )}
            </div>
          </DemoScene>
        )}

        {tab === 2 && (
          <DemoScene
            title="Task assignment — ACTs pipeline"
            subtitle="5-stage cognitive pipeline with live scoring"
            isLoading={assignLoading}
            error={assignError}
          >
            <div className="mb-4 flex flex-wrap gap-3 items-end">
              <div>
                <label className="text-xs text-gray-500">Open task</label>
                <select
                  value={selectedTaskObj?.id || ''}
                  onChange={(e) => setTaskPick(e.target.value)}
                  className="mt-1 block rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm min-w-[220px]"
                >
                  {openTasks.length === 0 && <option value="">No open tasks</option>}
                  {openTasks.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.title}
                    </option>
                  ))}
                </select>
              </div>
              <button
                type="button"
                disabled={!selectedTaskObj || assignLoading}
                onClick={handleAssign}
                className="rounded-lg bg-[#2563EB] px-4 py-2 text-sm font-medium disabled:opacity-50"
              >
                Assign Task
              </button>
            </div>

            <ACTsStepper
              currentAct={actStep >= 6 ? 6 : actStep}
              actData={actData}
            />

            {actStep >= 6 && assignResult && (
              <div className="mt-6 space-y-3">
                <h4 className="text-sm font-semibold">Ranked recommendations</h4>
                {scores.length === 0 && (
                  <div className="rounded-lg border border-gray-800 p-3 text-sm">
                    <p>
                      Top pick: <strong>{assignResult.assigned_to}</strong> — {assignResult.reason}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Risk: {assignResult.risk}</p>
                  </div>
                )}
                {scores.map((row, i) => (
                  <div key={i} className="rounded-lg border border-gray-800 bg-gray-900/50 p-3">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{row.member}</span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${
                          row.risk_level === 'HIGH' ? 'bg-red-900 text-red-300' : 'bg-gray-800 text-gray-300'
                        }`}
                      >
                        {row.risk_level}
                      </span>
                    </div>
                    <div className="mt-2 h-2 w-full rounded-full bg-gray-800">
                      <div
                        className="h-2 rounded-full bg-[#2563EB]"
                        style={{ width: `${Math.min(100, (row.recommendation_score || 0) * 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">{row.explanation}</p>
                  </div>
                ))}
              </div>
            )}
          </DemoScene>
        )}

        {tab === 3 && (
          <DemoScene
            title="Meeting intelligence"
            subtitle="Summarize transcript and retain memories"
            isLoading={meetLoading}
            error={meetError}
          >
            <textarea
              value={meetingText}
              onChange={(e) => setMeetingText(e.target.value)}
              className="w-full min-h-[160px] rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm"
            />
            <button
              type="button"
              onClick={handleSummarizeMeeting}
              disabled={meetLoading}
              className="mt-3 rounded-lg bg-[#2563EB] px-4 py-2 text-sm font-medium"
            >
              Summarize Meeting
            </button>
            {meetSummary && <SummaryView summary={meetSummary} />}
          </DemoScene>
        )}

        {tab === 4 && (
          <DemoScene
            title="Sprint planner"
            subtitle="Generate sprint plan with memory context"
            isLoading={sprintLoading}
            error={sprintError}
          >
            <div className="grid md:grid-cols-2 gap-6 mb-4">
              <div>
                <h4 className="text-xs text-gray-500 mb-2">Available tasks</h4>
                <div className="space-y-2 max-h-56 overflow-y-auto">
                  {openTasks.map((t) => (
                    <label key={t.id} className="flex items-center gap-2 text-sm text-gray-300">
                      <input
                        type="checkbox"
                        checked={!!sprintSelected[t.id]}
                        onChange={(e) =>
                          setSprintSelected((s) => ({ ...s, [t.id]: e.target.checked }))
                        }
                      />
                      {t.title}
                    </label>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-xs text-gray-500 mb-2">Team workload</h4>
                <div className="space-y-2">
                  {members.map((m) => (
                    <WorkloadGauge
                      key={m.id}
                      memberName={m.name}
                      activeTasks={m.active_tasks ?? 1}
                      capacity={3}
                      mini
                    />
                  ))}
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={handleSprintPlan}
              disabled={sprintLoading}
              className="rounded-lg bg-[#2563EB] px-4 py-2 text-sm font-medium"
            >
              Generate Sprint Plan
            </button>
            {sprintStage >= 0 && sprintLoading && (
              <div className="mt-4 space-y-2">
                {SPRINT_STAGES.map((s, i) => (
                  <div key={s} className={`text-sm flex items-center gap-2 ${i <= sprintStage ? 'text-white' : 'text-gray-600'}`}>
                    <span className={`w-2 h-2 rounded-full ${i <= sprintStage ? 'bg-[#2563EB]' : 'bg-gray-700'}`} />
                    {s}
                  </div>
                ))}
              </div>
            )}
            {sprintPlan && !sprintLoading && <SprintCard plan={sprintPlan} />}
          </DemoScene>
        )}

        {tab === 5 && (
          <DemoScene title="Analytics" subtitle="Live risk, workload, strategy, memory" isLoading={analyticsLoading} error={null}>
            <div className="mb-6">
              <h3 className="text-sm font-semibold mb-2">Risk</h3>
              <RiskChart risks={currentRisks} />
            </div>
            <div className="mb-6">
              <h3 className="text-sm font-semibold mb-2">Workload</h3>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {members.map((m) => (
                  <WorkloadGauge
                    key={m.id}
                    memberName={m.name}
                    activeTasks={m.active_tasks ?? 1}
                    capacity={3}
                  />
                ))}
              </div>
            </div>
            <StrategyLog entries={strategyLog} />
            <div className="mt-6">
              <h3 className="text-sm font-semibold mb-2">Memory timeline (client)</h3>
              <MemoryTimeline events={memoryTimeline} />
            </div>
          </DemoScene>
        )}

        {tab === 6 && (
          <DemoScene title="Memory timeline" subtitle="Hindsight growth and recent events" isLoading={false} error={null}>
            <div className="mb-6 flex flex-wrap gap-6 items-center">
              <div>
                <p className="text-xs text-gray-500">Total memories (session counter)</p>
                <p className="text-2xl font-bold text-teal-400">{memCountDisplay}</p>
              </div>
              <div className="flex gap-4 text-sm">
                <span className="rounded bg-gray-800 px-2 py-1">meetings-bank: {memStatus?.memory_bank_counts?.meetings ?? '—'}</span>
                <span className="rounded bg-gray-800 px-2 py-1">members-bank: {memStatus?.memory_bank_counts?.members ?? '—'}</span>
                <span className="rounded bg-gray-800 px-2 py-1">tasks-bank: {memStatus?.memory_bank_counts?.tasks ?? '—'}</span>
              </div>
            </div>
            <p className="text-xs text-gray-500 mb-4">
              Memory(t+1) = Memory(t) + E(t) — each retain and reflection grows the bank.
            </p>
            <MemoryTimeline events={memoryTimeline} max={20} />
          </DemoScene>
        )}

        {tab === 7 && (
          <DemoScene title="Before / After" subtitle="Assignment with vs without Hindsight" isLoading={false} error={null}>
            <BeforeAfterLive
              result={baResult}
              isLoading={baLoading}
              onCompare={handleBeforeAfter}
              memberNames={members.length ? members.map((m) => m.name) : ['Alice', 'Bob', 'Priya', 'Raj']}
            />
          </DemoScene>
        )}
      </div>
    </div>
  );
}
