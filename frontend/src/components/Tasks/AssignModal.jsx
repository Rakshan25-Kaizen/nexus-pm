import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { assignTask } from '../../api/client';
import useNexusStore from '../../store/useNexusStore';
import { UserCheck, Check, Zap } from 'lucide-react';
import { CursorCaption, SpotlightCard, SmartTooltip, AnomalyTooltipContent, AIInsightTooltipContent } from '../Shared/CursorSystem';

const acts = [
  { label: 'PERCEIVING', desc: 'Analyzing task requirements...' },
  { label: 'RECALLING MEMORIES', desc: 'Searching Hindsight memory banks...' },
  { label: 'REASONING', desc: 'LLM + XGBoost processing...' },
  { label: 'ADAPTING STRATEGY', desc: 'Applying current strategy weights...' },
  { label: 'LEARNING', desc: 'Storing experience for future decisions...' },
];

// Build caption for each candidate
function candidateCaption(s) {
  const conf = Math.round((s.recommendation_score || s.confidence || 0) * 100);
  if (s.risk_level === 'HIGH')
    return `${s.member} carries high delay risk for this task`;
  if (conf >= 80)
    return `${s.member} is NEXUS's top recommendation`;
  if (conf >= 60)
    return `${s.member} is a reasonable choice`;
  return `${s.member} — limited history for this task type`;
}

