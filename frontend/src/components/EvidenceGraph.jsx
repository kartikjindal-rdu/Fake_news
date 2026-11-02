import React from 'react';
import { Network, CheckCircle, XCircle, AlertCircle, ArrowRight } from 'lucide-react';

export const EvidenceGraph = ({ claimText = "Primary news assertion extracted from scanned document." }) => {
  const sources = [
    { name: "Reuters Wire Service", status: "SUPPORTS", type: "Official News Agency", color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10", icon: CheckCircle },
    { name: "Associated Press (AP)", status: "SUPPORTS", type: "Wire Verification", color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10", icon: CheckCircle },
    { name: "Unverified Blog Post", status: "CONTRADICTS", type: "Social Syndicate", color: "text-rose-400 border-rose-500/30 bg-rose-500/10", icon: XCircle },
    { name: "Academic Peer Review", status: "SUPPORTS", type: "Scientific Journal", color: "text-blue-400 border-blue-500/30 bg-blue-500/10", icon: CheckCircle }
  ];

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <Network className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-bold text-white">Cross-Source Evidence Graph</h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
          Source Convergence
        </span>
      </div>

      {/* Central Claim Node */}
      <div className="p-4 rounded-xl bg-blue-600/10 border border-blue-500/30 text-center space-y-1">
        <span className="text-[10px] uppercase font-bold tracking-wider text-blue-400">Target Core Assertion</span>
        <p className="text-sm font-semibold text-slate-100 italic">"{claimText}"</p>
      </div>

      {/* Connection Links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
        {sources.map((src, idx) => {
          const Icon = src.icon;
          return (
            <div key={idx} className={`p-3.5 rounded-xl border ${src.color} flex items-center justify-between`}>
              <div className="space-y-0.5">
                <p className="text-xs font-bold text-white">{src.name}</p>
                <p className="text-[10px] text-slate-400">{src.type}</p>
              </div>
              <div className="flex items-center gap-1 text-xs font-extrabold uppercase font-mono">
                <Icon className="w-4 h-4" />
                <span>{src.status}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
