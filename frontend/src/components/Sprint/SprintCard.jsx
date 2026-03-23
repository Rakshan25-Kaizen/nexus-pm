import React from 'react';
import { Database } from 'lucide-react';

const riskColors = { HIGH: 'text-red-400', MEDIUM: 'text-amber-400', LOW: 'text-green-400' };

export default function SprintCard({ plan }) {
  const memoryEvidence = plan.memory_evidence || [];
  const assignments = plan.recommended_tasks || plan.assignments || [];

  return (
    <div className="mt-6 bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold">{plan.sprint_name || 'Sprint Plan'}</h3>
        <span className="text-xs bg-teal-900 text-teal-300 px-2 py-1 rounded">Memories Used: {plan.memories_used || 0}</span>
      </div>
      {assignments.length > 0 && (
        <table className="w-full text-sm">
          <thead><tr className="text-gray-400 border-b border-gray-700">
            <th className="text-left py-2">Task</th><th className="text-left py-2">Member</th>
            <th className="text-left py-2">Risk</th><th className="text-left py-2">Confidence</th>
            <th className="text-left py-2">Reason</th>
          </tr></thead>
          <tbody>{assignments.map((a, i) => {
            const conf = a.confidence || 0;
            const confPct = Math.round(conf * 100);
            return (
              <tr key={i} className="border-b border-gray-800">
                <td className="py-2">{a.task_id}</td>
                <td className="py-2">{a.assigned_to}</td>
                <td className={`py-2 font-medium ${riskColors[a.risk] || ''}`}>{a.risk}</td>
                <td className="py-2">
                  {conf > 0 ? (
                    <div>
                      <span className={`font-medium ${confPct >= 80 ? 'text-green-400' : confPct >= 60 ? 'text-amber-400' : 'text-red-400'}`}>{confPct}%</span>
                      <div className="w-16 bg-gray-700 rounded-full h-1 mt-0.5">
                        <div className={`h-1 rounded-full ${confPct >= 80 ? 'bg-green-500' : confPct >= 60 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${confPct}%` }} />
                      </div>
                    </div>
                  ) : (
                    <span className="text-gray-500">—</span>
                  )}
                </td>
                <td className="py-2 text-gray-400 text-xs">{a.reason}</td>
              </tr>
            );
          })}</tbody>
        </table>
      )}
      {plan.capacity_warnings?.length > 0 && (
        <div className="mt-4 space-y-1">{plan.capacity_warnings.map((w, i) => (
          <div key={i} className="bg-amber-900/20 border border-amber-700 rounded p-2 text-xs text-amber-300">{w}</div>
        ))}</div>
      )}
      {plan.risk_summary && <p className="mt-3 text-sm text-gray-400">{plan.risk_summary}</p>}

      {/* Memory Evidence Section */}
      {memoryEvidence.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Database size={14} className="text-teal-400" />
            <span className="text-xs font-semibold text-teal-400">NEXUS MEMORY EVIDENCE</span>
            <span className="text-xs text-gray-500">{memoryEvidence.length} memories used to generate this plan</span>
          </div>
          {memoryEvidence.map((snippet, i) => (
            <div key={i} className="border-l-2 border-teal-600 pl-3 mb-2">
              <p className="text-xs text-gray-400">{snippet}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
