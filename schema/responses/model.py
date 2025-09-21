from pydantic import BaseModel, Field
from typing import List, Optional

class ModelMetrics(BaseModel):
    decision_tree_accuracy: float
    svm_accuracy: float
    cross_validation_mean: float
    total_symptoms: int
    total_diseases: int


class ModelStatus(BaseModel):
    loaded: bool
    last_loaded: Optional[str] = None
    data_path: str
    master_data_path: str
    metrics: Optional[ModelMetrics] = None