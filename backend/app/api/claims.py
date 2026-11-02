"""
claims.py
=========
FastAPI routes for Claim Intelligence, AI Research Agent Investigation,
Claim Relationship Graph Generation, and Fact-Check Archive Search in VeriNews AI 3.0.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.services import (
    claim_verification_service,
    research_agent_service,
    claim_graph_service,
    factcheck_service,
)

router = APIRouter()


class VerifyClaimRequest(BaseModel):
    claim: str = Field(..., min_length=3, description="Claim or statement to verify against evidence repositories")


class ExtractClaimsRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Full news text from which to extract candidate factual assertions")
    max_claims: Optional[int] = Field(5, ge=1, le=10, description="Maximum number of claims to extract")


class ResearchInvestigationRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Claim or article text to investigate")
    headline: Optional[str] = Field(None, description="Optional article headline")
    url: Optional[str] = Field(None, description="Optional canonical URL")
    max_claims: Optional[int] = Field(4, ge=1, le=8, description="Maximum checkable claims to extract")


class BuildGraphRequest(BaseModel):
    investigation: Dict[str, Any] = Field(..., description="Completed investigation object from /api/claims/research")


class FactCheckSearchRequest(BaseModel):
    claim: str = Field(..., min_length=3, description="Claim statement or headline to query in fact-check wires")
    max_results: Optional[int] = Field(5, ge=1, le=15, description="Maximum matches to return")


@router.post("/verify")
def verify_claim(req: VerifyClaimRequest) -> Dict[str, Any]:
    """
    Search legitimate open sources (Wikipedia OpenSearch, DuckDuckGo) for evidence
    corroborating, contradicting, or contextualizing a single factual claim.
    """
    if not req.claim or not req.claim.strip():
        raise HTTPException(status_code=400, detail="Claim text is required.")

    return claim_verification_service.verify_single_claim(req.claim)


@router.post("/extract")
def extract_claims(req: ExtractClaimsRequest) -> Dict[str, Any]:
    """
    Isolate candidate factual assertions from a news article or user text.
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is required.")

    claims = claim_verification_service.extract_factual_claims_from_text(
        text=req.text,
        max_claims=req.max_claims or 5,
    )

    return {
        "text_length": len(req.text),
        "claims_extracted": len(claims),
        "claims": claims,
    }


@router.post("/research")
def conduct_research_investigation(req: ResearchInvestigationRequest) -> Dict[str, Any]:
    """
    Execute full multi-step AI Research Agent workflow:
    1. Preserves input.
    2. Identifies distinct checkable factual claims, separated from opinion/rhetoric.
    3. Queries open knowledge bases and fact-check wires.
    4. Evaluates evidence relationships (supports, contradicts, provides_context, unresolved).
    5. Returns claim-level assessments and citations without conflating ML predictions with factual truth.
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text or claim is required.")

    return research_agent_service.execute_research_workflow(
        text=req.text,
        headline=req.headline,
        url=req.url,
        max_claims=req.max_claims or 4,
    )


@router.post("/graph")
def generate_claim_graph(req: BuildGraphRequest) -> Dict[str, Any]:
    """
    Construct interactive Claim Relationship Graph from an actual investigation report.
    Returns typed nodes (claim, article, publisher, primary_source, fact_check) and edges
    with provenance and syndication markers.
    """
    if not req.investigation or not isinstance(req.investigation, dict):
        raise HTTPException(status_code=400, detail="Valid investigation object required.")

    return claim_graph_service.build_graph_from_investigation(req.investigation)


@router.post("/factcheck")
def search_factchecks(req: FactCheckSearchRequest) -> Dict[str, Any]:
    """
    Query official Google Fact Check Tools API and open-access fact-check wires (GDELT, Alt News, BOOM)
    for previously verified claims. Preserves exact ratings and publisher citations.
    """
    if not req.claim or not req.claim.strip():
        raise HTTPException(status_code=400, detail="Claim text is required.")

    return factcheck_service.search_existing_factchecks(
        claim_text=req.claim,
        max_results=req.max_results or 5,
    )
