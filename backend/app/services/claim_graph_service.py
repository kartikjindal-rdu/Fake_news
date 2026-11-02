"""
claim_graph_service.py
======================
Builds an interactive, provenance-backed Claim Relationship Graph for VeriNews AI 3.0.
Constructs network topology from actual research investigation records, live feeds,
and fact-checking wires.

Node Types:
- claim
- article
- publisher
- primary_source
- fact_check
- evidence_passage
- related_event

Relationship Types:
- reports_on
- supports
- contradicts
- evaluates
- references
- same_event (syndicated wire release)
"""

import re
import logging
import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def build_graph_from_investigation(investigation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construct nodes and edges from a completed research agent investigation report.
    Guarantees that all nodes correspond strictly to actual retrieved records.
    """
    nodes = []
    edges = []
    seen_node_ids = set()
    seen_edge_keys = set()

    inv_id = investigation.get("investigation_id", "INV-UNKNOWN")
    input_summary = investigation.get("input_summary", {})
    headline = input_summary.get("headline") or "Submitted Document"
    canonical_url = input_summary.get("canonical_url")

    # 1. Root Article Node
    article_node_id = f"art_{abs(hash(headline)) % 100000}"
    nodes.append({
        "id": article_node_id,
        "type": "article",
        "label": headline[:45] + ("..." if len(headline) > 45 else ""),
        "title": headline,
        "url": canonical_url,
        "category": "Submission",
        "provenance": "Input Document",
        "created_at": investigation.get("investigation_timestamp"),
        "metrics": {"claim_count": len(investigation.get("claims", []))},
    })
    seen_node_ids.add(article_node_id)

    # 2. Iterate through extracted claims
    for claim_obj in investigation.get("claims", []):
        cid = claim_obj.get("claim_id", f"c_{abs(hash(claim_obj['claim'])) % 10000}")
        claim_label = claim_obj["claim"][:50] + ("..." if len(claim_obj["claim"]) > 50 else "")

        claim_node_id = f"node_{cid}"
        if claim_node_id not in seen_node_ids:
            nodes.append({
                "id": claim_node_id,
                "type": "claim",
                "label": claim_label,
                "title": claim_obj["claim"],
                "topic": claim_obj.get("topic", "General"),
                "assessment": claim_obj.get("assessment", "Insufficient evidence"),
                "assessment_code": claim_obj.get("assessment_code", "INSUFFICIENT_EVIDENCE"),
                "provenance": f"Extracted Factual Assertion ({claim_obj.get('sentence_type', 'Claim')})",
                "created_at": claim_obj.get("investigated_at"),
            })
            seen_node_ids.add(claim_node_id)

        # Edge: Article -> reports_on -> Claim
        edge_key = f"{article_node_id}->reports_on->{claim_node_id}"
        if edge_key not in seen_edge_keys:
            edges.append({
                "id": f"e_{len(edges) + 1}",
                "source": article_node_id,
                "target": claim_node_id,
                "relationship": "reports_on",
                "label": "Reports On",
                "is_tentative": False,
                "is_syndicated": False,
            })
            seen_edge_keys.add(edge_key)

        # 3. Add Evidence Sources for this claim
        for ev in claim_obj.get("evidence_records", []):
            ev_id = ev.get("id", f"ev_{abs(hash(ev['url'])) % 100000}")
            stype = ev.get("source_type", "evidence_passage")
            publisher_name = ev.get("publisher", "Independent Source")
            
            # Map source_type
            if "fact_check" in stype:
                node_type = "fact_check"
            elif "primary" in stype or "encyclopedic" in stype:
                node_type = "primary_source"
            else:
                node_type = "evidence_passage"

            if ev_id not in seen_node_ids:
                nodes.append({
                    "id": ev_id,
                    "type": node_type,
                    "label": ev["source_title"][:40] + "...",
                    "title": ev["source_title"],
                    "publisher": publisher_name,
                    "url": ev.get("url"),
                    "excerpt": ev.get("excerpt"),
                    "published_at": ev.get("published_at"),
                    "retrieved_at": ev.get("retrieved_at"),
                    "content_availability": ev.get("content_availability", "summary-only"),
                    "reliability_tier": ev.get("reliability_tier", "Open Public Knowledge"),
                    "provenance": publisher_name,
                })
                seen_node_ids.add(ev_id)

            # Publisher Node
            pub_node_id = f"pub_{abs(hash(publisher_name)) % 100000}"
            if pub_node_id not in seen_node_ids:
                nodes.append({
                    "id": pub_node_id,
                    "type": "publisher",
                    "label": publisher_name,
                    "title": publisher_name,
                    "provenance": "Issuing Authority / Publisher",
                })
                seen_node_ids.add(pub_node_id)

            # Edge: Publisher -> references/issues -> Evidence Node
            pub_edge_key = f"{pub_node_id}->references->{ev_id}"
            if pub_edge_key not in seen_edge_keys:
                edges.append({
                    "id": f"e_{len(edges) + 1}",
                    "source": pub_node_id,
                    "target": ev_id,
                    "relationship": "references",
                    "label": "Published By",
                    "is_tentative": False,
                    "is_syndicated": False,
                })
                seen_edge_keys.add(pub_edge_key)

            # Edge: Evidence Node -> (supports | contradicts | evaluates) -> Claim Node
            rel = ev.get("relationship", "provides_context")
            if rel == "supports":
                rel_type = "supports"
                rel_label = "Corroborates"
            elif rel == "contradicts":
                rel_type = "contradicts"
                rel_label = "Contradicts"
            elif node_type == "fact_check":
                rel_type = "evaluates"
                rel_label = "Evaluates"
            else:
                rel_type = "provides_context"
                rel_label = "Provides Context"

            ev_edge_key = f"{ev_id}->{rel_type}->{claim_node_id}"
            if ev_edge_key not in seen_edge_keys:
                edges.append({
                    "id": f"e_{len(edges) + 1}",
                    "source": ev_id,
                    "target": claim_node_id,
                    "relationship": rel_type,
                    "label": rel_label,
                    "is_tentative": rel_type == "provides_context",
                    "is_syndicated": False,
                })
                seen_edge_keys.add(ev_edge_key)

    # 4. Detect Syndication across Articles covering the same topic
    # Check if multiple articles have word overlap > 0.45
    article_nodes = [n for n in nodes if n["type"] == "article"]
    for i, a1 in enumerate(article_nodes):
        for j, a2 in enumerate(article_nodes):
            if i < j:
                w1 = set(re.findall(r"\w+", a1["title"].lower()))
                w2 = set(re.findall(r"\w+", a2["title"].lower()))
                if w1 and w2:
                    overlap = len(w1 & w2) / max(1, len(w1 | w2))
                    if overlap > 0.45:
                        s_key = f"{a1['id']}->same_event->{a2['id']}"
                        if s_key not in seen_edge_keys:
                            edges.append({
                                "id": f"e_{len(edges) + 1}",
                                "source": a1["id"],
                                "target": a2["id"],
                                "relationship": "same_event",
                                "label": "Syndicated Coverage",
                                "is_tentative": False,
                                "is_syndicated": True,
                            })
                            seen_edge_keys.add(s_key)

    # Calculate graph summary stats
    type_counts = {}
    for n in nodes:
        t = n["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    rel_counts = {}
    for e in edges:
        r = e["relationship"]
        rel_counts[r] = rel_counts.get(r, 0) + 1

    return {
        "investigation_id": inv_id,
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": type_counts,
            "relationship_types": rel_counts,
        },
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "is_empty": len(nodes) == 0,
    }


def get_empty_graph(message: str = "No graph data available. Run an investigation to generate nodes.") -> Dict[str, Any]:
    """Return an honest empty state graph."""
    return {
        "investigation_id": None,
        "nodes": [],
        "edges": [],
        "stats": {
            "total_nodes": 0,
            "total_edges": 0,
            "node_types": {},
            "relationship_types": {},
        },
        "message": message,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "is_empty": True,
    }
