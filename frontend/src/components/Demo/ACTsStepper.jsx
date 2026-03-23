import React from 'react';

const STAGES = [
  { id: 1, name: 'ACT 1 PERCEIVING', short: 'PERCEIVING' },
  { id: 2, name: 'ACT 2 RECALLING MEMORIES', short: 'RECALLING' },
  { id: 3, name: 'ACT 3 REASONING', short: 'REASONING' },
  { id: 4, name: 'ACT 4 ADAPTING STRATEGY', short: 'ADAPTING' },
  { id: 5, name: 'ACT 5 LEARNING', short: 'LEARNING' },
];

function StageCircle({ num, status }) {
  const pending = status === 'pending';
  const active = status === 'active';
  const done = status === 'done';

  return (
    <div
      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 text-sm font-bold transition-all ${
        pending
          ? 'border-gray-600 bg-gray-800 text-gray-500'
          : active
          ? 'border-[#2563EB] bg-[#2563EB]/20 text-[#2563EB] ring-2 ring-[#2563EB]/40 animate-pulse'
          : 'border-green-600 bg-green-900/40 text-green-400'
      }`}
    >
      {done ? '✓' : num}
    </div>
  );
}

export default function ACTsStepper({ currentAct, actData }) {
  const taskTitle = actData?.task_title || 'Task';
  const category = actData?.task_category || 'Backend';
  const complexity = actData?.complexity || 'high';
  const memoriesFound = actData?.memories_found ?? 0;
  const weights = actData?.strategy_weights || {};

  const weightPills = Object.entries(weights).slice(0, 4);

  const statusFor = (id) => {
    if (!currentAct || currentAct < 1) return 'pending';
    if (currentAct > 5) return 'done';
    if (id < currentAct) return 'done';
    if (id === currentAct) return 'active';
    return 'pending';
  };

  const descFor = (id) => {
    const s = statusFor(id);
    switch (id) {
      case 1:
        if (s === 'active')
          return `Analyzing: ${taskTitle}. Category: ${category}. Complexity: ${complexity}.`;
        if (s === 'done') return 'Task context parsed. 4 candidates identified.';
        return 'Waiting...';
      case 2:
        if (s === 'active') return 'Searching members-bank and tasks-bank...';
        if (s === 'done')
          return `Found ${memoriesFound} memories. Behavioral history retrieved.`;
        return 'Waiting...';
      case 3:
        if (s === 'active') return 'Groq LLM + XGBoost scoring all candidates...';
        if (s === 'done') return 'Recommendation generated. Risk scores computed.';
        return 'Waiting...';
      case 4:
        if (s === 'active') return 'Checking strategy weights...';
        if (s === 'done')
          return (
            <span className="flex flex-wrap gap-1">
              Weights applied:
              {weightPills.length > 0
                ? weightPills.map(([k, v]) => (
                    <span
                      key={k}
                      className="rounded bg-gray-700 px-2 py-0.5 text-xs text-gray-200"
                    >
                      {k}:{typeof v === 'number' ? v.toFixed(2) : String(v)}
                    </span>
                  ))
                : ' defaults'}
            </span>
          );
        return 'Waiting...';
      case 5:
        if (s === 'active') return 'Storing this assignment to Hindsight...';
        if (s === 'done') return 'Experience retained. Future assignments will be smarter.';
        return 'Waiting...';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-4">
      {STAGES.map((stage) => {
        const st = statusFor(stage.id);
        return (
          <div key={stage.id} className="flex gap-4">
            <StageCircle num={stage.id} status={st} />
            <div className="min-w-0 flex-1 border-b border-gray-800 pb-4">
              <p className="font-bold text-white">{stage.name}</p>
              <div className="mt-1 text-sm text-gray-400">{descFor(stage.id)}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
