"""
Entity Extractor — Deterministic identification of teams, engineers, sprints, and concepts.

Improvements in this version:
- Uses SynonymEngine to resolve natural language variations to canonical forms.
- Extracts key business concepts (burnout, overworked, highest performer, etc.)
  for the query-aware context builder.
- Deterministic regex and lookup — zero LLM cost.
"""

import re
import logging
from typing import Dict, List, Set, Any, Optional

from app.models.schemas import Dataset
from app.services.dataset_loader import DatasetLoader
from app.ai.synonym_engine import SynonymEngine

logger = logging.getLogger("cuia.ai.entities")

class ExtractedEntities:
    """Container for all deterministically extracted entities and concepts."""
    def __init__(self):
        self.team_ids: Set[str] = set()
        self.engineer_ids: Set[str] = set()
        self.sprints: Set[str] = set()
        self.skills: Set[str] = set()
        self.concepts: Set[str] = set()  # "overutilized", "burnout risk", "best performer"
        self.timeframes: Set[str] = set() # "next sprint", "current sprint"

    def to_dict(self) -> Dict[str, list]:
        return {
            "team_ids": list(self.team_ids),
            "engineer_ids": list(self.engineer_ids),
            "sprints": list(self.sprints),
            "skills": list(self.skills),
            "concepts": list(self.concepts),
            "timeframes": list(self.timeframes)
        }

    def has_any(self) -> bool:
        """Returns True if any entity or concept was extracted."""
        return any([self.team_ids, self.engineer_ids, self.sprints, 
                   self.skills, self.concepts, self.timeframes])


class EntityExtractor:
    """
    Extracts explicit entities (names, teams, sprints) and implicit concepts
    (burnout, overworked, performance) using the dataset and SynonymEngine.
    """
    
    # Cache for name->id lookups to avoid rebuilding on every request
    _name_to_eng_id: Dict[str, str] = {}
    _name_to_team_id: Dict[str, str] = {}
    _all_skills: Set[str] = set()
    _initialized: bool = False

    @classmethod
    def _initialize(cls):
        """Build the lookup dictionaries from the dataset."""
        if cls._initialized:
            return
        
        try:
            dataset = DatasetLoader.get_dataset()
            
            # Build engineer lookups (allow partial matches like first name)
            for eng in dataset.engineers:
                cls._name_to_eng_id[eng.name.lower()] = eng.id
                parts = eng.name.lower().split()
                if len(parts) > 1:
                    cls._name_to_eng_id[parts[0]] = eng.id
                    cls._name_to_eng_id[parts[-1]] = eng.id
                
                # Collect skills while we're at it
                cls._all_skills.update([s.lower() for s in eng.primarySkills])
                cls._all_skills.update([s.lower() for s in eng.secondarySkills])
                cls._all_skills.update([s.lower() for s in eng.learningSkills])
                
            # Build team lookups (strip 'team' prefix/suffix for matching)
            for team in dataset.teams:
                cls._name_to_team_id[team.name.lower()] = team.id
                clean_name = team.name.lower().replace("team", "").strip()
                if clean_name:
                    cls._name_to_team_id[clean_name] = team.id
            
            cls._initialized = True
            logger.info("EntityExtractor initialized. %d engineers, %d teams, %d skills.", 
                        len(dataset.engineers), len(dataset.teams), len(cls._all_skills))
        except Exception as e:
            logger.error("Failed to initialize EntityExtractor: %s", str(e))

    @classmethod
    def extract(cls, question: str) -> ExtractedEntities:
        """
        Extract all entities and concepts from the question.
        """
        cls._initialize()
        entities = ExtractedEntities()
        
        # 1. Normalize the question using SynonymEngine to get canonical forms
        # This replaces "overworked" with "overutilized", "bus factor" with "single point of failure", etc.
        q_norm = SynonymEngine.normalize(question)
        
        # 2. Extract concepts based on canonical terms in the normalized string
        cls._extract_concepts(q_norm, entities)
        
        # 3. Extract explicit entities (engineers, teams)
        # Tokenize preserving some punctuation for strict matching
        q_clean = re.sub(r"[?!.,;:]+", " ", q_norm)
        # Strip possessive 's from words
        words = [w.replace("'s", "") for w in q_clean.split()]
        tokens = set(words)
        
        # Bigrams for two-word names/teams
        bigrams = set(f"{words[i]} {words[i+1]}" for i in range(len(words)-1))
        
        # Match Engineers
        for token in tokens:
            if token in cls._name_to_eng_id:
                entities.engineer_ids.add(cls._name_to_eng_id[token])
        for bigram in bigrams:
            if bigram in cls._name_to_eng_id:
                entities.engineer_ids.add(cls._name_to_eng_id[bigram])
                
        # Match Teams
        for token in tokens:
            if token in cls._name_to_team_id:
                entities.team_ids.add(cls._name_to_team_id[token])
        for bigram in bigrams:
            if bigram in cls._name_to_team_id:
                entities.team_ids.add(cls._name_to_team_id[bigram])
                
        # Match Skills
        for skill in cls._all_skills:
            if skill in q_clean:
                entities.skills.add(skill)
                
        # 4. Regex extractions (Sprints)
        sprint_matches = re.findall(r'sprint\s+(\d+)', q_norm)
        for match in sprint_matches:
            entities.sprints.add(f"Sprint {match}")
            
        logger.info("Extracted entities: %s", entities.to_dict())
        return entities

    @classmethod
    def _extract_concepts(cls, q_norm: str, entities: ExtractedEntities):
        """Extract canonical concepts from the normalized string."""
        
        # Canonical forms that map to concepts
        concept_terms = [
            "overutilized", "underutilized", "burnout risk", 
            "busiest", "least busy", "best performer", "worst performer",
            "healthiest team", "unhealthiest team", "single point of failure"
        ]
        
        for term in concept_terms:
            if term in q_norm:
                entities.concepts.add(term)
                
        # Timeframes
        timeframe_terms = ["next sprint", "next month", "current sprint", "forecast"]
        for term in timeframe_terms:
            if term in q_norm:
                entities.timeframes.add(term)
