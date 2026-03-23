import { create } from 'zustand';

const useNexusStore = create((set, get) => ({
  // State
  projectId: 'project-1',
  members: [],
  tasks: [],
  chatHistory: [],
  strategyLog: [],
  currentRisks: [],
  isLoading: false,
  memoryEnabled: true,
  lastMemorySnippets: [],
  totalMemoryEvents: 0,
  lastMemoryBank: null,
  agentGreeting: '',
  activeNudges: [],
  agentHistory: [],
  isAgentTyping: false,
  sprintPlans: [],
  workloadData: {},
  memoryTimeline: [],
  beforeAfterResults: null,
  wsConnected: false,
  // Fix 3: Confidence
  lastAssignmentConfidence: null,
  // Fix 4: Morning digest
  morningDigest: '',
  digestTimestamp: '',

  // Actions
  setProjectId: (id) => set({ projectId: id }),
  setMemoryEnabled: (v) => set({ memoryEnabled: v }),
  addMember: (m) => set((s) => ({ members: [...s.members, m] })),
  setMembers: (m) => set({ members: m }),
  addTask: (t) => set((s) => ({ tasks: [...s.tasks, t] })),
  setTasks: (t) => set({ tasks: t }),
  updateTask: (id, data) =>
    set((s) => ({
      tasks: s.tasks.map((t) => (t.id === id ? { ...t, ...data } : t)),
    })),
  addChatMessage: (msg) =>
    set((s) => ({ chatHistory: [...s.chatHistory, msg] })),
  addStrategyEntry: (e) =>
    set((s) => ({ strategyLog: [...s.strategyLog, e] })),
  setRisks: (r) => set({ currentRisks: r }),
  setLoading: (v) => set({ isLoading: v }),
  setLastMemorySnippets: (s) => set({ lastMemorySnippets: s }),
  incrementMemoryEvents: (n) =>
    set((s) => ({ totalMemoryEvents: s.totalMemoryEvents + n })),
  setAgentGreeting: (g) => set({ agentGreeting: g }),
  addNudge: (n) => set((s) => ({ activeNudges: [...s.activeNudges, n] })),
  markNudgeRead: (id) =>
    set((s) => ({
      activeNudges: s.activeNudges.filter((n) => n.id !== id),
    })),
  addAgentMessage: (msg) =>
    set((s) => ({ agentHistory: [...s.agentHistory, msg] })),
  setAgentTyping: (v) => set({ isAgentTyping: v }),
  addSprintPlan: (p) =>
    set((s) => ({ sprintPlans: [...s.sprintPlans, p] })),
  setWorkloadData: (d) => set({ workloadData: d }),
  addMemoryEvent: (e) =>
    set((s) => ({
      memoryTimeline: [e, ...s.memoryTimeline].slice(0, 50),
      totalMemoryEvents: s.totalMemoryEvents + (e.count || 1),
      lastMemoryBank: e.bank || null,
    })),
  setLastMemoryBank: (bank) => set({ lastMemoryBank: bank }),
  setBeforeAfterResults: (r) => set({ beforeAfterResults: r }),
  setWsConnected: (v) => set({ wsConnected: v }),
  // Fix 3
  setLastAssignmentConfidence: (data) => set({ lastAssignmentConfidence: data }),
  // Fix 4
  setMorningDigest: (text) => set({ morningDigest: text }),
  setDigestTimestamp: (ts) => set({ digestTimestamp: ts }),
}));

export default useNexusStore;
