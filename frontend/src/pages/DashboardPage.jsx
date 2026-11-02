import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, ShieldAlert, ShieldCheck, PieChart, Activity, Zap } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, PieChart as RePieChart, Pie, Cell } from 'recharts';

export const DashboardPage = () => {
  const [stats, setStats] = useState({
    totalScans: 148,
    highRiskScans: 42,
    verifiedFacts: 86,
    uncertainScans: 20,
    avgRiskScore: 41.2,
    avgConfidence: 94.6
  });

  const dailyActivity = [
    { day: "Mon", scans: 18, risk: 38 },
    { day: "Tue", scans: 24, risk: 45 },
    { day: "Wed", scans: 31, risk: 52 },
    { day: "Thu", scans: 28, risk: 40 },
    { day: "Fri", scans: 36, risk: 48 },
    { day: "Sat", scans: 22, risk: 35 },
    { day: "Sun", scans: 19, risk: 32 }
  ];

  const riskDistribution = [
    { name: "Low Risk (0-25)", count: 58, color: "#10b981" },
    { name: "Moderate (26-50)", count: 48, color: "#f59e0b" },
    { name: "High Risk (51-75)", count: 28, color: "#f97316" },
    { name: "Critical (76-100)", count: 14, color: "#ef4444" }
  ];

  const topTriggers = [
    { trigger: "Miracle / Secret Cure", count: 34 },
    { trigger: "Urgent Share / Forward", count: 29 },
    { trigger: "Illuminati / Secret Society", count: 22 },
    { trigger: "Excessive Punctuation (!!!)", count: 19 },
    { trigger: "Guaranteed 100% / Free Crypto", count: 17 }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Intelligence Radar & Analytics
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time telemetry, threat distribution trends, and linguistic trigger frequencies.
          </p>
        </div>
        <span className="text-xs font-mono text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded border border-blue-500/20">
          ● Live Aggregation Active
        </span>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Total Scans Audited</span>
          <p className="text-2xl sm:text-3xl font-black text-white font-mono">{stats.totalScans}</p>
          <p className="text-[11px] text-blue-400 font-medium">↑ +14% from last week</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-rose-500/20 space-y-2">
          <span className="text-[10px] uppercase font-bold tracking-wider text-rose-400">High Risk Misinformation</span>
          <p className="text-2xl sm:text-3xl font-black text-rose-400 font-mono">{stats.highRiskScans}</p>
          <p className="text-[11px] text-slate-400">28.3% of total corpus</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-emerald-500/20 space-y-2">
          <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400">Verified Fact Articles</span>
          <p className="text-2xl sm:text-3xl font-black text-emerald-400 font-mono">{stats.verifiedFacts}</p>
          <p className="text-[11px] text-slate-400">58.1% fact adherence</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-amber-500/20 space-y-2">
          <span className="text-[10px] uppercase font-bold tracking-wider text-amber-400">Average Threat Score</span>
          <p className="text-2xl sm:text-3xl font-black text-amber-400 font-mono">{stats.avgRiskScore} / 100</p>
          <p className="text-[11px] text-slate-400">Moderate Threat Baseline</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Daily Activity Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              <span>Daily Scan Volume & Risk Trajectory</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Last 7 Days</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dailyActivity}>
                <defs>
                  <linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" textAnchor="middle" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                <Area type="monotone" dataKey="scans" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#scanGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution Breakdown */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <span>4-Tier Threat Category Distribution</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Total Samples: 148</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Manipulation Triggers List */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <span>Most Frequently Flagged Misinformation Triggers</span>
          </h3>
          <span className="text-[10px] font-mono text-slate-400">Lexical Frequency</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {topTriggers.map((t, idx) => (
            <div key={idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-200">{t.trigger}</span>
              <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                {t.count} hits
              </span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
