package com.fakenews.detector.classifier;

import com.fakenews.detector.model.DomainReputation;
import com.fakenews.detector.model.DomainReputation.TrustLevel;

import java.net.URI;
import java.util.HashMap;
import java.util.Map;

/**
 * Evaluates the trustworthiness of news sources and website domains against authoritative registries.
 */
public class DomainCredibilityChecker {

    private static final Map<String, DomainReputation> DOMAIN_REGISTRY = new HashMap<>();

    static {
        // --- HIGHLY TRUSTED & VERIFIED SOURCES ---
        addDomain("reuters.com", TrustLevel.HIGHLY_TRUSTED, "International Wire News", "Global news agency with strict editorial standards.");
        addDomain("apnews.com", TrustLevel.HIGHLY_TRUSTED, "International Wire News", "Associated Press wire service.");
        addDomain("bbc.com", TrustLevel.HIGHLY_TRUSTED, "Public Broadcast Media", "British Broadcasting Corporation.");
        addDomain("bbc.co.uk", TrustLevel.HIGHLY_TRUSTED, "Public Broadcast Media", "British Broadcasting Corporation.");
        addDomain("nature.com", TrustLevel.HIGHLY_TRUSTED, "Scientific Journal", "Peer-reviewed scientific publications.");
        addDomain("who.int", TrustLevel.HIGHLY_TRUSTED, "Official Health Agency", "World Health Organization.");
        addDomain("cdc.gov", TrustLevel.HIGHLY_TRUSTED, "Official Health Agency", "Centers for Disease Control and Prevention.");
        addDomain("nasa.gov", TrustLevel.HIGHLY_TRUSTED, "Space & Science Agency", "National Aeronautics and Space Administration.");
        addDomain("snopes.com", TrustLevel.HIGHLY_TRUSTED, "Fact-Checking Outlet", "Dedicated fact-checking organization.");
        addDomain("factcheck.org", TrustLevel.HIGHLY_TRUSTED, "Fact-Checking Outlet", "Nonpartisan fact-checking organization.");
        addDomain("politifact.com", TrustLevel.HIGHLY_TRUSTED, "Fact-Checking Outlet", "Pulitzer Prize-winning fact-checking organization.");

        // --- GENERALLY RELIABLE OUTLETS ---
        addDomain("theguardian.com", TrustLevel.GENERALLY_RELIABLE, "Mainstream Journalism", "Established UK publication.");
        addDomain("nytimes.com", TrustLevel.GENERALLY_RELIABLE, "Mainstream Journalism", "The New York Times.");
        addDomain("washingtonpost.com", TrustLevel.GENERALLY_RELIABLE, "Mainstream Journalism", "The Washington Post.");
        addDomain("thehindu.com", TrustLevel.GENERALLY_RELIABLE, "Mainstream Journalism", "National newspaper of record.");
        addDomain("ndtv.com", TrustLevel.GENERALLY_RELIABLE, "Mainstream Journalism", "Major Indian news network.");
        addDomain("bloomberg.com", TrustLevel.GENERALLY_RELIABLE, "Financial Journalism", "Global business and financial data.");
        addDomain("wsj.com", TrustLevel.GENERALLY_RELIABLE, "Financial Journalism", "The Wall Street Journal.");
        addDomain("aljazeera.com", TrustLevel.GENERALLY_RELIABLE, "International News", "Middle East and global reporting.");
        addDomain("sciencedaily.com", TrustLevel.GENERALLY_RELIABLE, "Science News", "Aggregates peer-reviewed press releases.");

        // --- SATIRE / PARODY (Not real news) ---
        addDomain("theonion.com", TrustLevel.UNRELIABLE_OR_HOAX, "Satire & Parody", "Humorous satirical news site (not factual).");
        addDomain("babylonbee.com", TrustLevel.UNRELIABLE_OR_HOAX, "Satire & Parody", "Christian news satire site.");
        addDomain("clickhole.com", TrustLevel.UNRELIABLE_OR_HOAX, "Satire & Parody", "Clickbait parody publication.");
        addDomain("fakingnews.com", TrustLevel.UNRELIABLE_OR_HOAX, "Satire & Parody", "Indian satirical entertainment site.");
        addDomain("newsthump.com", TrustLevel.UNRELIABLE_OR_HOAX, "Satire & Parody", "UK satirical news website.");

        // --- KNOWN HOAX / CONSPIRACY / PROPAGANDA OUTLETS ---
        addDomain("infowars.com", TrustLevel.UNRELIABLE_OR_HOAX, "Conspiracy & Disinformation", "Known for fabricated claims and conspiracy theories.");
        addDomain("worldnewsdailyreport.com", TrustLevel.UNRELIABLE_OR_HOAX, "Fabricated News", "Publishes fabricated hoax stories.");
        addDomain("beforeitsnews.com", TrustLevel.UNRELIABLE_OR_HOAX, "Unverified / Conspiracy", "User-submitted unvetted conspiracy content.");
        addDomain("naturalnews.com", TrustLevel.UNRELIABLE_OR_HOAX, "Health Misinformation", "Pseudoscience and unproven medical claims.");
        addDomain("yournewswire.com", TrustLevel.UNRELIABLE_OR_HOAX, "Fake News Syndicate", "Frequently debunked misinformation site.");
        addDomain("empirenews.net", TrustLevel.UNRELIABLE_OR_HOAX, "Fabricated Hoaxes", "Sensationalist fake news generator.");
        addDomain("nationalreport.net", TrustLevel.UNRELIABLE_OR_HOAX, "Fake News / Hoax", "Fabricated sensational headlines.");
    }

