from datetime import datetime
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    time: datetime | None


class PredictResponse(BaseModel):
    result: str
    time: datetime | None


class BatchResponse(BaseModel):
    result:list[str]
    time: datetime | None 