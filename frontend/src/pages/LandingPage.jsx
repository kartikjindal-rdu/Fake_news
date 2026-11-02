import React from 'react';
import { 
  ShieldCheck, Cpu, ArrowRight, Zap, CheckCircle, Search, 
  FileText, Globe, Sparkles, Layers, Terminal, AlertTriangle, 
  Eye, Lock, Database, RefreshCw, BarChart3, LineChart, Network,
  Radio
} from 'lucide-react';
import { LiveNewsFeed } from '../components/LiveNewsFeed';

export const LandingPage = ({ setActivePage, onAnalyzeArticle }) => {
  const handleSelectFeedArticle = (articlePayload) => {
    if (onAnalyzeArticle) {
      onAnalyzeArticle(articlePayload);
    } else {
      setActivePage('scanner');
    }
  };
  const features = [
    {
      icon: Cpu,
      title: "AI Fake News Detection",
      desc: "Multinomial Naive Bayes and Random Forest ensemble classifiers trained on multi-domain political, health, and science news.",
      tag: "ML Core"
    },
    {
      icon: Eye,
      title: "Explainable AI Forensic Layer",
      desc: "Transparent reasoning breakdowns that explain exactly why a document was flagged without heuristic opacity.",
      tag: "XAI"
    },
    {
      icon: Search,
      title: "Automated Claim Extraction",
      desc: "Parses core factual assertions and maps them against empirical evidence repositories and fact-checking indexes.",
      tag: "Claims"
    },
    {
      icon: Globe,
      title: "Source & Domain Intelligence",
      desc: "Heuristic domain structure inspection, HTTPS verification, spoofed naming detection, and verified publisher registry.",
      tag: "Reputation"
    },
    {
      icon: Zap,
      title: "Clickbait & Curiosity Gap Radar",
      desc: "Identifies deceptive headline syntax, listicle hooks, and capitalization ratios engineered to manufacture viral clicks.",
      tag: "Clickbait"
    },
    {
      icon: AlertTriangle,
      title: "Emotional Manipulation Analysis",
      desc: "Detects fear-mongering, outrage triggers, artificial panic, and extreme hyperbole in textual narrative structure.",
      tag: "Sentiment"
    },
    {
      icon: FileText,
      title: "Screenshot OCR Analysis",
      desc: "Upload screenshots from messaging apps or social media; extracts text via OCR pipeline for instant verification.",
      tag: "OCR"
    },
    {
      icon: Network,
      title: "Cross-Source Evidence Graph",
      desc: "Visualizes convergence and contradictions across wire agencies, peer-reviewed journals, and unverified blogs.",
      tag: "Graph"
    },
    {
      icon: Layers,
      title: "10-Factor Scoring Architecture",
      desc: "Composite metrics including credibility score, language risk, source trust, sensationalism index, and readability.",
      tag: "Metrics"
    },
    {
      icon: Database,
      title: "Persistent Audit & Scan History",
      desc: "SQLite/PostgreSQL backed session log with search, filters, sorting, and one-click forensic CSV/JSON report exports.",
      tag: "Database"
    },
    {
      icon: BarChart3,
      title: "Intelligence Analytics Radar",
      desc: "Interactive Recharts data visualizations showing daily scanning volume, threat distributions, and trigger frequencies.",
      tag: "Analytics"
    },
    {
      icon: Terminal,
      title: "Cloud-Native REST & Mobile API",
      desc: "FastAPI headless endpoints ready for plug-and-play integration into Android apps or cloud microservices.",
      tag: "Cloud"
    }
  ];

  const pipeline = [
    { num: "01", title: "INPUT NEWS", desc: "Headline, body text, source URL, or uploaded screenshot." },
    { num: "02", title: "NLP & TOKENIZATION", desc: "Porter stemming, stopword purging, and n-gram extraction." },
    { num: "03", title: "ML CLASSIFICATION", desc: "TF-IDF log-probabilities calculated via Scikit-learn models." },
    { num: "04", title: "HEURISTIC AUDIT", desc: "Clickbait, sensationalism, emotion & domain reputation scores." },
    { num: "05", title: "EXPLAINABLE SYNTHESIS", desc: "Risk level, claim verification matrix, and forensic report." }
  ];

  return (
    <div className="space-y-24 pb-20">
      
      {/* Hero Section */}
      <section className="relative pt-12 pb-8 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          
          {/* Top Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold shadow-sm animate-pulse">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Next-Generation AI Misinformation Intelligence</span>
          </div>

          {/* Main Hero Heading */}
          <div className="max-w-4xl mx-auto space-y-4">
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-[1.1]">
              Verify Before <br />
              <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-emerald-400 bg-clip-text text-transparent">
                You Believe.
              </span>
            </h1>
            <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
              AI-powered misinformation intelligence that analyzes suspicious news, detects linguistic manipulation patterns, evaluates source credibility signals, and empowers investigators before content is shared.
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <button
              onClick={() => setActivePage('scanner')}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl text-sm font-bold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-xl shadow-blue-500/25 flex items-center justify-center gap-2 transition-all transform hover:-translate-y-0.5"
            >
              <span>⚡ Start Live AI Scanner</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => setActivePage('dashboard')}
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl text-sm font-semibold bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-slate-700 transition-all"
            >
              📊 View Intelligence Dashboard
            </button>
          </div>

          {/* Hero Intelligence Visualization Preview */}
          <div className="pt-8 max-w-5xl mx-auto">
            <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-slate-800 shadow-2xl space-y-4 text-left">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  <span className="text-xs text-slate-400 font-mono ml-2">VERITAS_AI_CORE_INFERENCE // LIVE SESSION</span>
                </div>
                <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  ● SYSTEM READY
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs text-slate-300">
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <p className="text-slate-500 text-[10px]">PREDICTIVE CLASSIFIER</p>
                  <p className="font-bold text-white text-sm">3-Model Ensemble (LR+SVM+RF)</p>
                  <p className="text-emerald-400 text-[11px] mt-1">99.2% ISOT Test Accuracy (8,980 Split)</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <p className="text-slate-500 text-[10px]">ANALYSIS DIMENSIONS</p>
                  <p className="font-bold text-white text-sm">10-Factor Multi-Score</p>
                  <p className="text-blue-400 text-[11px] mt-1">Linguistic + XAI Engine</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <p className="text-slate-500 text-[10px]">DATABASE AUDIT</p>
                  <p className="font-bold text-white text-sm">SQLite & PostgreSQL</p>
                  <p className="text-indigo-400 text-[11px] mt-1">Persistent Forensic Log</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Live News Intelligence Feed Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                <Radio className="w-3.5 h-3.5 animate-pulse" />
              </div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
                Live Global & Indian News Wire
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Real-time dispatches from The Hindu, NDTV, BBC, WHO, NPR, UN News, and GDELT DOC 2.0. Select any story to analyze instantly in the scanner.
            </p>
          </div>
          <button
            onClick={() => setActivePage('scanner')}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 flex items-center gap-1.5 transition-all"
          >
            <span>Open Custom Scanner</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800/80">
          <LiveNewsFeed
            onSelectArticle={handleSelectFeedArticle}
            isScanning={false}
          />
        </div>
      </section>

      {/* How It Works Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-widest text-blue-400">Analysis Pipeline</h2>
          <h3 className="text-3xl sm:text-4xl font-extrabold text-white">How Veritas AI Analyzes News</h3>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            From raw claims to explainable forensic intelligence through an orchestrated 5-stage pipeline.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {pipeline.map((step, idx) => (
            <div key={idx} className="glass-panel p-5 rounded-2xl border border-slate-800 relative space-y-3 glass-card-hover">
              <span className="text-2xl font-black text-blue-500/40 font-mono">{step.num}</span>
              <h4 className="text-sm font-bold text-white tracking-wide">{step.title}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features Grid Section (12 Large Cards) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-widest text-emerald-400">Platform Capabilities</h2>
          <h3 className="text-3xl sm:text-4xl font-extrabold text-white">Enterprise Intelligence Capabilities</h3>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            Engineered with modern Natural Language Processing and Scikit-Learn machine learning algorithms.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div 
                key={idx} 
                onClick={() => setActivePage('scanner')}
                className="glass-panel p-6 rounded-2xl border border-slate-800/80 glass-card-hover cursor-pointer space-y-4"
              >
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    {feat.tag}
                  </span>
                </div>
                <div className="space-y-1.5">
                  <h4 className="text-base font-bold text-slate-100">{feat.title}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">{feat.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* College Minor Project Showcase Box */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 rounded-3xl bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-slate-900/60 border border-blue-500/30 text-center space-y-4 shadow-2xl">
          <span className="text-xs font-bold uppercase tracking-widest text-blue-400 font-mono">
            ACADEMIC & EVALUATION READY
          </span>
          <h3 className="text-2xl sm:text-3xl font-bold text-white">
            “Fake AI News Detection Using Machine Learning and Cloud Computing”
          </h3>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Full-stack demonstration system featuring Scikit-Learn TF-IDF vectorizers, confusion matrices, SQLite/PostgreSQL persistence, and Dockerized cloud architecture.
          </p>
          <div className="pt-2">
            <button
              onClick={() => setActivePage('model')}
              className="px-6 py-2.5 rounded-xl text-xs font-bold bg-white text-slate-900 hover:bg-slate-100 shadow-lg transition-transform hover:scale-105"
            >
              Explore Model Studio & Confusion Matrix
            </button>
          </div>
        </div>
      </section>

    </div>
  );
};
