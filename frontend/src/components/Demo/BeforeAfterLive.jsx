import React, { useState, useEffect } from 'react';
import AgentAvatar from '../Agent/AgentAvatar';

const CATEGORIES = ['Backend', 'Frontend', 'Testing', 'DevOps', 'ML', 'General'];

const defaultCandidates = ['Alice', 'Bob', 'Priya', 'Raj'];

export default function BeforeAfterLive({ result, isLoading, onCompare, memberNames = defaultCandidates }) {
  const [taskTitle, setTaskTitle] = useState('Backend data processing pipeline');
  const [category, setCategory] = useState('Backend');
  const [selected, setSelected] = useState(() =>
    memberNames.reduce((acc, n) => ({ ...acc, [n]: true }), {})
  );
  const [phase, setPhase] = useState('idle');

  useEffect(() => {
    setSelected((prev) => {
      const next = { ...prev };
      memberNames.forEach((n) => {
        if (next[n] === undefined) next[n] = true;
      });
      return next;
    });
  }, [memberNames]);

  useEffect(() => {
    if (isLoading) {
      setPhase('loading');
      return;
    }
    if (!result) {
      setPhase('idle');
      return;
    }
    setPhase('revealing_left');
    const t1 = setTimeout(() => setPhase('revealing_right'), 400);
    const t2 = setTimeout(() => setPhase('complete'), 1200);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [result, isLoading]);

  const toggle = (name) => setSelected((s) => ({ ...s, [name]: !s[name] }));

  const handleCompare = () => {
    const candidates = memberNames.filter((n) => selected[n]);
    if (!taskTitle.trim() || candidates.length === 0) return;
    onCompare({
      task_title: taskTitle,
      task_category: category,
      complexity: 'high',
      deadline: '2025-04-01',
      candidates,
    });
  };

  const wo = result?.without_memory;
  const wm = result?.with_memory;
  const changed =
    wo && wm && String(wo.assigned_to).trim() !== String(wm.assigned_to).trim();
  const impact = result?.memory_impact_score ?? 0;

  const leftCls =
    'transition-all duration-500 ease-out ' +
    (phase === 'idle' || phase === 'loading'
      ? 'opacity-0 -translate-x-8'
      : 'opacity-100 translate-x-0');
  const rightCls =
    'transition-all duration-500 ease-out ' +
    (phase === 'revealing_right' || phase === 'complete'
      ? 'opacity-100 translate-x-0'
      : 'opacity-0 translate-x-8');

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-800 bg-[#0A1628] p-4 space-y-3">
        <div>
          <label className="text-xs text-gray-500">Task title</label>
          <input
            value={taskTitle}
            onChange={(e) => setTaskTitle(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm"
          />
        </div>
        <div className="flex flex-wrap gap-3">
          <div>
            <label className="text-xs text-gray-500">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="mt-1 block rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-2">Candidates</p>
          <div className="flex flex-wrap gap-3">
            {memberNames.map((n) => (
              <label key={n} className="flex items-center gap-2 text-sm text-gray-300">
                <input
                  type="checkbox"
                  checked={!!selected[n]}
                  onChange={() => toggle(n)}
                  className="rounded border-gray-600"
                />
                {n}
              </label>
            ))}
          </div>
        </div>
        <button
          type="button"
          onClick={handleCompare}
          disabled={isLoading}
          className="rounded-lg bg-[#2563EB] px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
        >
          {isLoading ? 'Comparing…' : 'Compare'}
        </button>
      </div>

      {isLoading && (
        <div className="flex flex-col items-center gap-3 py-8">
          <AgentAvatar size={56} state="thinking" />
          <p className="text-sm text-gray-400">Running decision with and without memory...</p>
        </div>
      )}

      {result && !isLoading && (
        <div className="grid gap-6 md:grid-cols-2">
          <div
            className={`rounded-xl border border-gray-700 bg-gray-900/80 p-5 ${leftCls}`}
            style={{ borderLeft: '4px solid #6B7280' }}
          >
            <h3 className="text-sm font-bold text-gray-400 mb-3">Without Memory</h3>
            <p className="text-2xl font-bold text-gray-200">{wo?.assigned_to || '—'}</p>
            <p className="mt-2 text-xs text-gray-500">
              Confidence {((wo?.confidence ?? 0) * 100).toFixed(0)}%
            </p>
            <div className="mt-2 h-2 w-full rounded-full bg-gray-800">
              <div
                className="h-2 rounded-full bg-gray-500"
                style={{ width: `${Math.min(100, (wo?.confidence ?? 0) * 100)}%` }}
              />
            </div>
            <p className="mt-3 text-sm text-gray-400">{wo?.reason}</p>
            <p className="mt-2 text-xs italic text-gray-600">Memory Evidence: None</p>
          </div>

          <div
            className={`rounded-xl border border-[#2563EB]/50 bg-[#0A1628] p-5 ${rightCls}`}
            style={{ borderLeft: '4px solid #2563EB' }}
          >
            <h3 className="text-sm font-bold text-blue-400 mb-3">With Memory</h3>
            <p className="text-2xl font-bold text-white">{wm?.assigned_to || '—'}</p>
            <p className="mt-2 text-xs text-gray-400">
              Confidence {((wm?.confidence ?? 0) * 100).toFixed(0)}%
            </p>
            <div className="mt-2 h-2 w-full rounded-full bg-gray-800">
              <div
                className="h-2 rounded-full bg-[#2563EB]"
                style={{ width: `${Math.min(100, (wm?.confidence ?? 0) * 100)}%` }}
              />
            </div>
            <p className="mt-3 text-sm text-gray-300">{wm?.reason}</p>
            <div className="mt-3 space-y-2">
              {(wm?.memory_evidence || []).slice(0, 3).map((q, i) => (
                <div
                  key={i}
                  className="border-l-2 border-[#2563EB] pl-3 text-xs italic text-gray-400"
                  style={{ padding: '8px 12px', fontSize: 13 }}
                >
                  {q}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {result && !isLoading && phase === 'complete' && (
        <div className="space-y-3">
          {changed && (
            <div className="rounded-lg bg-green-900/30 border border-green-700 px-4 py-2 text-center text-sm font-medium text-green-400">
              Assignment changed by memory!
            </div>
          )}
          <div className="rounded-xl border border-gray-800 bg-[#0A1628] p-4">
            <p className="text-xs text-gray-500 mb-1">Memory impact score</p>
            <div className="h-3 w-full rounded-full bg-gray-800">
              <div
                className="h-3 rounded-full bg-teal-600 transition-all"
                style={{ width: `${Math.min(100, impact * 100)}%` }}
              />
            </div>
            <p className="mt-3 text-sm text-gray-300">{result.difference_summary}</p>
          </div>
        </div>
      )}
    </div>
  );
}
