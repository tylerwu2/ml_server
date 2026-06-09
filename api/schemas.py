from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List

class HealthResponse(BaseModel):
    status: str
    time: datetime | None
    model_loaded: bool
    cache_connected: bool 

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Input text")

    @field_validator("text")
    @classmethod
    def strip_text(s: str):
        return s.strip() 


class PredictResponse(BaseModel):
    label: str 
    result: str
    time: datetime | None
    cache: bool = False 

class BatchPredictRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=100)

class BatchResponse(BaseModel):
    result: list[PredictResponse]
    responses: int
    time: datetime | None 
