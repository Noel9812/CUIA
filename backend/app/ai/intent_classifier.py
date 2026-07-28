"""
Weighted Intent Classifier — comprehensive keyword taxonomy with scored routing.

Improvements in this version:
- Synonym normalization before classification (overworked→overutilized, etc.)
- Greeting/conversational detection (no analytics invoked)
- Expanded keyword groups covering all natural language variations
- Structured logging of classification decisions
"""

import logging
import re
from typing import Dict, Tuple, Optional

from app.ai.synonym_engine import SynonymEngine

logger = logging.getLogger("cuia.ai.intent")

# ──────────────────────────────────────────────
# Scoring thresholds
# ──────────────────────────────────────────────

MIN_CONFIDENCE_SCORE = 2
AMBIGUITY_MARGIN = 1
MALICIOUS_INSTANT_THRESHOLD = 1

# ──────────────────────────────────────────────
# Weight tiers
# ──────────────────────────────────────────────

W_STRONG = 3
W_MEDIUM = 2
W_WEAK = 1

# ──────────────────────────────────────────────
# Greeting / Conversational patterns (Part 17)
# ──────────────────────────────────────────────

GREETING_PATTERNS = [
    "hello", "hi", "hey", "howdy", "good morning", "good afternoon",
    "good evening", "good night", "greetings", "yo", "sup", "what's up",
    "whats up", "hiya", "hi there", "hello there", "hey there",
]

FAREWELL_PATTERNS = [
    "bye", "goodbye", "good bye", "see you", "see ya", "later",
    "take care", "farewell", "catch you later", "cya", "ttyl",
]

GRATITUDE_PATTERNS = [
    "thanks", "thank you", "thx", "ty", "appreciate it", "much appreciated",
    "thanks a lot", "thank you so much", "cheers",
]

IDENTITY_PATTERNS = [
    "who are you", "what are you", "what can you do", "what do you do",
    "how can you help", "what is cuia", "what's cuia", "tell me about yourself",
    "introduce yourself", "your name", "what is your name",
]

SMALLTALK_PATTERNS = [
    "how are you", "how r u", "how's it going", "how do you do",
    "nice to meet you", "pleased to meet you", "what's new",
]

CONVERSATIONAL_GROUPS = {
    "greeting": GREETING_PATTERNS,
    "farewell": FAREWELL_PATTERNS,
    "gratitude": GRATITUDE_PATTERNS,
    "identity": IDENTITY_PATTERNS,
    "smalltalk": SMALLTALK_PATTERNS,
}

# ──────────────────────────────────────────────
# Analytics Keywords
# ──────────────────────────────────────────────

