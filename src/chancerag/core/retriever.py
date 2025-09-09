"""RAG retriever module for document retrieval."""

import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio

from langchain.schema import Document
from ..utils.korean_tokenizer import KoreanTokenizer

from .vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)


class RAGRetriever:
    """RAG retriever for Korean document search."""
    
    def __init__(
        self,
        vector_store: FAISSVectorStore,
        top_k: int = 5,
        score_threshold: float = 0.7,
    ):
        """
        Initialize RAG retriever.
        
        Args:
            vector_store: FAISS vector store instance
            top_k: Number of top documents to retrieve
            score_threshold: Minimum similarity score threshold
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.korean_tokenizer = KoreanTokenizer()
    
    async def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score
            
        Returns:
            List of (document, score) tuples
        """
        try:
            # Use provided parameters or defaults
            k = top_k or self.top_k
            threshold = score_threshold or self.score_threshold
            
            logger.info(f"Retrieving documents for query: {query}")
            
            # Perform similarity search
            results = await self.vector_store.similarity_search(
                query=query,
                k=k,
                score_threshold=threshold
            )
            
            # Post-process results
            processed_results = await self._post_process_results(results, query)
            
            logger.info(f"Retrieved {len(processed_results)} relevant documents")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise
    
    async def _post_process_results(
        self, 
        results: List[Tuple[Document, float]], 
        query: str
    ) -> List[Tuple[Document, float]]:
        """
        Post-process retrieval results.
        
        Args:
            results: Raw retrieval results
            query: Original query
            
        Returns:
            Processed results
        """
        processed_results = []
        
        for doc, score in results:
            try:
                # Add query relevance metadata
                doc.metadata.update({
                    "relevance_score": score,
                    "query": query,
                })
                
                processed_results.append((doc, score))
                
            except Exception as e:
                logger.warning(f"Error processing result: {e}")
                # Keep original result if processing fails
                processed_results.append((doc, score))
        
        return processed_results
    
    async def retrieve_with_context(
        self, 
        query: str,
        context_window: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents with expanded context.
        
        Args:
            query: Search query
            context_window: Number of surrounding chunks to include
            
        Returns:
            List of documents with expanded context
        """
        try:
            # Get initial results
            results = await self.retrieve(query)
            
            expanded_results = []
            for doc, score in results:
                # Get surrounding context if available
                expanded_doc = await self._expand_context(doc, context_window)
                
                expanded_results.append({
                    "document": expanded_doc,
                    "score": score,
                    "source": doc.metadata.get("source", ""),
                    "page": doc.metadata.get("page", 0),
                })
            
            return expanded_results
            
        except Exception as e:
            logger.error(f"Error retrieving with context: {e}")
            raise
    
    async def _expand_context(
        self, 
        document: Document, 
        context_window: int
    ) -> Document:
        """
        Expand document context with surrounding chunks.
        
        Args:
            document: Original document
            context_window: Number of surrounding chunks to include
            
        Returns:
            Document with expanded context
        """
        try:
            # For now, return original document
            # In a more sophisticated implementation, you could:
            # 1. Find adjacent chunks from the same source
            # 2. Merge them with the original chunk
            # 3. Return expanded document
            
            return document
            
        except Exception as e:
            logger.warning(f"Error expanding context: {e}")
            return document
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get retrieval statistics.
        
        Returns:
            Dictionary with retrieval stats
        """
        return {
            "top_k": self.top_k,
            "score_threshold": self.score_threshold,
            "vector_store_stats": self.vector_store.get_stats(),
        }
