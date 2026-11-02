import React, { useState } from 'react';
import { 
  Search, CheckCircle2, AlertTriangle, XCircle, HelpCircle, 
  ExternalLink, ArrowRight, Loader2, Sparkles, BookOpen, Globe,
  Network, CheckSquare, Printer, RefreshCw, Layers, Shield, FileText
} from 'lucide-react';
import { api } from '../services/api';
import { InteractiveClaimGraph } from '../components/InteractiveClaimGraph';

export const ClaimIntelligencePage = () => {
  const [activeTab, setActiveTab] = useState('research'); // 'research' | 'graph' | 'factcheck'
  const [inputText, setInputText] = useState('');
  const [headline, setHeadline] = useState('');
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [investigationResult, setInvestigationResult] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [selectedClaimIndex, setSelectedClaimIndex] = useState(0);
  const [investigationError, setInvestigationError] = useState(null);

  // Fact-Check Search state
  const [fcQuery, setFcQuery] = useState('');
  const [isSearchingFc, setIsSearchingFc] = useState(false);
  const [fcResults, setFcResults] = useState(null);

  // Execute full research agent workflow
  const handleExecuteResearch = async (e) => {
    if (e) e.preventDefault();
    if (!inputText.trim()) return;

    setIsInvestigating(true);
    setInvestigationError(null);

    try {
      const inv = await api.conductResearch({
        text: inputText.trim(),
        headline: headline.trim() || undefined,
        max_claims: 4,
      });

      setInvestigationResult(inv);
      setSelectedClaimIndex(0);

      // Generate Graph
      const g = await api.generateClaimGraph(inv);
      setGraphData(g);
    } catch (err) {
      setInvestigationError(err.message || "Research agent workflow encountered an error.");
    } finally {
      setIsInvestigating(false);
    }
  };

  // Execute Fact-Check search
  const handleFactCheckSearch = async (e) => {
    if (e) e.preventDefault();
    if (!fcQuery.trim()) return;

    setIsSearchingFc(true);
    try {
      const res = await api.searchFactChecks(fcQuery.trim(), 6);
      setFcResults(res);
    } catch (err) {
      setFcResults({
        query: fcQuery,
        matches_found: 0,
        status: "ERROR",
        message: "Failed to connect to fact-check search provider.",
        results: [],
      });
    } finally {
      setIsSearchingFc(false);
    }
  };

  // Handle Export Dossier
  const handleExportDossier = () => {
    if (!investigationResult) return;
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const payload = JSON.stringify(investigationResult);
    // Submit to export endpoint via form POST
    const form = printWindow.document.createElement('form');
    form.method = 'POST';
    form.action = '/api/export/investigation/export';

    const input = printWindow.document.createElement('input');
    input.type = 'hidden';
    input.name = 'payload';
    input.value = payload;

    // Send JSON fetch and write HTML directly
    fetch('/api/export/investigation/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload,
    })
      .then(res => res.text())
      .then(html => {
        printWindow.document.open();
        printWindow.document.write(html);
        printWindow.document.close();
      })
      .catch(() => {
        printWindow.close();
      });
  };

  const currentClaim = investigationResult?.claims?.[selectedClaimIndex];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Search className="w-5 h-5 text-blue-400" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              AI Research Agent & Grounded Evidence Matrix
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Isolate checkable factual assertions, ground them against open knowledge repositories & fact-check wires, and inspect relationship provenance.
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          {investigationResult && (
            <button
              onClick={handleExportDossier}
              className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 flex items-center gap-1.5 transition-all shadow-sm"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Dossier</span>
            </button>
          )}
          <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
            Decoupled Evidence Engine
          </span>
        </div>
      </div>

      {/* Mode Switch Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800/80 pb-2">
        <button
          onClick={() => setActiveTab('research')}
          className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === 'research'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
              : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>AI Research Workflow</span>
        </button>

        <button
          onClick={() => setActiveTab('graph')}
          className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === 'graph'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
              : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <Network className="w-3.5 h-3.5" />
          <span>Claim Relationship Graph</span>
        </button>

        <button
          onClick={() => setActiveTab('factcheck')}
          className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === 'factcheck'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
              : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <CheckSquare className="w-3.5 h-3.5 text-purple-400" />
          <span>Fact-Check Archive Search</span>
        </button>
      </div>

      {/* ============================================================
          TAB 1: AI RESEARCH AGENT WORKFLOW
         ============================================================ */}
      {activeTab === 'research' && (
        <div className="space-y-6">
          
          {/* Research Input Form */}
          <form onSubmit={handleExecuteResearch} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-200 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-400" />
                <span>Submit Any Article, Claim, or Social Post for Grounded Investigation</span>
              </label>
              <span className="text-[10px] text-slate-400 font-mono">
                Decoupled from ML Stylistic Predictions • Multi-Source Verification
              </span>
            </div>

            <div className="space-y-3">
              <input
                type="text"
                value={headline}
                onChange={(e) => setHeadline(e.target.value)}
                placeholder="Optional Headline or Context (e.g. 'WHO: Clinical Guidelines for Hypertension')..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />

              <textarea
                rows={3}
                required
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Paste news text, statement, or press release to extract and verify checkable factual claims..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none font-sans"
              />
            </div>

            {investigationError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300">
                {investigationError}
              </div>
            )}

            <div className="flex items-center justify-between pt-1">
              <span className="text-[11px] text-slate-500">
                Queries Wikipedia OpenSearch, DuckDuckGo Knowledge, & GDELT Fact-Check Wire.
              </span>
              <button
                type="submit"
                disabled={isInvestigating || !inputText.trim()}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-2 transition-all disabled:opacity-50 shadow-md shadow-blue-600/20 shrink-0"
              >
                {isInvestigating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Investigating Claims & Sources...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span>Run AI Research Investigation</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Research Results View */}
          {investigationResult && (
            <div className="space-y-6 animate-fadeIn">
              
              {/* Overall Findings Banner */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-slate-400 uppercase">
                      Investigation ID: {investigationResult.investigation_id}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      {investigationResult.claims?.length || 0} Subclaims Audited
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white">
                    {investigationResult.overall_verdict}
                  </h3>
                </div>

                <button
                  onClick={() => setActiveTab('graph')}
                  className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-blue-600/15 hover:bg-blue-600/25 text-blue-300 border border-blue-500/30 flex items-center gap-1.5 transition-all shrink-0"
                >
                  <Network className="w-3.5 h-3.5" />
                  <span>View in Relationship Graph</span>
                </button>
              </div>

              {/* Subclaims Split View */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                
                {/* Claims List (5 Cols) */}
                <div className="lg:col-span-5 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Audited Factual Assertions ({investigationResult.claims?.length || 0})
                  </h4>

                  <div className="space-y-2.5">
                    {investigationResult.claims?.map((c, idx) => {
                      const isSelected = selectedClaimIndex === idx;
                      let badgeColor = "bg-slate-800 text-slate-300";
                      if (c.assessment_code === 'SUPPORTED') badgeColor = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30";
                      else if (c.assessment_code === 'CONTRADICTED') badgeColor = "bg-rose-500/10 text-rose-400 border border-rose-500/30";
                      else if (c.assessment_code === 'DISPUTED') badgeColor = "bg-amber-500/10 text-amber-400 border border-amber-500/30";

                      return (
                        <div
                          key={c.claim_id}
                          onClick={() => setSelectedClaimIndex(idx)}
                          className={`p-4 rounded-xl border cursor-pointer space-y-2 transition-all ${
                            isSelected
                              ? 'bg-blue-950/20 border-blue-500/60 shadow-lg shadow-blue-500/10'
                              : 'bg-slate-900/70 hover:bg-slate-900 border-slate-800'
                          }`}
                        >
                          <div className="flex items-center justify-between text-[10px]">
                            <span className="font-mono text-blue-400 font-bold">{c.claim_id} • {c.topic}</span>
                            <span className={`px-2 py-0.5 rounded font-bold uppercase ${badgeColor}`}>
                              {c.assessment}
                            </span>
                          </div>

                          <p className="text-xs font-semibold text-slate-200 line-clamp-2">
                            "{c.claim}"
                          </p>

                          <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
                            <span>{c.evidence_records?.length || 0} Evidence Passages</span>
                            <span className="text-blue-400 flex items-center gap-1 font-bold">
                              <span>Inspect Passages</span>
                              <ArrowRight className="w-3 h-3" />
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Evidence Passages & Citations (7 Cols) */}
                <div className="lg:col-span-7 space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Evidence Passages & Citation Grounding
                  </h4>

                  {currentClaim && (
                    <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
                      
                      {/* Claim Header */}
                      <div className="space-y-2 border-b border-slate-800 pb-4">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono text-slate-400">REF: {currentClaim.claim_id}</span>
                          <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border uppercase ${
                            currentClaim.assessment_code === 'SUPPORTED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                            currentClaim.assessment_code === 'CONTRADICTED' ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' :
                            'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          }`}>
                            {currentClaim.assessment}
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-white leading-relaxed">
                          "{currentClaim.claim}"
                        </h4>
                        <p className="text-xs text-slate-300 leading-relaxed">
                          {currentClaim.explanation}
                        </p>
                      </div>

                      {/* Missing Context Warnings */}
                      {currentClaim.missing_context && currentClaim.missing_context.length > 0 && (
                        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 space-y-1">
                          <span className="font-bold flex items-center gap-1 text-[11px] uppercase">
                            <AlertTriangle className="w-3 h-3" /> Context Limitations
                          </span>
                          <ul className="list-disc list-inside text-[11px] text-amber-200/90 space-y-0.5">
                            {currentClaim.missing_context.map((m, i) => (
                              <li key={i}>{m}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Retrieved Passages */}
                      <div className="space-y-3">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                          <BookOpen className="w-3.5 h-3.5 text-blue-400" />
                          <span>Retrieved Evidence Records ({currentClaim.evidence_records?.length || 0})</span>
                        </span>

                        {currentClaim.evidence_records?.length > 0 ? (
                          <div className="space-y-2.5">
                            {currentClaim.evidence_records.map(ev => {
                              const isSupport = ev.relationship === 'supports';
                              const isContradict = ev.relationship === 'contradicts';
                              return (
                                <div key={ev.id} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                                  <div className="flex items-center justify-between gap-2">
                                    <span className="font-bold text-slate-200 text-xs">{ev.source_title}</span>
                                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono uppercase ${
                                      isSupport ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                                      isContradict ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                                      'bg-slate-800 text-slate-300 border border-slate-700'
                                    }`}>
                                      {ev.relationship?.replace('_', ' ')}
                                    </span>
                                  </div>
                                  <p className="text-xs text-slate-300 leading-relaxed italic">
                                    "{ev.excerpt}"
                                  </p>
                                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                                    <span>Publisher: {ev.publisher}</span>
                                    {ev.url && (
                                      <a
                                        href={ev.url}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1"
                                      >
                                        <span>Open Source</span>
                                        <ExternalLink className="w-3 h-3" />
                                      </a>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center text-xs text-slate-500">
                            No external evidence records located matching this specific subclaim.
                          </div>
                        )}
                      </div>

                    </div>
                  )}

                </div>

              </div>

            </div>
          )}

        </div>
      )}

      {/* ============================================================
          TAB 2: CLAIM RELATIONSHIP GRAPH
         ============================================================ */}
      {activeTab === 'graph' && (
        <div className="space-y-4">
          <InteractiveClaimGraph graphData={graphData} />
        </div>
      )}

      {/* ============================================================
          TAB 3: FACT-CHECK ARCHIVE SEARCH
         ============================================================ */}
      {activeTab === 'factcheck' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-200 flex items-center gap-2">
                <CheckSquare className="w-4 h-4 text-purple-400" />
                <span>Search Prior Fact-Checking Investigations & Certified Debunks</span>
              </label>
              <span className="text-[10px] text-slate-400 font-mono">
                Google Fact Check API • GDELT Wire • Alt News • BOOM Live
              </span>
            </div>

            <form onSubmit={handleFactCheckSearch} className="flex gap-2.5">
              <input
                type="text"
                value={fcQuery}
                onChange={(e) => setFcQuery(e.target.value)}
                placeholder="Search previously evaluated claim, e.g. 'miracle lemon cure for cancer'..."
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500 font-sans"
              />
              <button
                type="submit"
                disabled={isSearchingFc || !fcQuery.trim()}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-purple-600 hover:bg-purple-500 text-white flex items-center gap-2 transition-all disabled:opacity-50 shrink-0"
              >
                {isSearchingFc ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                <span>Search Archive</span>
              </button>
            </form>
          </div>

          {/* Results Grid */}
          {fcResults && (
            <div className="space-y-4 animate-fadeIn">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>{fcResults.message}</span>
                <span className="font-mono text-[10px]">Query: "{fcResults.query}"</span>
              </div>

              {fcResults.results?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {fcResults.results.map(item => (
                    <div key={item.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 flex flex-col justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono text-purple-400 font-bold uppercase">{item.publisher}</span>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-mono uppercase">
                            {item.rating}
                          </span>
                        </div>
                        <h4 className="text-xs font-bold text-white leading-relaxed">
                          "{item.claim_reviewed}"
                        </h4>
                      </div>

                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400">
                        <span>Provider: {item.source_provider}</span>
                        {item.url && (
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-purple-400 hover:text-purple-300 font-bold flex items-center gap-1"
                          >
                            <span>Read Debunk</span>
                            <ExternalLink className="w-2.5 h-2.5" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center space-y-2">
                  <p className="text-xs font-bold text-slate-300">No Prior Fact-Checks Located</p>
                  <p className="text-[11px] text-slate-500 max-w-sm mx-auto">
                    No certified fact-checking report was found matching this claim in the public archives. This assertion may be unexamined or novel.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

    </div>
  );
};
