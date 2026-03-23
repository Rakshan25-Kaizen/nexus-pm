import React from 'react';
import { NavLink } from 'react-router-dom';
import useNexusStore from '../../store/useNexusStore';
import AgentAvatar from '../Agent/AgentAvatar';
import {
  LayoutDashboard,
  BrainCircuit,
  LayoutList,
  CalendarDays,
  Zap,
  Users,
  MessageCircle,
  BarChart2,
  FileText,
  Play,
} from 'lucide-react';

const navItems = [
  {
    path: '/demo',
    label: 'Strategic Intelligence',
    subtitle: 'Real-time AI Engine',
    icon: Play,
    demo: true,
  },
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/agent', label: 'NEXUS Conversation', subtitle: 'Memory · Evidence · History', icon: BrainCircuit, highlight: true },
  { path: '/tasks', label: 'Tasks', icon: LayoutList },
  { path: '/meetings', label: 'Meetings', icon: CalendarDays },
  { path: '/sprint', label: 'Sprint Planner', icon: Zap },
  { path: '/members', label: 'Team Members', icon: Users },
  { path: '/chat', label: 'Memory Chat', icon: MessageCircle },
  { path: '/analytics', label: 'Analytics', icon: BarChart2 },
  { path: '/report', label: 'Project Report', subtitle: 'What NEXUS learned', icon: FileText },
];

export default function Sidebar() {
  const { memoryEnabled, setMemoryEnabled } = useNexusStore();

  return (
    <div className="fixed left-0 top-0 w-60 h-screen bg-[#0A1628] border-r border-gray-800 flex flex-col z-30">
      {/* Header */}
      <div className="p-4 flex items-center gap-3 border-b border-gray-800">
        <AgentAvatar size={24} state="idle" />
        <span className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          NEXUS-PM
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map(({ path, label, subtitle, icon: Icon, highlight, demo }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                demo
                  ? isActive
                    ? 'bg-[#2563EB] text-white shadow-lg shadow-blue-500/30'
                    : 'bg-[#2563EB]/20 text-white hover:bg-[#2563EB]/35'
                  : isActive
                  ? 'bg-accent text-white shadow-lg shadow-blue-500/20'
                  : highlight
                  ? 'text-blue-400 hover:bg-gray-800 hover:text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`
            }
          >
            <Icon size={18} />
            <div className="flex flex-col">
              <span>{label}</span>
              {subtitle && <span className="text-[10px] text-gray-500 leading-tight">{subtitle}</span>}
            </div>
          </NavLink>
        ))}
      </nav>

      {/* Memory Toggle */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">Memory</span>
          <button
            onClick={() => setMemoryEnabled(!memoryEnabled)}
            className={`relative w-10 h-5 rounded-full transition-colors ${
              memoryEnabled ? 'bg-green-500' : 'bg-red-500'
            }`}
          >
            <span
              className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                memoryEnabled ? 'left-5' : 'left-0.5'
              }`}
            />
          </button>
        </div>
        <span className={`text-xs mt-1 block ${memoryEnabled ? 'text-green-400' : 'text-red-400'}`}>
          {memoryEnabled ? 'Hindsight ON' : 'Memory OFF'}
        </span>
      </div>
    </div>
  );
}
