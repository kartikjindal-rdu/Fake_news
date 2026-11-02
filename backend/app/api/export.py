"""
export.py
=========
Report export endpoints for VeritasAI / VeriNews AI 3.0.
Generates self-contained, printable, branded forensic investigation reports (HTML/Printable PDF)
incorporating:
- Full ML Ensemble predictions & uncertainty status
- Extracted factual subclaims
- Grounded evidence assessments & citations
- Conflicting evidence & fact-check matches
- Calibration baseline & methodological limitations
"""

import html
import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Response, Body
from fastapi.responses import HTMLResponse

from app.api.scans import get_scan_by_id

router = APIRouter()


def _generate_html_report(scan: dict) -> str:
    """Generate self-contained, enterprise styled printable HTML forensic report."""
    scan_id = html.escape(str(scan.get("scanId") or scan.get("id") or "UNKNOWN-ID"))
    timestamp = html.escape(str(scan.get("timestamp") or "N/A"))
    headline = html.escape(str(scan.get("headline") or "Untitled Submission"))
    content = html.escape(str(scan.get("content") or ""))
    url = html.escape(str(scan.get("url") or "N/A"))
    
    # Verdict & scores
    final_verdict = html.escape(str(scan.get("finalVerdict") or scan.get("verdict") or "UNDER EVALUATION"))
    risk_level_obj = scan.get("riskLevel") or {}
    risk_level = html.escape(str(risk_level_obj.get("label") if isinstance(risk_level_obj, dict) else risk_level_obj or "UNKNOWN"))
    
    scores = scan.get("scores") or {}
    risk_score = float(scores.get("riskScore", scan.get("riskScore", 0)))
    fake_prob = float(scores.get("fakeProbability", scan.get("fakeProbability", 0)))
    real_prob = float(scores.get("realProbability", scan.get("realProbability", 0)))
    confidence = float(scores.get("aiConfidence", scan.get("confidence", 0)))
    
    # ML Votes
    ml = scan.get("mlPrediction") or {}
    lr_vote = html.escape(str((ml.get("lr") or {}).get("prediction") or "N/A"))
    svm_vote = html.escape(str((ml.get("svm") or {}).get("prediction") or "N/A"))
    rf_vote = html.escape(str((ml.get("rf") or {}).get("prediction") or "N/A"))
    trans_obj = ml.get("transformer") or {}
    trans_vote = html.escape(str(trans_obj.get("prediction") or ("FALLBACK (Offline)" if ml.get("fallback_active") else "N/A")))
    ensemble_vote = html.escape(str(ml.get("final_prediction") or ml.get("final") or "N/A"))
    uncertainty_status = html.escape(str(ml.get("uncertainty_status") or "NOT_CALCULATED"))

    # Claims extracted
    claims_list = scan.get("claims") or []
    claims_html = ""
    if claims_list:
        for c in claims_list:
            c_text = html.escape(str(c.get("text") or c.get("claim") or ""))
            c_imp = html.escape(str(c.get("importance") or "Factual Assertion"))
            c_stat = html.escape(str(c.get("verificationStatus") or c.get("status") or "UNVERIFIED"))
            claims_html += f"""
            <div style="margin-bottom: 8px; padding: 10px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 10px; font-family: monospace; color: #2563eb; font-weight: bold; text-transform: uppercase;">[{c_imp}]</span>
                    <span style="font-size: 12px; font-weight: 600; color: #1e293b; margin-left: 6px;">"{c_text}"</span>
                </div>
                <span style="font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 4px; background: #e2e8f0; color: #475569;">{c_stat}</span>
            </div>
            """
    else:
        claims_html = "<p style='font-size: 12px; color: #64748b; font-style: italic;'>No distinct subclaims isolated.</p>"

    # Language
    lang = scan.get("languageDetection") or {}
    detected_lang = html.escape(str(lang.get("detected_language") or "English"))

    # Evidence items
    evidence = scan.get("evidence") or {}
    items = evidence.get("items") or []
    
    evidence_html = ""
    if items:
        for it in items:
            s_title = html.escape(str(it.get("source_title") or "Source Record"))
            s_url = html.escape(str(it.get("url") or "#"))
            s_snip = html.escape(str(it.get("snippet") or ""))
            s_stat = html.escape(str(it.get("evidence_status") or "INSUFFICIENT_EVIDENCE"))
            badge_c = "#065f46" if "SUPPORT" in s_stat else ("#991b1b" if "CONTRADICT" in s_stat else "#475569")
            badge_b = "#ecfdf5" if "SUPPORT" in s_stat else ("#fee2e2" if "CONTRADICT" in s_stat else "#f1f5f9")

            evidence_html += f"""
            <div style="margin-bottom: 12px; padding: 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: bold;">
                    <span>{s_title}</span>
                    <span style="background: {badge_b}; color: {badge_c}; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{s_stat}</span>
                </div>
                <p style="font-size: 12px; color: #475569; margin: 6px 0;">{s_snip}</p>
                <a href="{s_url}" target="_blank" style="font-size: 11px; color: #2563eb; text-decoration: underline;">{s_url}</a>
            </div>
            """
    else:
        evidence_html = "<p style='font-size: 13px; color: #64748b; font-style: italic;'>No external corroborating evidence located or configured.</p>"

    badge_bg = "#fee2e2" if "FAKE" in final_verdict or "HIGH" in risk_level else "#ecfdf5"
    badge_color = "#991b1b" if "FAKE" in final_verdict or "HIGH" in risk_level else "#065f46"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>VeritasAI Forensic Investigation Certificate — {scan_id}</title>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: #f1f5f9;
        color: #0f172a;
        margin: 0;
        padding: 40px 20px;
    }}
    .container {{
        max-width: 860px;
        margin: 0 auto;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        overflow: hidden;
    }}
    .header {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 32px 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .header h1 {{ margin: 0; font-size: 22px; letter-spacing: -0.5px; }}
    .header p {{ margin: 4px 0 0 0; font-size: 12px; color: #94a3b8; }}
    .scan-badge {{
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 6px 12px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 12px;
    }}
    .content-body {{ padding: 36px 40px; }}
    .verdict-banner {{
        background: {badge_bg};
        color: {badge_color};
        padding: 16px 20px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 28px;
        font-weight: bold;
    }}
    .section-title {{
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #334155;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 8px;
        margin-top: 28px;
        margin-bottom: 14px;
    }}
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 24px;
    }}
    .metric-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }}
    .metric-card .val {{ font-size: 20px; font-weight: 800; color: #0f172a; }}
    .metric-card .lbl {{ font-size: 11px; text-transform: uppercase; color: #64748b; margin-top: 4px; }}
    .votes-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 24px;
    }}
    .votes-table th, .votes-table td {{
        border: 1px solid #e2e8f0;
        padding: 10px 14px;
        font-size: 13px;
        text-align: left;
    }}
    .votes-table th {{ background: #f8fafc; color: #475569; }}
    .text-box {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        font-size: 13px;
        line-height: 1.6;
        color: #1e293b;
        max-height: 250px;
        overflow-y: auto;
        white-space: pre-wrap;
    }}
    .disclaimer-box {{
        background: #fffbeb;
        border: 1px solid #fef3c7;
        color: #92400e;
        padding: 16px;
        border-radius: 10px;
        font-size: 11px;
        line-height: 1.6;
        margin-top: 32px;
    }}
    .footer-actions {{
        background: #f8fafc;
        border-top: 1px solid #e2e8f0;
        padding: 20px 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .btn {{
        background: #2563eb;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
    }}
    @media print {{
        body {{ padding: 0; background: white; }}
        .container {{ border: none; box-shadow: none; }}
        .footer-actions {{ display: none; }}
    }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <h1>VeritasAI Forensic Intelligence Audit</h1>
            <p>VeriNews AI 3.0 • Decoupled Machine Learning & Grounded Evidence Verification</p>
        </div>
        <div class="scan-badge">{scan_id}</div>
    </div>

    <div class="content-body">
        <div class="verdict-banner">
            <div>
                <span>FINAL VERDICT: {final_verdict}</span>
                <span style="font-size: 13px; margin-left: 12px; opacity: 0.85;">(Risk: {risk_level})</span>
            </div>
            <div><span>Timestamp: {timestamp}</span></div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="val">{risk_score:.1f}/100</div>
                <div class="lbl">Forensic Risk</div>
            </div>
            <div class="metric-card">
                <div class="val">{fake_prob:.1f}%</div>
                <div class="lbl">Fake Probability</div>
            </div>
            <div class="metric-card">
                <div class="val">{real_prob:.1f}%</div>
                <div class="lbl">Credibility Prob</div>
            </div>
            <div class="metric-card">
                <div class="val">{confidence:.1f}%</div>
                <div class="lbl">AI Confidence</div>
            </div>
        </div>

        <div class="section-title">Machine Learning Classifier Vote Matrix</div>
        <table class="votes-table">
            <thead>
                <tr>
                    <th>Model Architecture</th>
                    <th>Feature Dimensions</th>
                    <th>Classifier Prediction</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Logistic Regression</strong></td>
                    <td>50,000 TF-IDF N-Grams</td>
                    <td><span style="font-weight:bold;">{lr_vote}</span></td>
                </tr>
                <tr>
                    <td><strong>Linear Support Vector Machine (LinearSVC)</strong></td>
                    <td>50,000 TF-IDF N-Grams</td>
                    <td><span style="font-weight:bold;">{svm_vote}</span></td>
                </tr>
                <tr>
                    <td><strong>Random Forest Ensemble (100 Trees)</strong></td>
                    <td>First 5,000 TF-IDF Features</td>
                    <td><span style="font-weight:bold;">{rf_vote}</span></td>
                </tr>
                <tr>
                    <td><strong>Semantic Transformer (BERT/RoBERTa)</strong></td>
                    <td>Contextual Attention (512 Tokens Max)</td>
                    <td><span style="font-weight:bold;">{trans_vote}</span></td>
                </tr>
                <tr style="background: #f1f5f9;">
                    <td><strong>Hybrid Multi-Branch Ensemble ({uncertainty_status})</strong></td>
                    <td>Calibrated Probability Fusion Layer</td>
                    <td><span style="font-weight:bold; color: #0f172a;">{ensemble_vote}</span></td>
                </tr>
            </tbody>
        </table>

        <div class="section-title">Submitted Document Text</div>
        <div style="font-size: 12px; color: #64748b; margin-bottom: 6px;">
            Headline: <strong>{headline}</strong> | Language: <strong>{detected_lang}</strong> | Source: <strong>{url}</strong>
        </div>
        <div class="text-box">{content or headline}</div>

        <div class="section-title">Extracted Factual Subclaims</div>
        {claims_html}

        <div class="section-title">External Evidence Corroboration & Citations</div>
        {evidence_html}

        <div class="disclaimer-box">
            <strong>RESEARCH & METHODOLOGICAL INTEGRITY DISCLAIMER:</strong><br>
            This forensic report is generated by automated statistical Natural Language Processing (NLP) models trained on the ISOT benchmark dataset and open web evidence queries. Model classifications and heuristic scores do not constitute definitive legal, medical, or factual proof. Always cross-reference high-consequence health, financial, and political claims with primary sources and certified fact-checking authorities.
        </div>
    </div>

    <div class="footer-actions">
        <span style="font-size: 12px; color: #64748b;">VeritasAI Platform v3.0 • Enterprise Forensic Audit</span>
        <button class="btn" onclick="window.print()">Print / Save as PDF</button>
    </div>
</div>
</body>
</html>"""


@router.get("/{scan_id}/export")
def export_scan_report(scan_id: str):
    """
    Download or print an official, self-contained HTML investigation certificate for a scan.
    """
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan ID '{scan_id}' not found.")

    html_content = _generate_html_report(scan)
    return HTMLResponse(
        content=html_content,
        headers={
            "Content-Disposition": f"inline; filename=veritas_investigation_{scan_id}.html"
        },
    )


@router.post("/investigation/export")
def export_investigation_report(payload: Dict[str, Any] = Body(...)):
    """
    Generate printable HTML certificate from a completed Research Agent investigation report.
    """
    inv_id = html.escape(str(payload.get("investigation_id") or "INV-REPORT"))
    status = html.escape(str(payload.get("overall_status") or "EVIDENCE_INSUFFICIENT"))
    verdict = html.escape(str(payload.get("overall_verdict") or "Investigation Completed"))
    timestamp = html.escape(str(payload.get("investigation_timestamp") or datetime.datetime.now(datetime.timezone.utc).isoformat()))

    claims_items = payload.get("claims") or []
    claims_html = ""
    for c in claims_items:
        cid = html.escape(str(c.get("claim_id") or "CLM"))
        c_text = html.escape(str(c.get("claim") or ""))
        c_assess = html.escape(str(c.get("assessment") or "Insufficient evidence"))
        c_code = html.escape(str(c.get("assessment_code") or "INSUFFICIENT_EVIDENCE"))
        c_expl = html.escape(str(c.get("explanation") or ""))

        badge_c = "#065f46" if "SUPPORT" in c_code else ("#991b1b" if "CONTRADICT" in c_code else "#92400e")
        badge_b = "#ecfdf5" if "SUPPORT" in c_code else ("#fee2e2" if "CONTRADICT" in c_code else "#fffbeb")

        ev_records = c.get("evidence_records") or []
        ev_sub_html = ""
        for ev in ev_records:
            s_title = html.escape(str(ev.get("source_title") or "Source"))
            s_url = html.escape(str(ev.get("url") or "#"))
            s_snip = html.escape(str(ev.get("excerpt") or ""))
            s_rel = html.escape(str(ev.get("relationship") or "context").upper())
            ev_sub_html += f"""
            <div style="margin-top: 6px; padding: 8px 10px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 11px;">
                <div style="display:flex; justify-content:space-between; font-weight:bold;">
                    <span>{s_title}</span>
                    <span style="font-family:monospace; color:#2563eb;">[{s_rel}]</span>
                </div>
                <p style="margin: 4px 0; color: #475569;">{s_snip}</p>
                <a href="{s_url}" target="_blank" style="color:#2563eb;">{s_url}</a>
            </div>
            """

        claims_html += f"""
        <div style="margin-bottom: 18px; padding: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                <span style="font-size: 11px; font-family: monospace; font-weight: bold; color: #64748b;">REF // {cid}</span>
                <span style="background:{badge_b}; color:{badge_c}; font-size: 11px; font-weight: bold; padding: 3px 10px; border-radius: 6px;">{c_assess}</span>
            </div>
            <h4 style="font-size: 13px; font-weight: bold; color: #0f172a; margin: 0 0 6px 0;">"{c_text}"</h4>
            <p style="font-size: 12px; color: #475569; margin: 0 0 10px 0;">{c_expl}</p>
            {ev_sub_html if ev_sub_html else "<p style='font-size: 11px; color:#94a3b8; font-style:italic;'>No primary evidence passages located.</p>"}
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>VeritasAI Research Agent Dossier — {inv_id}</title>
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f1f5f9; color: #0f172a; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 860px; margin: 0 auto; background: white; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; }}
    .header {{ background: #0f172a; color: white; padding: 32px 40px; display: flex; justify-content: space-between; align-items: center; }}
    .body {{ padding: 36px 40px; }}
    .banner {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 10px; margin-bottom: 24px; }}
    .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px 40px; display: flex; justify-content: space-between; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <h2 style="margin:0;">VeritasAI Grounded Research Dossier</h2>
            <p style="margin:4px 0 0; color:#94a3b8; font-size:12px;">Multi-Source Evidence Synthesis & Provenance Audit</p>
        </div>
        <span style="font-family:monospace; background:rgba(255,255,255,0.1); padding:6px 12px; border-radius:8px;">{inv_id}</span>
    </div>
    <div class="body">
        <div class="banner">
            <div style="font-size:12px; font-weight:bold; color:#64748b; text-transform:uppercase;">Overall Research Finding</div>
            <div style="font-size:16px; font-weight:bold; color:#0f172a; margin-top:4px;">{verdict}</div>
            <div style="font-size:11px; color:#94a3b8; font-family:monospace; margin-top:4px;">Generated: {timestamp}</div>
        </div>
        <h3 style="font-size:13px; font-weight:bold; text-transform:uppercase; color:#475569; border-bottom:2px solid #f1f5f9; padding-bottom:6px;">Audited Factual Assertions ({len(claims_items)})</h3>
        {claims_html}
    </div>
    <div class="footer">
        <span style="font-size:12px; color:#64748b;">VeritasAI v3.0 Evidence Intelligence Engine</span>
        <button onclick="window.print()" style="background:#2563eb; color:white; border:none; padding:8px 16px; border-radius:6px; font-weight:bold; cursor:pointer;">Print Dossier</button>
    </div>
</div>
</body>
</html>"""

    return HTMLResponse(content=html_content)
