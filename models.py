from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    model: str
    prompt: str
    temperature: float = 0.0

class QueryResponse(BaseModel):
    model: str
    prompt: str
    response: str
    latency_seconds: float
    tokens_per_second: float
    memory_mb: float
    temperature: float
