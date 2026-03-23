import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell
} from 'recharts';
import { SmartTooltip, RiskBarTooltipContent } from '../Shared/CursorSystem';

const colors = {
  HIGH:   '#DC2626',
  MEDIUM: '#D97706',
  LOW:    '#16A34A',
};

export default function RiskChart({ risks }) {
  const [activeIdx, setActiveIdx] = useState(null);

  if (!risks?.length) {
    return (
      <p className="text-sm text-gray-500">
        No risk data yet. Assign tasks to generate risk scores.
      </p>
    );
  }

  const data = risks.map(r => ({
    name:  (r.task_title || 'Task').slice(0, 14) +
           ((r.task_title || '').length > 14 ? '…' : ''),
    score: Math.round((r.risk_score ?? 0) * 100),
    level: String(r.risk_level || 'MEDIUM').toUpperCase(),
    raw:   r,
  }));

  return (
    <div className="space-y-4">
      {/* Plain-English risk summary above the chart */}
      <div className="flex gap-4 text-xs text-gray-400">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block shadow-sm shadow-red-500/20"/>
          Likely to be delayed
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block shadow-sm shadow-amber-500/20"/>
          Some risk
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-green-500 inline-block shadow-sm shadow-green-500/20"/>
          On track
        </span>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <XAxis
              dataKey="name"
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              axisLine={{ stroke: '#374151' }}
            />
            <YAxis
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              axisLine={{ stroke: '#374151' }}
              domain={[0, 100]}
              tickFormatter={v => v === 0 ? 'Safe' : v === 50 ? 'Risk' : v === 100 ? 'High' : ''}
            />
            <Bar dataKey="score" radius={[4,4,0,0]}>
              {data.map((entry, i) => (
                <Cell
                  key={i}
                  fill={colors[entry.level] || colors.MEDIUM}
                  opacity={activeIdx === null || activeIdx === i ? 1 : 0.4}
                  className="transition-opacity duration-200"
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Hover cards below the chart — plain English per task */}
      <div className="grid grid-cols-2 gap-2 mt-2">
        {data.map((d, i) => (
          <SmartTooltip
            key={i}
            content={<RiskBarTooltipContent task={d.raw} />}
            position="top"
          >
            <div
              className={`
                flex items-center gap-2 px-3 py-2 rounded-lg
                bg-gray-900/50 border border-gray-800
                hover:border-blue-500/50 hover:bg-gray-800 transition-all cursor-pointer
              `}
              onMouseEnter={() => setActiveIdx(i)}
              onMouseLeave={() => setActiveIdx(null)}
            >
              <div
                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                style={{ background: colors[d.level] }}
              />
              <span className="text-xs text-gray-300 truncate flex-1">
                {d.raw.task_title || d.name}
              </span>
              <span className={`text-xs font-bold flex-shrink-0 ${
                d.level === 'HIGH'   ? 'text-red-400'
                : d.level === 'MEDIUM' ? 'text-amber-400'
                : 'text-green-400'
              }`}>
                {d.score}%
              </span>
            </div>
          </SmartTooltip>
        ))}
      </div>
    </div>
  );
}
