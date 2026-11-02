export const APP_NAME = "VERITAS AI";
export const APP_TAGLINE = "Advanced Fake News & Misinformation Intelligence Platform";
export const APP_VERSION = "2.5.0-ENTERPRISE";

export const PIPELINE_STEPS = [
  "Validating input & source metadata",
  "Extracting assertions & claim statements",
  "Sanitizing & tokenizing text corpus",
  "Running NLP syntactic & readability analysis",
  "Evaluating clickbait patterns & curiosity gaps",
  "Detecting emotional manipulation & outrage triggers",
  "Executing Scikit-learn Machine Learning models",
  "Computing multi-factor composite risk matrix",
  "Synthesizing explainable AI forensic rationale",
  "Generating audit certificate & verification report"
];

export const PRESET_SAMPLES = [
  {
    id: "real-1",
    label: "📰 NASA: Webb Telescope Oldest Galaxy (Verified Real)",
    category: "Science",
    url: "https://www.nasa.gov/news/webb-galaxy-discovery",
    headline: "NASA James Webb Space Telescope discovers oldest known galaxy in universe",
    content: "Astronomers using NASA James Webb Space Telescope have identified the most distant and oldest galaxy ever observed, dating back just 300 million years after the Big Bang. The research was published in the journal Nature following extensive peer-reviewed data analysis from international astrophysical observatories."
  },
  {
    id: "real-2",
    label: "🧬 WHO: Clinical Guidelines for Hypertension (Verified Real)",
    category: "Health",
    url: "https://www.who.int/news/hypertension-guidelines",
    headline: "World Health Organization releases updated clinical guidelines for hypertension management",
    content: "The World Health Organization (WHO) released new pharmacological and lifestyle guidelines for treating adult hypertension. The comprehensive report emphasizes early screening, balanced dietary habits, regular cardiovascular exercise, and structured medication compliance."
  },
  {
    id: "fake-1",
    label: "⚠️ Medical Hoax: Lemon Peel Dissolves Cancer (Fake / Danger)",
    category: "Health Hoax",
    url: "http://natural-miracle-cures.xyz/lemon-secret",
    headline: "SHOCKING TRUTH: Doctors HATE this secret lemon peel cure that destroys ALL diseases overnight!!!",
    content: "Big Pharma and corrupt hospital doctors are panicking because this ancient secret miracle home remedy dissolves cancer, diabetes, and heart disease in just 24 hours! The government is trying to ban this video before it gets deleted! Share urgently with everyone you know before it's taken down!"
  },
  {
    id: "fake-2",
    label: "👽 Conspiracy: Illuminati Apocalypse Leaked Audio (Fake)",
    category: "Conspiracy",
    url: "http://infowars-leaks.top/apocalypse-audio",
    headline: "LEAKED AUDIO: Secret Illuminati council meeting reveals world will end next Friday!!",
    content: "Unbelievable leaked classified documents and top secret audio prove that world leaders and the Illuminati have already built underground bunkers for the upcoming alien invasion and doomsday catastrophe! Mainstream media is covering up the shocking truth!"
  },
  {
    id: "fake-3",
    label: "💰 Financial Scam: 50,000 Free Bitcoin Giveaway (Fake)",
    category: "Crypto Scam",
    url: "https://crypto-giveaway-daily.click/free-btc",
    headline: "Famous billionaire gives away 50,000 free bitcoins to anyone who visits this website link right now!",
    content: "In an unscripted shocking live television interview, the tech billionaire accidentally revealed a secret algorithmic loop hole that allows anyone to generate $10,000 daily from home with zero investment! Banks tried to stop the broadcast! Tap here now to claim your grant!"
  }
];

export const RISK_LEVELS = {
  LOW: {
    label: "LOW RISK",
    color: "#10b981",
    badgeBg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    recommendation: "Content appears relatively low-risk and structured with standard journalistic tone. Independent verification is still good practice."
  },
  MODERATE: {
    label: "MODERATE RISK",
    color: "#f59e0b",
    badgeBg: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    recommendation: "Exercise caution. Content contains moderate emotional or sensationalist markers. Verify claims with trusted primary sources."
  },
  HIGH: {
    label: "HIGH RISK",
    color: "#f97316",
    badgeBg: "bg-orange-500/10 text-orange-400 border-orange-500/30",
    recommendation: "Multiple suspicious manipulation indicators detected. Do not distribute or rely upon without thorough fact-checking."
  },
  CRITICAL: {
    label: "CRITICAL RISK",
    color: "#ef4444",
    badgeBg: "bg-rose-500/10 text-rose-400 border-rose-500/30",
    recommendation: "Strong misinformation patterns, hyperbole, or known fabricated claims detected. High probability of deception."
  }
};
