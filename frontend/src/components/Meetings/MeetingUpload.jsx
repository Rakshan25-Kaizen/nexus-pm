import React, { useState } from 'react';
import { summarizeMeeting } from '../../api/client';
import useNexusStore from '../../store/useNexusStore';
import SummaryView from './SummaryView';

export default function MeetingUpload() {
  const { projectId } = useNexusStore();
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSummarize = async () => {
    if (!transcript.trim()) return;
    setLoading(true); setError('');
    try {
      const data = await summarizeMeeting({ transcript, project_id: projectId });
      setSummary(data);
      useNexusStore.getState().incrementMemoryEvents(data.memories_stored || 0);
    } catch (e) { setError('Failed to summarize. Check backend connection.'); }
    setLoading(false);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Meeting Summarizer</h1>
      <textarea value={transcript} onChange={e => setTranscript(e.target.value)} rows={8}
        placeholder="Paste your meeting transcript here... e.g.&#10;Alice: The API endpoints are done. Bob: I'll start the frontend tomorrow.&#10;Priya: We need to fix the CI pipeline first, it's blocking deployments."
        className="w-full bg-gray-900 border border-gray-700 rounded-xl p-4 text-sm resize-y min-h-[200px] focus:outline-none focus:border-accent" />
      {error && <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 mt-3 text-red-300 text-sm">{error}</div>}
      <button onClick={handleSummarize} disabled={loading || !transcript.trim()}
        className="mt-4 px-6 py-2.5 bg-accent rounded-lg font-medium hover:bg-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed">
        {loading ? '⏳ Summarizing...' : '🧠 Summarize Meeting'}
      </button>
      {summary && <SummaryView summary={summary} />}
    </div>
  );
}
