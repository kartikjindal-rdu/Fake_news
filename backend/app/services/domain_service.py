import re
from urllib.parse import urlparse

TRUSTED_DOMAINS = {
    "reuters.com": ("Verified Authoritative International Wire Agency", 95),
    "apnews.com": ("Associated Press Wire Service", 95),
    "bbc.com": ("Public Broadcast Media", 90),
    "nature.com": ("Peer-Reviewed Scientific Journal", 98),
    "who.int": ("World Health Organization", 98),
    "nasa.gov": ("National Aeronautics & Space Administration", 98),
    "thehindu.com": ("National Newspaper of Record", 88),
    "bloomberg.com": ("Financial & Market Journalism", 88)
}

HOAX_DOMAINS = {
    "infowars.com": ("Cataloged Disinformation / Conspiracy Outlet", 15),
    "naturalnews.com": ("Pseudoscience & Unproven Medical Claims", 15),
    "beforeitsnews.com": ("Unverified User Conspiracy Feed", 20),
    "worldnewsdailyreport.com": ("Fabricated Satire / Hoax Syndicate", 10)
}

def analyze_domain(url: str) -> dict:
    if not url:
        return {
            "name": "Direct Input",
            "hasHttps": False,
            "trustScore": 50.0,
            "category": "Text-only scan; no source URL provided.",
            "riskLevel": "LOW RISK"
        }

    clean = url.lower().strip()
    if not clean.startswith("http://") and not clean.startswith("https://"):
        clean = "https://" + clean

    parsed = urlparse(clean)
    host = parsed.netloc.replace("www.", "")

    has_https = url.lower().startswith("https://")
    category = "Independent / Unregistered Domain"
    trust_score = 55.0

    if host in TRUSTED_DOMAINS:
        category, trust_score = TRUSTED_DOMAINS[host]
    elif host in HOAX_DOMAINS:
        category, trust_score = HOAX_DOMAINS[host]
    elif any(host.endswith(tld) for tld in [".xyz", ".top", ".click", ".buzz", ".vu"]):
        category = "Suspicious Disposable Top-Level Domain"
        trust_score = 25.0

    risk_level = "LOW RISK"
    if trust_score < 40:
        risk_level = "CRITICAL RISK"
    elif trust_score < 65:
        risk_level = "MODERATE RISK"

    return {
        "name": host,
        "hasHttps": has_https,
        "trustScore": trust_score,
        "category": category,
        "riskLevel": risk_level
    }
