from pydantic import BaseModel, Field
from typing import Optional, Dict

class ChatQuestion(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)

class ChatResponse(BaseModel):
    answer: str
    confidence: float
    source: str
    entities: Dict = {}