ANALYTICS_KEYWORDS: list[tuple[str, int]] = [
    # Capacity & Utilization
    ("capacity utilization", W_STRONG), ("resource utilization", W_STRONG),
    ("utilization rate", W_STRONG), ("capacity allocation", W_STRONG),
    ("resource allocation", W_STRONG), ("capacity metrics", W_STRONG),
    ("engineering capacity", W_STRONG), ("team capacity", W_STRONG),
    ("resource capacity", W_STRONG), ("available capacity", W_STRONG),
    ("remaining capacity", W_STRONG), ("capacity gap", W_MEDIUM),
    ("over capacity", W_STRONG), ("under capacity", W_STRONG),
    ("utilization", W_MEDIUM), ("capacity", W_WEAK),

    # Overutilization / Underutilization (canonical forms from SynonymEngine)
    ("overutilized", W_STRONG), ("underutilized", W_STRONG),
    ("overworked", W_STRONG), ("overloaded", W_STRONG),
    ("underworked", W_STRONG),
    ("too much work", W_STRONG), ("high workload", W_STRONG),
    ("low workload", W_STRONG), ("heavy workload", W_STRONG),
    ("spare capacity", W_STRONG), ("excess capacity", W_STRONG),
    ("swamped", W_STRONG), ("overwhelmed", W_STRONG),
    ("stretched thin", W_STRONG), ("maxed out", W_STRONG),
    ("overburdened", W_STRONG),

    # Allocation & Availability
    ("allocation", W_MEDIUM), ("resource planning", W_MEDIUM),
    ("work distribution", W_STRONG), ("workload distribution", W_STRONG),
    ("availability", W_MEDIUM), ("free engineers", W_STRONG),
    ("available engineers", W_STRONG), ("idle engineers", W_STRONG),
    ("busy engineers", W_STRONG), ("overloaded engineers", W_STRONG),
    ("unassigned", W_MEDIUM), ("workload", W_MEDIUM),
    ("resource usage", W_MEDIUM), ("on bench", W_STRONG),
    ("bench engineers", W_STRONG), ("idle", W_MEDIUM),

    # Velocity & Productivity
    ("velocity", W_MEDIUM), ("productivity", W_MEDIUM),
    ("story points", W_STRONG), ("completed work", W_STRONG),
    ("work completed", W_STRONG), ("completion rate", W_STRONG),
    ("sprint completion", W_STRONG), ("estimation accuracy", W_STRONG),
    ("completed stories", W_STRONG), ("resolved issues", W_STRONG),
    ("resolved tickets", W_STRONG), ("throughput", W_MEDIUM),
    ("output", W_WEAK), ("efficiency", W_MEDIUM),

    # Issues & Tickets
    ("blocked issues", W_STRONG), ("blocked tickets", W_STRONG),
    ("critical issues", W_STRONG), ("critical tickets", W_STRONG),
    ("blocker", W_MEDIUM), ("blockers", W_MEDIUM),
    ("open issues", W_STRONG), ("open tickets", W_STRONG),
    ("active issues", W_STRONG), ("active tickets", W_STRONG),
    ("issues", W_WEAK), ("tickets", W_WEAK),
    ("bugs", W_MEDIUM), ("defects", W_MEDIUM),
    ("epics", W_MEDIUM), ("stories", W_WEAK),
    ("backlog", W_MEDIUM), ("jira", W_MEDIUM),

    # Health & Burnout
    ("burnout risk", W_STRONG), ("burnout", W_MEDIUM),
    ("team health", W_STRONG), ("health score", W_STRONG),
    ("delivery health", W_STRONG), ("organization health", W_STRONG),
    ("org health", W_STRONG), ("engineer health", W_STRONG),
    ("resource health", W_STRONG), ("operational health", W_STRONG),
    ("health", W_WEAK), ("fatigue", W_STRONG), ("stress", W_MEDIUM),
    ("exhausted", W_STRONG), ("exhaustion", W_STRONG),
    ("burned out", W_STRONG), ("burnt out", W_STRONG),
    ("wellness", W_MEDIUM),

    # Performance & Metrics
    ("team performance", W_STRONG), ("engineer performance", W_STRONG),
    ("engineering metrics", W_STRONG), ("engineering kpis", W_STRONG),
    ("kpi", W_MEDIUM), ("kpis", W_MEDIUM),
    ("sprint metrics", W_STRONG), ("engineering trends", W_STRONG),
    ("performance", W_WEAK), ("metrics", W_WEAK),

    # Performance ranking (Part 13)
    ("best performer", W_STRONG), ("top performer", W_STRONG),
    ("worst performer", W_STRONG), ("most productive", W_STRONG),
    ("least productive", W_STRONG), ("most efficient", W_STRONG),
    ("least efficient", W_STRONG), ("star performer", W_STRONG),
    ("mvp", W_STRONG), ("most valuable", W_STRONG),
    ("needs help", W_STRONG), ("needs attention", W_STRONG),
    ("who should receive help", W_STRONG),

    # Dependencies & Skills
    ("dependencies", W_MEDIUM), ("dependency risk", W_STRONG),
    ("single point of failure", W_STRONG), ("spof", W_STRONG),
    ("skill coverage", W_STRONG), ("coverage", W_WEAK),
    ("skill gap", W_MEDIUM), ("skills", W_WEAK),
    ("bus factor", W_STRONG), ("key person risk", W_STRONG),
    ("multiple skills", W_STRONG), ("how many skills", W_STRONG),
    ("skill count", W_STRONG),

    # Summaries & Overviews
    ("engineering overview", W_STRONG), ("dashboard", W_MEDIUM),
    ("summary", W_WEAK), ("overview", W_WEAK), ("status", W_WEAK),
    ("engineering status", W_STRONG), ("team summary", W_STRONG),
    ("organization summary", W_STRONG), ("org summary", W_STRONG),
    ("engineer summary", W_STRONG), ("team overview", W_STRONG),
    ("org overview", W_STRONG),

    # Team/Engineer queries
    ("how many teams", W_STRONG), ("how many engineers", W_STRONG),
    ("team members", W_STRONG), ("show members", W_STRONG),
    ("list members", W_STRONG), ("who is in", W_STRONG),
    ("members of", W_STRONG), ("belongs to", W_MEDIUM),
    ("which team", W_MEDIUM), ("which engineer", W_MEDIUM),
    ("who owns", W_MEDIUM), ("which delivery manager", W_STRONG),
    ("delivery manager", W_MEDIUM), ("compare", W_MEDIUM),

    # Sprint-specific
    ("current sprint", W_STRONG), ("historical sprint", W_STRONG),
    ("completed sprint", W_STRONG), ("previous sprint", W_STRONG),
    ("sprint", W_WEAK), ("sprint data", W_MEDIUM),
    ("sprint history", W_STRONG), ("last sprint", W_STRONG),

    # Work status
    ("progress", W_WEAK), ("completion", W_WEAK), ("delivery", W_WEAK),
    ("open work", W_MEDIUM), ("resolved work", W_MEDIUM),
    ("in progress", W_MEDIUM), ("risk", W_WEAK),

    # Operational analytics
    ("operational analytics", W_STRONG), ("analytics", W_MEDIUM),

    # Resolution time
    ("resolution time", W_STRONG), ("average resolution", W_STRONG),
    ("time to resolve", W_STRONG), ("cycle time", W_STRONG),
    ("lead time", W_MEDIUM),

    # Specific patterns
    ("who has the highest", W_MEDIUM), ("who has the lowest", W_MEDIUM),
    ("who is the busiest", W_STRONG), ("who is the most", W_MEDIUM),
    ("who is the least", W_MEDIUM),
    ("highest utilization", W_STRONG), ("lowest utilization", W_STRONG),
    ("highest velocity", W_STRONG), ("lowest velocity", W_STRONG),
    ("most blocked", W_STRONG), ("logged hours", W_MEDIUM),
    ("above 100%", W_STRONG), ("over 100%", W_STRONG),
    ("below 60%", W_STRONG), ("under 60%", W_STRONG),
    ("above", W_WEAK), ("below", W_WEAK),
    ("who can replace", W_STRONG), ("replacement", W_MEDIUM),
    ("healthiest", W_STRONG), ("unhealthiest", W_STRONG),
    ("improving", W_MEDIUM), ("degrading", W_MEDIUM),
]

