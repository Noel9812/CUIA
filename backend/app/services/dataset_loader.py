import json
import os
from app.models.schemas import Dataset

class DatasetLoader:
    _instance = None
    _dataset = None

    @classmethod
    def get_dataset(cls) -> Dataset:
        if cls._dataset is None:
            # Assuming it's run from the backend directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            dataset_path = os.path.join(base_dir, 'sample_data', 'dataset.json')
            
            with open(dataset_path, 'r') as f:
                data = json.load(f)
                cls._dataset = Dataset(**data)
                
        return cls._dataset
