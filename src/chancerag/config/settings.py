"""Application settings."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    app_name: str = Field(default="ChanceRAG", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    host: str = Field(default="0.0.0.0", description="Host address")
    port: int = Field(default=8000, description="Port number")
    
    # OpenAI Settings
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")
    openai_temperature: float = Field(default=0.1, description="OpenAI temperature")
    openai_max_tokens: int = Field(default=1000, description="OpenAI max tokens")
    
    # Embedding Settings
    embedding_model: str = Field(default="text-embedding-ada-002", description="Embedding model")
    use_openai_embeddings: bool = Field(default=True, description="Use OpenAI embeddings")
    
    # Vector Store Settings
    vector_store_path: str = Field(default="./data/vector_store", description="Vector store path")
    chunk_size: int = Field(default=1000, description="Text chunk size")
    chunk_overlap: int = Field(default=100, description="Text chunk overlap")
    
    # Retrieval Settings
    top_k: int = Field(default=5, description="Number of documents to retrieve")
    score_threshold: float = Field(default=0.7, description="Minimum similarity score")
    
    # Data Settings
    data_path: str = Field(default="./data", description="Data directory path")
    upload_path: str = Field(default="./data/uploads", description="Upload directory path")
    
    # Logging Settings
    log_level: str = Field(default="INFO", description="Log level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields in .env file


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
