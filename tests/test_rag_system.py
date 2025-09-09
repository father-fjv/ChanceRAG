"""Test RAG system components."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from pathlib import Path

from src.chancerag.core.document_processor import DocumentProcessor
from src.chancerag.core.vector_store import FAISSVectorStore
from src.chancerag.core.retriever import RAGRetriever
from src.chancerag.core.generator import RAGGenerator
from src.chancerag.utils.korean_tokenizer import KoreanTokenizer


class TestDocumentProcessor:
    """Test document processor."""
    
    def test_init(self):
        """Test document processor initialization."""
        processor = DocumentProcessor()
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 100
        assert processor.korean_tokenizer is not None
    
    def test_get_document_info(self):
        """Test document info extraction."""
        processor = DocumentProcessor()
        
        # Mock documents
        docs = [
            Mock(page_content="Test content 1", metadata={"source": "test1.pdf"}),
            Mock(page_content="Test content 2", metadata={"source": "test2.pdf"}),
        ]
        
        info = processor.get_document_info(docs)
        
        assert info["total_chunks"] == 2
        assert info["unique_sources"] == 2
        assert "test1.pdf" in info["sources"]
        assert "test2.pdf" in info["sources"]


class TestFAISSVectorStore:
    """Test FAISS vector store."""
    
    @patch('src.chancerag.core.vector_store.OpenAIEmbeddings')
    def test_init_with_openai(self, mock_embeddings):
        """Test vector store initialization with OpenAI."""
        mock_embeddings.return_value = Mock()
        
        vector_store = FAISSVectorStore(use_openai=True)
        
        assert vector_store.use_openai is True
        assert vector_store.dimension == 1536
        assert vector_store.embeddings is not None
    
    def test_get_stats(self):
        """Test getting vector store statistics."""
        vector_store = FAISSVectorStore(use_openai=False)
        
        stats = vector_store.get_stats()
        
        assert "total_documents" in stats
        assert "index_size" in stats
        assert "embedding_dimension" in stats
        assert "embedding_model" in stats


class TestRAGRetriever:
    """Test RAG retriever."""
    
    def test_init(self):
        """Test retriever initialization."""
        mock_vector_store = Mock()
        retriever = RAGRetriever(mock_vector_store)
        
        assert retriever.top_k == 5
        assert retriever.score_threshold == 0.7
        assert retriever.vector_store == mock_vector_store
    
    def test_get_retrieval_stats(self):
        """Test getting retrieval statistics."""
        mock_vector_store = Mock()
        mock_vector_store.get_stats.return_value = {"test": "stats"}
        
        retriever = RAGRetriever(mock_vector_store)
        stats = retriever.get_retrieval_stats()
        
        assert "top_k" in stats
        assert "score_threshold" in stats
        assert "vector_store_stats" in stats


class TestRAGGenerator:
    """Test RAG generator."""
    
    @patch('src.chancerag.core.generator.ChatOpenAI')
    def test_init(self, mock_chat):
        """Test generator initialization."""
        mock_chat.return_value = Mock()
        mock_retriever = Mock()
        
        generator = RAGGenerator(mock_retriever)
        
        assert generator.model_name == "gpt-4o"
        assert generator.temperature == 0.1
        assert generator.max_tokens == 1000
        assert generator.retriever == mock_retriever
    
    def test_get_generator_stats(self):
        """Test getting generator statistics."""
        mock_retriever = Mock()
        mock_retriever.get_retrieval_stats.return_value = {"test": "stats"}
        
        generator = RAGGenerator(mock_retriever)
        stats = generator.get_generator_stats()
        
        assert "model_name" in stats
        assert "temperature" in stats
        assert "max_tokens" in stats
        assert "retriever_stats" in stats


class TestKoreanTokenizer:
    """Test Korean tokenizer."""
    
    def test_init(self):
        """Test tokenizer initialization."""
        tokenizer = KoreanTokenizer()
        assert tokenizer is not None
    
    def test_tokenize_korean_text(self):
        """Test Korean text tokenization."""
        tokenizer = KoreanTokenizer()
        text = "안녕하세요. 반갑습니다."
        tokens = tokenizer.tokenize(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert "안녕하세요" in tokens or "안녕" in tokens
    
    def test_tokenize_mixed_text(self):
        """Test mixed Korean and English text."""
        tokenizer = KoreanTokenizer()
        text = "Hello 안녕하세요 world"
        tokens = tokenizer.tokenize(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) > 0
    
    def test_preprocess_for_embedding(self):
        """Test text preprocessing for embedding."""
        tokenizer = KoreanTokenizer()
        text = "안녕하세요.   반갑습니다!"
        processed = tokenizer.preprocess_for_embedding(text)
        
        assert isinstance(processed, str)
        assert len(processed) > 0
        # Should normalize whitespace
        assert "  " not in processed


if __name__ == "__main__":
    pytest.main([__file__])
