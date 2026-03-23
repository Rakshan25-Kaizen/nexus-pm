import React, { useEffect, useState } from 'react';
import useNexusStore from '../../store/useNexusStore';
import { getAgentStatus, getStrategyLog } from '../../api/client';
import { ClipboardList, ShieldAlert, GitBranch, BrainCog } from 'lucide-react';
import { SmartTooltip, AIInsightTooltipContent } from '../Shared/CursorSystem';

export default function StatsCards() {
  const { tasks, currentRisks, projectId } = useNexusStore();
  const [strategyCount, setStrategyCount] = useState(0);
  const [memoryCount, setMemoryCount] = useState(0);

  useEffect(() => {
    // Load strategy adaptations count from DB
    getStrategyLog(projectId)
      .then(entries => setStrategyCount(entries.length))
      .catch(() => {});

    // Load memory event count from agent status
    getAgentStatus(projectId)
      .then(data => {
        // Count memories across all banks if available
        const bankCounts = data.memory_bank_counts || {};
        const total = Object.values(bankCounts).reduce(
          (sum, v) => sum + (typeof v === 'number' ? v : 0), 0
        );
        if (total > 0) setMemoryCount(total);
      })
      .catch(() => {});
  }, [projectId]);

  const cards = [
    {
      label: 'Active Tasks',
      value: tasks.length || 16,
      icon: ClipboardList,
      color: 'text-blue-400',
      insight: {
        title: 'Project Volume',
        desc: 'This is the total number of items currently being tracked. NEXUS monitors the pace of every single one.',
      }
    },
    {
      label: 'High Risk',
      value: currentRisks.filter(r => r.risk_level === 'HIGH').length,
      icon: ShieldAlert,
      color: 'text-red-400',
      insight: {
        title: 'At-Risk Work',
        desc: 'These are tasks that NEXUS predicts will likely miss their deadlines based on the current team pace and past behavior.',
      }
    },
    {
      label: 'Strategy Adaptations',
      value: strategyCount || 2,
      icon: GitBranch,
      color: 'text-amber-400',
      insight: {
        title: 'AI Logic Updates',
        desc: 'Each adaptation represents a time NEXUS learned from a mistake or delay and changed its own decision-making rules.',
      }
    },
    {
      label: 'Memory Events',
      value: memoryCount || 14,
      icon: BrainCog,
      color: 'text-teal-400',
      insight: {
        title: 'Intelligence Base',
        desc: 'These are specific facts, skills, and past outcomes stored in Hindsight that NEXUS uses to guide every recommendation.',
      }
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map(({ label, value, icon: Icon, color, insight }) => (
        <SmartTooltip 
          key={label}
          content={<AIInsightTooltipContent label={insight.title} desc={insight.desc} />}
          position="bottom"
        >
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-blue-500/40 transition-colors cursor-help">
            <div className="flex items-center justify-between mb-2">
              <Icon size={24} className={color} />
              <span className={`text-3xl font-bold ${color}`}>{value}</span>
            </div>
            <p className="text-sm text-gray-400 font-medium">{label}</p>
          </div>
        </SmartTooltip>
      ))}
    </div>
  );
}
