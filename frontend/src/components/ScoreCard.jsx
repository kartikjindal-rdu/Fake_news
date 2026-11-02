import React from 'react';

export const ScoreCard = ({ title, score = 0, max = 100, unit = "%", icon: Icon, color = "blue", description }) => {
  const normalized = Math.min(max, Math.max(0, score));

  const colorMap = {
    blue: { bg: 'bg-blue-500/10', border: 'border-blue-500/20', text: 'text-blue-400', bar: 'bg-blue-500' },
    emerald: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', text: 'text-emerald-400', bar: 'bg-emerald-500' },
    rose: { bg: 'bg-rose-500/10', border: 'border-rose-500/20', text: 'text-rose-400', bar: 'bg-rose-500' },
    amber: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400', bar: 'bg-amber-500' },
    purple: { bg: 'bg-purple-500/10', border: 'border-purple-500/20', text: 'text-purple-400', bar: 'bg-purple-500' },
    indigo: { bg: 'bg-indigo-500/10', border: 'border-indigo-500/20', text: 'text-indigo-400', bar: 'bg-indigo-500' }
  };

  const activeColor = colorMap[color] || colorMap.blue;

  return (
    <div className={`p-4 rounded-xl glass-panel ${activeColor.border} glass-card-hover space-y-3`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {Icon && (
            <div className={`w-7 h-7 rounded-lg ${activeColor.bg} flex items-center justify-center ${activeColor.text}`}>
              <Icon className="w-4 h-4" />
            </div>
          )}
          <span className="text-xs font-bold text-slate-300 tracking-wide">{title}</span>
        </div>
        <span className={`text-base font-extrabold font-mono ${activeColor.text}`}>
          {score.toFixed(1)}{unit}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden">
        <div 
          className={`h-2 rounded-full transition-all duration-700 ${activeColor.bar}`}
          style={{ width: `${(normalized / max) * 100}%` }}
        />
      </div>

      {description && (
        <p className="text-[11px] text-slate-400 leading-tight">
          {description}
        </p>
      )}
    </div>
  );
};
