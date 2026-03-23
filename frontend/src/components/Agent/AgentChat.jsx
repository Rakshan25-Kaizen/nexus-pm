import React, { useState, useEffect, useRef } from 'react';
import useNexusStore from '../../store/useNexusStore';
import { agentChat, agentGreet } from '../../api/client';
import AgentAvatar from './AgentAvatar';
import VoiceInput from './VoiceInput';
import { Send, Database, Info, X } from 'lucide-react';

const suggestions = ['Who\'s at risk?', 'Last meeting summary?', 'Team health?', 'Assign next task?'];

export default function AgentChat() {
  const { projectId, memoryEnabled, agentHistory, isAgentTyping, totalMemoryEvents, addAgentMessage, setAgentTyping } = useNexusStore();
  const [input, setInput] = useState('');
  const [showInfoBanner, setShowInfoBanner] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (agentHistory.length === 0) {
      agentGreet(projectId).then((data) => {
        addAgentMessage({ role: 'nexus', content: data.message, memories_used: 0 });
      }).catch(() => {
        addAgentMessage({ role: 'nexus', content: 'Looks like a fresh start. Tell me about your team.', memories_used: 0 });
      });
    }
  }, []);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [agentHistory]);

  const handleSend = async (text) => {
    const msg = text || input;
    if (!msg.trim()) return;
    setInput('');
    addAgentMessage({ role: 'user', content: msg });
    setAgentTyping(true);
    try {
      const data = await agentChat({ message: msg, project_id: projectId, memory_enabled: memoryEnabled });
      addAgentMessage({ role: 'nexus', content: data.agent_message, memories_used: data.memories_used });
      useNexusStore.getState().incrementMemoryEvents(data.memories_used);
    } catch {
      addAgentMessage({ role: 'nexus', content: 'Connection error. Is the backend running?', memories_used: 0 });
    }
    setAgentTyping(false);
  };

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)]">
      {/* Left Panel */}
      <div className="w-72 flex-shrink-0 bg-gray-900/50 rounded-xl p-6 flex flex-col items-center border border-gray-800">
        <AgentAvatar size={80} state={isAgentTyping ? 'thinking' : 'idle'} />
        <h1 className="text-xl font-bold mt-4">NEXUS</h1>
        <p className="text-gray-400 text-sm">AI Project Manager</p>
        <p className="text-xs text-gray-500 mt-1">Full conversation with memory evidence</p>
        <div className="mt-4 text-xs space-y-2 w-full">
          <div className="flex items-center gap-2">
            <Database size={12} className="text-green-400" />
            <span className="text-gray-400">Connected to Hindsight</span>
          </div>
          <div className="text-gray-500">Memory events: {totalMemoryEvents}</div>
        </div>
        <div className="mt-4 w-full space-y-2 overflow-y-auto flex-1">
          {agentHistory.slice(-3).filter(m => m.role === 'nexus').map((m, i) => (
            <div key={i} className="text-xs text-gray-500 bg-gray-800/50 p-2 rounded truncate">{m.content.slice(0, 80)}...</div>
          ))}
        </div>
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col bg-gray-900/30 rounded-xl border border-gray-800">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Info banner — show once */}
          {showInfoBanner && (
            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-3 flex items-start gap-2">
              <Info size={16} className="text-blue-400 mt-0.5 shrink-0" />
              <p className="text-xs text-blue-300 flex-1">
                This is NEXUS's full conversation mode. Your history is saved,
                memory evidence is shown for every response, and confidence scores
                are visible. Use the top bar for quick one-off questions.
              </p>
              <button onClick={() => setShowInfoBanner(false)} className="text-gray-500 hover:text-white shrink-0">
                <X size={14} />
              </button>
            </div>
          )}
          {agentHistory.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] p-3 rounded-xl text-sm ${
                msg.role === 'user' ? 'bg-accent text-white' : 'bg-gray-800 text-gray-200'
              }`}>
                <p>{msg.content}</p>
                {msg.role === 'nexus' && msg.memories_used > 0 && (
                  <span className="mt-1 inline-block text-xs bg-teal-900 text-teal-300 px-2 py-0.5 rounded">
                    Used {msg.memories_used} memories
                  </span>
                )}
              </div>
            </div>
          ))}
          {isAgentTyping && (
            <div className="flex justify-start">
              <div className="bg-gray-800 p-3 rounded-xl text-sm flex gap-1">
                <span className="animate-bounce">●</span>
                <span className="animate-bounce" style={{ animationDelay: '0.1s' }}>●</span>
                <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>●</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggestion chips */}
        <div className="px-4 pb-2 flex gap-2 flex-wrap">
          {suggestions.map((s) => (
            <button key={s} onClick={() => handleSend(s)} className="text-xs px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded-full text-gray-300 transition">
              {s}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-800 flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
            placeholder="Ask NEXUS..."
            rows={1}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm resize-none focus:outline-none focus:border-accent"
          />
          <VoiceInput onTranscript={(t) => setInput(t)} />
          <button onClick={() => handleSend()} className="px-4 py-2 bg-accent rounded-lg text-sm font-medium hover:bg-blue-600 transition flex items-center gap-1.5">
            <Send size={14} />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  );
}
