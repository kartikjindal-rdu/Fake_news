import React, { useState } from 'react';
import { AlertCircle, HelpCircle } from 'lucide-react';

export const TextHighlighter = ({ text = "", highlights = {} }) => {
  const [activeTooltip, setActiveTooltip] = useState(null);

  if (!text) {
    return <p className="text-xs text-slate-500 italic">No text provided for analysis.</p>;
  }

  const triggerKeys = Object.keys(highlights);
  if (triggerKeys.length === 0) {
    return <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{text}</p>;
  }

  // Build regex for all trigger keys
  const pattern = new RegExp(`\\b(${triggerKeys.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b`, 'gi');
  const parts = text.split(pattern);

  return (
    <div className="space-y-4">
      {/* Highlighted text body */}
      <div className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap p-4 rounded-xl bg-slate-900/80 border border-slate-800">
        {parts.map((part, idx) => {
          const matchedKey = triggerKeys.find(k => k.toLowerCase() === part.toLowerCase());
          if (matchedKey) {
            const reason = highlights[matchedKey];
            return (
              <span
                key={idx}
                onMouseEnter={() => setActiveTooltip({ word: part, reason })}
                onMouseLeave={() => setActiveTooltip(null)}
                className="bg-rose-500/25 text-rose-300 font-bold px-1.5 py-0.5 rounded border border-rose-500/40 cursor-help transition-all hover:bg-rose-500/40 inline-flex items-center gap-1 mx-0.5 shadow-sm"
              >
                {part}
              </span>
            );
          }
          return <span key={idx}>{part}</span>;
        })}
      </div>

      {/* Interactive Tooltip Card / Legend */}
      <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start gap-3">
        <HelpCircle className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <p className="font-semibold text-slate-200">
            {activeTooltip ? `Inspecting: "${activeTooltip.word}"` : "Interactive Linguistic Trigger Inspector"}
          </p>
          <p className="text-slate-400">
            {activeTooltip ? activeTooltip.reason : "Hover over any highlighted text above to inspect the specific manipulation reason."}
          </p>
        </div>
      </div>
    </div>
  );
};
