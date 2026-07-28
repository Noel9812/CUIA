"""
Deterministic Synonym Engine — maps natural language variations to canonical concepts.

Supports:
- Common synonyms and abbreviations
- Plural forms
- Typos and spelling variations
- Punctuation-insensitive matching

Usage:
    from app.ai.synonym_engine import SynonymEngine
    normalized = SynonymEngine.normalize(question)
    # "who is overloaded" → "who is overutilized"
"""

import re
import logging
from typing import Dict, List, Set, Tuple

logger = logging.getLogger("cuia.ai.synonyms")


# ──────────────────────────────────────────────
# Canonical concept mappings
# Each key is the canonical term; values are all synonyms.
# ──────────────────────────────────────────────

SYNONYM_GROUPS: Dict[str, List[str]] = {
    # ── Overutilization ──
    "overutilized": [
        "overworked", "overloaded", "over worked", "over loaded",
        "over-worked", "over-loaded", "too much work", "swamped",
        "overwhelmed", "stretched thin", "stretched too thin",
        "maxed out", "maxed-out", "at capacity", "above capacity",
        "over capacity", "over-capacity", "overcapacity",
        "high workload", "heavy workload", "excessive workload",
        "overburdened", "over-burdened", "overstretched",
        "over-stretched", "working too much", "too many tasks",
        "too many tickets", "too many issues",
    ],

    # ── Underutilization ──
    "underutilized": [
        "underworked", "under worked", "under-worked",
        "idle", "idling", "not busy", "not working",
        "low workload", "light workload", "low utilization",
        "spare capacity", "excess capacity", "free capacity",
        "available", "on bench", "on the bench", "benched",
        "below capacity", "under capacity", "under-capacity",
        "undercapacity", "not enough work", "too little work",
        "underloaded", "under-loaded", "under loaded",
    ],

    # ── Burnout ──
    "burnout risk": [
        "burnout", "burn out", "burned out", "burnt out",
        "burn-out", "burning out", "fatigue", "fatigued",
        "stress", "stressed", "stressed out", "exhausted",
        "exhaustion", "mental health", "wellness",
        "work life balance", "work-life balance",
        "needs rest", "needs break", "overexerted",
    ],

    # ── Busy / High utilization ──
    "busiest": [
        "most busy", "most utilized", "highest utilization",
        "highest workload", "most overloaded", "most overworked",
        "most loaded", "most active", "heaviest workload",
    ],

    # ── Free / Low utilization ──
    "least busy": [
        "most free", "most idle", "most available",
        "lowest utilization", "least utilized", "least loaded",
        "least active", "lightest workload", "fewest tasks",
    ],

    # ── Performance ──
    "best performer": [
        "top performer", "highest performer", "most productive",
        "most efficient", "star performer", "best performing",
        "highest performing", "mvp", "most valuable",
        "strongest engineer", "best engineer",
    ],
    "worst performer": [
        "lowest performer", "poorest performer",
        "least productive", "least efficient",
        "weakest performer", "struggling engineer",
        "underperforming", "under-performing", "under performing",
    ],

    # ── Team health ──
    "healthiest team": [
        "best team", "strongest team", "most healthy team",
        "top team", "best performing team",
    ],
    "unhealthiest team": [
        "worst team", "weakest team", "least healthy team",
        "most unhealthy team", "needs attention",
        "struggling team", "at risk team", "at-risk team",
    ],

    # ── Skills ──
    "skills": [
        "skill set", "skillset", "skill-set",
        "expertise", "competencies", "competency",
        "capabilities", "capability", "proficiency",
        "technology", "technologies", "tech stack",
    ],

    # ── Single point of failure ──
    "single point of failure": [
        "spof", "s.p.o.f", "dependency risk",
        "bus factor", "key person risk", "key-person risk",
        "critical dependency", "sole owner", "only person",
        "only engineer", "single owner",
    ],

    # ── Forecast ──
    "forecast": [
        "prediction", "projection", "predict",
        "project forward", "look ahead", "outlook",
    ],
    "next sprint": [
        "upcoming sprint", "following sprint",
        "next iteration", "next cycle",
    ],
    "next month": [
        "next period", "coming month", "upcoming month",
    ],

    # ── Simulation ──
    "what if": [
        "what-if", "suppose", "assume", "imagine",
        "hypothetically", "hypothetical", "scenario",
    ],

    # ── Reports ──
    "generate report": [
        "create report", "make report", "build report",
        "produce report", "export report", "download report",
    ],
    "executive summary": [
        "exec summary", "management summary",
        "leadership summary", "high level summary",
        "high-level summary",
    ],

    # ── Common question patterns ──
    "who has": [
        "which engineer has", "which engineers have",
        "which person has", "who's got",
    ],
    "how many": [
        "what is the count", "what is the number",
        "total number of", "count of",
    ],
    "show me": [
        "display", "list", "show", "give me",
        "tell me about", "what are", "what is",
    ],
}


