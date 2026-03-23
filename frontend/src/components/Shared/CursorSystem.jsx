/**
 * NEXUS-PM Unified Cursor System
 *
 * 4 effects in one system:
 *   1. SmartTooltip  — rich popup on hover with plain-English insight
 *   2. CursorCaption — 1-line label that follows the mouse
 *   3. SpotlightCard — magnetic blue glow inside card on hover
 *   4. NexusCursor   — custom branded cursor (demo route only)
 */

import React, {
  useState, useRef, useEffect, useCallback
} from 'react';

// ─── 1. SMART TOOLTIP ──────────────────────────────────────────────────────

/**
 * SmartTooltip wraps any element and shows a rich popup on hover.
 * position: 'top' | 'bottom' | 'left' | 'right' (default 'top')
 */
export function SmartTooltip({ children, content, position = 'top', delay = 120 }) {
  const [visible, setVisible] = useState(false);
  const timerRef = useRef(null);

  const show = () => {
    timerRef.current = setTimeout(() => setVisible(true), delay);
  };
  const hide = () => {
    clearTimeout(timerRef.current);
    setVisible(false);
  };

  const posStyles = {
    top:    'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left:   'right-full top-1/2 -translate-y-1/2 mr-2',
    right:  'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  const arrowStyles = {
    top:    'top-full left-1/2 -translate-x-1/2 border-t-[#1e293b]',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-[#1e293b]',
    left:   'left-full top-1/2 -translate-y-1/2 border-l-[#1e293b]',
    right:  'right-full top-1/2 -translate-y-1/2 border-r-[#1e293b]',
  };

  return (
    <div
      className="relative inline-block"
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
    >
      {children}
      {visible && content && (
        <div
          className={`
            absolute z-50 w-64 pointer-events-none
            ${posStyles[position]}
          `}
          style={{ filter: 'drop-shadow(0 8px 24px rgba(0,0,0,0.5))' }}
        >
          <div className="
            bg-[#0f1729] border border-[#334155] rounded-xl p-4
            text-white text-xs leading-relaxed
            animate-in fade-in zoom-in-95 duration-100
          ">
            {content}
          </div>
          {/* Arrow */}
          <div className={`
            absolute w-0 h-0 border-4 border-transparent
            ${arrowStyles[position]}
          `} />
        </div>
      )}
    </div>
  );
}

/**
 * Pre-built tooltip content blocks for NEXUS elements.
 * All text written in plain, non-technical English.
 */
export function TaskTooltipContent({ task }) {
  if (!task) return null;

  const riskLabel = {
    HIGH:   { text: 'High Priority Risk', color: 'text-red-400',   bg: 'bg-red-900/40', desc: 'NEXUS expects significant delays based on historical patterns.' },
    MEDIUM: { text: 'Watch List',      color: 'text-amber-400', bg: 'bg-amber-900/40', desc: 'Some risk detected. Worth a quick check-in with the owner.' },
    LOW:    { text: 'Healthy',         color: 'text-green-400', bg: 'bg-green-900/40', desc: 'On track. No behavioral red flags found.' },
  }[task.risk_level] || { text: 'Not Yet Scored', color: 'text-gray-400', bg: 'bg-gray-800', desc: 'Awaiting first analysis.' };

  const confLabel = task.confidence
    ? task.confidence >= 0.8 ? 'NEXUS is very sure about this prediction.'
    : task.confidence >= 0.6 ? 'NEXUS is reasonably sure based on current data.'
    : 'New territory: NEXUS has very little history for this type of work.'
    : null;

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-1">
        <div className="font-bold text-white text-base leading-tight">
          {task.title}
        </div>
        <div className="text-gray-400 text-[10px] uppercase tracking-wider font-semibold">
          {task.category || 'General Task'}
        </div>
      </div>
      
      <div className={`p-3 rounded-xl border border-white/10 ${riskLabel.bg}`}>
        <div className={`font-bold text-xs mb-1 ${riskLabel.color}`}>
          {riskLabel.text}
        </div>
        <div className="text-white/80 text-[11px] leading-relaxed">
          {riskLabel.desc}
        </div>
      </div>

      <div className="space-y-2 py-2 border-y border-white/5">
        {task.complexity && (
          <div className="flex justify-between text-[11px]">
            <span className="text-gray-500">Complexity</span>
            <span className="text-white font-medium capitalize">{task.complexity}</span>
          </div>
        )}
        {task.confidence != null && (
          <div className="flex justify-between text-[11px]">
            <span className="text-gray-500">AI Confidence</span>
            <span className="text-white font-medium">
              {Math.round(task.confidence * 100)}%
            </span>
          </div>
        )}
      </div>

      <div className="text-blue-300 text-[10px] italic leading-relaxed bg-blue-500/10 p-2 rounded-lg">
        " {confLabel} "
      </div>

      {task.assignment_reason && (
        <div className="text-gray-400 text-[11px] leading-relaxed italic">
          Why this owner? — {task.assignment_reason}
        </div>
      )}
    </div>
  );
}

export function MemberTooltipContent({ member }) {
  if (!member) return null;

  const workloadLevel = 
    (member.active_tasks || 0) >= 3 ? { text: 'Working at Limit', color: 'text-red-400', sub: 'Adding more tasks will likely cause delays.' }
  : (member.active_tasks || 0) >= 2 ? { text: 'Moderately Busy', color: 'text-amber-400', sub: 'Doing well, but starting to fill up.' }
  : { text: 'Ready for Work', color: 'text-green-400', sub: 'Has plenty of capacity for new assignments.' };

  const onTimeRate = member.completion_rate ? Math.round(member.completion_rate * 100) : null;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-blue-500/20">
          {member.name?.[0]}
        </div>
        <div>
          <div className="font-bold text-white text-base leading-none mb-1">{member.name}</div>
          <div className="text-blue-400 text-xs font-medium uppercase tracking-tighter">{member.role}</div>
        </div>
      </div>

      <div className="p-3 bg-white/5 rounded-xl border border-white/10">
        <div className={`font-bold text-xs mb-1 ${workloadLevel.color}`}>{workloadLevel.text}</div>
        <div className="text-gray-400 text-[11px] leading-snug">{workloadLevel.sub}</div>
      </div>

      <div className="grid grid-cols-2 gap-2 pt-1">
        <div className="bg-white/5 p-2 rounded-lg">
          <div className="text-gray-500 text-[9px] uppercase font-bold mb-0.5">Focus Area</div>
          <div className="text-white text-[11px] truncate">{(member.skills || [])[0] || 'Flexible'}</div>
        </div>
        <div className="bg-white/5 p-2 rounded-lg">
          <div className="text-gray-500 text-[9px] uppercase font-bold mb-0.5">On-Time %</div>
          <div className={`text-[11px] font-bold ${onTimeRate >= 85 ? 'text-green-400' : 'text-amber-400'}`}>
            {onTimeRate ?? 'N/A'}%
          </div>
        </div>
      </div>

      <div className="text-[10px] text-blue-400 font-bold flex items-center gap-1.5 bg-blue-400/5 p-2 rounded-lg">
        <span className="animate-pulse">●</span> NEXUS tracks historical performance daily.
      </div>
    </div>
  );
}

