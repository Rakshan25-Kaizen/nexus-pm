import { SmartTooltip, StrategyTooltipContent, SpotlightCard } from '../Shared/CursorSystem';

export default function StrategyLog({ entries }) {
  if (!entries?.length) {
    return (
      <div className="rounded-xl border border-gray-800 bg-[#0A1628] p-6">
        <p className="text-sm text-gray-500">
          No strategy adaptations recorded yet. They appear when NEXUS adjusts weights after task outcomes.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {entries.map((e, i) => (
        <SmartTooltip
          key={e.id || i}
          content={<StrategyTooltipContent entry={e} />}
          position="right"
        >
          <SpotlightCard className="rounded-lg border border-gray-700/80 bg-gray-900/50 p-3 text-sm cursor-pointer hover:border-blue-500/50 transition-all">
            <p className="text-gray-200">
              {e.trigger_pattern?.replace(/_/g,' ') || e.message || 'Adaptation'}
            </p>
            {e.new_weights && (
              <p className="text-xs text-gray-500 mt-1">
                Workload weight: {Math.round((e.old_weights?.current_load||0)*100)}%
                → {Math.round((e.new_weights?.current_load||0)*100)}%
              </p>
            )}
            <p className="text-[10px] text-blue-400 mt-1 font-medium">
              💡 Hover for explanation in plain English
            </p>
          </SpotlightCard>
        </SmartTooltip>
      ))}
    </div>
  );
}
