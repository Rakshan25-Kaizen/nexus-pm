import React from 'react';
import { SmartTooltip, WorkloadTooltipContent } from '../Shared/CursorSystem';

export default function WorkloadGauge({ memberName, activeTasks, capacity, mini = false }) {
  const pct = Math.min((activeTasks / capacity) * 100, 100);
  const color = pct >= 90 ? 'bg-red-500' : pct >= 60 ? 'bg-amber-500' : 'bg-green-500';
  const textColor = pct >= 90 ? 'text-red-400' : pct >= 60 ? 'text-amber-400' : 'text-green-400';

  if (mini) {
    return (
      <SmartTooltip
        content={
          <WorkloadTooltipContent
            memberName={memberName}
            activeTasks={activeTasks}
            capacity={capacity}
          />
        }
        position="right"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm w-16 truncate">{memberName}</span>
          <div className="flex-1 bg-gray-700 rounded-full h-2">
            <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
          </div>
          <span className={`text-xs ${textColor}`}>{activeTasks}/{capacity}</span>
        </div>
      </SmartTooltip>
    );
  }

  return (
    <SmartTooltip
      content={
        <WorkloadTooltipContent
          memberName={memberName}
          activeTasks={activeTasks}
          capacity={capacity}
        />
      }
      position="top"
    >
      <div className="bg-gray-800/50 rounded-lg p-3 text-center">
        <p className="text-sm font-medium mb-2">{memberName}</p>
        <div className="relative w-16 h-16 mx-auto mb-2">
          <svg viewBox="0 0 36 36" className="w-full h-full">
            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3" />
            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none" stroke={pct >= 90 ? '#EF4444' : pct >= 60 ? '#F59E0B' : '#10B981'}
              strokeWidth="3" strokeDasharray={`${pct}, 100`} strokeLinecap="round" />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-sm font-bold ${textColor}`}>{activeTasks}</span>
          </div>
        </div>
        <p className="text-xs text-gray-500">{activeTasks}/{capacity} tasks</p>
      </div>
    </SmartTooltip>
  );
}
