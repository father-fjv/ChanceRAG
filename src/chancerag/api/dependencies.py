"""API dependencies."""

import logging
from typing import Generator
from fastapi import Depends

from ..config import get_settings
from ..core.document_processor import DocumentProcessor
from ..core.vector_store import FAISSVectorStore
from ..core.retriever import RAGRetriever
from ..core.generator import RAGGenerator

logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG system container."""
    
    def __init__(self):
        """Initialize RAG system components."""
        self.settings = get_settings()
        self.document_processor = None
        self.vector_store = None
        self.retriever = None
        self.generator = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize RAG system components."""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing RAG system...")
            
            # Initialize document processor
            self.document_processor = DocumentProcessor(
                chunk_size=self.settings.chunk_size,
                chunk_overlap=self.settings.chunk_overlap,
            )
            
            # Initialize vector store
            self.vector_store = FAISSVectorStore(
                embedding_model=self.settings.embedding_model,
                use_openai=self.settings.use_openai_embeddings,
                index_path=self.settings.vector_store_path,
            )
            
            # Initialize retriever
            self.retriever = RAGRetriever(
                vector_store=self.vector_store,
                top_k=self.settings.top_k,
                score_threshold=self.settings.score_threshold,
            )
            
            # Initialize generator
            self.generator = RAGGenerator(
                retriever=self.retriever,
                model_name=self.settings.openai_model,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens,
            )
            
            self._initialized = True
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            raise
    
    def get_document_processor(self) -> DocumentProcessor:
        """Get document processor."""
        if not self._initialized:
            raise RuntimeError("RAG system not initialized")
        return self.document_processor
    
    def get_vector_store(self) -> FAISSVectorStore:
        """Get vector store."""
        if not self._initialized:
            raise RuntimeError("RAG system not initialized")
        return self.vector_store
    
    def get_retriever(self) -> RAGRetriever:
        """Get retriever."""
        if not self._initialized:
            raise RuntimeError("RAG system not initialized")
        return self.retriever
    
    def get_generator(self) -> RAGGenerator:
        """Get generator."""
        if not self._initialized:
            raise RuntimeError("RAG system not initialized")
        return self.generator


# Global RAG system instance
_rag_system: RAGSystem = None


async def get_rag_system() -> Generator[RAGSystem, None, None]:
    """
    Get RAG system dependency.
    
    Yields:
        RAGSystem instance
    """
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
        await _rag_system.initialize()
    
    yield _rag_system