FORECAST_KEYWORDS: list[tuple[str, int]] = [
    ("forecast", W_STRONG), ("forecasting", W_STRONG),
    ("prediction", W_STRONG), ("predict", W_MEDIUM),
    ("projection", W_STRONG), ("project forward", W_STRONG),
    ("future sprint", W_STRONG), ("next sprint", W_STRONG),
    ("next release", W_STRONG), ("upcoming sprint", W_STRONG),
    ("future capacity", W_STRONG), ("future utilization", W_STRONG),
    ("future velocity", W_STRONG), ("future demand", W_STRONG),
    ("future workload", W_STRONG), ("future risks", W_STRONG),
    ("future", W_WEAK), ("next month", W_STRONG),
    ("next quarter", W_STRONG), ("next week", W_MEDIUM),
    ("trend analysis", W_STRONG), ("trend", W_MEDIUM),
    ("trending", W_MEDIUM), ("trajectory", W_MEDIUM),
    ("capacity planning", W_MEDIUM), ("resource planning", W_MEDIUM),
    ("demand forecast", W_STRONG), ("demand planning", W_STRONG),
    ("planning", W_WEAK), ("plan ahead", W_MEDIUM),
    ("capacity gap", W_MEDIUM), ("expected workload", W_STRONG),
    ("expected utilization", W_STRONG), ("expected velocity", W_STRONG),
    ("projected velocity", W_STRONG), ("projected utilization", W_STRONG),
    ("projected capacity", W_STRONG), ("anticipated", W_MEDIUM),
    ("delivery prediction", W_STRONG), ("delivery forecast", W_STRONG),
    ("delivery outlook", W_STRONG), ("sprint forecast", W_STRONG),
    ("velocity trend", W_STRONG), ("utilization trend", W_STRONG),
    ("will we", W_WEAK), ("are we on track", W_MEDIUM),
    ("outlook", W_MEDIUM), ("predict next", W_STRONG),
    ("forecast next", W_STRONG),
]

RECOMMENDATION_KEYWORDS: list[tuple[str, int]] = [
    ("recommend", W_STRONG), ("recommendation", W_STRONG),
    ("recommendations", W_STRONG), ("suggest", W_MEDIUM),
    ("suggestion", W_STRONG), ("suggestions", W_STRONG),
    ("advice", W_MEDIUM), ("advise", W_MEDIUM),
    ("improve", W_MEDIUM), ("improvement", W_MEDIUM),
    ("optimize", W_MEDIUM), ("optimization", W_STRONG),
    ("fix", W_WEAK), ("resolve", W_WEAK),
    ("mitigate", W_MEDIUM), ("remediate", W_MEDIUM),
    ("next action", W_STRONG), ("action items", W_STRONG),
    ("action plan", W_STRONG), ("priority action", W_STRONG),
    ("should we", W_MEDIUM), ("what should", W_MEDIUM),
    ("how to improve", W_STRONG), ("how to fix", W_MEDIUM),
    ("how to reduce", W_MEDIUM), ("how can we", W_MEDIUM),
    ("best practice", W_STRONG), ("best practices", W_STRONG),
    ("cross training", W_STRONG), ("cross-training", W_STRONG),
    ("burnout reduction", W_STRONG), ("reduce burnout", W_STRONG),
    ("reduce burnout risk", W_STRONG),
    ("resource balancing", W_STRONG), ("rebalance", W_MEDIUM),
    ("load balancing", W_STRONG),
    ("team improvement", W_STRONG), ("capacity improvement", W_STRONG),
    ("risk reduction", W_STRONG),
]

