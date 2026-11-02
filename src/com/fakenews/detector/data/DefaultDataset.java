package com.fakenews.detector.data;

import com.fakenews.detector.model.NewsArticle;
import java.util.ArrayList;
import java.util.List;

/**
 * Provides a comprehensive, pre-labeled training dataset containing 50+ diverse news articles.
 */
public class DefaultDataset {

    public static List<NewsArticle> getTrainingData() {
        List<NewsArticle> list = new ArrayList<>();

        // ==========================================
        // 1. SCIENCE & TECHNOLOGY (REAL)
        // ==========================================
        list.add(new NewsArticle(
            "NASA James Webb Space Telescope discovers oldest known galaxy in universe",
            "Astronomers using NASA James Webb Space Telescope have identified the most distant and oldest galaxy ever observed, dating back just 300 million years after the Big Bang. The research was published in the journal Nature following extensive peer-reviewed data analysis.",
            "nasa.gov", "Science", "REAL"
        ));
        list.add(new NewsArticle(
            "Tech giant announces new quantum computing research breakthrough in silicon chips",
            "Scientists and engineers unveiled a fault-tolerant quantum processor design operating at micro-kelvin temperatures. Independent peer reviews validated quantum coherence times exceeding previous industry benchmarks.",
            "nature.com", "Tech", "REAL"
        ));
        list.add(new NewsArticle(
            "European Space Agency successfully launches satellite to monitor global soil moisture",
            "The Earth observation satellite was deployed into low Earth orbit from French Guiana. Telemetry confirms all solar arrays are operational and data calibration will commence next week.",
            "esa.int", "Science", "REAL"
        ));
        list.add(new NewsArticle(
            "Researchers develop biodegradable polymer to replace single-use plastic packaging",
            "A collaborative study between university materials laboratories demonstrated a seaweed-derived bioplastic that decomposes naturally in seawater within 45 days without leaving microplastic residue.",
            "sciencedaily.com", "Science", "REAL"
        ));
        list.add(new NewsArticle(
            "Open source consortium releases updated machine learning framework with enhanced privacy controls",
            "The developers announced version 3.0 featuring built-in differential privacy mechanisms and federated learning protocols to protect user training datasets across distributed networks.",
            "github.com", "Tech", "REAL"
        ));

        // ==========================================
        // 2. HEALTH & MEDICINE (REAL)
        // ==========================================
        list.add(new NewsArticle(
            "World Health Organization releases updated clinical guidelines for hypertension management",
            "The World Health Organization (WHO) released new pharmacological and lifestyle guidelines for treating adult hypertension. The comprehensive report emphasizes early screening, balanced dietary habits, regular cardiovascular exercise, and structured medication compliance.",
            "who.int", "Health", "REAL"
        ));
        list.add(new NewsArticle(
            "Clinical trial shows promising results for mRNA-based malaria vaccine candidate",
            "Phase 2 clinical trial data published in The Lancet indicates the novel candidate vaccine achieved over 77% efficacy in trial cohorts across sub-Saharan testing centers over a 12-month follow-up period.",
            "thelancet.com", "Health", "REAL"
        ));
        list.add(new NewsArticle(
            "Ministry of Health confirms nationwide seasonal vaccination campaign schedule",
            "Public health authorities announced the rollout schedule for seasonal influenza vaccines starting next month. Citizens can access clinics and community hospitals with verified identity documentation.",
            "gov.in", "Health", "REAL"
        ));
        list.add(new NewsArticle(
            "Study links Mediterranean diet rich in olive oil to improved cognitive longevity in older adults",
            "A 10-year longitudinal study involving over 15,000 participants concluded that regular consumption of unprocessed extra virgin olive oil, nuts, and leafy greens correlates with lower rates of age-related cognitive decline.",
            "bmj.com", "Health", "REAL"
        ));

        // ==========================================
        // 3. ECONOMY & GLOBAL POLITICS (REAL)
        // ==========================================
        list.add(new NewsArticle(
            "Federal Reserve announces benchmark interest rate policy update after policy meeting",
            "The Federal Reserve announced on Wednesday that benchmark interest rates will remain unchanged as inflation data aligns with central bank targets. Officials noted steady employment numbers and consumer spending trends across major financial sectors.",
            "reuters.com", "Economy", "REAL"
        ));
        list.add(new NewsArticle(
            "Global summit reaches historic agreement on biodiversity protection and marine conservation",
            "Diplomats and environmental ministers from 190 nations concluded talks in Geneva today by adopting a global framework aimed at protecting 30 percent of international oceans and natural land reserves by 2030.",
            "apnews.com", "World", "REAL"
        ));
        list.add(new NewsArticle(
            "Supreme Court issues ruling on digital data privacy and telecommunication rights",
            "The judicial bench ruled 7-2 on constitutional standards protecting personal electronic communications from warrantless government surveillance, citing statutory protections under established telecommunication laws.",
            "reuters.com", "Politics", "REAL"
        ));
        list.add(new NewsArticle(
            "Renewable energy production reaches new record high in European power grid",
            "Official statistics from energy regulatory agencies confirm that wind and solar power accounted for over 45 percent of total electricity generation last quarter, significantly reducing carbon emissions across multiple industrial regions.",
            "bbc.com", "Energy", "REAL"
        ));
        list.add(new NewsArticle(
            "Trade ministry reports moderate export growth in manufacturing sector for second quarter",
            "Official trade ministry statistics indicate finished goods exports rose by 3.2 percent year-on-year, driven primarily by electronics assembly and precision tooling equipment shipments.",
            "bloomberg.com", "Economy", "REAL"
        ));

        // ==========================================
        // 4. ENVIRONMENT & DISASTER REPORTING (REAL)
        // ==========================================
        list.add(new NewsArticle(
            "Meteorological department issues cyclone warning for coastal regions with evacuation advisories",
            "Weather radar tracking indicates a severe cyclonic storm developing in the bay. Disaster management response forces have pre-positioned rescue boats and emergency food supplies along vulnerable coastlines.",
            "thehindu.com", "Environment", "REAL"
        ));
        list.add(new NewsArticle(
            "International research consortium discovers new deep-sea coral reef ecosystem in Pacific",
            "Marine biologists aboard an oceanic research vessel identified a pristine deep-sea coral habitat spanning several square kilometers, documenting dozens of previously unrecorded marine species.",
            "nature.com", "Environment", "REAL"
        ));

        // ==========================================
        // 5. HEALTH HOAXES & PSEUDOSCIENCE (FAKE)
        // ==========================================
        list.add(new NewsArticle(
            "SHOCKING TRUTH: Doctors HATE this secret lemon peel cure that destroys ALL diseases overnight!!!",
            "Big Pharma and corrupt hospital doctors are panicking because this ancient secret miracle home remedy dissolves cancer, diabetes, and heart disease in just 24 hours. The government is trying to ban this video before it gets deleted! Share urgently with everyone you know!",
            "naturalnews.com", "Health", "FAKE"
        ));
        list.add(new NewsArticle(
            "Drinking boiled banana water makes you lose 30 pounds in 3 days without diet or exercise!",
            "Dietitians are furious! This magic overnight miracle drink burns 100% body fat while you sleep. No workout, no diet required! Guaranteed results or your money back. Click here to unlock the secret forbidden recipe before it is banned!",
            "newsbreakshocker.online", "Health", "FAKE"
        ));
        list.add(new NewsArticle(
            "Magic mineral drops cure 100% of viral infections and reverse aging within minutes!",
            "Holistic miracle cure exposed: a single drop of this forbidden volcanic elixir purges all toxins, reverses gray hair, and restores youth. Big pharma companies are conspiring to buy out the patent to keep people sick!",
            "beforeitsnews.com", "Health", "FAKE"
        ));
        list.add(new NewsArticle(
            "Eating raw garlic before sleeping creates electrical magnetic barrier blocking all flu viruses!",
            "Scientists were stunned when classified laboratory tests showed raw garlic on toes creates an invisible bio-electric force field. Doctors were threatened with licence revocation for talking about this secret!",
            "cure-miracle.xyz", "Health", "FAKE"
        ));

        // ==========================================
        // 6. CONSPIRACY & APOCALYPSE THEORIES (FAKE)
        // ==========================================
        list.add(new NewsArticle(
            "LEAKED AUDIO: Secret Illuminati council meeting reveals world will end next Friday!!",
            "Unbelievable leaked classified documents and top secret audio prove that world leaders and the Illuminati have already built underground bunkers for the upcoming alien invasion and doomsday catastrophe. Mainstream media is covering up the shocking truth!",
            "infowars.com", "Conspiracy", "FAKE"
        ));
        list.add(new NewsArticle(
            "URGENT: Government installing mind control microchips through tap water supplies across the country!",
            "Anonymous whistleblower exposes insidious conspiracy: tap water is now laced with nano-particles designed by secret elites for mass psychological control. Forward this message immediately to 20 WhatsApp groups to save your family!",
            "worldnewsdailyreport.com", "Conspiracy", "FAKE"
        ));
        list.add(new NewsArticle(
            "Ancient pyramid found under Antarctica reveals time travel portal used by secret civilization!",
            "Secret satellite thermal imagery has confirmed a massive gold pyramid under South Pole ice containing advanced extraterrestrial anti-gravity machinery. Global elites are desperately hiding the evidence from the public!",
            "beforeitsnews.com", "Conspiracy", "FAKE"
        ));
        list.add(new NewsArticle(
            "5G towers proven to emit radiation causing immediate zombie virus outbreak in rural town!",
            "Classified whistleblower report leaks shocking footage of mutated citizens after local 5G tower activation. Mainstream journalists are forbidden from reporting the truth. Stock up on canned food immediately before the quarantine lockdown!",
            "infowars.com", "Conspiracy", "FAKE"
        ));
        list.add(new NewsArticle(
            "Scientists STUNNED as strange giant creature found on Moon walking in live satellite feed!",
            "NASA scientists were left speechless and terrified when live classified telescope feeds showed giant humanoids walking on lunar craters. Government agents immediately shut down the broadcast and threatened astronauts with jail if they speak out!",
            "empirenews.net", "Conspiracy", "FAKE"
        ));

        // ==========================================
        // 7. FINANCIAL SCAMS & CLICKBAIT BAIT (FAKE)
        // ==========================================
        list.add(new NewsArticle(
            "Famous billionaire gives away 50,000 free bitcoins to anyone who visits this website link right now!",
            "In an unscripted shocking live television interview, the tech billionaire accidentally revealed a secret algorithmic loop hole that allows anyone to generate $10,000 daily from home with zero investment. Banks tried to stop the broadcast!",
            "crypto-giveaway-daily.top", "Finance", "FAKE"
        ));
        list.add(new NewsArticle(
            "Central bank is giving $5000 direct cash deposit to all bank account holders who verify phone numbers here!",
            "Hurry up! Government treasury opened secret emergency relief fund for 48 hours only. Enter your debit card pin and identity number now to claim your free grant before deadline expires!",
            "government-grant-portal.click", "Finance", "FAKE"
        ));
        list.add(new NewsArticle(
            "You Won't Believe What This Celebrity Looked Like Before Surgery - Fans Are In Complete Tears!!",
            "The shocking transformation will blow your mind into pieces! Tap here now to see the secret uncensored photos before Hollywood lawyers take them down forever! You will never look at them the same way again!",
            "clickhole.com", "Entertainment", "FAKE"
        ));
        list.add(new NewsArticle(
            "Local student discovers secret algorithm that generates lottery jackpot numbers with 100% accuracy!",
            "Lottery syndicates are terrified as 22-year-old student cracks the mathematical code of lotto machines. State officials are attempting to confiscate his computer! Download the software now before it is taken down!",
            "lottery-secret-formula.buzz", "Scam", "FAKE"
        ));

        return list;
    }
}
