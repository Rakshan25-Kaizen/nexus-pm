import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  SmartTooltip,
  MemberTooltipContent,
  CursorCaption,
  SpotlightCard,
} from '../Shared/CursorSystem';

function buildMemberCaption(member) {
  const tasks  = member.active_tasks || 0;
  const rate   = member.completion_rate
    ? Math.round(member.completion_rate * 100) : null;

  if (tasks >= 3)
    return `${member.name} is fully loaded right now`;
  if (rate !== null && rate < 75)
    return `${member.name} has had some delays recently`;
  if (rate !== null && rate >= 90)
    return `${member.name} is a top performer`;
  return `${member.name} — ${member.role}`;
}

export default function MemberCard({ member }) {
  const navigate = useNavigate();
  const caption  = buildMemberCaption(member);

  // Skill bar colors — green = strong skill, red = less confident
  const barColors = ['bg-green-500','bg-green-500','bg-green-500','bg-amber-500','bg-red-500'];

  return (
    <CursorCaption caption={caption}>
      <SmartTooltip
        content={<MemberTooltipContent member={member} />}
        position="top"
      >
        <SpotlightCard
          className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition"
          data-cursor={caption}
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-accent/20 rounded-full flex
                 items-center justify-center text-accent font-bold relative">
              {member.name?.[0] || '?'}
              {/* Workload dot */}
              {(member.active_tasks || 0) >= 3 && (
                <span className="absolute -top-0.5 -right-0.5 w-3 h-3
                     bg-red-500 rounded-full border-2 border-gray-900"
                  title="At capacity"
                />
              )}
            </div>
            <div>
              <p className="font-medium">{member.name}</p>
              <p className="text-xs text-gray-400">{member.role}</p>
            </div>
            {member.completion_rate != null && (
              <span className={`ml-auto text-xs font-medium px-2 py-0.5 rounded-full ${
                member.completion_rate >= 0.85 ? 'bg-green-900/50 text-green-400'
                : member.completion_rate >= 0.70 ? 'bg-amber-900/50 text-amber-400'
                : 'bg-red-900/50 text-red-400'
              }`}>
                {Math.round(member.completion_rate * 100)}%
              </span>
            )}
          </div>

          <div className="flex flex-wrap gap-1.5 mb-3">
            {(member.skills || []).map(s => (
              <span key={s}
                className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded">
                {s}
              </span>
            ))}
          </div>

          {/* Skill / reliability bar */}
          <div className="flex gap-1 mb-3" title="Performance score">
            {barColors.map((color, i) => {
              const filled = i < Math.round((member.completion_rate || 0.7) * 5);
              return (
                <div key={i}
                  className={`h-2 flex-1 rounded ${filled ? color : 'bg-gray-700'}`}
                />
              );
            })}
          </div>

          {/* Active tasks indicator */}
          {member.active_tasks != null && (
            <div className="flex items-center gap-1.5 mb-3 text-xs text-gray-500">
              <div className={`w-2 h-2 rounded-full ${
                (member.active_tasks || 0) >= 3 ? 'bg-red-500'
                : (member.active_tasks || 0) >= 1 ? 'bg-blue-500'
                : 'bg-gray-600'
              }`} />
              {member.active_tasks === 0
                ? 'No active tasks — available'
                : `${member.active_tasks} task${member.active_tasks !== 1 ? 's' : ''} in progress`}
            </div>
          )}

          <button
            onClick={() => navigate('/agent')}
            className="w-full text-xs py-1.5 bg-gray-800 hover:bg-gray-700
                 rounded-lg transition text-gray-300"
          >
            Ask NEXUS about {member.name}
          </button>
        </SpotlightCard>
      </SmartTooltip>
    </CursorCaption>
  );
}
