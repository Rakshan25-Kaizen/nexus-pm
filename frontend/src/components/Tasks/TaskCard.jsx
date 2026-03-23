import React, { useState } from 'react';
import {
  SmartTooltip,
  TaskTooltipContent,
  CursorCaption,
  SpotlightCard,
} from '../Shared/CursorSystem';

const categoryColors = {
  Backend:  'bg-purple-900 text-purple-300',
  Frontend: 'bg-blue-900 text-blue-300',
  ML:       'bg-green-900 text-green-300',
  Testing:  'bg-yellow-900 text-yellow-300',
  Design:   'bg-pink-900 text-pink-300',
  DevOps:   'bg-orange-900 text-orange-300',
  General:  'bg-gray-700 text-gray-300',
};

const riskColors = {
  HIGH:   'bg-red-900 text-red-300',
  MEDIUM: 'bg-amber-900 text-amber-300',
  LOW:    'bg-green-900 text-green-300',
};

// Plain-English cursor captions for non-technical users
function buildCaption(task) {
  if (!task.risk_level) return 'Click to see task details';
  if (task.risk_level === 'HIGH')   return '⚠️ High delay risk — NEXUS flagged this task';
  if (task.risk_level === 'MEDIUM') return '👀 Some risk — worth keeping an eye on';
  return '✅ On track — low risk of delay';
}

export default function TaskCard({ task }) {
  const [expanded, setExpanded] = useState(false);
  const caption = buildCaption(task);

  return (
    <CursorCaption caption={caption}>
      <SmartTooltip
        content={<TaskTooltipContent task={task} />}
        position="right"
      >
        <SpotlightCard
          className="bg-gray-800/80 rounded-lg p-3 cursor-pointer hover:bg-gray-800 transition border border-gray-700/50"
          data-cursor={caption}
        >
          <div onClick={() => setExpanded(!expanded)}>
            <p className="text-sm font-medium mb-2">{task.title}</p>
            <div className="flex flex-wrap gap-1.5">
              {task.category && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded
                  ${categoryColors[task.category] || categoryColors.General}`}>
                  {task.category}
                </span>
              )}
              {task.risk_level && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded
                  ${riskColors[task.risk_level] || ''}`}>
                  {task.risk_level === 'HIGH'   ? '⚠ High risk'
                  : task.risk_level === 'MEDIUM' ? '~ Some risk'
                  : '✓ Low risk'}
                </span>
              )}
              {task.confidence != null && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                  task.confidence >= 0.8 ? 'bg-green-900 text-green-300'
                  : task.confidence >= 0.6 ? 'bg-amber-900 text-amber-300'
                  : 'bg-red-900 text-red-300'
                }`}>
                  {Math.round(task.confidence * 100)}% confident
                </span>
              )}
            </div>
            {expanded && task.description && (
              <p className="text-xs text-gray-400 mt-2 border-t border-gray-700 pt-2">
                {task.description}
              </p>
            )}
            {expanded && task.assignment_reason && (
              <p className="text-xs text-blue-400 mt-2 italic">
                {task.assignment_reason}
              </p>
            )}
          </div>
        </SpotlightCard>
      </SmartTooltip>
    </CursorCaption>
  );
}
