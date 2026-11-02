import React, { useState, useMemo } from 'react';
import { 
  Network, Filter, ZoomIn, ZoomOut, RotateCcw, 
  ExternalLink, Shield, CheckCircle2, XCircle, HelpCircle,
  FileText, CheckSquare, Layers, AlertTriangle, Eye, X
} from 'lucide-react';

export const InteractiveClaimGraph = ({ graphData }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [filterRel, setFilterRel] = useState('all');
  const [zoomLevel, setZoomLevel] = useState(1);

  const rawNodes = graphData?.nodes || [];
  const rawEdges = graphData?.edges || [];

  // Filtered nodes
  const filteredNodes = useMemo(() => {
    return rawNodes.filter(n => {
      if (filterType !== 'all' && n.type !== filterType) return false;
      return true;
    });
  }, [rawNodes, filterType]);

  const activeNodeIds = useMemo(() => new Set(filteredNodes.map(n => n.id)), [filteredNodes]);

  // Filtered edges
  const filteredEdges = useMemo(() => {
    return rawEdges.filter(e => {
      if (!activeNodeIds.has(e.source) || !activeNodeIds.has(e.target)) return false;
      if (filterRel !== 'all' && e.relationship !== filterRel) return false;
      return true;
    });
  }, [rawEdges, activeNodeIds, filterRel]);

  // Node positions in a radial circular layout for deterministic, responsive rendering
  const nodePositions = useMemo(() => {
    const positions = {};
    const centerNode = filteredNodes.find(n => n.type === 'article') || filteredNodes[0];
    const otherNodes = filteredNodes.filter(n => n.id !== centerNode?.id);

    const width = 640;
    const height = 440;
    const centerX = width / 2;
    const centerY = height / 2;

    if (centerNode) {
      positions[centerNode.id] = { x: centerX, y: centerY };
    }

    const total = otherNodes.length;
    otherNodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / Math.max(1, total);
      // Ring radius depends on node type
      let radius = 170;
      if (node.type === 'claim') radius = 130;
      else if (node.type === 'publisher') radius = 210;
      else if (node.type === 'fact_check') radius = 180;

      positions[node.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      };
    });

    return positions;
  }, [filteredNodes]);

  const getNodeColor = (type, assessment) => {
    switch (type) {
      case 'claim':
        if (assessment === 'CONTRADICTED') return '#f43f5e'; // rose
        if (assessment === 'SUPPORTED') return '#10b981'; // emerald
        return '#3b82f6'; // blue
      case 'article':
        return '#6366f1'; // indigo
      case 'fact_check':
        return '#a855f7'; // purple
      case 'primary_source':
        return '#059669'; // dark emerald
      case 'publisher':
        return '#f59e0b'; // amber
      case 'evidence_passage':
      default:
        return '#06b6d4'; // cyan
    }
  };

  const getEdgeStroke = (rel) => {
    switch (rel) {
      case 'supports': return '#10b981';
      case 'contradicts': return '#f43f5e';
      case 'evaluates': return '#a855f7';
      case 'same_event': return '#f59e0b';
      case 'reports_on': return '#3b82f6';
      default: return '#64748b';
    }
  };

  if (!graphData || rawNodes.length === 0) {
    return (
      <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center space-y-3">
        <Network className="w-8 h-8 text-slate-500 mx-auto" />
        <h4 className="text-xs font-bold text-slate-300">No Relationship Graph Available</h4>
        <p className="text-[11px] text-slate-500 max-w-sm mx-auto">
          Execute an AI Research Agent investigation or select a factual assertion to build the provenance network.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      {/* Top Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-blue-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-white">
            Claim Relationship & Provenance Network
          </h3>
          <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
            {filteredNodes.length} Nodes • {filteredEdges.length} Edges
          </span>
        </div>

        {/* View Controls & Filters */}
        <div className="flex items-center gap-2 flex-wrap">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-[11px] text-slate-300 font-medium focus:outline-none"
          >
            <option value="all">All Node Types</option>
            <option value="claim">Claims Only</option>
            <option value="primary_source">Primary Sources</option>
            <option value="fact_check">Fact-Checks</option>
            <option value="publisher">Publishers</option>
            <option value="evidence_passage">Evidence Passages</option>
          </select>

          <select
            value={filterRel}
            onChange={(e) => setFilterRel(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-[11px] text-slate-300 font-medium focus:outline-none"
          >
            <option value="all">All Relationships</option>
            <option value="supports">Corroborates (Supports)</option>
            <option value="contradicts">Contradicts</option>
            <option value="evaluates">Evaluates</option>
            <option value="reports_on">Reports On</option>
          </select>

          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-lg p-0.5">
            <button
              onClick={() => setZoomLevel(z => Math.max(0.6, z - 0.15))}
              className="p-1 hover:text-white text-slate-400"
              title="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoomLevel(1)}
              className="p-1 hover:text-white text-slate-400 font-mono text-[10px]"
              title="Reset zoom"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
            <button
              onClick={() => setZoomLevel(z => Math.min(1.6, z + 0.15))}
              className="p-1 hover:text-white text-slate-400"
              title="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Graph & Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        
        {/* SVG Graph View (8 Cols on large, full on small) */}
        <div className={`rounded-xl bg-slate-950/70 border border-slate-800/80 overflow-hidden relative ${selectedNode ? 'lg:col-span-8' : 'lg:col-span-12'}`}>
          <div className="w-full overflow-auto flex items-center justify-center p-2">
            <svg 
              viewBox="0 0 640 440" 
              className="w-full h-80 sm:h-96 transition-transform duration-200"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
                </marker>
              </defs>

              {/* Render Edges */}
              {filteredEdges.map(edge => {
                const p1 = nodePositions[edge.source];
                const p2 = nodePositions[edge.target];
                if (!p1 || !p2) return null;

                const strokeColor = getEdgeStroke(edge.relationship);
                const isDashed = edge.is_syndicated || edge.is_tentative || edge.relationship === 'same_event';

                return (
                  <g key={edge.id} className="opacity-80 hover:opacity-100 transition-opacity">
                    <line
                      x1={p1.x}
                      y1={p1.y}
                      x2={p2.x}
                      y2={p2.y}
                      stroke={strokeColor}
                      strokeWidth={edge.relationship === 'contradicts' ? "2.5" : "1.75"}
                      strokeDasharray={isDashed ? "4,4" : undefined}
                      markerEnd="url(#arrow)"
                    />
                  </g>
                );
              })}

              {/* Render Nodes */}
              {filteredNodes.map(node => {
                const pos = nodePositions[node.id];
                if (!pos) return null;

                const isSelected = selectedNode?.id === node.id;
                const nodeColor = getNodeColor(node.type, node.assessment_code);
                const radius = node.type === 'article' ? 18 : (node.type === 'claim' ? 14 : 11);

                return (
                  <g 
                    key={node.id} 
                    transform={`translate(${pos.x}, ${pos.y})`}
                    onClick={() => setSelectedNode(node)}
                    className="cursor-pointer group"
                  >
                    {/* Pulsing ring if selected */}
                    {isSelected && (
                      <circle
                        r={radius + 6}
                        fill="none"
                        stroke={nodeColor}
                        strokeWidth="2"
                        className="animate-ping opacity-50"
                      />
                    )}

                    {/* Node Circle */}
                    <circle
                      r={radius}
                      fill={nodeColor}
                      stroke="#0f172a"
                      strokeWidth="2.5"
                      className="transition-transform group-hover:scale-125"
                    />

                    {/* Node Label */}
                    <text
                      y={radius + 12}
                      textAnchor="middle"
                      fill="#cbd5e1"
                      fontSize="9"
                      fontWeight="bold"
                      className="pointer-events-none select-none drop-shadow"
                    >
                      {node.label?.length > 18 ? node.label.slice(0, 16) + '..' : node.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Graph Legend */}
          <div className="p-2.5 bg-slate-900/90 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400 overflow-x-auto gap-3">
            <span className="font-bold text-slate-300">Legend:</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500" /> Claim</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-indigo-500" /> Article</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-purple-500" /> Fact-Check</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500" /> Primary Source</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500" /> Publisher</span>
            <span className="flex items-center gap-1 font-mono text-rose-400">── Contradiction</span>
            <span className="flex items-center gap-1 font-mono text-emerald-400">── Corroboration</span>
            <span className="flex items-center gap-1 font-mono text-amber-400">- - Syndicated</span>
          </div>
        </div>

        {/* Selected Node Inspector Drawer (4 Cols) */}
        {selectedNode && (
          <div className="lg:col-span-4 p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 animate-fadeIn text-xs">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="text-[10px] font-mono uppercase font-bold text-blue-400">
                {selectedNode.type.replace('_', ' ')} Record
              </span>
              <button onClick={() => setSelectedNode(null)} className="text-slate-400 hover:text-white">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-1.5">
              <h4 className="font-bold text-white leading-relaxed">
                {selectedNode.title || selectedNode.label}
              </h4>
              {selectedNode.publisher && (
                <p className="text-[11px] text-slate-400">
                  Publisher / Outlet: <strong className="text-slate-200">{selectedNode.publisher}</strong>
                </p>
              )}
            </div>

            {selectedNode.excerpt && (
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-300 leading-relaxed italic">
                "{selectedNode.excerpt}"
              </div>
            )}

            {selectedNode.assessment && (
              <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/80 flex items-center justify-between">
                <span className="text-slate-400">Assessment:</span>
                <span className={`font-bold uppercase text-[10px] px-2 py-0.5 rounded ${
                  selectedNode.assessment_code === 'CONTRADICTED' ? 'bg-rose-500/10 text-rose-400' :
                  selectedNode.assessment_code === 'SUPPORTED' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                }`}>
                  {selectedNode.assessment}
                </span>
              </div>
            )}

            {selectedNode.reliability_tier && (
              <p className="text-[10px] text-slate-500">
                Reliability: {selectedNode.reliability_tier} • {selectedNode.content_availability || 'summary-only'}
              </p>
            )}

            {selectedNode.url && (
              <a
                href={selectedNode.url}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1 pt-1"
              >
                <span>Open canonical record</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        )}

      </div>
    </div>
  );
};
