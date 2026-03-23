import React from 'react';
import AgentAvatar from '../Agent/AgentAvatar';

export default function DemoScene({ title, subtitle, isLoading, error, children }) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-white" style={{ fontSize: 18 }}>
          {title}
        </h2>
        {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
      </div>

      {isLoading && (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <AgentAvatar size={64} state="thinking" />
          <p className="text-sm text-gray-400">NEXUS is working...</p>
        </div>
      )}

      {!isLoading && error && (
        <div className="rounded-lg border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-200">
          NEXUS could not complete this step. Check backend is running at localhost:8000
          {error && typeof error === 'string' && (
            <span className="block mt-1 text-red-300/80">{error}</span>
          )}
        </div>
      )}

      {!isLoading && !error && children}
    </div>
  );
}
