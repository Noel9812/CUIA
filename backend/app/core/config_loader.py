"""
Configuration loader for the CUIA platform.

Loads all business rules and configuration from JSON files in the config/ directory.
All configuration is cached after first load. Changing a threshold or weight
requires editing the JSON file, never Python code.
"""

import json
import os
import logging
from typing import Dict, Any, List
from functools import lru_cache

logger = logging.getLogger("cuia.config")

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")


class ConfigLoader:
    """Centralized configuration loader. All business rules live in JSON files."""
    
    _cache: Dict[str, Any] = {}
    
    @classmethod
    def _load_json(cls, filename: str) -> Dict[str, Any]:
        """Load and cache a JSON config file."""
        if filename in cls._cache:
            return cls._cache[filename]
        
        filepath = os.path.join(CONFIG_DIR, filename)
        if not os.path.exists(filepath):
            logger.error("Configuration file not found: %s", filepath)
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        cls._cache[filename] = data
        logger.info("Loaded configuration: %s", filename)
        return data
    
    @classmethod
    def get_priority_weights(cls) -> Dict[str, int]:
        """Load priority weights mapping (e.g., Low→1, Medium→3, High→5, Critical→8)."""
        return cls._load_json("priority_weights.json")
    
    @classmethod
    def get_analytics_rules(cls) -> Dict[str, Any]:
        """Load analytics computation rules (thresholds, statuses, weights)."""
        return cls._load_json("analytics_rules.json")
    
    @classmethod
    def get_recommendation_rules(cls) -> Dict[str, Any]:
        """Load recommendation business rules and templates."""
        return cls._load_json("recommendation_rules.json")
    
    @classmethod
    def get_forecast_rules(cls) -> Dict[str, Any]:
        """Load forecast configuration (horizons, smoothing, risk thresholds)."""
        return cls._load_json("forecast_rules.json")
    
    @classmethod
    def get_health_rules(cls) -> Dict[str, Any]:
        """Load health scoring configuration (weights, penalties, ranges)."""
        return cls._load_json("health_rules.json")
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached configurations. Useful for testing or hot-reload."""
        cls._cache.clear()
        logger.info("Configuration cache cleared.")
