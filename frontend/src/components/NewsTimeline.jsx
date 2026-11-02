import React, { useState, useEffect } from 'react';
import { 
  Clock, AlertTriangle, ShieldCheck, HelpCircle, Radio, 
  ExternalLink, Layers, Search, RefreshCw 
} from 'lucide-react';
import { api } from '../services/api';

export const NewsTimeline = ({ defaultQuery = "election OR health" }) => {
  const [topicQuery, setTopicQuery] = useState(defaultQuery);
  const [loading, setLoading] = useState(false);
  const [timelineData, setTimelineData] = useState(null);

  const fetchTimeline = async (q) => {
    setLoading(true);
    try {
      const data = await api.getNewsTimeline(q, 15);
      setTimelineData(data);
    } catch (err) {
      console.error("Timeline fetch failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline(defaultQuery);
  }, [defaultQuery]);

  const fallbackEvents = [
    { published_at: "08:15 AM UTC", headline: "First Social Post & Alert Surfaced", publisher: "Wire Monitor", coverage_type: "Social Post", category: "Alert" },
    { published_at: "09:30 AM UTC", headline: "Cross-Syndication Across Regional Aggregators", publisher: "Syndicated Wire", coverage_type: "Syndicated / Wire Pickup", category: "Syndication" },
    { published_at: "11:45 AM UTC", headline: "Independent Fact-Checking Review", publisher: "Fact Check Wire", coverage_type: "Independent Coverage", category: "Fact Check" },
    { published_at: "02:00 PM UTC", headline: "Official Press Agency Clarification", publisher: "Official Wire", coverage_type: "Independent Coverage", category: "Official" }
  ];

  const items = timelineData?.timeline && timelineData.timeline.length > 0
    ? timelineData.timeline
    : fallbackEvents;

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
      
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <Clock className="w-5 h-5 text-blue-400" />
          <div>
            <h3 className="text-sm font-bold text-white">
              Multi-Publisher Coverage Timeline & Syndication Radar
            </h3>
            <p className="text-[11px] text-slate-400">
              Track publication timestamps and detect syndicated wire copies vs independent reports.
            </p>
          </div>
        </div>

        {/* Topic Search Input */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <input
            type="text"
            value={topicQuery}
            onChange={(e) => setTopicQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchTimeline(topicQuery)}
            placeholder="Filter topic..."
            className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 w-36 sm:w-44"
          />
          <button
            onClick={() => fetchTimeline(topicQuery)}
            disabled={loading}
            className="p-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 border border-blue-500/30 transition-colors"
            title="Refresh Timeline"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Syndication Detection Summary Banner */}
      {timelineData && (
        <div className={`p-3.5 rounded-xl border text-xs flex items-start gap-2.5 ${
          timelineData.has_syndication
            ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
            : 'bg-blue-500/10 border-blue-500/30 text-blue-300'
        }`}>
          <Layers className="w-4 h-4 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-bold">
              {timelineData.has_syndication ? 'Syndication Detected' : 'Independent Reporting Structure'}:
            </span>
            <p className="text-[11px] opacity-90 leading-normal">
              {timelineData.syndication_summary} ({timelineData.publishers_count} distinct media outlets tracked).
            </p>
          </div>
        </div>
      )}

      {/* Timeline Stream */}
      <div className="space-y-4 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-800">
        {items.map((evt, idx) => {
          const isSyndicated = evt.coverage_type?.includes('Syndicated');
          const isOfficial = evt.category === 'Health' || evt.category === 'Official';

          const badgeBg = isSyndicated
            ? 'text-amber-400 bg-amber-500/10 border-amber-500/30'
            : isOfficial
            ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
            : 'text-blue-400 bg-blue-500/10 border-blue-500/30';

          return (
            <div key={idx} className="relative flex items-start gap-4 pl-1">
              <div className={`w-7 h-7 rounded-full border ${badgeBg} flex items-center justify-center shrink-0 z-10`}>
                <Clock className="w-3.5 h-3.5" />
              </div>
              <div className="space-y-1.5 flex-1 p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-xs font-bold text-slate-100">{evt.headline}</span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase ${badgeBg}`}>
                    {evt.coverage_type || 'Coverage'}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400 font-mono">
                  <span>Publisher: <strong className="text-slate-300">{evt.publisher}</strong></span>
                  {evt.published_at && (
                    <span>Time: <strong className="text-slate-300">{evt.published_at}</strong></span>
                  )}
                  {evt.category && (
                    <span>Category: <strong className="text-slate-300">{evt.category}</strong></span>
                  )}
                </div>
                {evt.url && (
                  <a
                    href={evt.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] text-blue-400 hover:text-blue-300 flex items-center gap-1 pt-0.5"
                  >
                    <span>Read original publisher coverage</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
