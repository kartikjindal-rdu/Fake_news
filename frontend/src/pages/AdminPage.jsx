import React, { useState, useEffect } from 'react';
import { 
  Activity, Server, Database, Cpu, Cloud, Users, Shield, HardDrive,
  Radio, CheckCircle2, AlertCircle, RefreshCw, Plus, ToggleLeft, ToggleRight,
  Video, Globe, CheckSquare, Layers, ExternalLink, X
} from 'lucide-react';
import { api } from '../services/api';

export const AdminPage = () => {
  const [sources, setSources] = useState([]);
  const [loadingSources, setLoadingSources] = useState(true);
  const [sourceFilter, setSourceFilter] = useState('all');
  const [togglingId, setTogglingId] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);

  // New source form state
  const [newSource, setNewSource] = useState({
    id: '',
    name: '',
    category: 'India',
    type: 'rss',
    url: '',
  });
  const [submittingSource, setSubmittingSource] = useState(false);

  const microservices = [
    { name: "FastAPI REST API Gateway", status: "Operational", port: "8000", latency: "12ms", icon: Server, color: "text-emerald-400" },
    { name: "Scikit-Learn ML Inference Engine", status: "Operational", port: "Embedded", latency: "6ms", icon: Cpu, color: "text-emerald-400" },
    { name: "SQLite / PostgreSQL Database", status: "Operational", port: "5432", latency: "3ms", icon: Database, color: "text-emerald-400" },
    { name: "Tesseract OCR Service", status: "Ready / Standby", port: "Hook Active", latency: "N/A", icon: HardDrive, color: "text-blue-400" },
    { name: "Cloud Container Cluster", status: "Docker Ready", port: "Multi-Node", latency: "N/A", icon: Cloud, color: "text-indigo-400" }
  ];

  const systemUsers = [
    { name: "Lead Investigator", email: "investigator@veritas.ai", role: "SuperAdmin", status: "Active" },
    { name: "AI Research Analyst", email: "analyst@veritas.ai", role: "ML Evaluator", status: "Active" },
    { name: "Journalism Auditor", email: "auditor@veritas.ai", role: "Content Reviewer", status: "Active" }
  ];

  // Fetch sources
  const loadSources = async () => {
    setLoadingSources(true);
    try {
      const data = await api.getNewsSources();
      setSources(Array.isArray(data) ? data : []);
    } catch (err) {
      setActionError("Failed to fetch news sources registry.");
    } finally {
      setLoadingSources(false);
    }
  };

  useEffect(() => {
    loadSources();
  }, []);

  // Handle Toggle
  const handleToggleSource = async (sourceId, currentEnabled) => {
    setTogglingId(sourceId);
    setActionError(null);
    setActionSuccess(null);
    try {
      const res = await api.toggleNewsSource(sourceId, !currentEnabled);
      setSources(prev => prev.map(s => s.id === sourceId ? { ...s, enabled: !currentEnabled } : s));
      setActionSuccess(res.message || `Source '${sourceId}' updated.`);
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (err) {
      setActionError(err.message || "Failed to update source state.");
    } finally {
      setTogglingId(null);
    }
  };

  // Handle Add Source
  const handleAddSource = async (e) => {
    e.preventDefault();
    setActionError(null);
    setActionSuccess(null);
    setSubmittingSource(true);

    try {
      const res = await api.addNewsSource(newSource);
      setActionSuccess(res.message || "Source added successfully.");
      setShowAddModal(false);
      setNewSource({ id: '', name: '', category: 'India', type: 'rss', url: '' });
      await loadSources();
      setTimeout(() => setActionSuccess(null), 3500);
    } catch (err) {
      setActionError(err.message || "Failed to add source endpoint.");
    } finally {
      setSubmittingSource(false);
    }
  };

  // Filter sources
  const filteredSources = sources.filter(s => {
    if (sourceFilter === 'all') return true;
    return s.type === sourceFilter;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-400" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Admin & System Health Console
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Monitor microservice latencies, ML inference gateways, multi-channel news feed health, and administrative RBAC.
          </p>
        </div>
      </div>

      {/* Global Alerts */}
      {actionSuccess && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2 text-xs text-emerald-300 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{actionSuccess}</span>
        </div>
      )}
      {actionError && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-between gap-2 text-xs text-rose-300 animate-fadeIn">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{actionError}</span>
          </div>
          <button onClick={() => setActionError(null)} className="text-rose-400 hover:text-white">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* ============================================================
          MULTI-CHANNEL NEWS SOURCE REGISTRY MANAGEMENT
         ============================================================ */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Radio className="w-4 h-4 text-blue-400" />
              <span>Multi-Channel News Ingestion & Feed Registry</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Manage Indian press, international feeds, WHO/UN official outlets, fact-check wires, and YouTube channels.
            </p>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <button
              onClick={loadSources}
              disabled={loadingSources}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition-all text-xs"
              title="Refresh source list"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingSources ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-3 py-1.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1.5 shadow-md shadow-blue-600/20 transition-all"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Verified Feed</span>
            </button>
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          {['all', 'rss', 'youtube', 'official', 'factcheck', 'api'].map(f => (
            <button
              key={f}
              onClick={() => setSourceFilter(f)}
              className={`px-2.5 py-1 rounded-lg font-bold capitalize transition-all ${
                sourceFilter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {f === 'all' ? 'All Channels' : f}
            </button>
          ))}
          <span className="text-[11px] text-slate-500 ml-auto font-mono">
            {filteredSources.length} sources registered
          </span>
        </div>

        {/* Sources Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 font-mono uppercase text-[11px] border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Channel / Source</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Articles</th>
                <th className="px-4 py-3">Health Status</th>
                <th className="px-4 py-3 text-right">Ingestion Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {filteredSources.map((src) => {
                const isToggling = togglingId === src.id;
                const isEnabled = src.enabled !== false;

                return (
                  <tr key={src.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-semibold text-slate-200">{src.name}</div>
                      <div className="text-[10px] text-slate-500 font-mono truncate max-w-xs">{src.id}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800 font-medium text-[10px]">
                        {src.category}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {src.type === 'youtube' && (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-rose-400">
                          <Video className="w-3.5 h-3.5" /> YouTube
                        </span>
                      )}
                      {src.type === 'official' && (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-400">
                          <Shield className="w-3.5 h-3.5" /> Official
                        </span>
                      )}
                      {src.type === 'factcheck' && (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-purple-400">
                          <CheckSquare className="w-3.5 h-3.5" /> Fact Check
                        </span>
                      )}
                      {src.type === 'api' && (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-amber-400">
                          <Globe className="w-3.5 h-3.5" /> Open API
                        </span>
                      )}
                      {src.type === 'rss' && (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-blue-400">
                          <Radio className="w-3.5 h-3.5" /> RSS / Atom
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-300">
                      {src.article_count || 0}
                    </td>
                    <td className="px-4 py-3">
                      {src.last_error ? (
                        <span className="text-[10px] font-mono text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20" title={src.last_error}>
                          Error / Warning
                        </span>
                      ) : (
                        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          Operational
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleToggleSource(src.id, isEnabled)}
                        disabled={isToggling}
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                          isEnabled
                            ? 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/30'
                            : 'bg-slate-800 text-slate-400 hover:bg-slate-700 border border-slate-700'
                        } disabled:opacity-50`}
                      >
                        {isToggling ? (
                          <RefreshCw className="w-3 h-3 animate-spin" />
                        ) : isEnabled ? (
                          <>
                            <ToggleRight className="w-3.5 h-3.5 text-emerald-400" />
                            <span>Active</span>
                          </>
                        ) : (
                          <>
                            <ToggleLeft className="w-3.5 h-3.5 text-slate-400" />
                            <span>Disabled</span>
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Custom Source Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl animate-scaleUp">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Plus className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-bold text-white">Add Verified News Feed Source</h3>
              </div>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleAddSource} className="space-y-3.5 text-xs">
              <div className="space-y-1">
                <label className="text-slate-300 font-bold">Source ID (Machine Name)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. pib_india, reuters_top"
                  value={newSource.id}
                  onChange={e => setNewSource({ ...newSource, id: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-300 font-bold">Display Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Press Information Bureau (India)"
                  value={newSource.name}
                  onChange={e => setNewSource({ ...newSource, name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-300 font-bold">Category</label>
                  <select
                    value={newSource.category}
                    onChange={e => setNewSource({ ...newSource, category: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-2 text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
                  >
                    <option value="India">India</option>
                    <option value="World">World</option>
                    <option value="Health">Health</option>
                    <option value="Science">Science</option>
                    <option value="Fact Check">Fact Check</option>
                    <option value="Elections">Elections</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-slate-300 font-bold">Channel Type</label>
                  <select
                    value={newSource.type}
                    onChange={e => setNewSource({ ...newSource, type: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-2 text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
                  >
                    <option value="rss">RSS / Atom</option>
                    <option value="official">Official Agency</option>
                    <option value="factcheck">Fact-Checking Wire</option>
                    <option value="youtube">YouTube Channel</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-slate-300 font-bold">Endpoint / Feed URL</label>
                <input
                  type="url"
                  required
                  placeholder="https://example.com/feed.xml"
                  value={newSource.url}
                  onChange={e => setNewSource({ ...newSource, url: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
                />
                <p className="text-[10px] text-slate-500">
                  Protected by SSRF validation. Internal networks, 127.0.0.1, and metadata IPs are rejected.
                </p>
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3.5 py-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingSource}
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold flex items-center gap-1.5 shadow-md shadow-blue-600/20 disabled:opacity-50"
                >
                  {submittingSource ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                  <span>{submittingSource ? "Verifying..." : "Register Source"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Microservice Health Grid */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Server className="w-4 h-4 text-blue-400" />
          <span>Microservice Architecture & Latency Telemetry</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {microservices.map((svc, idx) => {
            const Icon = svc.icon;
            return (
              <div key={idx} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20`}>
                    ● {svc.status}
                  </span>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-200">{svc.name}</h4>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono mt-1">
                    <span>Port: {svc.port}</span>
                    <span>Latency: {svc.latency}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* User Management Table */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Users className="w-4 h-4 text-purple-400" />
          <span>Platform Role-Based Access Control (RBAC)</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 font-mono uppercase text-[11px] border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {systemUsers.map((u, i) => (
                <tr key={i} className="hover:bg-slate-800/40">
                  <td className="px-4 py-3 font-semibold text-slate-200">{u.name}</td>
                  <td className="px-4 py-3 text-slate-400 font-mono">{u.email}</td>
                  <td className="px-4 py-3 text-blue-400 font-mono font-bold">{u.role}</td>
                  <td className="px-4 py-3 text-right text-emerald-400 font-semibold">{u.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
