import React, { useState, useEffect } from 'react';
import { 
  Scan, Globe, Image as ImageIcon, Sparkles, Trash2, Copy, 
  Download, ExternalLink, ShieldCheck, AlertTriangle, AlertOctagon,
  FileText, CheckCircle2, RefreshCw, Upload, Eye, Layers, Network, Clock, Radio, ChevronDown, ChevronUp
} from 'lucide-react';
import { RISK_LEVELS } from '../utils/constants';
import { performClientAnalysis, api } from '../services/api';
import { CircularGauge } from '../components/CircularGauge';
import { RiskMeter } from '../components/RiskMeter';
import { ScoreCard } from '../components/ScoreCard';
import { TextHighlighter } from '../components/TextHighlighter';
import { PipelineModal } from '../components/PipelineModal';
import { EvidenceGraph } from '../components/EvidenceGraph';
import { NewsTimeline } from '../components/NewsTimeline';
import { LiveNewsFeed } from '../components/LiveNewsFeed';

export const ScannerPage = ({ initialPayload, onClearInitialPayload }) => {
  // Input State
  const [inputTab, setInputTab] = useState('text'); // 'text' | 'url' | 'image'
  const [headline, setHeadline] = useState('');
  const [content, setContent] = useState('');
  const [url, setUrl] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageMetadata, setImageMetadata] = useState(null);
  const [showAdvancedFields, setShowAdvancedFields] = useState(false);

  // Live News Stream State
  const [feedExpanded, setFeedExpanded] = useState(true);
  const [selectedArticleId, setSelectedArticleId] = useState(null);
  const [activeArticleMeta, setActiveArticleMeta] = useState(null);

  // Load article if passed from Landing Page
  useEffect(() => {
    if (initialPayload) {
      setInputTab('text');
      setHeadline(initialPayload.headline || '');
      setContent(initialPayload.content || '');
      setUrl(initialPayload.url || '');
      setActiveArticleMeta({
        publisher: initialPayload.publisher,
        has_full_text: initialPayload.has_full_text,
        extraction_note: initialPayload.extraction_note,
        article_id: initialPayload.article_id,
      });
      setSelectedArticleId(initialPayload.article_id);
      if (onClearInitialPayload) onClearInitialPayload();
    }
  }, [initialPayload]);

  // Pipeline modal & result state
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [scanError, setScanError] = useState(null);
  const [activeResultTab, setActiveResultTab] = useState('highlights'); // 'highlights' | 'claims' | 'explain' | 'ml' | 'evidence' | 'graph' | 'timeline'
  const [copySuccess, setCopySuccess] = useState(false);

  // Word & Char counts
  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
  const charCount = content.length;

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const objUrl = URL.createObjectURL(file);
      setImagePreview(objUrl);

      // Extract genuine image file metadata
      const img = new Image();
      img.onload = () => {
        setImageMetadata({
          name: file.name,
          sizeKb: (file.size / 1024).toFixed(1),
          type: file.type || 'image/unknown',
          lastModified: new Date(file.lastModified).toLocaleString(),
          width: img.naturalWidth || img.width,
          height: img.naturalHeight || img.height,
        });
      };
      img.src = objUrl;

      // Provide editable OCR text template based on genuine file name
      if (!content.trim()) {
        setContent(`[Screenshot from ${file.name}]: Transcribe or verify the headline/claim here before scanning...`);
      }
    }
  };

  const handleStartScan = () => {
    // Validate that required input is provided
    if (inputTab === 'url') {
      if (!url.trim()) {
        setScanError("Please enter an article URL to analyze.");
        return;
      }
    } else {
      const textToAnalyze = `${headline || ''} ${content || ''}`.trim();
      if (!textToAnalyze && !imageFile) {
        setScanError("Please paste or type news text into the textarea to analyze.");
        return;
      }
    }
    setScanError(null);
    setResult(null);
    setIsScanning(true);
  };

  const handlePipelineComplete = async () => {
    setIsScanning(false);
    setScanError(null);
    try {
      let scanOutput;
      if (inputTab === 'url' && url) {
        // URL tab: send to /api/analyze/url
        scanOutput = await api.analyzeUrl(url);
      } else {
        // Text / Image tab: send to /api/analyze/text with multi-channel provenance
        scanOutput = await api.analyzeText({
          headline,
          content,
          url,
          publisher: activeArticleMeta?.publisher,
          source_type: activeArticleMeta?.source_type,
          content_availability: activeArticleMeta?.content_availability,
        });
      }
      setResult(scanOutput);
      // Save to localStorage history
      try {
        const existing = JSON.parse(localStorage.getItem('veritas_scan_history') || '[]');
        const updated = [scanOutput, ...existing].slice(0, 50);
        localStorage.setItem('veritas_scan_history', JSON.stringify(updated));
      } catch (_) {}
    } catch (err) {
      setScanError('Analysis failed. The backend may be offline or returned an unexpected error.');
    }
  };

  const handleClear = () => {
    setHeadline('');
    setContent('');
    setUrl('');
    setImageFile(null);
    setImagePreview(null);
    setResult(null);
    setScanError(null);
    setSelectedArticleId(null);
    setActiveArticleMeta(null);
  };

  const handleSelectLiveArticle = (payload) => {
    setHeadline(payload.headline || '');
    setContent(payload.content || '');
    setUrl(payload.url || '');
    setActiveArticleMeta({
      publisher: payload.publisher,
      has_full_text: payload.has_full_text,
      extraction_note: payload.extraction_note,
      article_id: payload.article_id,
      source_type: payload.source_type,
      content_availability: payload.content_availability,
    });
    setSelectedArticleId(payload.article_id);
    setInputTab('text');
    setScanError(null);
    setResult(null);
    setIsScanning(true);
  };

  const handleCopyReport = () => {
    if (!result) return;
    const textReport = `=======================================================
VERITAS AI FORENSIC ANALYSIS REPORT
Scan ID: ${result.scanId}
Timestamp: ${result.timestamp}
Verdict: ${result.verdict}
Risk Score: ${result.scores.riskScore}/100 (${result.riskLevel.label})
Confidence: ${result.scores.aiConfidence}%
Fake Probability: ${result.scores.fakeProbability}%
Fact Likelihood: ${result.scores.realProbability}%
Sensationalism Score: ${result.scores.sensationalismScore}%
Clickbait Index: ${result.scores.clickbaitScore}%
Emotional Bias: ${result.scores.emotionalManipulationScore}% (${result.linguistic.emotionalTone})
Recommendation: ${result.recommendedAction}
=======================================================`;
    navigator.clipboard.writeText(textReport);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const handleDownloadJson = () => {
    if (!result) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `veritas_report_${result.scanId}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Scan className="w-5 h-5 text-blue-400" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Live AI Misinformation Scanner
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Analyze news text, verify URLs, and extract screenshot OCR claims through our 10-tier forensic engine.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
            ● Model Inference Active
          </span>
        </div>
      </div>

      {/* =========================================
          LIVE NEWS STREAM SECTION (Open-Access Feeds)
         ========================================= */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Radio className="w-4 h-4 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-black uppercase tracking-wider text-white">
                  Real-Time Verified News Feed
                </h2>
                <span className="text-[10px] font-mono font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20 hidden sm:inline-block">
                  Open Publisher Feeds
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Browse and analyze live articles directly from BBC News, WHO, NPR, UN News, and GDELT DOC 2.0
              </p>
            </div>
          </div>

          <button
            onClick={() => setFeedExpanded(!feedExpanded)}
            className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 flex items-center gap-1.5 transition-all"
          >
            {feedExpanded ? (
              <>
                <span>Collapse Stream</span>
                <ChevronUp className="w-3.5 h-3.5" />
              </>
            ) : (
              <>
                <span>Expand Live Stream</span>
                <ChevronDown className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

        {feedExpanded && (
          <div className="pt-2">
            <LiveNewsFeed
              onSelectArticle={handleSelectLiveArticle}
              selectedArticleId={selectedArticleId}
              isScanning={isScanning}
            />
          </div>
        )}
      </div>

      {/* Main Grid Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* =========================================
            LEFT INPUT PANEL (5 Cols)
           ========================================= */}
        <div className="lg:col-span-5 glass-panel p-5 rounded-2xl border border-slate-800 space-y-5">
          
          {/* Input Mode Tabs */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setInputTab('text')}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  inputTab === 'text' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                📝 News Text
              </button>
              <button
                onClick={() => setInputTab('url')}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  inputTab === 'url' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                🌐 Article URL
              </button>
              <button
                onClick={() => setInputTab('image')}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  inputTab === 'image' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                📷 Screenshot OCR
              </button>
            </div>

            <button
              onClick={handleClear}
              className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 p-1.5"
              title="Clear all inputs"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          </div>

          {/* Active Article Metadata Banner if loaded from Live Feed */}
          {activeArticleMeta && (
            <div className={`p-3 rounded-xl border text-xs space-y-1.5 animate-fadeIn ${
              activeArticleMeta.has_full_text
                ? 'bg-blue-500/10 border-blue-500/30 text-blue-200'
                : 'bg-amber-500/10 border-amber-500/30 text-amber-200'
            }`}>
              <div className="flex items-center justify-between">
                <span className="font-bold flex items-center gap-1.5">
                  {activeArticleMeta.source_type === 'youtube'
                    ? (activeArticleMeta.has_full_text ? '🎬 Official Spoken Transcript Loaded' : '⚠️ YouTube Video Metadata Evaluation')
                    : (activeArticleMeta.has_full_text ? '📄 Full Article Body Loaded' : '⚠️ Headline & Excerpt Analysis')}
                </span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800">
                  {activeArticleMeta.publisher || 'Live Feed'}
                </span>
              </div>
              {!activeArticleMeta.has_full_text && (
                <p className="text-[11px] text-amber-300/90 leading-relaxed">
                  {activeArticleMeta.source_type === 'youtube'
                    ? "Video broadcast captions were disabled or unavailable. Evaluation is running on the official video title and publisher description. You can paste spoken dialogue directly in the text area below."
                    : "Publisher restricted automated full-body scraping. Analysis evaluates the headline and available summary. You may paste the complete article body in the text area below."}
                </p>
              )}
            </div>
          )}

          {/* TAB 1: TEXT INPUT (Primary Input) */}
          {inputTab === 'text' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-blue-400" />
                    <span>News Article / Claim Statement</span>
                  </label>
                  <span className="text-[11px] text-slate-500 font-mono">
                    {wordCount} words • {charCount} chars
                  </span>
                </div>
                <textarea
                  rows={9}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Paste any news article, headline, social media post, or claim here to analyze…"
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 leading-relaxed resize-y font-normal"
                />
              </div>

              {/* Optional Advanced Fields: Separate Headline & Source URL */}
              <div className="pt-1">
                <button
                  type="button"
                  onClick={() => setShowAdvancedFields(!showAdvancedFields)}
                  className="text-[11px] text-slate-400 hover:text-slate-300 font-semibold flex items-center gap-1 transition-colors"
                >
                  <span>{showAdvancedFields ? '▾ Hide optional headline & source URL' : '▸ Add optional separate headline / source URL'}</span>
                </button>

                {showAdvancedFields && (
                  <div className="space-y-3 pt-2.5 animate-fadeIn">
                    <div className="space-y-1">
                      <label className="text-[11px] font-bold text-slate-400">
                        Headline / Title (Optional)
                      </label>
                      <input
                        type="text"
                        value={headline}
                        onChange={(e) => setHeadline(e.target.value)}
                        placeholder="Optional separate headline..."
                        className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="text-[11px] font-bold text-slate-400">
                        Source Website / Domain (Optional)
                      </label>
                      <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="e.g. https://www.bbc.com or reuters.com"
                        className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: URL INPUT */}
          {inputTab === 'url' && (
            <div className="space-y-4 py-2">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300">
                  Article Full Web URL
                </label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/news/article-headline"
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <p className="text-xs text-slate-400 leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                The scanner will evaluate domain heuristics, top-level domains, HTTPS protocol, and compare domain names against verified media catalogs.
              </p>
            </div>
          )}

          {/* TAB 3: IMAGE OCR UPLOAD & FORENSICS */}
          {inputTab === 'image' && (
            <div className="space-y-4 py-2">
              <label className="border-2 border-dashed border-slate-800 hover:border-blue-500/50 rounded-2xl p-6 flex flex-col items-center justify-center gap-3 cursor-pointer bg-slate-900/40 transition-colors block">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                  <Upload className="w-6 h-6" />
                </div>
                <div className="text-center space-y-1">
                  <p className="text-xs font-bold text-slate-200">
                    {imageFile ? imageFile.name : "Upload or drag news screenshot"}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Supports PNG, JPG, WEBP (WhatsApp / Twitter / Facebook screenshots)
                  </p>
                </div>
              </label>

              {imagePreview && (
                <div className="space-y-3">
                  <div className="rounded-xl overflow-hidden border border-slate-800 max-h-48 bg-slate-950">
                    <img src={imagePreview} alt="Screenshot Preview" className="w-full object-contain max-h-48" />
                  </div>

                  {/* Genuine Image File Metadata Table */}
                  {imageMetadata && (
                    <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2 text-xs">
                      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                        <span className="font-bold text-white text-[11px] uppercase tracking-wider">
                          Image Forensic Metadata
                        </span>
                        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          Genuine Exif/File Data
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-300">
                        <div>
                          <span className="text-slate-500">Dimensions: </span>
                          <span className="font-semibold text-slate-200">{imageMetadata.width} × {imageMetadata.height} px</span>
                        </div>
                        <div>
                          <span className="text-slate-500">File Size: </span>
                          <span className="font-semibold text-slate-200">{imageMetadata.sizeKb} KB</span>
                        </div>
                        <div>
                          <span className="text-slate-500">MIME Type: </span>
                          <span className="font-semibold text-slate-200">{imageMetadata.type}</span>
                        </div>
                        <div>
                          <span className="text-slate-500">Modified: </span>
                          <span className="font-semibold text-slate-200">{imageMetadata.lastModified}</span>
                        </div>
                      </div>
                      <p className="text-[10px] text-slate-400 pt-1 leading-normal border-t border-slate-800/60">
                        ℹ️ <strong>Social Media Metadata Note:</strong> Social messaging apps (WhatsApp, X/Twitter, Facebook, Telegram) automatically strip EXIF camera metadata to preserve sender privacy. The absence of camera EXIF does not indicate forgery.
                      </p>

                      {/* Manual Reverse Image Search Verification Links */}
                      <div className="pt-2 flex flex-wrap items-center gap-2">
                        <span className="text-[10px] font-bold text-slate-400">Reverse Image Search:</span>
                        <a
                          href="https://images.google.com/"
                          target="_blank"
                          rel="noreferrer"
                          className="text-[10px] font-bold text-blue-400 hover:text-blue-300 bg-blue-500/10 px-2.5 py-1 rounded border border-blue-500/20 flex items-center gap-1"
                        >
                          <span>Google Images</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                        <a
                          href="https://lens.google.com/uploadbyurl"
                          target="_blank"
                          rel="noreferrer"
                          className="text-[10px] font-bold text-blue-400 hover:text-blue-300 bg-blue-500/10 px-2.5 py-1 rounded border border-blue-500/20 flex items-center gap-1"
                        >
                          <span>Google Lens</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                        <a
                          href="https://tineye.com/"
                          target="_blank"
                          rel="noreferrer"
                          className="text-[10px] font-bold text-blue-400 hover:text-blue-300 bg-blue-500/10 px-2.5 py-1 rounded border border-blue-500/20 flex items-center gap-1"
                        >
                          <span>TinEye</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      </div>
                    </div>
                  )}

                  {/* Editable OCR Text Area */}
                  <div className="space-y-1.5 pt-1">
                    <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
                      <span>Editable Screenshot Text / Headline</span>
                      <span className="text-[10px] font-mono text-slate-500">Edit before scanning</span>
                    </label>
                    <textarea
                      rows={4}
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      placeholder="Transcribe or paste the headline/claim visible in the screenshot to verify..."
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 leading-relaxed font-normal"
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Validation Notice Banner if validation fails */}
          {scanError && !result && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 flex items-start gap-2.5 text-xs text-rose-300 animate-fadeIn">
              <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold">Input Required</p>
                <p className="text-[11px] text-rose-300/90 mt-0.5">{scanError}</p>
              </div>
            </div>
          )}

          {/* Action Buttons: Clear Text & Analyze News */}
          <div className="flex items-center gap-3 pt-1">
            <button
              type="button"
              onClick={handleClear}
              disabled={isScanning || (!content && !headline && !url && !imageFile)}
              className="px-4 py-3 rounded-xl text-xs font-bold bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 flex items-center justify-center gap-1.5 transition-all disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
              title="Clear all text inputs"
            >
              <Trash2 className="w-3.5 h-3.5 text-slate-400" />
              <span>Clear Text</span>
            </button>

            <button
              type="button"
              onClick={handleStartScan}
              disabled={isScanning || (inputTab === 'url' ? !url.trim() : (!content.trim() && !headline.trim() && !imageFile))}
              className="flex-1 py-3 rounded-xl text-xs sm:text-sm font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-blue-500/25 flex items-center justify-center gap-2 transition-all transform hover:-translate-y-0.5 disabled:opacity-50 disabled:transform-none disabled:cursor-not-allowed"
            >
              {isScanning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Analyzing News...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Analyze News</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* =========================================
            RIGHT RESULTS PANEL (7 Cols)
           ========================================= */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* Scan Error Banner */}
          {scanError && (
            <div className="glass-panel p-4 rounded-2xl border border-rose-500/30 bg-rose-500/5 flex items-start gap-3">
              <span className="text-rose-400 text-lg">⚠️</span>
              <div>
                <p className="text-xs font-bold text-rose-300">Scan Error</p>
                <p className="text-xs text-rose-400/80 mt-0.5">{scanError}</p>
              </div>
            </div>
          )}

          {!result ? (
            /* Empty State */
            <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mx-auto">
                <Scan className="w-7 h-7" />
              </div>
              <div className="space-y-1.5 max-w-sm mx-auto">
                <h3 className="text-base font-bold text-white">Awaiting News Input</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Paste any news article, headline, social media post, or claim on the left to execute comprehensive 10-tier forensic AI verification.
                </p>
              </div>
            </div>
          ) : (
            /* Analysis Results Active View */
            <div className="space-y-6 animate-fadeIn">
              
              {/* Verdict Banner Card */}
              <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
                
                {/* Top Verdict Row */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-mono font-bold tracking-wider text-slate-400">
                      FORENSIC VERDICT // ID: {result.scanId}
                    </span>
                    <div className="flex items-center gap-3">
                      <span className={`text-lg sm:text-xl font-black px-3.5 py-1 rounded-xl border ${result.riskLevel.badgeBg}`}>
                        {result.verdict}
                      </span>
                      {/* ML Prediction Badge */}
                      {result.mlPrediction?.available && (
                        <span className={`text-xs font-bold px-2.5 py-1 rounded-lg border ${
                          result.mlPrediction.final_prediction === 'FAKE'
                            ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        }`}>
                          🤖 ML: {result.mlPrediction.final_prediction}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Circular Confidence Gauge */}
                  <CircularGauge 
                    value={result.scores.aiConfidence} 
                    title="AI Confidence" 
                    color={result.riskLevel.color}
                  />
                </div>

                {/* Language Warning Banner */}
                {result.languageDetection && !result.languageDetection.is_ml_supported && (
                  <div className="flex items-start gap-3 p-3 rounded-xl bg-amber-500/8 border border-amber-500/25 text-xs text-amber-300">
                    <span className="text-base mt-0.5">⚠️</span>
                    <div>
                      <span className="font-bold">{result.languageDetection.detected_language} detected — </span>
                      {result.languageDetection.warning}
                    </div>
                  </div>
                )}

                {/* Live Feed Headline-Only Notice */}
                {activeArticleMeta && !activeArticleMeta.has_full_text && (
                  <div className="flex items-start gap-3 p-3 rounded-xl bg-blue-500/10 border border-blue-500/30 text-xs text-blue-200">
                    <span className="text-base mt-0.5">ℹ️</span>
                    <div>
                      <span className="font-bold">Live Stream Notice ({activeArticleMeta.publisher || 'Publisher'}): </span>
                      Full article body was restricted by the publisher. This forensic evaluation was conducted on the headline and available news excerpt.
                    </div>
                  </div>
                )}

                {/* 4-Tier Risk Meter */}
                <RiskMeter score={result.scores.riskScore} level={result.riskLevel.label} />
              </div>

              {/* 10-Factor Scorecards Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <ScoreCard title="Fake Probability" score={result.scores.fakeProbability} color="rose" description="Composite ML & heuristic risk probability" />
                <ScoreCard title="Credibility Probability" score={result.scores.realProbability} color="emerald" description="Composite likelihood of credible reporting" />
                <ScoreCard title="Credibility Score" score={result.scores.credibilityScore} color="blue" description="Source & textual credibility index" />
                <ScoreCard title="Sensationalism Score" score={result.scores.sensationalismScore} color="amber" description="Hyperbole & miraculous claims" />
                <ScoreCard title="Clickbait Index" score={result.scores.clickbaitScore} color="purple" description="Curiosity gap & caps ratios" />
                <ScoreCard title="Emotional Bias" score={result.scores.emotionalManipulationScore} color="rose" description={result.linguistic.emotionalTone} />
              </div>

              {/* Sub-Tab Navigation for Deep Forensic Dive */}
              <div className="glass-panel rounded-2xl border border-slate-800 p-6 space-y-5">
                
                <div className="flex items-center gap-2 border-b border-slate-800 pb-3 overflow-x-auto">
                  <button
                    onClick={() => setActiveResultTab('highlights')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                      activeResultTab === 'highlights' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    🖍️ Flagged Triggers
                  </button>
                  <button
                    onClick={() => setActiveResultTab('claims')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                      activeResultTab === 'claims' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    🎯 Claims Matrix
                  </button>
                  <button
                    onClick={() => setActiveResultTab('explain')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                      activeResultTab === 'explain' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    🧠 AI Rationale
                  </button>
                  {/* VeriNews 2.0 — ML Models Tab */}
                  <button
                    onClick={() => setActiveResultTab('ml')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                      activeResultTab === 'ml' ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    🤖 ML Models
                  </button>
                  {/* VeriNews 2.0 — Evidence Tab */}
                  <button
                    onClick={() => setActiveResultTab('evidence')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                      activeResultTab === 'evidence' ? 'bg-teal-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    📰 Evidence
                  </button>
                  <button
                    onClick={() => setActiveResultTab('graph')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                      activeResultTab === 'graph' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    🕸️ Evidence Graph
                  </button>
                  <button
                    onClick={() => setActiveResultTab('timeline')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                      activeResultTab === 'timeline' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    ⏳ Story Timeline
                  </button>
                </div>

                {/* Sub-tab Content 1: Highlights */}
                {activeResultTab === 'highlights' && (
                  <TextHighlighter 
                    text={`${headline}\n\n${content}`} 
                    highlights={result.highlightedTriggers} 
                  />
                )}

                {/* Sub-tab Content 2: Claims Matrix */}
                {activeResultTab === 'claims' && (
                  <div className="space-y-3">
                    {result.claims && result.claims.length > 0 ? (
                      result.claims.map((c, idx) => (
                        <div key={idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-mono font-bold uppercase text-blue-400">
                              {c.importance}
                            </span>
                            <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                              {c.verificationStatus}
                            </span>
                          </div>
                          <p className="text-xs text-slate-200 font-medium">"{c.text}"</p>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-500 italic">No distinct factual assertions identified.</p>
                    )}
                  </div>
                )}

                {/* Sub-tab Content 3: Explainability Rationale */}
                {activeResultTab === 'explain' && (
                  <div className="space-y-4 text-xs text-slate-300 leading-relaxed">
                    <div className="space-y-1.5">
                      <h4 className="font-bold text-white uppercase text-[11px] tracking-wider text-blue-400">
                        Primary Analytical Findings
                      </h4>
                      <ul className="space-y-1 list-disc list-inside text-slate-400">
                        {result.primaryFindings.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="space-y-1.5">
                      <h4 className="font-bold text-white uppercase text-[11px] tracking-wider text-amber-400">
                        Recommended Action
                      </h4>
                      <p className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300">
                        {result.recommendedAction}
                      </p>
                    </div>
                  </div>
                )}

                {/* Sub-tab Content 4: Evidence Graph */}
                {activeResultTab === 'graph' && (
                  <EvidenceGraph claimText={headline || content.slice(0, 60)} />
                )}

                {/* Sub-tab Content: ML Models (VeriNews 2.0) */}
                {activeResultTab === 'ml' && (
                  <div className="space-y-5 text-xs">
                    {result.mlPrediction?.available ? (
                      <>
                        {/* Hybrid Architecture Strategy Banner */}
                        <div className="p-3.5 rounded-xl bg-violet-950/40 border border-violet-500/30 space-y-2">
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <span className="font-bold text-violet-300 text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                              <span>🧬 Architecture:</span>
                              <span className="text-white">{result.mlPrediction.architecture || "Hybrid Traditional ML + Semantic Transformer"}</span>
                            </span>
                            <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                              result.mlPrediction.fallback_active
                                ? 'text-amber-400 bg-amber-500/10 border-amber-500/20'
                                : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
                            }`}>
                              {result.mlPrediction.fallback_active ? '● Fallback Mode Active' : '● Hybrid Engine Active'}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400">
                            <strong>Strategy:</strong> {result.mlPrediction.hybrid_strategy || "Calibrated Multi-Branch Consensus Fusion"}
                          </p>
                        </div>

                        {/* Model Votes Grid (Traditional + Semantic Transformer) */}
                        <div className="space-y-2">
                          <h4 className="font-bold text-violet-400 uppercase tracking-wider text-[11px]">Individual Model & Branch Votes</h4>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            {[
                              { name: result.mlPrediction.lr?.model_name || "Logistic Regression", vote: result.mlPrediction.lr?.prediction, features: result.mlPrediction.lr?.features_used, branch: "Traditional" },
                              { name: result.mlPrediction.svm?.model_name || "Linear SVM", vote: result.mlPrediction.svm?.prediction, features: result.mlPrediction.svm?.features_used, branch: "Traditional" },
                              { name: result.mlPrediction.rf?.model_name || "Random Forest", vote: result.mlPrediction.rf?.prediction, features: result.mlPrediction.rf?.features_used, branch: "Traditional" },
                              {
                                name: "Semantic Transformer",
                                vote: result.mlPrediction.transformer?.prediction || (result.mlPrediction.fallback_active ? "FALLBACK" : "UNAVAILABLE"),
                                features: result.mlPrediction.transformer?.features_used || "Transformer weights offline",
                                branch: "Semantic NLP",
                                isFallback: result.mlPrediction.fallback_active,
                              },
                            ].map((m, i) => (
                              <div key={i} className={`p-3 rounded-xl border space-y-1 ${
                                m.isFallback
                                  ? 'bg-amber-500/8 border-amber-500/25'
                                  : m.vote === 'FAKE'
                                  ? 'bg-rose-500/8 border-rose-500/25'
                                  : 'bg-emerald-500/8 border-emerald-500/25'
                              }`}>
                                <div className="flex items-center justify-between">
                                  <p className="font-bold text-slate-200 text-[11px]">{m.name}</p>
                                  <span className="text-[9px] font-mono text-slate-500">{m.branch}</span>
                                </div>
                                <span className={`inline-block font-black text-sm ${
                                  m.isFallback
                                    ? 'text-amber-400'
                                    : m.vote === 'FAKE'
                                    ? 'text-rose-400'
                                    : 'text-emerald-400'
                                }`}>{m.vote}</span>
                                <p className="text-slate-500 text-[10px] leading-tight">{m.features}</p>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Agreement Bar */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <h4 className="font-bold text-violet-400 uppercase tracking-wider text-[11px]">
                              Model Consensus Agreement: {result.mlPrediction.model_agreement}%
                            </h4>
                            <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                              result.mlPrediction.uncertainty_status === 'MODEL_CONSENSUS'
                                ? 'bg-emerald-500/10 text-emerald-400'
                                : result.mlPrediction.uncertainty_status === 'MODEL_MAJORITY'
                                ? 'bg-blue-500/10 text-blue-400'
                                : 'bg-amber-500/10 text-amber-400'
                            }`}>
                              {result.mlPrediction.uncertainty_status?.replace(/_/g, ' ')}
                            </span>
                          </div>
                          <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all ${
                                result.mlPrediction.model_agreement >= 100
                                  ? 'bg-emerald-500'
                                  : result.mlPrediction.model_agreement >= 75
                                  ? 'bg-blue-500'
                                  : result.mlPrediction.model_agreement >= 50
                                  ? 'bg-amber-400'
                                  : 'bg-rose-500'
                              }`}
                              style={{ width: `${result.mlPrediction.model_agreement}%` }}
                            />
                          </div>
                          <div className="flex gap-4 text-[10px] text-slate-500">
                            <span>FAKE votes: <b className="text-rose-400">{result.mlPrediction.fake_votes}</b></span>
                            <span>REAL votes: <b className="text-emerald-400">{result.mlPrediction.real_votes}</b></span>
                            {result.mlPrediction.weights_used && (
                              <span className="text-slate-400">
                                Weights: Trad <b>{result.mlPrediction.weights_used.traditional}</b> / Trans <b>{result.mlPrediction.weights_used.transformer}</b>
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Scientific note */}
                        <p className="text-[10px] text-slate-500 italic leading-relaxed border-t border-slate-800 pt-3">
                          ⚠️ {result.mlPrediction.note}
                        </p>

                        {/* Explainability Features */}
                        {result.explainability?.status === 'ok' && result.explainability.features?.length > 0 && (
                          <div className="space-y-2 border-t border-slate-800 pt-4">
                            <h4 className="font-bold text-violet-400 uppercase tracking-wider text-[11px]">Top Influential Features (LR)</h4>
                            <div className="space-y-1">
                              {result.explainability.features.slice(0, 8).map((f, i) => (
                                <div key={i} className="flex items-center gap-2">
                                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                                    f.direction === 'FAKE'
                                      ? 'bg-rose-500/10 text-rose-400'
                                      : 'bg-emerald-500/10 text-emerald-400'
                                  }`}>{f.direction}</span>
                                  <span className="font-medium text-slate-200">{f.word}</span>
                                  <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                      className={`h-full rounded-full ${
                                        f.direction === 'FAKE' ? 'bg-rose-500/60' : 'bg-emerald-500/60'
                                      }`}
                                      style={{ width: `${Math.min(100, f.contribution_score * 5000)}%` }}
                                    />
                                  </div>
                                  <span className="text-slate-600 font-mono">{f.contribution_score.toFixed(4)}</span>
                                </div>
                              ))}
                            </div>
                            <p className="text-[10px] text-slate-600 italic">{result.explainability.disclaimer}</p>
                          </div>
                        )}
                        {result.explainability?.status === 'unavailable' && (
                          <p className="text-[10px] text-slate-500 italic">Explainability unavailable: {result.explainability.reason}</p>
                        )}
                      </>
                    ) : (
                      <div className="text-center py-8 space-y-2">
                        <span className="text-3xl">🔴</span>
                        <p className="text-slate-400 font-medium">ML Models Unavailable</p>
                        <p className="text-slate-600 text-[11px]">{result.mlPrediction?.error || 'Model files not found. Set VERINEWS_MODEL_DIR.'}</p>
                        <p className="text-[10px] text-slate-600 mt-2">Analysis above uses heuristic linguistic signals only.</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Sub-tab Content: Evidence (VeriNews 2.0) */}
                {activeResultTab === 'evidence' && (
                  <div className="space-y-4 text-xs">
                    {result.evidence?.status === 'NOT_CONFIGURED' ? (
                      <div className="text-center py-8 space-y-3">
                        <span className="text-3xl">🔍</span>
                        <p className="text-slate-300 font-bold">Evidence Search Not Configured</p>
                        <p className="text-slate-500 leading-relaxed max-w-xs mx-auto">{result.evidence.message}</p>
                        <p className="text-[10px] text-slate-600 italic">{result.evidence.note}</p>
                        <div className="text-left bg-slate-900 rounded-xl p-3 border border-slate-800 text-[11px] text-slate-400 space-y-1 mt-2 max-w-sm mx-auto">
                          <p className="font-bold text-slate-300">To enable evidence search:</p>
                          <p>1. Set <code className="text-teal-400">EVIDENCE_SEARCH_API_KEY</code></p>
                          <p>2. Set <code className="text-teal-400">EVIDENCE_SEARCH_PROVIDER=serpapi</code> or <code className="text-teal-400">duckduckgo</code></p>
                          <p>3. Restart the backend server.</p>
                        </div>
                      </div>
                    ) : result.evidence?.status === 'OK' && result.evidence.items?.length > 0 ? (
                      <>
                        <div className="flex items-center justify-between">
                          <h4 className="font-bold text-teal-400 uppercase tracking-wider text-[11px]">
                            Retrieved Evidence ({result.evidence.items.length} items)
                          </h4>
                          <span className="text-[10px] text-slate-500">via {result.evidence.provider}</span>
                        </div>
                        {result.evidence.items.map((item, i) => (
                          <div key={i} className="p-3 rounded-xl border border-slate-800 bg-slate-900/60 space-y-1.5">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-slate-200 text-[11px]">{item.source_title}</span>
                              <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                                item.evidence_status === 'SUPPORTED' ? 'bg-emerald-500/10 text-emerald-400'
                                : item.evidence_status === 'REFUTED' ? 'bg-rose-500/10 text-rose-400'
                                : 'bg-slate-700 text-slate-400'
                              }`}>{item.evidence_status}</span>
                            </div>
                            <p className="text-slate-400 leading-relaxed">{item.snippet}</p>
                            <p className="text-slate-600 italic text-[10px]">{item.note}</p>
                            {item.url && (
                              <a href={item.url} target="_blank" rel="noreferrer"
                                className="text-teal-400 hover:underline text-[10px] truncate block">{item.url}</a>
                            )}
                          </div>
                        ))}
                        <p className="text-[10px] text-slate-600 italic">{result.evidence.note}</p>
                      </>
                    ) : (
                      <div className="text-center py-8 space-y-2">
                        <span className="text-3xl">📭</span>
                        <p className="text-slate-400 font-medium">{result.evidence?.status || 'No results'}</p>
                        <p className="text-slate-600">{result.evidence?.message}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Sub-tab Content 5: News Timeline */}
                {activeResultTab === 'timeline' && (
                  <NewsTimeline />
                )}

                {/* Bottom Action Buttons */}
                <div className="flex flex-wrap items-center justify-end gap-3 pt-4 border-t border-slate-800">
                  <a
                    href={result.factCheckUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-800 text-blue-400 hover:bg-slate-700 border border-slate-700 flex items-center gap-1.5"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>Fact-Check on Google</span>
                  </a>

                  <button
                    onClick={handleCopyReport}
                    className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700 flex items-center gap-1.5"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    <span>{copySuccess ? "Copied!" : "Copy Report"}</span>
                  </button>

                  <a
                    href={`/api/export/${result.scanId}/export`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-1.5 shadow-lg shadow-emerald-500/20"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Printable Report (HTML/PDF)</span>
                  </a>

                  <button
                    onClick={handleDownloadJson}
                    className="px-3.5 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1.5 shadow-lg shadow-blue-500/20"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download JSON Report</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 10-Step Progress Modal */}
      <PipelineModal isOpen={isScanning} onComplete={handlePipelineComplete} />
    </div>
  );
};
