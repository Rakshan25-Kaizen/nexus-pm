import React, { useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Layout/Sidebar';
import NexusAgentBar from './components/Layout/NexusAgentBar';
import NudgeToast from './components/Agent/NudgeToast';
import Dashboard from './components/Dashboard/Dashboard';
import TaskBoard from './components/Tasks/TaskBoard';
import MeetingUpload from './components/Meetings/MeetingUpload';
import MemoryChat from './components/Chat/MemoryChat';
import MemoryPanel from './components/Chat/MemoryPanel';
import AnalyticsPage from './components/Analytics/AnalyticsPage';
import AgentChat from './components/Agent/AgentChat';
import SprintPlanner from './components/Sprint/SprintPlanner';
import MemberCard from './components/Members/MemberCard';
import OnboardingFlow from './components/Members/OnboardingFlow';
import useNexusStore from './store/useNexusStore';
import { useWebSocket } from './api/websocket';
import { agentGreet, getMembers } from './api/client';

import ReportPage from './components/Report/ReportPage';
import DemoPage from './components/Demo/DemoPage';

function MembersPage() {
  const { members, projectId } = useNexusStore();
  const [showOnboarding, setShowOnboarding] = React.useState(false);

  useEffect(() => {
    getMembers(projectId).then((data) => useNexusStore.getState().setMembers(data)).catch(() => {});
  }, [projectId]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Team Members</h1>
        <button
          onClick={() => setShowOnboarding(true)}
          className="px-4 py-2 bg-accent rounded-lg hover:bg-blue-600 transition"
        >
          + Add Member
        </button>
      </div>
      {showOnboarding && <OnboardingFlow onClose={() => setShowOnboarding(false)} />}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {members.map((m) => (
          <MemberCard key={m.id} member={m} />
        ))}
      </div>
      {members.length === 0 && (
        <p className="text-gray-500 text-center mt-12">No team members yet. Add your first member above.</p>
      )}
    </div>
  );
}

function ChatPage() {
  return (
    <div className="flex gap-4 h-[calc(100vh-8rem)]">
      <div className="flex-1"><MemoryChat /></div>
      <div className="w-72"><MemoryPanel /></div>
    </div>
  );
}

export default function App() {
  const { projectId, setAgentGreeting, addNudge, addAgentMessage, setWsConnected } = useNexusStore();
  const { isConnected, lastMessage } = useWebSocket(projectId);

  useEffect(() => {
    setWsConnected(isConnected);
  }, [isConnected]);

  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'nudge') {
        addNudge({ id: Date.now().toString(), ...lastMessage });
      } else if (lastMessage.type === 'agent_message') {
        addAgentMessage({ role: 'nexus', content: lastMessage.content, memories_used: lastMessage.memories_used || 0 });
      } else if (lastMessage.type === 'morning_digest') {
        useNexusStore.getState().setMorningDigest(lastMessage.content);
        useNexusStore.getState().setDigestTimestamp(lastMessage.timestamp);
      }
    }
  }, [lastMessage]);

  // SSE Listener for Proactive Nudges
  useEffect(() => {
    const sse = new EventSource(`/api/notifications/events/${projectId}`);
    
    sse.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'nudge') {
          addNudge({ id: Date.now().toString(), ...data });
        } else if (data.type === 'morning_digest') {
          useNexusStore.getState().setMorningDigest(data.content);
          useNexusStore.getState().setDigestTimestamp(data.timestamp);
        }
      } catch (err) {
        console.error("SSE parse error:", err);
      }
    };

    sse.onerror = () => {
      console.warn("SSE connection lost. Reconnecting...");
      sse.close();
    };

    return () => sse.close();
  }, [projectId]);

  useEffect(() => {
    agentGreet(projectId)
      .then((data) => setAgentGreeting(data.message))
      .catch(() => {});
  }, [projectId]);

  const location = useLocation();
  const isDemo = location.pathname === '/demo';

  return (
    <div className="flex h-screen bg-gray-950 text-white">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-60">
        <NexusAgentBar />
        <main className="flex-1 overflow-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<TaskBoard />} />
            <Route path="/meetings" element={<MeetingUpload />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/agent" element={<AgentChat />} />
            <Route path="/sprint" element={<SprintPlanner />} />
            <Route path="/members" element={<MembersPage />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="/demo" element={<DemoPage />} />
          </Routes>
        </main>
      </div>
      <NudgeToast />
    </div>
  );
}
