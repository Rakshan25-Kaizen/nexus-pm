import React from 'react';
import { Brain, Zap, CheckCircle, Bell } from 'lucide-react';

function iconFor(type) {
  const t = (type || '').toLowerCase();
  if (t.includes('strategy') || t.includes('adapt')) return Zap;
  if (t.includes('meeting')) return CheckCircle;
  if (t.includes('nudge')) return Bell;
  return Brain;
}

export default function MemoryTimeline({ events, max = 20 }) {
  const list = (events || []).slice(0, max);

  if (!list.length) {
    return (
      <p className="text-sm text-gray-500">
        No timeline events in the client store yet. Interact with NEXUS to populate memory events.
      </p>
    );
  }

  return (
    <div className="relative border-l border-gray-700 pl-4 space-y-4 ml-2">
      {list.map((ev, i) => {
        const Icon = iconFor(ev.type);
        return (
          <div key={ev.id || i} className="relative">
            <span className="absolute -left-[21px] top-1 flex h-6 w-6 items-center justify-center rounded-full bg-gray-800 border border-gray-600">
              <Icon size={12} className="text-blue-400" />
            </span>
            <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-3">
              <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
                {ev.ts && <span>{ev.ts}</span>}
                {ev.bank && (
                  <span className="rounded bg-gray-800 px-2 py-0.5 text-gray-300">{ev.bank}</span>
                )}
              </div>
              <p className="mt-1 text-sm text-gray-300">{ev.description || ev.text || JSON.stringify(ev)}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
