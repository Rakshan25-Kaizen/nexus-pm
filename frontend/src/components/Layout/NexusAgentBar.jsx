import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import useNexusStore from '../../store/useNexusStore';
import { agentChat } from '../../api/client';
import AgentAvatar from '../Agent/AgentAvatar';
import VoiceInput from '../Agent/VoiceInput';
import { Send, Bell, ArrowRight } from 'lucide-react';

export default function NexusAgentBar() {
  const navigate = useNavigate();
  const { projectId, memoryEnabled, wsConnected, isAgentTyping, activeNudges } = useNexusStore();
  const [input, setInput] = useState('');
  const [response, setResponse] = useState(null);
  const [showPanel, setShowPanel] = useState(false);
  const [showNudges, setShowNudges] = useState(false);
  const [lastQuestion, setLastQuestion] = useState('');

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!input.trim()) return;
    const msg = input;
    setLastQuestion(msg);
    setInput('');
    useNexusStore.getState().setAgentTyping(true);
    try {
      const data = await agentChat({ message: msg, project_id: projectId, memory_enabled: memoryEnabled });
      setResponse(data);
      setShowPanel(true);
      useNexusStore.getState().addAgentMessage({ role: 'nexus', content: data.agent_message, memories_used: data.memories_used });
    } catch (err) {
      setResponse({ agent_message: 'Connection error. Check backend.', memories_used: 0 });
      setShowPanel(true);
    }
    useNexusStore.getState().setAgentTyping(false);
  };

  const handleContinue = () => {
    // Prefill the agent chat with context
    useNexusStore.getState().addAgentMessage({ role: 'user', content: lastQuestion });
    if (response) {
      useNexusStore.getState().addAgentMessage({ role: 'nexus', content: response.agent_message, memories_used: response.memories_used });
    }
    setShowPanel(false);
    navigate('/agent');
  };

  return (
    <div className="relative">
      <div className="h-14 bg-[#0A1628] border-b border-gray-800 flex items-center px-4 gap-4">
        {/* Left: Avatar + Status */}
        <div className="flex items-center gap-2 min-w-[140px]">
          <AgentAvatar size={32} state={isAgentTyping ? 'thinking' : 'idle'} />
          <div className="flex flex-col">
            <span className="font-bold text-sm">NEXUS</span>
            <span className="text-[11px] text-gray-500">Quick answers</span>
          </div>
          <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-gray-500'}`} />
        </div>

        {/* Center: Input */}
        <form onSubmit={handleSubmit} className="flex-1 flex items-center gap-2">
          <div className="flex-1 relative">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Quick question for NEXUS... (Memory ${memoryEnabled ? 'ON' : 'OFF'})`}
              className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-accent transition"
            />
            <span className={`absolute right-3 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full ${
              memoryEnabled ? 'bg-green-400' : 'bg-red-400'
            }`} title={memoryEnabled ? 'Hindsight ON' : 'Memory OFF'} />
          </div>
          <VoiceInput onTranscript={(t) => setInput(t)} />
          <button type="submit" className="px-3 py-2 bg-accent rounded-lg text-sm hover:bg-blue-600 transition flex items-center gap-1.5">
            <Send size={14} />
            <span>Ask</span>
          </button>
        </form>

        {/* Right: Nudge bell */}
        <div className="relative">
          <button onClick={() => setShowNudges(!showNudges)} className="p-2 hover:bg-gray-800 rounded-lg transition relative">
            <Bell size={20} className="text-amber-400" />
            {activeNudges.length > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-xs flex items-center justify-center font-bold">
                {activeNudges.length}
              </span>
            )}
          </button>
          <AnimatePresence>
            {showNudges && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute right-0 top-12 w-80 bg-gray-900 border border-gray-700 rounded-lg shadow-xl p-3 z-50"
              >
                <h3 className="text-sm font-bold mb-2">Notifications</h3>
                {activeNudges.length === 0 ? (
                  <p className="text-gray-500 text-xs">No active notifications</p>
                ) : (
                  activeNudges.map((n) => (
                    <div key={n.id} className="p-2 bg-gray-800 rounded mb-1 text-xs">
                      {n.message}
                    </div>
                  ))
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Response Panel */}
      <AnimatePresence>
        {showPanel && response && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="bg-gray-900 border-b border-gray-800 px-6 py-3"
          >
            <div className="flex items-start justify-between gap-4">
              <p className="text-sm text-gray-200 flex-1">{response.agent_message}</p>
              <div className="flex items-center gap-2 shrink-0">
                {response.memories_used > 0 && (
                  <span className="text-xs bg-teal-900 text-teal-300 px-2 py-0.5 rounded">
                    Used {response.memories_used} memories
                  </span>
                )}
                <button onClick={() => setShowPanel(false)} className="text-gray-500 hover:text-white">×</button>
              </div>
            </div>
            {/* Continue conversation link */}
            <div className="mt-2 pt-2 border-t border-gray-800">
              <button
                onClick={handleContinue}
                className="text-xs text-accent hover:underline flex items-center gap-1"
              >
                <span>Continue conversation</span>
                <ArrowRight size={12} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
