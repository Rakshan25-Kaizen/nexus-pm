import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
});

// ─── Tasks ──────────────────────────────────────────
export const assignTask = (data) => api.post('/tasks/assign-task', data).then(r => r.data);
export const storeOutcome = (taskId, data) => api.post(`/tasks/${taskId}/complete`, data).then(r => r.data);
export const createTask = (data) => api.post('/tasks/', data).then(r => r.data);
export const getTasks = (projectId) => api.get(`/tasks/${projectId}`).then(r => r.data);
export const getTaskRisks = (projectId) => api.get(`/tasks/${projectId}/risks`).then(r => r.data);
export const getStrategyLog = (projectId) => api.get(`/tasks/${projectId}/strategy-log`).then(r => r.data);

// ─── Meetings ───────────────────────────────────────
export const summarizeMeeting = (data) => api.post('/meetings/summarize', data).then(r => r.data);
export const getMeetings = (projectId) => api.get(`/meetings/${projectId}`).then(r => r.data);

// ─── Chat ───────────────────────────────────────────
export const sendChat = (data) => api.post('/chat', data).then(r => r.data);

// ─── Members ────────────────────────────────────────
export const createMember = (data) => api.post('/members/', data).then(r => r.data);
export const getMembers = (projectId) => api.get(`/members/${projectId}`).then(r => r.data);
export const getMemberBehavior = (memberId) => api.get(`/members/${memberId}/behavior`).then(r => r.data);
export const getWorkloadForecast = (projectId) => api.get(`/members/${projectId}/forecast`).then(r => r.data);

// ─── Agent ──────────────────────────────────────────
export const agentChat = (data) => api.post('/agent/chat', data).then(r => r.data);
export const agentGreet = (projectId) => api.get(`/agent/greet/${projectId}`).then(r => r.data);
export const getNudges = (projectId) => api.get(`/agent/nudges/${projectId}`).then(r => r.data);
export const markNudgeRead = (nudgeId) => api.post(`/agent/nudges/${nudgeId}/read`).then(r => r.data);
export const getAgentStatus = (projectId) => api.get(`/agent/status/${projectId}`).then(r => r.data);
export const getMemoryStats = (projectId) => api.get(`/agent/memory-stats/${projectId}`).then(r => r.data);
export const beforeAfter = (data) => api.post('/agent/before-after', data).then(r => r.data);
export const explainTask = (taskId, projectId) => api.post(`/agent/explain/${taskId}?project_id=${projectId}`).then(r => r.data);
export const onboardMember = (data) => api.post('/agent/onboard', data).then(r => r.data);

// ─── Sprint ─────────────────────────────────────────
export const createSprint = (data) => api.post('/sprint/plan', data).then(r => r.data);
export const getSprints = (projectId) => api.get(`/sprint/${projectId}`).then(r => r.data);
export const getSprintHealth = (sprintId) => api.get(`/sprint/${sprintId}/health`).then(r => r.data);

// ─── Digest ─────────────────────────────────────────
export const getDigest = (projectId) => api.get(`/agent/digest/${projectId}`).then(r => r.data);
export const sendDigest = (projectId) => api.post(`/agent/digest/${projectId}/send`).then(r => r.data);

// ─── Report ─────────────────────────────────────────
export const generateReport = (projectId, opts = {}) => api.post(`/agent/report/${projectId}`, opts).then(r => r.data);
export const getQuickReport = (projectId) => api.get(`/agent/report/${projectId}/quick`).then(r => r.data);

// ─── Health ─────────────────────────────────────────
export const checkHealth = () => axios.get('http://localhost:8000/health').then(r => r.data);

export default api;