# ──────────────────────────────────────────────
# Common typo corrections
# ──────────────────────────────────────────────

TYPO_CORRECTIONS: Dict[str, str] = {
    "utiliztion": "utilization",
    "utlization": "utilization",
    "utilistion": "utilization",
    "utilizaton": "utilization",
    "utilizaiton": "utilization",
    "utiliation": "utilization",
    "ultilization": "utilization",
    "untilization": "utilization",
    "utilizaion": "utilization",
    "burnot": "burnout",
    "bornout": "burnout",
    "burnuot": "burnout",
    "bruonout": "burnout",
    "forcast": "forecast",
    "forcast": "forecast",
    "forecase": "forecast",
    "forcaste": "forecast",
    "forecats": "forecast",
    "recomendation": "recommendation",
    "recomendations": "recommendations",
    "reccomendation": "recommendation",
    "recommandation": "recommendation",
    "reccommendation": "recommendation",
    "simulaton": "simulation",
    "simulaiton": "simulation",
    "simluation": "simulation",
    "performace": "performance",
    "performence": "performance",
    "perfomance": "performance",
    "enginers": "engineers",
    "engneers": "engineers",
    "enginners": "engineers",
    "engineeers": "engineers",
    "productvity": "productivity",
    "productivty": "productivity",
    "prodcutivity": "productivity",
    "availble": "available",
    "availabe": "available",
    "avaialble": "available",
    "avaiable": "available",
    "capactiy": "capacity",
    "capcity": "capacity",
    "capacty": "capacity",
    "capaicty": "capacity",
    "velocty": "velocity",
    "veloicty": "velocity",
    "velociy": "velocity",
    "helath": "health",
    "heatlh": "health",
    "healht": "health",
    "blcokers": "blockers",
    "blocekrs": "blockers",
    "blokced": "blocked",
    "bloacked": "blocked",
    "overworkd": "overworked",
    "overwokred": "overworked",
    "overwroked": "overworked",
    "underworkd": "underworked",
    "underworekd": "underworked",
}


class SynonymEngine:
    """
    Deterministic synonym normalization engine.

    Replaces synonyms, typos, and abbreviations with canonical terms
    before intent classification and entity extraction.
    """

    # Pre-compiled: synonym → canonical mapping (built once)
    _synonym_map: Dict[str, str] = {}
    _initialized: bool = False

    @classmethod
    def _initialize(cls):
        """Build the reverse synonym lookup map."""
        if cls._initialized:
            return

        for canonical, synonyms in SYNONYM_GROUPS.items():
            for synonym in synonyms:
                # Map synonym to canonical (longest match wins later)
                cls._synonym_map[synonym.lower()] = canonical.lower()

        cls._initialized = True
        logger.info(
            "SynonymEngine initialized: %d canonical groups, %d total synonyms, %d typo corrections.",
            len(SYNONYM_GROUPS), len(cls._synonym_map), len(TYPO_CORRECTIONS),
        )

    @classmethod
    def normalize(cls, question: str) -> str:
        """
        Normalize a question by replacing synonyms and fixing typos.

        Returns a new string with canonical terms substituted.
        The original casing/structure is preserved where possible.
        """
        cls._initialize()

        q = question.lower().strip()

        # Step 1: Fix typos (word-level replacement)
        words = q.split()
        corrected_words = [TYPO_CORRECTIONS.get(w, w) for w in words]
        q = " ".join(corrected_words)

        # Step 2: Strip redundant punctuation for matching
        q_clean = re.sub(r"[?!.,;:]+$", "", q).strip()
        q_clean = re.sub(r"\s+", " ", q_clean)

        # Step 3: Replace multi-word synonyms (longest first for greedy matching)
        sorted_synonyms = sorted(cls._synonym_map.keys(), key=len, reverse=True)
        for synonym in sorted_synonyms:
            if synonym in q_clean:
                canonical = cls._synonym_map[synonym]
                q_clean = q_clean.replace(synonym, canonical)

        return q_clean

    @classmethod
    def get_canonical(cls, term: str) -> str:
        """Get the canonical form of a single term, or return it unchanged."""
        cls._initialize()
        return cls._synonym_map.get(term.lower().strip(), term.lower().strip())
