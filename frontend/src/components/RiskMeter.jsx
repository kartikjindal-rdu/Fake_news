import React from 'react';
import { AlertTriangle, ShieldCheck, AlertOctagon, Info } from 'lucide-react';

export const RiskMeter = ({ score = 0, level = "LOW RISK" }) => {
  const normalizedScore = Math.min(100, Math.max(0, score));

  // Determine active tier
  let activeTier = 0; // 0=Low, 1=Moderate, 2=High, 3=Critical
  if (normalizedScore > 75) activeTier = 3;
  else if (normalizedScore > 50) activeTier = 2;
  else if (normalizedScore > 25) activeTier = 1;

  const tiers = [
    { label: "LOW", range: "0-25", color: "bg-emerald-500", text: "text-emerald-400", border: "border-emerald-500/30" },
    { label: "MODERATE", range: "26-50", color: "bg-amber-500", text: "text-amber-400", border: "border-amber-500/30" },
    { label: "HIGH", range: "51-75", color: "bg-orange-500", text: "text-orange-400", border: "border-orange-500/30" },
    { label: "CRITICAL", range: "76-100", color: "bg-rose-500", text: "text-rose-400", border: "border-rose-500/30" }
  ];

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5 font-bold">
          {activeTier >= 2 ? (
            <AlertOctagon className="w-4 h-4 text-rose-400" />
          ) : activeTier === 1 ? (
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          ) : (
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          )}
          <span className={tiers[activeTier].text}>
            {level} ({score.toFixed(1)} / 100)
          </span>
        </div>
        <span className="text-slate-400 text-[11px] font-mono">
          4-Tier Threat Matrix
        </span>
      </div>

      {/* 4 Segmented Bars */}
      <div className="grid grid-cols-4 gap-1.5 h-3">
        {tiers.map((t, idx) => {
          const isFilled = idx <= activeTier;
          return (
            <div
              key={t.label}
              className={`rounded-full transition-all duration-500 relative overflow-hidden ${
                isFilled ? t.color : 'bg-slate-800'
              }`}
            >
              {idx === activeTier && (
                <div className="absolute inset-0 bg-white/25 animate-pulse" />
              )}
            </div>
          );
        })}
      </div>

      {/* Scale Labels */}
      <div className="grid grid-cols-4 gap-1 text-[10px] text-slate-500 font-mono text-center">
        <span>0-25</span>
        <span>26-50</span>
        <span>51-75</span>
        <span>76-100</span>
      </div>
    </div>
  );
};
