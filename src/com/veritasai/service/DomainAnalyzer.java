package com.veritasai.service;

import com.fakenews.detector.classifier.DomainCredibilityChecker;
import com.fakenews.detector.model.DomainReputation;
import com.veritasai.model.DomainAnalysis;
import com.veritasai.util.Constants.RiskLevel;
import com.veritasai.util.ValidationUtils;

/**
 * Inspects domain structures, heuristic risk indicators, HTTPS protocols, and registered reputation.
 */
public class DomainAnalyzer {

    public static DomainAnalysis analyze(String urlOrDomain) {
        if (urlOrDomain == null || urlOrDomain.trim().isEmpty()) {
            DomainAnalysis empty = new DomainAnalysis("");
            empty.setSourceTrustScore(50.0);
            empty.setRiskLevel(RiskLevel.LOW);
            empty.setEditorialCategory("No Domain Specified");
            empty.setAssessmentSummary("Text-only scan; no source URL evaluated.");
            return empty;
        }

        String domain = DomainCredibilityChecker.extractDomain(urlOrDomain);
        DomainAnalysis da = new DomainAnalysis(domain);
        da.setHasHttps(ValidationUtils.isHttps(urlOrDomain));
        da.setDomainLength(domain.length());

        // Subdomain count
        String[] parts = domain.split("\\.");
        da.setSubdomainCount(Math.max(0, parts.length - 2));

        // URL Structure
        da.setUrlStructure((da.isHasHttps() ? "https://" : "http://") + domain);

        // Registry lookup
        DomainReputation rep = DomainCredibilityChecker.checkDomain(domain);
        if (rep != null) {
            da.setEditorialCategory(rep.getCategory());
            switch (rep.getTrustLevel()) {
                case HIGHLY_TRUSTED:
                    da.setSourceTrustScore(95.0);
                    da.setRiskLevel(RiskLevel.LOW);
                    da.setAssessmentSummary("Verified authoritative international journalism/science publisher (" + rep.getDomain() + ").");
                    break;
                case GENERALLY_RELIABLE:
                    da.setSourceTrustScore(80.0);
                    da.setRiskLevel(RiskLevel.LOW);
                    da.setAssessmentSummary("Established media outlet with recognized editorial oversight (" + rep.getDomain() + ").");
                    break;
                case UNRELIABLE_OR_HOAX:
                    da.setSourceTrustScore(10.0);
                    da.setRiskLevel(RiskLevel.CRITICAL);
                    da.addSuspiciousIndicator("Cataloged hoax / satire / fabricated news domain.");
                    da.setAssessmentSummary("CRITICAL WARNING: Domain is cataloged as a known source of hoaxes or satire.");
                    break;
                case QUESTIONABLE:
                    da.setSourceTrustScore(35.0);
                    da.setRiskLevel(RiskLevel.HIGH);
                    da.addSuspiciousIndicator("Domain contains impersonation or questionable editorial history.");
                    da.setAssessmentSummary("High risk domain pattern detected.");
                    break;
                default:
                    evaluateHeuristics(domain, da);
                    break;
            }
        } else {
            evaluateHeuristics(domain, da);
        }

        return da;
    }

    private static void evaluateHeuristics(String domain, DomainAnalysis da) {
        double trust = 60.0;

        // 1. Excessive hyphens (often used in phishing/impersonation)
        int hyphenCount = domain.length() - domain.replace("-", "").length();
        if (hyphenCount >= 2) {
            trust -= 20.0;
            da.addSuspiciousIndicator("Multiple hyphens in domain name (common in impersonator domains).");
        }

        // 2. Suspicious TLD
        if (domain.endsWith(".xyz") || domain.endsWith(".top") || domain.endsWith(".click") || domain.endsWith(".buzz") || domain.endsWith(".vu")) {
            trust -= 25.0;
            da.addSuspiciousIndicator("Unusual top-level domain extension (often associated with disposable spam sites).");
        }

        // 3. Deep subdomains (> 2)
        if (da.getSubdomainCount() > 2) {
            trust -= 15.0;
            da.addSuspiciousIndicator("Excessive subdomain depth (" + da.getSubdomainCount() + " levels).");
        }

        // 4. Missing HTTPS
        if (!da.isHasHttps()) {
            trust -= 10.0;
            da.addSuspiciousIndicator("Connection is not secured via HTTPS.");
        }

        da.setSourceTrustScore(Math.max(5.0, Math.min(100.0, trust)));

        if (trust >= 70.0) {
            da.setRiskLevel(RiskLevel.LOW);
            da.setAssessmentSummary("Independent domain with standard structural markers.");
        } else if (trust >= 45.0) {
            da.setRiskLevel(RiskLevel.MODERATE);
            da.setAssessmentSummary("Unregistered domain with moderate heuristic indicators.");
        } else {
            da.setRiskLevel(RiskLevel.HIGH);
            da.setAssessmentSummary("Domain exhibits multiple heuristic risk factors. Verify independently.");
        }
    }
}
