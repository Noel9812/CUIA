"""Dataset loader with validation."""

import json
import os
import logging
from typing import Optional

from app.models.schemas import Dataset

logger = logging.getLogger("cuia.dataset")


class DatasetLoader:
    """
    Loads and caches dataset.json — the simulated Jira data source.
    
    Validates the dataset on load to catch structural issues early.
    The dataset is the single source of truth for all analytics.
    """

    _dataset: Optional[Dataset] = None

    @classmethod
    def get_dataset(cls) -> Dataset:
        """Load and cache the dataset. Validates on first load."""
        if cls._dataset is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            dataset_path = os.path.join(base_dir, 'sample_data', 'dataset.json')
            
            if not os.path.exists(dataset_path):
                raise FileNotFoundError(f"Dataset not found: {dataset_path}")
            
            logger.info("Loading dataset from: %s", dataset_path)
            
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cls._dataset = Dataset(**data)
            
            logger.info(
                "Dataset loaded: %d engineers, %d teams, %d issues, %d delivery managers.",
                len(cls._dataset.engineers),
                len(cls._dataset.teams),
                len(cls._dataset.issues),
                len(cls._dataset.deliveryManagers),
            )
            
            # Run validation
            from app.core.data_validator import DataValidator
            errors = DataValidator.validate(cls._dataset)
            critical_errors = [e for e in errors if e.severity == "error"]
            if critical_errors:
                logger.error("Dataset has %d critical validation errors.", len(critical_errors))
                for err in critical_errors[:5]:
                    logger.error("  [%s] %s: %s", err.severity, err.field, err.message)
            
        return cls._dataset

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached dataset. Used for testing or reload."""
        cls._dataset = None
        logger.info("Dataset cache cleared.")
