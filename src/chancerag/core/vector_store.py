"""FAISS vector store implementation for Korean RAG."""

import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import faiss
from langchain.schema import Document
from langchain_community.embeddings import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer
from ..utils.korean_tokenizer import KoreanTokenizer

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS-based vector store optimized for Korean text."""
    
    def __init__(
        self,
        embedding_model: str = "text-embedding-ada-002",
        use_openai: bool = True,
        index_path: Optional[str] = None,
        dimension: int = 1536,  # OpenAI ada-002 dimension
    ):
        """
        Initialize FAISS vector store.
        
        Args:
            embedding_model: Name of embedding model
            use_openai: Whether to use OpenAI embeddings
            index_path: Path to save/load FAISS index
            dimension: Embedding dimension
        """
        self.embedding_model = embedding_model
        self.use_openai = use_openai
        self.index_path = index_path
        self.dimension = dimension
        
        # Initialize embedding model
        if use_openai:
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model,
                chunk_size=1000,
            )
        else:
            # Use Korean-optimized sentence transformer
            self.embeddings = SentenceTransformer(
                "jhgan/ko-sroberta-multitask",
                device="cpu"
            )
            self.dimension = self.embeddings.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.documents: List[Document] = []
        self.metadata: List[Dict[str, Any]] = []
        
        # Korean tokenizer for preprocessing
        self.korean_tokenizer = KoreanTokenizer()
        
        # Load existing index if path provided
        if index_path and Path(index_path).exists():
            self.load_index()
    
    async def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to vector store.
        
        Args:
            documents: List of documents to add
        """
        try:
            logger.info(f"Adding {len(documents)} documents to vector store")
            
            # Process documents in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                await self._add_batch(batch)
            
            logger.info(f"Successfully added {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def _add_batch(self, documents: List[Document]) -> None:
        """
        Add a batch of documents to the index.
        
        Args:
            documents: Batch of documents to add
        """
        try:
            # Extract texts and preprocess
            texts = [doc.page_content for doc in documents]
            processed_texts = await self._preprocess_korean_texts(texts)
            
            # Generate embeddings
            if self.use_openai:
                embeddings = await self._get_openai_embeddings(processed_texts)
            else:
                embeddings = await self._get_sentence_transformer_embeddings(processed_texts)
            
            # Normalize embeddings for cosine similarity
            embeddings = self._normalize_embeddings(embeddings)
            
            # Add to FAISS index
            self.index.add(embeddings.astype('float32'))
            
            # Store documents and metadata
            self.documents.extend(documents)
            for doc in documents:
                self.metadata.append({
                    "source": doc.metadata.get("source", ""),
                    "filename": doc.metadata.get("filename", ""),
                    "page": doc.metadata.get("page", 0),
                })
            
        except Exception as e:
            logger.error(f"Error adding batch: {e}")
            raise
    
    async def _preprocess_korean_texts(self, texts: List[str]) -> List[str]:
        """
        Preprocess Korean texts for better embedding.
        
        Args:
            texts: List of texts to preprocess
            
        Returns:
            List of preprocessed texts
        """
        processed_texts = []
        
        for text in texts:
            try:
                # Tokenize Korean text
                tokens = self.korean_tokenizer.tokenize(text)
                # Reconstruct with proper spacing
                processed_text = " ".join(tokens)
                processed_texts.append(processed_text)
            except Exception as e:
                logger.warning(f"Error preprocessing text: {e}")
                processed_texts.append(text)
        
        return processed_texts
    
    async def _get_openai_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings from OpenAI API.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        try:
            # Use asyncio to run in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                embeddings = await loop.run_in_executor(
                    executor, 
                    self.embeddings.embed_documents, 
                    texts
                )
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Error getting OpenAI embeddings: {e}")
            raise
    
    async def _get_sentence_transformer_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings from sentence transformer.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                embeddings = await loop.run_in_executor(
                    executor,
                    self.embeddings.encode,
                    texts
                )
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Error getting sentence transformer embeddings: {e}")
            raise
    
    def _normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Normalize embeddings for cosine similarity.
        
        Args:
            embeddings: Raw embeddings
            
        Returns:
            Normalized embeddings
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / (norms + 1e-8)
    
    async def similarity_search(
        self, 
        query: str, 
        k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of (document, score) tuples
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector store is empty")
                return []
            
            # Preprocess query
            processed_query = await self._preprocess_korean_texts([query])
            
            # Get query embedding
            if self.use_openai:
                query_embedding = await self._get_openai_embeddings(processed_query)
            else:
                query_embedding = await self._get_sentence_transformer_embeddings(processed_query)
            
            # Normalize query embedding
            query_embedding = self._normalize_embeddings(query_embedding)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            # Filter by score threshold and return results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1 and score >= score_threshold:
                    document = self.documents[idx]
                    results.append((document, float(score)))
            
            logger.info(f"Found {len(results)} similar documents for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    def save_index(self, path: Optional[str] = None) -> None:
        """
        Save FAISS index to disk.
        
        Args:
            path: Path to save index (uses self.index_path if None)
        """
        try:
            save_path = path or self.index_path
            if not save_path:
                raise ValueError("No path provided for saving index")
            
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, str(save_path / "faiss.index"))
            
            # Save documents and metadata
            with open(save_path / "documents.pkl", "wb") as f:
                pickle.dump(self.documents, f)
            
            with open(save_path / "metadata.pkl", "wb") as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Saved vector store to {save_path}")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise
    
    def load_index(self, path: Optional[str] = None) -> None:
        """
        Load FAISS index from disk.
        
        Args:
            path: Path to load index from (uses self.index_path if None)
        """
        try:
            load_path = path or self.index_path
            if not load_path:
                raise ValueError("No path provided for loading index")
            
            load_path = Path(load_path)
            
            # Load FAISS index
            self.index = faiss.read_index(str(load_path / "faiss.index"))
            
            # Load documents and metadata
            with open(load_path / "documents.pkl", "rb") as f:
                self.documents = pickle.load(f)
            
            with open(load_path / "metadata.pkl", "rb") as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"Loaded vector store from {load_path}")
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal,
            "embedding_dimension": self.dimension,
            "embedding_model": self.embedding_model,
            "use_openai": self.use_openai,
        }
