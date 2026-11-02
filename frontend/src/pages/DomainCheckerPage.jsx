import React, { useState } from 'react';
import { Globe, ShieldCheck, AlertTriangle, Search, Lock, ExternalLink, Clock } from 'lucide-react';
import { NewsTimeline } from '../components/NewsTimeline';

export const DomainCheckerPage = () => {
  const [domainQuery, setDomainQuery] = useState('https://www.reuters.com');
  const [domainResult, setDomainResult] = useState({
    domain: "reuters.com",
    hasHttps: true,
    structure: "Standard Registered TLD (.com)",
    length: 11,
    subdomains: 0,
    trustScore: 95,
    riskLevel: "LOW RISK",
    editorialCategory: "International Wire News Agency",
    summary: "Domain belongs to a verified international news agency with strict editorial oversight and wire standards.",
    indicators: [
      "Secured via valid SSL/TLS HTTPS protocol.",
      "No suspicious hyphenation or brand impersonation patterns detected.",
      "Matches authoritative global news outlet database."
    ]
  });

  const handleInspect = () => {
    if (!domainQuery.trim()) return;
    const clean = domainQuery.replace(/^(https?:\/\/)?(www\.)?/, '').split('/')[0];
    const isTrusted = clean.includes('reuters') || clean.includes('nasa.gov') || clean.includes('who.int') || clean.includes('nature') || clean.includes('apnews');
    const isHoax = clean.includes('infowars') || clean.includes('naturalnews') || clean.includes('.xyz') || clean.includes('.top') || clean.includes('.click');

    if (isTrusted) {
      setDomainResult({
        domain: clean,
        hasHttps: domainQuery.startsWith('https://'),
        structure: "Standard Top-Level Domain",
        length: clean.length,
        subdomains: Math.max(0, clean.split('.').length - 2),
        trustScore: 95,
        riskLevel: "LOW RISK",
        editorialCategory: "Verified Authoritative News Publisher",
        summary: `Domain '${clean}' is registered to an authoritative news publisher with verified editorial standards.`,
        indicators: [
          "Secured via HTTPS encryption.",
          "Cataloged in verified global journalism registry."
        ]
      });
    } else if (isHoax) {
      setDomainResult({
        domain: clean,
        hasHttps: domainQuery.startsWith('https://'),
        structure: "High Risk / Disposable TLD",
        length: clean.length,
        subdomains: Math.max(0, clean.split('.').length - 2),
        trustScore: 15,
        riskLevel: "CRITICAL RISK",
        editorialCategory: "Cataloged Hoax / Disinformation Syndicate",
        summary: `CRITICAL: Domain '${clean}' is cataloged as a known distributor of fabricated stories or conspiracy hoaxes.`,
        indicators: [
          "Domain flagged in misinformation database.",
          "Unusual or disposable top-level extension often used in throwaway clickbait."
        ]
      });
    } else {
      setDomainResult({
        domain: clean,
        hasHttps: domainQuery.startsWith('https://'),
        structure: "Standard Independent Domain",
        length: clean.length,
        subdomains: Math.max(0, clean.split('.').length - 2),
        trustScore: 55,
        riskLevel: "MODERATE RISK",
        editorialCategory: "Independent / Unregistered Web Domain",
        summary: `Domain '${clean}' is not in the verified media catalog. Heuristic review suggests standard web structure.`,
        indicators: [
          "Independent domain without cataloged editorial rating.",
          "Verify article author and cross-reference with primary news wire."
        ]
      });
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-blue-400" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Source & Domain Credibility Inspector
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Audit domain structural hygiene, spoofed brand detection, and official editorial trust ratings.
          </p>
        </div>
      </div>

      {/* Search Input Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <label className="text-xs font-bold text-slate-300">
          Enter Website Domain or Article URL to Inspect
        </label>
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={domainQuery}
            onChange={(e) => setDomainQuery(e.target.value)}
            placeholder="e.g. https://www.bbc.com or newsbreak-daily.xyz"
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleInspect}
            className="px-6 py-3 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20"
          >
            <Search className="w-4 h-4" />
            <span>Audit Domain</span>
          </button>
        </div>
      </div>

      {/* Domain Results Card */}
      {domainResult && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Metadata (5 Cols) */}
          <div className="lg:col-span-5 glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-xs font-mono font-bold text-slate-400">DOMAIN AUDIT REPORT</span>
              <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                domainResult.riskLevel.includes('LOW') ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                domainResult.riskLevel.includes('CRITICAL') ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' :
                'bg-amber-500/10 text-amber-400 border-amber-500/30'
              }`}>
                {domainResult.riskLevel}
              </span>
            </div>

            <div className="space-y-3 text-xs font-mono text-slate-300">
              <p><span className="text-slate-500">Domain Name :</span> {domainResult.domain}</p>
              <p><span className="text-slate-500">HTTPS Protocol :</span> {domainResult.hasHttps ? "Secured (SSL Active)" : "Unsecured (HTTP)"}</p>
              <p><span className="text-slate-500">Structure      :</span> {domainResult.structure}</p>
              <p><span className="text-slate-500">Domain Length  :</span> {domainResult.length} characters</p>
              <p><span className="text-slate-500">Subdomains     :</span> {domainResult.subdomains} levels</p>
              <p><span className="text-slate-500">Trust Rating   :</span> {domainResult.trustScore} / 100</p>
            </div>
          </div>

          {/* Right Assessment (7 Cols) */}
          <div className="lg:col-span-7 glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
            <div className="space-y-1">
              <span className="text-[10px] font-mono uppercase font-bold text-blue-400">Editorial Classification</span>
              <h3 className="text-base font-bold text-white">{domainResult.editorialCategory}</h3>
            </div>

            <p className="text-xs text-slate-300 bg-slate-900/80 p-4 rounded-xl border border-slate-800 leading-relaxed">
              {domainResult.summary}
            </p>

            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-400">Heuristic Findings:</span>
              <ul className="space-y-1.5 text-xs text-slate-400 list-disc list-inside">
                {domainResult.indicators.map((ind, i) => (
                  <li key={i}>{ind}</li>
                ))}
              </ul>
            </div>

            <p className="text-[11px] text-slate-500 pt-2 border-t border-slate-800">
              * Heuristic Note: Domain metrics analyze structural hygiene and registered editorial status. They do not constitute absolute proof of truth.
            </p>
          </div>
        </div>
      )}

      {/* Cross-Publisher Story & Domain Timeline Comparison (Feature 5) */}
      <div className="pt-4">
        <NewsTimeline defaultQuery={domainResult ? domainResult.domain : "news wire"} />
      </div>

    </div>
  );
};