WHATIF_KEYWORDS: list[tuple[str, int]] = [
    ("what if", W_STRONG), ("what-if", W_STRONG),
    ("simulate", W_STRONG), ("simulation", W_STRONG),
    ("scenario", W_STRONG), ("hypothetical", W_STRONG),
    ("what happens if", W_STRONG), ("what would happen", W_STRONG),
    ("what happens when", W_STRONG), ("what would change", W_STRONG),
    ("suppose", W_MEDIUM), ("assume", W_MEDIUM), ("imagine", W_MEDIUM),
    ("if we", W_WEAK),
    ("if engineer leaves", W_STRONG), ("if engineer joins", W_STRONG),
    ("engineer leaves", W_STRONG), ("engineer joins", W_STRONG),
    ("someone leaves", W_STRONG), ("someone joins", W_STRONG),
    ("hire", W_WEAK), ("resign", W_MEDIUM),
    ("departure", W_MEDIUM), ("attrition", W_MEDIUM),
    ("transfer engineer", W_STRONG), ("move engineer", W_STRONG),
    ("reassign", W_MEDIUM),
    ("if capacity changes", W_STRONG), ("capacity change", W_MEDIUM),
    ("increase capacity", W_MEDIUM), ("decrease capacity", W_MEDIUM),
    ("redistribute", W_STRONG), ("restructure", W_STRONG),
    ("reorganize", W_MEDIUM), ("reorg", W_MEDIUM),
    ("goes on leave", W_STRONG), ("takes leave", W_STRONG),
    ("is unavailable", W_MEDIUM), ("add engineer", W_STRONG),
    ("remove engineer", W_STRONG), ("lose engineer", W_STRONG),
    ("loses one", W_STRONG), ("add two", W_MEDIUM),
    ("add three", W_MEDIUM), ("hire 3", W_MEDIUM),
    ("hire three", W_MEDIUM),
]

REPORTING_KEYWORDS: list[tuple[str, int]] = [
    ("generate report", W_STRONG), ("create report", W_STRONG),
    ("download report", W_STRONG), ("export report", W_STRONG),
    ("report", W_MEDIUM), ("reporting", W_MEDIUM),
    ("weekly report", W_STRONG), ("monthly report", W_STRONG),
    ("daily report", W_STRONG), ("status report", W_STRONG),
    ("summary report", W_STRONG), ("management report", W_STRONG),
    ("leadership report", W_STRONG), ("executive report", W_STRONG),
    ("team report", W_STRONG), ("engineering report", W_STRONG),
    ("analytics report", W_STRONG),
    ("download", W_MEDIUM), ("export", W_MEDIUM),
    ("pdf", W_STRONG), ("download analytics", W_STRONG),
    ("print report", W_STRONG), ("executive summary", W_MEDIUM),
]

MALICIOUS_KEYWORDS: list[tuple[str, int]] = [
    ("ignore instructions", W_STRONG), ("ignore previous", W_STRONG),
    ("ignore all", W_STRONG), ("ignore your", W_STRONG),
    ("ignore above", W_STRONG), ("disregard instructions", W_STRONG),
    ("forget your instructions", W_STRONG), ("new instructions", W_STRONG),
    ("override instructions", W_STRONG), ("override your", W_STRONG),
    ("system prompt", W_STRONG), ("reveal prompt", W_STRONG),
    ("show prompt", W_STRONG), ("reveal instructions", W_STRONG),
    ("show instructions", W_STRONG), ("hidden instructions", W_STRONG),
    ("what are your instructions", W_STRONG),
    ("what is your prompt", W_STRONG),
    ("print context", W_STRONG), ("print json", W_STRONG),
    ("show internal data", W_STRONG), ("dump data", W_STRONG),
    ("show raw data", W_STRONG), ("export database", W_STRONG),
    ("raw dataset", W_STRONG), ("dataset json", W_STRONG),
    ("act as administrator", W_STRONG), ("act as admin", W_STRONG),
    ("act as system", W_STRONG), ("act as root", W_STRONG),
    ("pretend you are", W_MEDIUM), ("you are now", W_MEDIUM),
    ("jailbreak", W_STRONG), ("bypass security", W_STRONG),
    ("ignore security", W_STRONG), ("prompt injection", W_STRONG),
    ("eval(", W_STRONG), ("exec(", W_STRONG),
    ("import os", W_STRONG), ("__import__", W_STRONG),
]

