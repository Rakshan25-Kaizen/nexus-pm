import React, { useState } from 'react';
import { createMember, onboardMember } from '../../api/client';
import useNexusStore from '../../store/useNexusStore';
import AgentAvatar from '../Agent/AgentAvatar';
import { UserPlus, BrainCircuit, Check } from 'lucide-react';

const allSkills = ['Python','React','FastAPI','TypeScript','PostgreSQL','ML','DevOps','Testing','UI/UX','Tailwind','Docker','AWS'];

export default function OnboardingFlow({ onClose }) {
  const { projectId, addMember } = useNexusStore();
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [skills, setSkills] = useState([]);
  const [notes, setNotes] = useState('');
  const [onboardResult, setOnboardResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const toggleSkill = (s) => setSkills(prev => prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const r = await onboardMember({ member_name: name, role, skills, project_id: projectId, background_notes: notes });
      setOnboardResult(r);
      setStep(4);
    } catch { setOnboardResult({ welcome_message: 'Welcome to the team!', initial_tasks_suggested: [], skill_gaps_detected: [] }); setStep(4); }
    setLoading(false);
  };

  const handleConfirm = async () => {
    try {
      const m = await createMember({ name, role, skills, project_id: projectId });
      addMember(m);
      onClose();
    } catch { onClose(); }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-40" onClick={onClose}>
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-[500px] p-6" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-bold">Add Team Member — Step {step}/5</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">×</button>
        </div>
        <div className="flex gap-1 mb-6">{[1,2,3,4,5].map(i => <div key={i} className={`h-1 flex-1 rounded ${i <= step ? 'bg-accent' : 'bg-gray-700'}`} />)}</div>

        {step === 1 && (
          <div className="space-y-3">
            <input value={name} onChange={e => setName(e.target.value)} placeholder="Name" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm" />
            <input value={role} onChange={e => setRole(e.target.value)} placeholder="Role (e.g. Backend Engineer)" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm" />
            <button onClick={() => name && role && setStep(2)} className="w-full py-2 bg-accent rounded-lg text-sm">Next</button>
          </div>
        )}

        {step === 2 && (
          <div>
            <p className="text-sm text-gray-400 mb-3">Select skills:</p>
            <div className="flex flex-wrap gap-2 mb-4">
              {allSkills.map(s => (
                <button key={s} onClick={() => toggleSkill(s)} className={`px-3 py-1 rounded-full text-xs transition ${skills.includes(s) ? 'bg-accent text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}>
                  {s}
                </button>
              ))}
            </div>
            <button onClick={() => setStep(3)} className="w-full py-2 bg-accent rounded-lg text-sm">Next</button>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-3">
            <textarea value={notes} onChange={e => setNotes(e.target.value)} placeholder="Background notes (optional)" rows={3} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm resize-none" />
            <button onClick={handleAnalyze} disabled={loading} className="w-full py-2 bg-accent rounded-lg text-sm disabled:opacity-50">
              {loading ? <><AgentAvatar size={16} state="thinking" /> Analyzing...</> : <><BrainCircuit size={16} /> Ask NEXUS to Analyze</>}
            </button>
          </div>
        )}

        {step === 4 && onboardResult && (
          <div className="space-y-3">
            <div className="bg-gray-800 rounded-lg p-4 text-sm">
              <p className="text-gray-200 mb-2">{onboardResult.welcome_message}</p>
              {onboardResult.initial_tasks_suggested?.length > 0 && (
                <div className="mt-2"><p className="text-xs text-gray-400 mb-1">Suggested Tasks:</p>
                  {onboardResult.initial_tasks_suggested.map((t, i) => <p key={i} className="text-xs text-gray-300">• {t}</p>)}
                </div>
              )}
              {onboardResult.skill_gaps_detected?.length > 0 && (
                <div className="mt-2"><p className="text-xs text-amber-400 mb-1">Skill Gaps:</p>
                  {onboardResult.skill_gaps_detected.map((g, i) => <p key={i} className="text-xs text-amber-300">• {g}</p>)}
                </div>
              )}
            </div>
            <button onClick={() => setStep(5)} className="w-full py-2 bg-accent rounded-lg text-sm">Continue</button>
          </div>
        )}

        {step === 5 && (
          <div className="text-center space-y-4">
            <p className="text-lg">Ready to add <strong>{name}</strong>?</p>
            <p className="text-sm text-gray-400">{role} • {skills.length} skills</p>
            <button onClick={handleConfirm} className="w-full py-2.5 bg-green-600 rounded-lg font-medium hover:bg-green-700 transition flex items-center justify-center gap-2">
              <Check size={16} />
              <span>Confirm & Add</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
