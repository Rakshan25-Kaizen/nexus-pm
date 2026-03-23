import React, { useState, useEffect, useRef } from 'react';
import useNexusStore from '../../store/useNexusStore';
import { sendChat } from '../../api/client';
import VoiceInput from '../Agent/VoiceInput';

export default function MemoryChat() {
  const { projectId, chatHistory, memoryEnabled, addChatMessage, setLastMemorySnippets, incrementMemoryEvents, setAgentTyping, isAgentTyping } = useNexusStore();
  const [input, setInput] = useState('');
  const endRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [chatHistory]);

  useEffect(() => {
    // Auto-load greeting so page isn't blank
    const initChat = async () => {
      try {
        const data = await sendChat({
          message: "Hello NEXUS, give me a quick team status",
          project_id: projectId,
          memory_enabled: true,
        });
        addChatMessage({ role: 'nexus', content: data.response,
                         memories_used: data.memories_used || 0 });
      } catch {
        addChatMessage({
          role: 'nexus',
          content: 'Hey team — I\'m ready. Ask me about task history, '
                 + 'team patterns, or what we decided in any sprint.',
          memories_used: 0,
        });
      }
    };

    if (chatHistory.length === 0) {
      initChat();
    }
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;
    const msg = input; setInput('');
    addChatMessage({ role: 'user', content: msg });
    setAgentTyping(true);
    try {
      const data = await sendChat({ message: msg, project_id: projectId, memory_enabled: memoryEnabled });
      addChatMessage({ role: 'nexus', content: data.response, memories_used: data.memories_used });
      setLastMemorySnippets(data.memory_snippets || []);
      incrementMemoryEvents(data.memories_used);
    } catch {
      addChatMessage({ role: 'nexus', content: 'Connection error.', memories_used: 0 });
    }
    setAgentTyping(false);
  };

  return (
    <div className="flex flex-col h-full bg-gray-900/30 rounded-xl border border-gray-800">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {chatHistory.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-xl text-sm ${msg.role === 'user' ? 'bg-accent' : 'bg-gray-800'}`}>
              <p>{msg.content}</p>
              {msg.memories_used > 0 && <span className="text-xs bg-teal-900 text-teal-300 px-2 py-0.5 rounded mt-1 inline-block">Used {msg.memories_used} memories</span>}
            </div>
          </div>
        ))}
        {isAgentTyping && <div className="text-gray-400 text-sm animate-pulse">NEXUS is thinking...</div>}
        <div ref={endRef} />
      </div>
      <div className="p-3 border-t border-gray-800 flex gap-2">
        <textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
          placeholder="Ask a question..." rows={1} className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm resize-none focus:outline-none focus:border-accent" />
        <VoiceInput onTranscript={t => setInput(t)} />
        <button onClick={handleSend} className="px-4 py-2 bg-accent rounded-lg text-sm hover:bg-blue-600 transition">Send</button>
      </div>
    </div>
  );
}