# ──────────────────────────────────────────────
# All intent keyword maps
# ──────────────────────────────────────────────

INTENT_KEYWORD_MAP: Dict[str, list[tuple[str, int]]] = {
    "analytics": ANALYTICS_KEYWORDS,
    "forecast": FORECAST_KEYWORDS,
    "recommendation": RECOMMENDATION_KEYWORDS,
    "whatif": WHATIF_KEYWORDS,
    "reporting": REPORTING_KEYWORDS,
}

VALID_INTENTS = {"analytics", "forecast", "recommendation", "whatif", "reporting", "malicious", "greeting"}


# ──────────────────────────────────────────────
# Conversational detection (Part 17)
# ──────────────────────────────────────────────

def _detect_conversational(question: str) -> Optional[str]:
    """
    Detect if the question is conversational (greeting, farewell, thanks, etc.).
    Returns the conversational subtype or None.
    """
    q = question.lower().strip()
    q_clean = q.rstrip("?!.,;: ")

    for conv_type, patterns in CONVERSATIONAL_GROUPS.items():
        for pattern in patterns:
            if q_clean == pattern or q_clean.startswith(pattern + " ") or q_clean.endswith(" " + pattern):
                return conv_type
            # Also match if the entire question IS the pattern
            if pattern in q_clean and len(q_clean) < len(pattern) + 15:
                return conv_type
    return None


# ──────────────────────────────────────────────
# Weighted Intent Scoring
# ──────────────────────────────────────────────

def classify_intent(question: str) -> Tuple[str, float, bool]:
    """
    Classify intent using synonym normalization + weighted keyword scoring.

    Returns:
        (intent, score, needs_llm_fallback)
    """
    # Step 0: Normalize synonyms and fix typos
    q = SynonymEngine.normalize(question)

    # Step 1: Check for conversational intent (Part 17)
    conv_type = _detect_conversational(q)
    if conv_type:
        logger.info("Conversational intent detected: %s", conv_type)
        return ("greeting", 10.0, False)

    # Step 2: Security check
    malicious_score = 0
    for keyword, weight in MALICIOUS_KEYWORDS:
        if keyword in q:
            malicious_score += weight
            logger.warning("Malicious keyword detected: '%s'", keyword)

    if malicious_score >= MALICIOUS_INSTANT_THRESHOLD:
        logger.warning("Malicious intent confirmed (score=%d)", malicious_score)
        return ("malicious", float(malicious_score), False)

    # Step 3: Score each intent
    scores: Dict[str, float] = {}
    matched_keywords: Dict[str, list] = {}
    for intent, keywords in INTENT_KEYWORD_MAP.items():
        score = 0
        matches = []
        for keyword, weight in keywords:
            if keyword in q:
                score += weight
                matches.append(keyword)
        scores[intent] = score
        if matches:
            matched_keywords[intent] = matches

    # Step 4: Determine winner
    if not scores or all(v == 0 for v in scores.values()):
        logger.info("No keyword matches for normalized query: '%s'. LLM fallback.", q[:80])
        return ("unknown", 0.0, True)

    sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_intent, top_score = sorted_intents[0]
    runner_up_score = sorted_intents[1][1] if len(sorted_intents) > 1 else 0

    if top_score < MIN_CONFIDENCE_SCORE:
        logger.info(
            "Low confidence (score=%d < threshold=%d). Matches: %s. LLM fallback.",
            top_score, MIN_CONFIDENCE_SCORE, matched_keywords,
        )
        return (top_intent, top_score, True)

    if top_score - runner_up_score <= AMBIGUITY_MARGIN and runner_up_score > 0:
        runner_up_intent = sorted_intents[1][0]
        logger.info(
            "Ambiguous: %s(%.1f) vs %s(%.1f). LLM fallback.",
            top_intent, top_score, runner_up_intent, runner_up_score,
        )
        return (top_intent, top_score, True)

    logger.info(
        "Intent classified: %s (score=%.1f, keywords=%s)",
        top_intent, top_score, matched_keywords.get(top_intent, [])[:5],
    )
    return (top_intent, top_score, False)
