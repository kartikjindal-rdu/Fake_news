import React, { useState, useEffect } from 'react';
import { History, Search, Filter, Trash2, Download, ExternalLink, ShieldCheck, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

export const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [verdictFilter, setVerdictFilter] = useState('ALL');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    const data = await api.getScans();
    setHistory(data);
  };

  const handleDelete = async (scanId) => {
    if (confirm(`Are you sure you want to delete scan record ${scanId}?`)) {
      try {
        await api.deleteScan(scanId);
      } catch (_) {}
      const updated = history.filter(item => item.scanId !== scanId);
      setHistory(updated);
      localStorage.setItem('veritas_scan_history', JSON.stringify(updated));
    }
  };

  const handleClearAll = () => {
    if (confirm("Are you sure you want to clear all historical audit records?")) {
      setHistory([]);
      localStorage.removeItem('veritas_scan_history');
    }
  };

  const handleExportCsv = () => {
    if (history.length === 0) {
      alert("No history records available to export.");
      return;
    }

    const headers = ["ScanID", "Timestamp", "Verdict", "RiskScore", "Confidence", "FakeProbability", "RealProbability"];
    const rows = history.map(item => [
      item.scanId,
      item.timestamp,
      item.verdict,
      item.scores?.riskScore || 0,
      item.scores?.aiConfidence || 0,
      item.scores?.fakeProbability || 0,
      item.scores?.realProbability || 0
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `veritas_audit_history_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const filteredHistory = history.filter(item => {
    const matchQuery = !searchQuery || 
      item.scanId?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.verdict?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.domain?.name?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchVerdict = verdictFilter === 'ALL' || item.verdict?.includes(verdictFilter);
    return matchQuery && matchVerdict;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-blue-400" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Scan History & Audit Repository
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Browse, filter, and export all historical intelligence scans recorded across analysis sessions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleClearAll}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-400 hover:text-white border border-slate-700 transition-colors"
          >
            Clear All
          </button>
          <button
            onClick={handleExportCsv}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1.5 shadow-lg shadow-blue-500/20"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by ID, domain, or verdict..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs text-slate-400 font-medium">Filter Verdict:</span>
          <select
            value={verdictFilter}
            onChange={(e) => setVerdictFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Verdicts</option>
            <option value="REAL">Verified Real</option>
            <option value="FAKE">High Risk / Fake</option>
            <option value="SUSPICIOUS">Suspicious</option>
          </select>
        </div>
      </div>

      {/* History Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-mono text-[11px] uppercase border-b border-slate-800">
              <tr>
                <th className="px-5 py-3.5">Scan ID</th>
                <th className="px-5 py-3.5">Date & Timestamp</th>
                <th className="px-5 py-3.5">Source Domain</th>
                <th className="px-5 py-3.5">Verdict</th>
                <th className="px-5 py-3.5">Confidence</th>
                <th className="px-5 py-3.5">Risk Score</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {filteredHistory.length > 0 ? (
                filteredHistory.map((item) => (
                  <tr key={item.scanId} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-blue-400 font-bold">{item.scanId}</td>
                    <td className="px-5 py-3.5 text-slate-400">{new Date(item.timestamp).toLocaleString()}</td>
                    <td className="px-5 py-3.5 text-slate-300 font-medium">{item.domain?.name || 'Direct Input'}</td>
                    <td className="px-5 py-3.5">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border ${
                        item.verdict?.includes('FAKE') || item.verdict?.includes('HIGH') 
                          ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
                          : item.verdict?.includes('REAL') 
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>
                        {item.verdict}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-slate-200">{item.scores?.aiConfidence?.toFixed(1)}%</td>
                    <td className="px-5 py-3.5 font-mono text-slate-200">{item.scores?.riskScore?.toFixed(1)} / 100</td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <a
                          href={`/api/export/${item.scanId}/export`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-slate-400 hover:text-emerald-400 p-1 transition-colors"
                          title="Print / View Investigation Certificate"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                        <button
                          onClick={() => handleDelete(item.scanId)}
                          className="text-slate-500 hover:text-rose-400 p-1 transition-colors"
                          title="Delete record"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-5 py-10 text-center text-slate-500 italic">
                    No matching scan history records found. Execute a live scan to populate the audit log.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