export default function AssignModal({ onClose }) {
  const { members, memoryEnabled, projectId } = useNexusStore();
  const [form, setForm] = useState({ task_title: '', task_category: 'Backend', complexity: 'medium', deadline: '', days_remaining: 7, is_blocking: false });
  const [currentAct, setCurrentAct] = useState(-1);
  const [result, setResult] = useState(null);
  const [isComplete, setIsComplete] = useState(false);

  const handleAssign = async () => {
    if (!form.task_title || members.length === 0) return;
    setCurrentAct(0);
    for (let i = 0; i < 5; i++) {
      setCurrentAct(i);
      await new Promise(r => setTimeout(r, 800));
    }
    try {
      const data = await assignTask({
        ...form, project_id: projectId,
        candidates: members.map(m => m.name),
        memory_enabled: memoryEnabled,
      });
      setResult(data);
      // Update the matching task in store with returned confidence
      const { tasks, updateTask } = useNexusStore.getState();
      const matchedTask = tasks.find(t => t.title.toLowerCase() === form.task_title.toLowerCase());
      if (matchedTask) {
        updateTask(matchedTask.id, {
          risk_score: data.risk_score,
          risk_level: data.risk,
          confidence: data.confidence,
        });
      }
      setIsComplete(true);
    } catch (e) {
      setResult({ assigned_to: 'Error', reason: 'Assignment failed', all_scores: [] });
      setIsComplete(true);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-40" onClick={onClose}>
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-[600px] max-h-[80vh] overflow-y-auto p-6" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">AI Task Assignment</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-lg">×</button>
        </div>

        {!memoryEnabled && (
          <div className="bg-amber-900/30 border border-amber-700 rounded-lg p-3 mb-4 text-sm text-amber-300">
            Memory is OFF. Enable in sidebar for Hindsight-powered recommendations.
          </div>
        )}

        {!isComplete && currentAct === -1 && (
          <div className="space-y-3">
            <input value={form.task_title} onChange={e => setForm({...form, task_title: e.target.value})} placeholder="Task title" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm" />
            <div className="grid grid-cols-2 gap-3">
              <select value={form.task_category} onChange={e => setForm({...form, task_category: e.target.value})} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm">
                {['Backend','Frontend','ML','Testing','Design','DevOps','General'].map(c => <option key={c}>{c}</option>)}
              </select>
              <select value={form.complexity} onChange={e => setForm({...form, complexity: e.target.value})} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm">
                {['low','medium','high'].map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <button onClick={handleAssign} className="w-full py-2.5 bg-accent rounded-lg font-medium hover:bg-blue-600 transition flex items-center justify-center gap-2">
              <Zap size={16} />
              <span>Run AI Assignment</span>
            </button>
          </div>
        )}

        {currentAct >= 0 && !isComplete && (
          <div className="space-y-3 my-4">
            {acts.map((act, i) => (
              <motion.div key={i} initial={{ opacity: 0.3 }} animate={{ opacity: i <= currentAct ? 1 : 0.3 }}
                className="flex items-center gap-3 text-sm"
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                  i < currentAct ? 'bg-green-600' : i === currentAct ? 'bg-accent animate-pulse' : 'bg-gray-700'
                }`}>
                  {i < currentAct ? <Check size={12} /> : i + 1}
                </div>
                <div>
                  <span className="font-medium">{act.label}</span>
                  {i === currentAct && <span className="text-gray-400 ml-2 text-xs">{act.desc}</span>}
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {isComplete && result && (
          <div className="mt-4 space-y-3">
            {/* Top recommendation wrapped in SmartTooltip */}
            <SmartTooltip content={
              <AIInsightTooltipContent 
                label="Why this recommendation?" 
                desc={result.reason} 
                evidence={result.memory_evidence?.[0]} 
              />
            } position="bottom">
              <div className="bg-green-900/20 border border-green-700 rounded-lg p-4 cursor-help">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-bold text-green-400">Recommended: {result.assigned_to}</p>
                  {result.confidence != null && (
                    <span className="text-lg font-bold text-white">{Math.round(result.confidence * 100)}%</span>
                  )}
                </div>
                {result.confidence != null && (
                  <div className="mb-2">
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div className={`h-2 rounded-full ${result.confidence >= 0.8 ? 'bg-green-500' : result.confidence >= 0.5 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${result.confidence * 100}%` }} />
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className={`text-xs ${result.confidence >= 0.8 ? 'text-green-400' : result.confidence >= 0.5 ? 'text-amber-400' : 'text-red-400'}`}>
                        {result.confidence >= 0.8 ? 'High confidence' : result.confidence >= 0.5 ? 'Medium confidence' : 'Low confidence — limited history'}
                      </span>
                      {result.memories_used > 0 && (
                        <span className="text-xs text-teal-400">Based on {result.memories_used} historical events</span>
                      )}
                    </div>
                  </div>
                )}
                
                {result.anomaly?.is_anomaly && (
                  <SmartTooltip content={<AnomalyTooltipContent anomaly={result.anomaly} />}>
                    <div className="mt-3 mb-2 bg-amber-900/20 border border-amber-700 rounded-lg p-3 text-xs text-amber-300 flex items-center gap-2 cursor-help">
                      <span className="animate-ping w-2 h-2 rounded-full bg-amber-500" />
                      <span className="font-semibold uppercase tracking-tighter">Anomaly Flagged: </span>
                      <span className="truncate">{result.anomaly.message}</span>
                    </div>
                  </SmartTooltip>
                )}
                
                <p className="text-xs text-gray-300 leading-relaxed font-medium">"{result.reason}"</p>
              </div>
            </SmartTooltip>

            {/* All scores with confidence wrapped in cursor system */}
            {result.all_scores?.map((s, i) => {
              const conf    = Math.round((s.recommendation_score || s.confidence || 0) * 100);
              const caption = candidateCaption(s);
              return (
                <CursorCaption key={i} caption={caption}>
                  <SpotlightCard className="bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{s.member}</span>
                        <span className={`text-xs px-1.5 py-0.5 rounded ${
                          s.risk_level === 'HIGH' ? 'bg-red-900 text-red-300' : s.risk_level === 'MEDIUM' ? 'bg-amber-900 text-amber-300' : 'bg-green-900 text-green-300'
                        }`}>{s.risk_level}</span>
                      </div>
                      <span className={`text-sm font-bold ${conf >= 80 ? 'text-green-400' : conf >= 60 ? 'text-amber-400' : 'text-red-400'}`}>{conf}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-1.5">
                      <div className={`h-1.5 rounded-full ${conf >= 80 ? 'bg-green-500' : conf >= 60 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${conf}%` }} />
                    </div>
                    {conf < 50 && <span className="text-xs text-amber-400 mt-1 block">Low confidence — limited history</span>}
                  </SpotlightCard>
                </CursorCaption>
              );
            })}

            <button onClick={onClose} className="w-full py-2 bg-accent rounded-lg text-sm font-medium hover:bg-blue-600 transition mt-2 flex items-center justify-center gap-2">
              <UserCheck size={16} />
              <span>Confirm Assignment</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
