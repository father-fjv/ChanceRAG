"""Query data models."""

from typing import Optional, List
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Query request model."""
    
    question: str = Field(..., description="User question", min_length=1, max_length=1000)
    top_k: Optional[int] = Field(default=5, description="Number of documents to retrieve", ge=1, le=20)
    score_threshold: Optional[float] = Field(default=0.7, description="Minimum similarity score", ge=0.0, le=1.0)
    include_sources: bool = Field(default=True, description="Include source documents in response")
    streaming: bool = Field(default=False, description="Enable streaming response")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "question": "출장비 정산 한도는 얼마인가요?",
                "top_k": 5,
                "score_threshold": 0.7,
                "include_sources": True,
                "streaming": False
            }
        }


class QueryResponse(BaseModel):
    """Query response model."""
    
    answer: str = Field(..., description="Generated answer")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)
    processing_time: float = Field(..., description="Processing time in seconds")
    retrieved_docs: int = Field(..., description="Number of retrieved documents")
    sources: Optional[List[dict]] = Field(None, description="Source documents")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "answer": "출장비 정산 한도는 일 150,000원입니다.",
                "confidence": 0.95,
                "processing_time": 2.5,
                "retrieved_docs": 3,
                "sources": [
                    {
                        "content": "출장비 정산 규정...",
                        "filename": "travel_expense_policy.pdf",
                        "page": 5,
                        "score": 0.92
                    }
                ],
                "metadata": {
                    "model": "gpt-4o",
                    "question": "출장비 정산 한도는 얼마인가요?"
                }
            }
        }