export function RiskBarTooltipContent({ task }) {
  if (!task) return null;
  const score = task.risk_score ?? 0;
  const pct   = Math.round(score * 100);

  const explain = 
    pct >= 70 ? 'High probability of going over the deadline. This pattern is common for tasks of this complexity late in the sprint.'
  : pct >= 40 ? 'Moderate risk. Task is following a slightly slower-than-average pace.'
  : 'Task behavior looks great. It matches the profile of tasks that finish early.';

  return (
    <div className="space-y-3">
      <div className="font-bold text-white text-sm">{task.task_title || task.title}</div>
      <div className="bg-white/10 rounded-full h-3 overflow-hidden">
        <div className={`h-full transition-all duration-1000 ${pct >= 70 ? 'bg-red-500' : pct >= 40 ? 'bg-amber-500' : 'bg-green-500'}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="flex justify-between items-center text-[11px]">
        <span className="text-gray-500 font-medium font-mono uppercase tracking-widest">{pct}% Risk Score</span>
        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${pct >= 70 ? 'bg-red-500/20 text-red-400' : pct >= 40 ? 'bg-amber-500/20 text-amber-400' : 'bg-green-500/20 text-green-400'}`}>
          {pct >= 70 ? 'CRITICAL' : pct >= 40 ? 'STABLE' : 'OPTIMAL'}
        </span>
      </div>
      <p className="text-gray-300 text-[11px] leading-relaxed italic border-l-2 border-blue-500 pl-2">
        "{explain}"
      </p>
      {(task.top_factors || []).length > 0 && (
        <div className="bg-white/5 p-3 rounded-xl space-y-2">
          <div className="text-gray-500 text-[9px] uppercase font-bold">Risk Factors (AI Analysis)</div>
          {task.top_factors.map((f, i) => (
            <div key={i} className="flex items-start gap-2 text-[10px] text-gray-300 leading-snug">
              <span className="text-blue-500 mt-0.5">•</span> {f}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function WorkloadTooltipContent({ memberName, activeTasks, capacity }) {
  const pct = Math.round((activeTasks / capacity) * 100);
  const remaining = capacity - activeTasks;

  const statusText = 
    pct >= 100 ? `${memberName} currently has no more room for work. Adding tasks will likely push other deadlines.`
  : pct >= 67  ? `${memberName} is fairly busy. We recommend assigning only one more task if it is low complexity.`
  : `${memberName} has plenty of room to take on new initiatives right now.`;

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <span className="font-bold text-white text-sm">{memberName}'s Load</span>
        <span className={`text-xs font-bold ${pct >= 100 ? 'text-red-400' : pct >= 67 ? 'text-amber-400' : 'text-green-400'}`}>{pct}% Full</span>
      </div>
      <div className="bg-white/10 rounded-lg h-3 overflow-hidden">
        <div className={`h-full transition-all duration-700 ${pct >= 100 ? 'bg-red-500' : pct >= 67 ? 'bg-amber-500' : 'bg-green-500'}`} style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <p className="text-gray-300 text-[11px] leading-relaxed bg-white/5 p-2 rounded-lg border-l-2 border-gray-600">
        {statusText}
      </p>
      <div className="text-[10px] text-blue-500 font-bold flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
        {remaining} slots available until 100% capacity.
      </div>
    </div>
  );
}

export function StrategyTooltipContent({ entry }) {
  if (!entry) return null;
  const pattern = (entry.trigger_pattern || '').replace(/_/g, ' ');
  const rate    = Math.round((entry.failure_rate || 0) * 100);
  
  // Translate weight shifts into personality/strategy terms
  const isCautions = (entry.new_weights?.current_load || 0) > (entry.old_weights?.current_load || 0);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
        <div className="font-bold text-amber-500 text-xs uppercase tracking-widest">{pattern} Detected</div>
      </div>
      
      <p className="text-gray-300 text-[11px] leading-relaxed">
        NEXUS noticed that tasks following this pattern were struggling. In fact, {rate}% of them were running behind.
      </p>

      <div className="bg-blue-600/20 border border-blue-500/30 p-3 rounded-xl">
        <div className="text-blue-300 text-[11px] font-bold mb-1">
          {isCautions ? 'Strategic Shift: Playing it Safe' : 'Strategic Shift: Boosting Efficiency'}
        </div>
        <div className="text-white/80 text-[10px] leading-relaxed">
          NEXUS has automatically adjusted its ranking system to {isCautions ? 'be more cautious' : 'be more aggressive'} when recommending owners for this type of work in the future.
        </div>
      </div>

      <div className="text-[10px] text-gray-500 font-medium border-t border-white/5 pt-2">
        💡 This adjustment happens instantly as new data comes in.
      </div>
    </div>
  );
}

export function AnomalyTooltipContent({ anomaly }) {
  if (!anomaly) return null;
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-red-400">
        <span className="font-bold text-xs uppercase tracking-widest leading-none">Unusual Pattern Detected</span>
      </div>
      <p className="text-gray-300 text-[11px] leading-relaxed">
        NEXUS flagged this behavior because it differs significantly from how this person (or the team) usually operates.
      </p>
      <div className="bg-red-950/30 border border-red-500/30 p-2 rounded-lg text-red-200 text-[10px] leading-relaxed italic">
        " {anomaly.message || 'The statistical profile for this task is a 1-in-100 outlier.'} "
      </div>
      <div className="text-[10px] text-gray-500 font-medium">
        💡 This doesn't mean something is wrong, but it suggests this task might need extra manual attention.
      </div>
    </div>
  );
}

export function AIInsightTooltipContent({ label, desc, evidence }) {
  return (
    <div className="space-y-2.5">
      <div className="font-bold text-white text-sm border-b border-white/10 pb-1">{label}</div>
      <p className="text-gray-300 text-[11px] leading-relaxed">{desc}</p>
      {evidence && (
        <div className="bg-blue-900/10 border-l-2 border-blue-500 p-2 text-[10px] text-blue-300 italic">
          "{evidence}"
        </div>
      )}
      <div className="text-gray-500 text-[9px] uppercase font-bold tracking-tighter">
        NEXUS Strategic Reasoning Engine
      </div>
    </div>
  );
}

// ─── 2. CURSOR CAPTION ─────────────────────────────────────────────────────

/**
 * CursorCaption wraps an element and shows a floating 1-line caption
 * that follows the cursor — plain English, non-technical.
 */
export function CursorCaption({ children, caption, enabled = true }) {
  const [pos, setPos]       = useState({ x: 0, y: 0 });
  const [visible, setVisible] = useState(false);

  const onMove = useCallback((e) => {
    setPos({ x: e.clientX, y: e.clientY });
  }, []);

  if (!enabled || !caption) return <>{children}</>;

  return (
    <>
      <div 
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        onMouseMove={onMove}
        className="relative"
      >
        {children}
      </div>

      {visible && (
        <div 
          className="
            fixed z-[9999] pointer-events-none
            bg-[#2563EB] text-white text-xs font-medium
            px-3 py-1.5 rounded-full shadow-lg shadow-blue-500/30
            whitespace-nowrap
            transition-opacity duration-100
          "
          style={{
            left: pos.x + 16,
            top:  pos.y - 10,
            transform: 'translateY(-50%)',
          }}
        >
          {caption}
        </div>
      )}
    </>
  );
}

// ─── 3. SPOTLIGHT CARD ─────────────────────────────────────────────────────

/**
 * SpotlightCard wraps any card with a magnetic blue glow that
 * follows the cursor inside the card.
 * Use instead of plain <div className="...card...">
 */
export function SpotlightCard({ children, className = '', intensity = 0.15 }) {
  const cardRef    = useRef(null);
  const [pos, setPos] = useState({ x: 50, y: 50 });
  const [hovered, setHovered]   = useState(false);

  const onMove = (e) => {
    if (!cardRef.current) return;
    const r = cardRef.current.getBoundingClientRect();
    setPos({
      x: ((e.clientX - r.left) / r.width)  * 100,
      y: ((e.clientY - r.top)  / r.height) * 100,
    });
  };

  return (
    <div
      ref={cardRef}
      className={`relative overflow-hidden transition-all duration-200 ${className}`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onMouseMove={onMove}
    >
      {/* Spotlight glow */}
      <div 
        className="absolute inset-0 pointer-events-none transition-opacity duration-300 rounded-[inherit]"
        style={{
          opacity: hovered ? 1 : 0,
          background: `radial-gradient(
            circle at ${pos.x}% ${pos.y}%,
            rgba(37,99,235,${intensity}) 0%,
            transparent 60%
          )`,
        }}
      />
      {/* Subtle border glow */}
      <div 
        className="absolute inset-0 pointer-events-none rounded-[inherit] transition-opacity duration-300"
        style={{
          opacity: hovered ? 1 : 0,
          boxShadow: 'inset 0 0 0 1px rgba(37,99,235,0.35)',
        }}
      />
      {children}
    </div>
  );
}

// ─── Helper hook for easy tooltip state ───────────────────────────────────
export function useHoverTooltip() {
  const [hovered, setHovered] = useState(false);
  return {
    hovered,
    hoverProps: {
      onMouseEnter: () => setHovered(true),
      onMouseLeave: () => setHovered(false),
    },
  };
}
