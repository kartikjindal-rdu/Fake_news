import React, { useState, useEffect, useCallback } from 'react';
import { 
  RefreshCw, Search, ExternalLink, Sparkles, Filter, 
  Globe, AlertCircle, CheckCircle2, Clock, ChevronLeft, 
  ChevronRight, ArrowRight, Shield, Layers, Radio,
  Video, Play, FileText, CheckSquare, Eye, SlidersHorizontal
} from 'lucide-react';
import { api } from '../services/api';

const CHANNEL_CATEGORIES = [
  { id: 'all', label: 'All Intelligence Channels' },
  { id: 'India', label: 'Indian Press' },
  { id: 'World', label: 'International' },
  { id: 'official', label: 'Official / Primary' },
  { id: 'Fact Check', label: 'Fact-Checkers' },
  { id: 'youtube', label: 'YouTube News' },
];

export const LiveNewsFeed = ({ onSelectArticle, selectedArticleId, isScanning }) => {
  const [articles, setArticles] = useState([]);
  const [sources, setSources] = useState([]);
  const [categories, setCategories] = useState(["India", "World", "Health", "Science", "Fact Check"]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Filters
  const [activeChannelTab, setActiveChannelTab] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedSource, setSelectedSource] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // States
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [extractingId, setExtractingId] = useState(null);
  const [showSourceStatus, setShowSourceStatus] = useState(false);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1);
    }, 350);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Load feed data
  const loadFeed = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      let source_type = undefined;
      let category = selectedCategory === 'All' ? undefined : selectedCategory;

      if (activeChannelTab === 'youtube') {
        source_type = 'youtube';
      } else if (activeChannelTab === 'official') {
        source_type = 'official';
      } else if (activeChannelTab === 'Fact Check') {
        category = 'Fact Check';
      } else if (activeChannelTab === 'India') {
        category = 'India';
      } else if (activeChannelTab === 'World') {
        category = 'World';
      }

      const params = {
        page,
        limit: 9,
        category,
        source_type,
        source: selectedSource === 'All' ? undefined : selectedSource,
        search: debouncedSearch.trim() || undefined,
        refresh: isManualRefresh ? true : undefined,
      };

      const data = await api.getNewsFeed(params);
      if (data.error && (!data.articles || data.articles.length === 0)) {
        setError(data.error);
      } else {
        setArticles(data.articles || []);
        setTotal(data.total || 0);
        setTotalPages(data.total_pages || 1);
        setSources(data.sources || []);
        if (data.categories && data.categories.length > 0) {
          setCategories(data.categories);
        }
        setLastUpdated(data.last_updated);
      }
    } catch (err) {
      setError("Unable to load live news feed. Please verify the backend is active.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [page, activeChannelTab, selectedCategory, selectedSource, debouncedSearch]);

  useEffect(() => {
    loadFeed(false);
  }, [loadFeed]);

  // Handle article selection & analysis trigger
  const handleAnalyzeClick = async (article) => {
    setExtractingId(article.id);
    try {
      // 1. If YouTube video, try extracting video transcript
      if (article.source_type === 'youtube' && article.video_id) {
        const ytData = await api.getYoutubeTranscript(article.video_id);
        const payload = {
          headline: article.headline,
          content: ytData.has_transcript && ytData.transcript
            ? ytData.transcript
            : (article.summary || article.headline),
          url: article.url,
          publisher: article.publisher,
          source_type: "youtube",
          content_availability: ytData.has_transcript ? "full-text" : (article.summary ? "summary-only" : "headline-only"),
          has_full_text: ytData.has_transcript,
          extraction_note: ytData.note || "YouTube video transcript extraction evaluated.",
          article_id: article.id,
        };
        onSelectArticle(payload);
        return;
      }

      // 2. Otherwise safely fetch full body text via backend SSRF-protected extractor
      const extracted = await api.fetchArticleContent(article.url);
      
      const payload = {
        headline: article.headline,
        content: extracted.has_full_text && extracted.content
          ? extracted.content
          : (article.summary || article.headline),
        url: article.url,
        publisher: article.publisher,
        source_type: article.source_type || "rss",
        content_availability: extracted.content_availability || (extracted.has_full_text ? "full-text" : "summary-only"),
        has_full_text: extracted.has_full_text,
        extraction_note: extracted.note,
        article_id: article.id,
      };

      onSelectArticle(payload);
    } catch (err) {
      // Fallback to feed summary
      onSelectArticle({
        headline: article.headline,
        content: article.summary || article.headline,
        url: article.url,
        publisher: article.publisher,
        source_type: article.source_type || "rss",
        content_availability: article.summary ? "summary-only" : "headline-only",
        has_full_text: false,
        extraction_note: "Could not extract full body; analyzing feed summary.",
        article_id: article.id,
      });
    } finally {
      setExtractingId(null);
    }
  };

  // Helper date formatter
  const formatDate = (isoString) => {
    if (!isoString) return null;
    try {
      const d = new Date(isoString);
      if (isNaN(d.getTime())) return isoString.slice(0, 16);
      return d.toLocaleDateString(undefined, { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch {
      return null;
    }
  };

  // Badge helpers
  const getSourceTypeBadge = (type) => {
    switch (type) {
      case 'youtube':
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <Video className="w-2.5 h-2.5 text-rose-400" />
            YouTube News
          </span>
        );
      case 'official':
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Shield className="w-2.5 h-2.5 text-emerald-400" />
            Official Agency
          </span>
        );
      case 'factcheck':
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <CheckSquare className="w-2.5 h-2.5 text-purple-400" />
            Fact Check
          </span>
        );
      case 'api':
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Globe className="w-2.5 h-2.5 text-amber-400" />
            GDELT Stream
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Radio className="w-2.5 h-2.5 text-blue-400" />
            Verified Press
          </span>
        );
    }
  };

  const getAvailabilityBadge = (avail, hasFullText) => {
    if (hasFullText || avail === 'full-text') {
      return (
        <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          Full Body
        </span>
      );
    }
    if (avail === 'summary-only') {
      return (
        <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30">
          Summary Available
        </span>
      );
    }
    return (
      <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
        Headline Only
      </span>
    );
  };

  const activeSourcesCount = sources.filter(s => s.status === 'OK' && s.enabled !== false).length;

  return (
    <div className="space-y-4">
      
      {/* Top Banner / Feed Controls Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-slate-900/90 border border-slate-800 p-3.5 rounded-2xl shadow-sm">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-blue-600/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Radio className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider text-white">
                Multi-Channel News Intelligence Stream
              </span>
              <span className="flex items-center gap-1 text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                Live Multi-Feed
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Indian Press • International • WHO & UN Official • Fact-Checkers • YouTube Channels
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          {/* Source Health Button */}
          <button
            onClick={() => setShowSourceStatus(!showSourceStatus)}
            className="px-2.5 py-1.5 rounded-xl text-[11px] font-bold bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 flex items-center gap-1.5 transition-all"
            title="Inspect feed sources status & health"
          >
            <Shield className="w-3.5 h-3.5 text-blue-400" />
            <span>{activeSourcesCount > 0 ? `${activeSourcesCount} Channels Active` : 'Sources Status'}</span>
          </button>

          {/* Refresh Button */}
          <button
            onClick={() => loadFeed(true)}
            disabled={loading || refreshing}
            className="px-3 py-1.5 rounded-xl text-[11px] font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1.5 shadow-md shadow-blue-600/20 disabled:opacity-50 transition-all"
            title="Fetch fresh articles from all active channels"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>
        </div>
      </div>

      {/* Multi-Channel Navigation Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none border-b border-slate-800/80">
        {CHANNEL_CATEGORIES.map(tab => (
          <button
            key={tab.id}
            onClick={() => { setActiveChannelTab(tab.id); setPage(1); }}
            className={`px-3 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
              activeChannelTab === tab.id
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 border border-slate-800/80'
            }`}
          >
            {tab.id === 'youtube' && <Video className="w-3.5 h-3.5 text-rose-400" />}
            {tab.id === 'official' && <Shield className="w-3.5 h-3.5 text-emerald-400" />}
            {tab.id === 'Fact Check' && <CheckSquare className="w-3.5 h-3.5 text-purple-400" />}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Source Status Drawer (Collapsible) */}
      {showSourceStatus && (
        <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2.5 animate-fadeIn text-xs">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="font-bold text-slate-200 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-blue-400" />
              Connected Multi-Channel Endpoints ({sources.length})
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              Zero API Keys Needed • SSRF Protected • 5m TTL Cache
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {sources.map(src => (
              <div 
                key={src.source_id} 
                className="p-2 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between gap-2"
              >
                <div className="truncate">
                  <p className="font-bold text-slate-200 truncate">{src.name}</p>
                  <p className="text-[10px] text-slate-400 truncate">
                    {src.source_type?.toUpperCase()} • {src.category} • {src.article_count} items
                  </p>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold shrink-0 ${
                  src.status === 'OK' 
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                    : src.status === 'DISABLED'
                    ? 'bg-slate-700/20 text-slate-400 border border-slate-700/30'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                }`}>
                  {src.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-12 gap-2.5 items-center">
        
        {/* Search Input */}
        <div className="sm:col-span-6 relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search verified articles, headlines, or claims..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs px-1"
            >
              ✕
            </button>
          )}
        </div>

        {/* Source Dropdown Filter */}
        <div className="sm:col-span-3">
          <select
            value={selectedSource}
            onChange={(e) => { setSelectedSource(e.target.value); setPage(1); }}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-medium truncate"
          >
            <option value="All">All Sources ({sources.length || '16'})</option>
            {sources.map(s => (
              <option key={s.source_id} value={s.source_id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        {/* Category Filter */}
        <div className="sm:col-span-3">
          <select
            value={selectedCategory}
            onChange={(e) => { setSelectedCategory(e.target.value); setPage(1); }}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="All">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Articles View */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-3 animate-pulse">
              <div className="flex items-center justify-between">
                <div className="w-20 h-4 bg-slate-800 rounded" />
                <div className="w-14 h-4 bg-slate-800 rounded" />
              </div>
              <div className="w-full h-8 bg-slate-800 rounded" />
              <div className="w-full h-12 bg-slate-800/60 rounded" />
              <div className="w-full h-8 bg-slate-800 rounded-xl" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="p-8 rounded-2xl bg-rose-500/5 border border-rose-500/20 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
          <h4 className="text-sm font-bold text-rose-300">Live Feed Notice</h4>
          <p className="text-xs text-rose-400/80 max-w-md mx-auto">{error}</p>
          <button
            onClick={() => loadFeed(true)}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-xl border border-slate-700 transition-all inline-flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Reconnecting</span>
          </button>
        </div>
      ) : articles.length === 0 ? (
        <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center space-y-2">
          <p className="text-xs font-bold text-slate-300">No articles matched your current filters</p>
          <p className="text-xs text-slate-500">Try switching channel tabs or clearing search keywords.</p>
          <button
            onClick={() => { setSearchQuery(''); setSelectedCategory('All'); setSelectedSource('All'); setActiveChannelTab('all'); }}
            className="text-xs text-blue-400 hover:underline pt-1"
          >
            Reset all filters
          </button>
        </div>
      ) : (
        /* Dynamic Article Cards Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {articles.map(article => {
            const isSelected = selectedArticleId === article.id;
            const isExtracting = extractingId === article.id;
            const pubDate = formatDate(article.published_at);
            const isYouTube = article.source_type === 'youtube';

            return (
              <div
                key={article.id}
                className={`flex flex-col justify-between p-4 rounded-2xl border transition-all ${
                  isSelected
                    ? 'bg-blue-950/20 border-blue-500/50 shadow-lg shadow-blue-500/10'
                    : 'bg-slate-900/70 hover:bg-slate-900 border-slate-800/90 hover:border-slate-700'
                }`}
              >
                <div className="space-y-2.5">
                  
                  {/* Lead Image or Video Thumbnail */}
                  {article.image_url && (
                    <div className="relative w-full h-32 rounded-xl overflow-hidden bg-slate-950 mb-2 border border-slate-800/80">
                      <img 
                        src={article.image_url} 
                        alt={article.headline} 
                        className="w-full h-full object-cover opacity-85 hover:opacity-100 transition-opacity"
                        loading="lazy"
                        onError={(e) => { e.currentTarget.style.display = 'none'; }}
                      />
                      {isYouTube && (
                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center pointer-events-none">
                          <div className="w-8 h-8 rounded-full bg-rose-600/90 text-white flex items-center justify-center shadow-lg">
                            <Play className="w-4 h-4 fill-white ml-0.5" />
                          </div>
                        </div>
                      )}
                      <div className="absolute top-2 left-2">
                        {getSourceTypeBadge(article.source_type)}
                      </div>
                      <div className="absolute bottom-2 right-2">
                        {getAvailabilityBadge(article.content_availability, article.has_full_text)}
                      </div>
                    </div>
                  )}

                  {/* Top Metadata Badges when no image */}
                  {!article.image_url && (
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5 truncate">
                        {getSourceTypeBadge(article.source_type)}
                        <span className="text-[10px] font-bold text-slate-300 truncate max-w-[110px]">
                          {article.publisher}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0">
                        {getAvailabilityBadge(article.content_availability, article.has_full_text)}
                      </div>
                    </div>
                  )}

                  {/* Date and Category bar */}
                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-300 font-medium">
                      {article.category}
                    </span>
                    {pubDate && (
                      <span className="flex items-center gap-1 text-slate-500 font-mono">
                        <Clock className="w-2.5 h-2.5" />
                        {pubDate}
                      </span>
                    )}
                  </div>

                  {/* Headline */}
                  <h4 className="text-xs font-bold text-slate-100 hover:text-blue-300 transition-colors line-clamp-2 leading-relaxed">
                    {article.headline}
                  </h4>

                  {/* Summary / Excerpt */}
                  {article.summary && (
                    <p className="text-[11px] text-slate-400 line-clamp-3 leading-relaxed">
                      {article.summary}
                    </p>
                  )}
                </div>

                {/* Bottom Card Actions: Explicit Two Actions */}
                <div className="pt-3.5 mt-3.5 border-t border-slate-800/80 flex items-center justify-between gap-2">
                  {/* Action 1: Open Original Article or Watch on YouTube */}
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-medium text-slate-400 hover:text-slate-100 flex items-center gap-1 transition-colors px-2 py-1 rounded-lg hover:bg-slate-800/60"
                    title={isYouTube ? "Watch broadcast on YouTube" : "Open original publisher article"}
                  >
                    <span>{isYouTube ? "Watch Video" : "Original"}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>

                  {/* Action 2: Analyze with VeriNews */}
                  <button
                    onClick={() => handleAnalyzeClick(article)}
                    disabled={isScanning || isExtracting}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all shadow-sm ${
                      isSelected
                        ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                        : isYouTube
                        ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/20'
                        : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-600/20'
                    } disabled:opacity-50`}
                  >
                    {isExtracting ? (
                      <>
                        <RefreshCw className="w-3 h-3 animate-spin" />
                        <span>{isYouTube ? "Captions..." : "Extracting..."}</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-3 h-3" />
                        <span>{isSelected ? 'In Scanner' : 'Analyze'}</span>
                        <ArrowRight className="w-3 h-3" />
                      </>
                    )}
                  </button>
                </div>

              </div>
            );
          })}
        </div>
      )}

      {/* Pagination Bar */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2 text-xs text-slate-400">
          <span className="font-mono text-[11px]">
            Page {page} of {totalPages} • {total} Feed Articles
          </span>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page <= 1 || loading}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 disabled:opacity-40 transition-all"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || loading}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 disabled:opacity-40 transition-all"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
