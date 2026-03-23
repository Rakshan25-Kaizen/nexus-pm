import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useNexusStore from '../../store/useNexusStore';
import { getTasks, getTaskRisks, getDigest, sendDigest, getWorkloadForecast } from '../../api/client';
import StatsCards from './StatsCards';
import AgentAvatar from '../Agent/AgentAvatar';
import { RefreshCw, ArrowRight, Send } from 'lucide-react';

const DeliveryBadges = ({ delivered }) => (
  <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
    {delivered?.slack && <span style={{ background: '#F0FDF4', color: '#16A34A', padding: '2px 8px', borderRadius: 4, fontSize: 12, fontWeight: 600 }}>Slack sent</span>}
    {delivered?.email && <span style={{ background: '#EFF6FF', color: '#2563EB', padding: '2px 8px', borderRadius: 4, fontSize: 12, fontWeight: 600 }}>Email sent</span>}
    {(!delivered?.slack && !delivered?.email) && <span style={{ color: '#94A3B8', fontSize: 12 }}>In-app only — add Slack or SMTP to .env to deliver externally</span>}
  </div>
);

export default function Dashboard() {
  const navigate = useNavigate();
  const { projectId, setTasks, setRisks, agentHistory, strategyLog, agentGreeting } = useNexusStore();
  const [digestText, setDigestText] = useState('');
  const [digestTime, setDigestTime] = useState('');
  const [digestLoading, setDigestLoading] = useState(true);
  const [sendingDigest, setSendingDigest] = useState(false);
  const [deliveredVia, setDeliveredVia] = useState(null);
  const [forecastWarnings, setForecastWarnings] = useState([]);

  useEffect(() => {
    getTasks(projectId).then(setTasks).catch(() => {});
    getTaskRisks(projectId).then(setRisks).catch(() => {});
    loadDigest();
    getWorkloadForecast(projectId).then(data => {
      const warnings = data.forecasts
        .filter(f => f.overload_risk)
        .map(f => f.warning);
      if (warnings.length > 0) {
        setForecastWarnings(warnings);
      }
    }).catch(() => {});
  }, [projectId]);

  const loadDigest = async () => {
    setDigestLoading(true);
    setDeliveredVia(null);
    try {
      const data = await getDigest(projectId);
      setDigestText(data.digest);
      setDigestTime(new Date(data.generated_at).toLocaleString());
      useNexusStore.getState().setMorningDigest(data.digest);
      useNexusStore.getState().setDigestTimestamp(data.generated_at);
    } catch (e) {
      setDigestText('NEXUS morning brief unavailable. Check that the backend is running.');
    }
    setDigestLoading(false);
  };

  const handleSendNow = async () => {
    setSendingDigest(true);
    try {
      const data = await sendDigest(projectId);
      setDigestText(data.digest);
      setDigestTime(new Date(data.generated_at).toLocaleString());
      setDeliveredVia(data.delivered_via);
    } catch (e) {
      console.error('Failed to dispatch digest manually', e);
    }
    setSendingDigest(false);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      {agentGreeting && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 mb-6">
          <p className="text-sm text-gray-300 italic">{agentGreeting}</p>
        </div>
      )}
      <StatsCards />

      {forecastWarnings?.length > 0 && (
        <div className="bg-amber-900/20 border border-amber-700 rounded-xl p-4 mt-4">
          <h3 className="text-sm font-semibold text-amber-400 mb-2">
            Workload Forecast — Next Sprint
          </h3>
          {forecastWarnings.map((w, i) => (
            <p key={i} className="text-xs text-amber-300 mb-1">{w}</p>
          ))}
          <p className="text-xs text-gray-500 mt-2">
            Powered by LinearRegression forecast model
          </p>
        </div>
      )}

      {/* NEXUS Morning Brief */}
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-5 mt-4">
        <div className="flex items-center gap-2 mb-3">
          <AgentAvatar size={24} state="speaking" />
          <span className="font-semibold text-white">NEXUS Morning Brief</span>
          <span className="text-xs text-gray-500 ml-auto">{digestTime}</span>
          <button
            onClick={loadDigest}
            disabled={digestLoading || sendingDigest}
            className="text-xs text-accent hover:underline flex items-center gap-1 disabled:opacity-50 mr-2"
          >
            <RefreshCw size={12} className={digestLoading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleSendNow}
            disabled={digestLoading || sendingDigest}
            className="text-xs bg-accent text-white px-2 py-1 rounded hover:bg-blue-600 flex items-center gap-1 transition-colors disabled:opacity-50"
          >
            <Send size={12} className={sendingDigest ? 'animate-pulse' : ''} />
            <span>{sendingDigest ? 'Sending...' : 'Send Now'}</span>
          </button>
        </div>
        
        {deliveredVia && <DeliveryBadges delivered={deliveredVia} />}

        <div className="mt-3">
          {digestLoading ? (
            <div className="space-y-2">
              <div className="h-3 bg-gray-800 rounded animate-pulse w-full" />
              <div className="h-3 bg-gray-800 rounded animate-pulse w-3/4" />
              <div className="h-3 bg-gray-800 rounded animate-pulse w-1/2" />
            </div>
          ) : (
            <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-line mt-2">
              {digestText || 'Loading NEXUS morning brief...'}
            </p>
          )}
        </div>
        <div className="mt-3 pt-3 border-t border-gray-800">
          <button
            onClick={() => navigate('/agent')}
            className="text-xs text-accent hover:underline flex items-center gap-1"
          >
            <span>Continue conversation with NEXUS</span>
            <ArrowRight size={12} />
          </button>
        </div>
        {/* Team Section */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold mb-4 text-white">Project Intelligence Team</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {useNexusStore.getState().members?.map(m => (
            <div key={m.id} className="flex items-center gap-3 p-3 bg-gray-800/40 rounded-lg border border-gray-800/50 hover:border-accent/30 transition-colors">
              <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-sm font-bold text-accent">
                {m.name[0]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{m.name}</p>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider">{m.role}</p>
              </div>
              <div className="text-right">
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                  m.active_tasks > 0
                    ? 'bg-blue-900/40 text-blue-400 border border-blue-800/50'
                    : 'bg-gray-800/60 text-gray-500 border border-gray-700/50'
                }`}>
                  {m.active_tasks} active
                </span>
                <p className="text-[10px] text-gray-400 mt-1">{Math.round((m.completion_rate || 0.85) * 100)}% reliability</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
    </div>
  );
}
