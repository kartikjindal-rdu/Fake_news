import re
from typing import List
from app.schemas.analysis import ClaimItem

def extract_claims(headline: str, body: str, fake_prob: float) -> List[ClaimItem]:
    combined = f"{headline or ''}. {body or ''}"
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', combined) if len(s.strip()) > 20]
    claims = []

    for idx, s in enumerate(sentences[:3]):
        status = "Requires Verification"
        if fake_prob > 65:
            status = "Conflicting Evidence"
        elif fake_prob < 35:
            status = "Supported Evidence"

        risk_level = "HIGH" if fake_prob > 50 else ("MODERATE" if fake_prob > 25 else "LOW")

        claims.append(ClaimItem(
            id=f"claim-{idx + 1}",
            text=s,
            importance="Primary Assertion" if idx == 0 else "Supporting Claim",
            riskLevel=risk_level,
            verificationStatus=status
        ))

    if not claims and combined.strip():
        claims.append(ClaimItem(
            id="claim-1",
            text=combined.strip()[:100] + "...",
            importance="Core Claim Statement",
            riskLevel="MODERATE",
            verificationStatus="Requires Verification"
        ))

    return claims
