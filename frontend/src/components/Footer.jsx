import React from 'react';
import { ShieldCheck, Heart, Github, Cpu, Cloud, Terminal } from 'lucide-react';

export const Footer = ({ setActivePage }) => {
  return (
    <footer className="glass-panel border-t border-slate-800/80 mt-20 pt-12 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          
          {/* Brand Info */}
          <div className="md:col-span-1 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <span className="font-bold text-lg text-white tracking-tight">VERITAS AI</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Enterprise AI & Machine Learning platform for detecting synthetic misinformation, deceptive claims, and linguistic manipulation patterns.
            </p>
            <div className="flex items-center gap-2 pt-2 text-xs text-blue-400 font-mono">
              <Terminal className="w-3.5 h-3.5" />
              <span>v2.5.0-ENTERPRISE-PRO</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs uppercase font-bold text-slate-300 tracking-wider mb-3">Intelligence Suite</h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li><button onClick={() => setActivePage('scanner')} className="hover:text-blue-400">Live AI Scanner</button></li>
              <li><button onClick={() => setActivePage('claims')} className="hover:text-blue-400">Claim Extraction Matrix</button></li>
              <li><button onClick={() => setActivePage('domain')} className="hover:text-blue-400">Source & Domain Intel</button></li>
              <li><button onClick={() => setActivePage('dashboard')} className="hover:text-blue-400">Analytics & Trend Radar</button></li>
            </ul>
          </div>

          {/* Machine Learning Architecture */}
          <div>
            <h4 className="text-xs uppercase font-bold text-slate-300 tracking-wider mb-3">AI & ML Architecture</h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li><button onClick={() => setActivePage('model')} className="hover:text-blue-400">Model Studio & Confusion Matrix</button></li>
              <li><span className="text-slate-500">TF-IDF N-Gram Vectorizer</span></li>
              <li><span className="text-slate-500">Random Forest & Naive Bayes</span></li>
              <li><span className="text-slate-500">Flesch-Kincaid Readability</span></li>
            </ul>
          </div>

          {/* Minor College Project & Cloud Info */}
          <div>
            <h4 className="text-xs uppercase font-bold text-slate-300 tracking-wider mb-3">College Minor Project</h4>
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 text-xs text-slate-400 space-y-2">
              <p className="font-semibold text-slate-200">
                “Fake AI News Detection Using Machine Learning & Cloud Computing”
              </p>
              <div className="flex items-center gap-2 text-[11px] text-emerald-400 font-medium">
                <Cloud className="w-3.5 h-3.5" />
                <span>Docker & Cloud Deployment Ready</span>
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer & Bottom Bar */}
        <div className="border-t border-slate-800/80 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>
            * Legal & Research Disclaimer: Machine learning outputs and linguistic indicators are heuristic analytical assessments and do not constitute legal or absolute proof of truth.
          </p>
          <p className="flex items-center gap-1 font-medium text-slate-400 whitespace-nowrap">
            Built for Academic Research & Enterprise Intelligence
          </p>
        </div>
      </div>
    </footer>
  );
};
