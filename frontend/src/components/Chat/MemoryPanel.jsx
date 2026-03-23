import React from 'react';
import useNexusStore from '../../store/useNexusStore';

export default function MemoryPanel() {
  const { memoryEnabled, lastMemorySnippets, totalMemoryEvents } = useNexusStore();

  return (
    <div className="h-full bg-gray-900/30 rounded-xl border border-gray-800 p-4 flex flex-col">
      <h3 className="text-sm font-bold mb-3">Memory Evidence</h3>
      <div className="mb-3">
        <span className={`text-xs px-2 py-1 rounded ${memoryEnabled ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
          Memory: {memoryEnabled ? 'ON' : 'OFF'}
        </span>
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto">
        {lastMemorySnippets.length === 0 ? (
          <p className="text-gray-500 text-xs">No memories used yet.</p>
        ) : (
          lastMemorySnippets.map((s, i) => (
            <div key={i} className="bg-gray-800 border-l-2 border-blue-500 rounded p-2.5 text-xs text-gray-300 line-clamp-2">
              "{s}"
            </div>
          ))
        )}
      </div>
      <div className="mt-3 pt-3 border-t border-gray-800">
        <p className="text-xs text-gray-500">Total memories accessed: {totalMemoryEvents}</p>
      </div>
    </div>
  );
}