    private static void addDomain(String domain, TrustLevel level, String cat, String notes) {
        DOMAIN_REGISTRY.put(domain.toLowerCase(), new DomainReputation(domain, level, cat, notes));
    }

    /**
     * Extracts domain from full URL or domain string and checks its reputation.
     */
    public static DomainReputation checkDomain(String urlOrDomain) {
        if (urlOrDomain == null || urlOrDomain.trim().isEmpty()) {
            return null;
        }

        String domain = extractDomain(urlOrDomain);
        if (domain.isEmpty()) {
            return new DomainReputation(urlOrDomain, TrustLevel.UNKNOWN_DOMAIN, "Unspecified", "Could not parse domain.");
        }

        // Direct match
        if (DOMAIN_REGISTRY.containsKey(domain)) {
            return DOMAIN_REGISTRY.get(domain);
        }

        // Subdomain check (e.g. news.bbc.co.uk -> bbc.co.uk)
        for (String registered : DOMAIN_REGISTRY.keySet()) {
            if (domain.endsWith("." + registered)) {
                return DOMAIN_REGISTRY.get(registered);
            }
        }

        // Suspicious TLD / Spoofing heuristics
        if (domain.endsWith(".xyz") || domain.endsWith(".top") || domain.endsWith(".click") || domain.endsWith(".buzz") || domain.endsWith(".vu")) {
            return new DomainReputation(domain, TrustLevel.QUESTIONABLE, "Suspicious TLD", "Unusual top-level domain often associated with throwaway clickbait sites.");
        }

        // Check for spoofed popular names like "bbc-news-live.com"
        String[] famousBrands = {"bbc", "cnn", "nytimes", "reuters", "who", "cdc", "nasa"};
        for (String brand : famousBrands) {
            if (domain.contains(brand) && !DOMAIN_REGISTRY.containsKey(domain)) {
                return new DomainReputation(domain, TrustLevel.QUESTIONABLE, "Potential Domain Impersonation", "Domain contains brand name '" + brand + "' but does not match official registered servers.");
            }
        }

        return new DomainReputation(domain, TrustLevel.UNKNOWN_DOMAIN, "Independent / Unregistered", "Not in current verified media database. Validate content carefully.");
    }

    public static String extractDomain(String input) {
        if (input == null) return "";
        String s = input.trim().toLowerCase();
        if (!s.startsWith("http://") && !s.startsWith("https://")) {
            s = "https://" + s;
        }
        try {
            URI uri = new URI(s);
            String host = uri.getHost();
            if (host != null) {
                if (host.startsWith("www.")) {
                    host = host.substring(4);
                }
                return host;
            }
        } catch (Exception ignored) {
        }
        return input.replaceAll("^(https?://)?(www\\.)?", "").split("/")[0];
    }
}
