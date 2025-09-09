"""Document data models."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Document metadata model."""
    
    source: str = Field(..., description="Source file path")
    filename: str = Field(..., description="Filename")
    page: int = Field(default=0, description="Page number")
    file_type: str = Field(default="pdf", description="File type")
    upload_date: Optional[str] = Field(None, description="Upload date")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    chunk_index: Optional[int] = Field(None, description="Chunk index in document")
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            # Add custom encoders if needed
        }


class DocumentModel(BaseModel):
    """Document model."""
    
    id: str = Field(..., description="Unique document ID")
    content: str = Field(..., description="Document content")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    embedding: Optional[list] = Field(None, description="Document embedding vector")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            # Add custom encoders if needed
        }
