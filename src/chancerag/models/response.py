"""Response data models."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SourceInfo(BaseModel):
    """Source information model."""
    
    content: str = Field(..., description="Source content")
    source: str = Field(..., description="Source file path")
    filename: str = Field(..., description="Source filename")
    page: int = Field(..., description="Page number")
    score: float = Field(..., description="Relevance score", ge=0.0, le=1.0)
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "content": "출장비 정산 규정 제3조 2항...",
                "source": "/data/policies/travel_expense_policy.pdf",
                "filename": "travel_expense_policy.pdf",
                "page": 5,
                "score": 0.92
            }
        }


class RAGResponse(BaseModel):
    """RAG response model."""
    
    answer: str = Field(..., description="Generated answer")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)
    sources: List[SourceInfo] = Field(default_factory=list, description="Source documents")
    processing_time: float = Field(..., description="Processing time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "answer": "출장비 정산 한도는 일 150,000원입니다. 이는 숙박비 기준이며, 식비는 별도로 정산됩니다.",
                "confidence": 0.95,
                "sources": [
                    {
                        "content": "출장비 정산 규정 제3조 2항...",
                        "source": "/data/policies/travel_expense_policy.pdf",
                        "filename": "travel_expense_policy.pdf",
                        "page": 5,
                        "score": 0.92
                    }
                ],
                "processing_time": 2.5,
                "metadata": {
                    "model": "gpt-4o",
                    "retrieved_docs": 3,
                    "question": "출장비 정산 한도는 얼마인가요?"
                }
            }
        }
