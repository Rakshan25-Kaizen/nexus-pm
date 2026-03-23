import React from 'react';

const riskConfig = {
  HIGH: { bg: 'bg-red-600', text: 'text-white' },
  MEDIUM: { bg: 'bg-amber-500', text: 'text-black' },
  LOW: { bg: 'bg-green-600', text: 'text-white' },
};

export default function RiskHeatmap({ risks }) {
  const categories = [...new Set(risks.map(r => r.task_title?.split(' ')[0] || 'Task'))];

  return (
    <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${Math.min(risks.length, 6)}, 1fr)` }}>
      {risks.map((r, i) => {
        const { bg, text } = riskConfig[r.risk_level] || riskConfig.MEDIUM;
        return (
          <div key={i} className={`${bg} ${text} rounded-lg p-3 text-center cursor-pointer hover:opacity-90 transition`} 
               title={r.explanation || ''}>
            <p className="text-xs font-medium truncate">{r.task_title}</p>
            <p className="text-lg font-bold mt-1">{(r.risk_score * 100).toFixed(0)}%</p>
            <p className="text-xs opacity-80">{r.risk_level}</p>
          </div>
        );
      })}
    </div>
  );
}
