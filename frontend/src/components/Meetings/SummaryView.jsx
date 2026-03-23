import React from 'react';

const severityColors = { high: 'bg-red-900 text-red-300', medium: 'bg-amber-900 text-amber-300', low: 'bg-green-900 text-green-300' };

export default function SummaryView({ summary }) {
  return (
    <div className="mt-6 space-y-4">
      {summary.summary && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-bold mb-2">Summary</h3>
          <p className="text-sm text-gray-300">{summary.summary}</p>
        </div>
      )}
      {summary.decisions?.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-bold mb-2">Decisions</h3>
          <div className="space-y-2">{summary.decisions.map((d, i) => (
            <div key={i} className="bg-gray-800 rounded-lg p-3 text-sm">
              <p className="font-medium">{d.decision}</p>
              <p className="text-gray-400 text-xs mt-1">Owner: {d.owner} {d.context && `• ${d.context}`}</p>
            </div>
          ))}</div>
        </div>
      )}
      {summary.action_items?.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-bold mb-2">Action Items</h3>
          {summary.action_items.map((a, i) => (
            <div key={i} className="flex items-center gap-2 py-1 text-sm">
              <input type="checkbox" className="rounded" readOnly /> <span>{a.task}</span>
              <span className="text-gray-400 text-xs ml-auto">{a.assigned_to} • {a.due_date}</span>
            </div>
          ))}
        </div>
      )}
      {summary.blockers?.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-bold mb-2">Blockers</h3>
          {summary.blockers.map((b, i) => (
            <div key={i} className="flex items-center gap-2 py-1 text-sm">
              <span className={`text-xs px-1.5 py-0.5 rounded ${severityColors[b.severity] || ''}`}>{b.severity}</span>
              <span>{b.description}</span>
              <span className="text-gray-400 text-xs ml-auto">by {b.raised_by}</span>
            </div>
          ))}
        </div>
      )}
      {summary.behavioral_insights?.length > 0 && (
        <div className="bg-blue-900/20 border border-blue-700 rounded-xl p-4">
          <h3 className="text-sm font-bold mb-2 text-blue-400">Behavioral Insights</h3>
          {summary.behavioral_insights.map((i, idx) => <p key={idx} className="text-sm text-gray-300">• {i}</p>)}
        </div>
      )}
      <div className="text-right"><span className="text-xs bg-green-900 text-green-300 px-2 py-1 rounded">Memories Stored: {summary.memories_stored || 0}</span></div>
    </div>
  );
}
