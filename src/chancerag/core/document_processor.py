"""PDF document processing module for Korean text."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from ..utils.korean_tokenizer import KoreanTokenizer

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """PDF document processor with Korean text optimization."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        separators: Optional[List[str]] = None,
    ):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks
            separators: Text separators for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Korean-optimized separators
        if separators is None:
            separators = [
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence endings
                "! ",    # Exclamation
                "? ",    # Question
                "。",    # Korean period
                "！",    # Korean exclamation
                "？",    # Korean question
                " ",     # Space
                "",      # Character level
            ]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
        )
        
        # Initialize Korean tokenizer
        self.korean_tokenizer = KoreanTokenizer()
        
    async def process_pdf(self, pdf_path: str) -> List[Document]:
        """
        Process PDF file and return list of documents.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of processed documents
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Load PDF using PyPDFLoader
            loader = PyPDFLoader(str(pdf_path))
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    "source": str(pdf_path),
                    "filename": pdf_path.name,
                    "file_type": "pdf",
                })
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Process Korean text for better chunking
            processed_chunks = await self._process_korean_text(chunks)
            
            logger.info(f"Processed {len(processed_chunks)} chunks from {pdf_path}")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise
    
    async def _process_korean_text(self, documents: List[Document]) -> List[Document]:
        """
        Process Korean text in documents for better chunking.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of processed documents
        """
        processed_docs = []
        
        for doc in documents:
            try:
                # Tokenize Korean text
                tokens = self.korean_tokenizer.tokenize(doc.page_content)
                
                # Reconstruct text with proper spacing
                processed_text = " ".join(tokens)
                
                # Create new document with processed text
                processed_doc = Document(
                    page_content=processed_text,
                    metadata=doc.metadata.copy()
                )
                
                processed_docs.append(processed_doc)
                
            except Exception as e:
                logger.warning(f"Error processing Korean text: {e}")
                # Fallback to original document
                processed_docs.append(doc)
        
        return processed_docs
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[Document]:
        """
        Process multiple PDF files concurrently.
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            List of all processed documents
        """
        async def process_all():
            tasks = [self.process_pdf(pdf_path) for pdf_path in pdf_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_documents = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error processing PDF: {result}")
                else:
                    all_documents.extend(result)
            
            return all_documents
        
        return asyncio.run(process_all())
    
    def get_document_info(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Get information about processed documents.
        
        Args:
            documents: List of documents
            
        Returns:
            Dictionary with document statistics
        """
        total_chunks = len(documents)
        total_chars = sum(len(doc.page_content) for doc in documents)
        avg_chunk_size = total_chars / total_chunks if total_chunks > 0 else 0
        
        sources = set(doc.metadata.get("source", "unknown") for doc in documents)
        
        return {
            "total_chunks": total_chunks,
            "total_characters": total_chars,
            "average_chunk_size": avg_chunk_size,
            "unique_sources": len(sources),
            "sources": list(sources),
        }
