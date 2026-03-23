import React, { useState } from 'react';
import { motion } from 'framer-motion';
import useNexusStore from '../../store/useNexusStore';
import { createSprint } from '../../api/client';
import SprintCard from './SprintCard';
import WorkloadGauge from '../Analytics/WorkloadGauge';

const stages = ['Recalling past sprint performance...', 'Analyzing team capacity...', 'Optimizing task assignments...', 'Generating sprint plan...'];

export default function SprintPlanner() {
  const { projectId, tasks, members } = useNexusStore();
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState(-1);
  const [plan, setPlan] = useState(null);

  const handleGenerate = async () => {
    setLoading(true); setPlan(null);
    for (let i = 0; i < stages.length; i++) { setStage(i); await new Promise(r => setTimeout(r, 600)); }
    try {
      const data = await createSprint({
        project_id: projectId, sprint_number: 1,
        available_members: members.map(m => m.name),
        available_tasks: tasks.filter(t => t.status !== 'done').map(t => ({ id: t.id, title: t.title, category: t.category, complexity: t.complexity })),
        velocity_target: 5,
      });
      setPlan(data);
      useNexusStore.getState().addSprintPlan(data);
    } catch { setPlan({ error: true }); }
    setLoading(false); setStage(-1);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Sprint Planner</h1>
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <h3 className="text-sm font-semibold mb-3 text-gray-400">Available Tasks</h3>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {tasks.filter(t => t.status !== 'done').map(t => (
              <div key={t.id} className="bg-gray-900 border border-gray-800 rounded-lg p-3 flex items-center gap-2 text-sm">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="flex-1">{t.title}</span>
                <span className="text-xs text-gray-500">{t.category}</span>
              </div>
            ))}
            {tasks.filter(t => t.status !== 'done').length === 0 && <p className="text-gray-500 text-sm">No tasks available</p>}
          </div>
        </div>
        <div>
          <h3 className="text-sm font-semibold mb-3 text-gray-400">Team</h3>
          <div className="space-y-4">
            {members.map(m => <WorkloadGauge key={m.id} memberName={m.name} activeTasks={1} capacity={3} mini />)}
            {members.length === 0 && <p className="text-gray-500 text-sm">No team members</p>}
          </div>
        </div>
      </div>

      <button onClick={handleGenerate} disabled={loading} className="mt-6 px-6 py-2.5 bg-accent rounded-lg font-medium hover:bg-blue-600 transition disabled:opacity-50">
        {loading ? '⏳ Generating...' : '⚡ Generate Sprint Plan'}
      </button>

      {stage >= 0 && !plan && (
        <div className="mt-4 space-y-2">
          {stages.map((s, i) => (
            <motion.div key={i} initial={{ opacity: 0.3 }} animate={{ opacity: i <= stage ? 1 : 0.3 }}
              className="text-sm flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${i <= stage ? 'bg-accent' : 'bg-gray-700'}`} />
              {s}
            </motion.div>
          ))}
        </div>
      )}

      {plan && !plan.error && <SprintCard plan={plan} />}
      {plan?.sprint_health && (
        <div className={`flex items-center gap-2 p-3 rounded-lg mt-4 ${
          plan.sprint_health.on_track_probability >= 0.75
            ? 'bg-green-900/20 border border-green-700'
            : plan.sprint_health.on_track_probability >= 0.5
            ? 'bg-amber-900/20 border border-amber-700'
            : 'bg-red-900/20 border border-red-700'
        }`}>
          <span className="text-xl">{plan.sprint_health.health_emoji}</span>
          <div>
            <p className="text-sm font-semibold">
              Sprint health: {plan.sprint_health.health_label}
              {' '}({Math.round(plan.sprint_health.on_track_probability * 100)}% on-track)
            </p>
            <p className="text-xs text-gray-400">
              {plan.sprint_health.model}
            </p>
            {plan.sprint_health.risk_factors?.map((f, i) => (
              <p key={i} className="text-xs text-amber-400">• {f}</p>
            ))}
          </div>
        </div>
      )}
      {plan?.error && <p className="mt-4 text-red-400 text-sm">Failed to generate sprint plan. Check backend.</p>}
    </div>
  );
}
