"""API routes."""

import logging
import time
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import asyncio

from ..config import get_settings
from ..models.query import QueryRequest, QueryResponse
from ..models.response import RAGResponse, SourceInfo
from .dependencies import get_rag_system, RAGSystem

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ChanceRAG API",
        "version": "0.1.0",
        "status": "running"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """
    Query documents and get answer.
    
    Args:
        request: Query request
        rag_system: RAG system dependency
        
    Returns:
        Query response with answer
    """
    try:
        start_time = time.time()
        
        logger.info(f"Processing query: {request.question}")
        
        # Generate answer
        result = await rag_system.get_generator().generate_answer(
            question=request.question,
            top_k=request.top_k,
            score_threshold=request.score_threshold
        )
        
        processing_time = time.time() - start_time
        
        # Prepare sources if requested
        sources = None
        if request.include_sources and result.get("sources"):
            sources = [
                {
                    "content": source["content"],
                    "filename": source["filename"],
                    "page": source["page"],
                    "score": source["score"]
                }
                for source in result["sources"]
            ]
        
        return QueryResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            processing_time=processing_time,
            retrieved_docs=result["metadata"].get("retrieved_docs", 0),
            sources=sources,
            metadata=result["metadata"]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def query_documents_stream(
    request: QueryRequest,
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """
    Query documents and get streaming answer.
    
    Args:
        request: Query request
        rag_system: RAG system dependency
        
    Returns:
        Streaming response
    """
    try:
        logger.info(f"Processing streaming query: {request.question}")
        
        async def generate_stream():
            """Generate streaming response."""
            try:
                async for token in rag_system.get_generator().generate_streaming_answer(
                    question=request.question,
                    top_k=request.top_k,
                    score_threshold=request.score_threshold
                ):
                    yield f"data: {token}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for better UX
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                yield f"data: Error: {str(e)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing streaming query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """
    Upload and process PDF document.
    
    Args:
        file: PDF file to upload
        rag_system: RAG system dependency
        
    Returns:
        Upload result
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        logger.info(f"Uploading file: {file.filename}")
        
        # Save uploaded file
        settings = get_settings()
        upload_path = settings.upload_path
        file_path = f"{upload_path}/{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        documents = await rag_system.get_document_processor().process_pdf(file_path)
        
        # Add to vector store
        await rag_system.get_vector_store().add_documents(documents)
        
        # Save vector store
        rag_system.get_vector_store().save_index()
        
        return {
            "message": "Document uploaded and processed successfully",
            "filename": file.filename,
            "chunks": len(documents),
            "file_path": file_path
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_system_stats(
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """
    Get system statistics.
    
    Args:
        rag_system: RAG system dependency
        
    Returns:
        System statistics
    """
    try:
        vector_store_stats = rag_system.get_vector_store().get_stats()
        retriever_stats = rag_system.get_retriever().get_retrieval_stats()
        generator_stats = rag_system.get_generator().get_generator_stats()
        
        return {
            "vector_store": vector_store_stats,
            "retriever": retriever_stats,
            "generator": generator_stats,
            "system_status": "running"
        }
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/faq/questions")
async def get_faq_questions(count: int = 4):
    """
    Get random FAQ questions.
    
    Args:
        count: Number of questions to return (default: 4)
        
    Returns:
        List of random FAQ questions
    """
    try:
        # Import FAQ questions
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from faq_questions import get_random_questions
        
        questions = get_random_questions(count)
        return {
            "questions": questions,
            "count": len(questions)
        }
        
    except Exception as e:
        logger.error(f"Error getting FAQ questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/faq/related")
async def get_related_questions(
    request: QueryRequest,
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """
    Get related questions based on current query.
    
    Args:
        request: Query request
        rag_system: RAG system dependency
        
    Returns:
        List of related questions
    """
    try:
        # Import FAQ questions
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from faq_questions import get_all_questions
        
        all_questions = get_all_questions()
        
        # Use vector store to find similar questions
        vector_store = rag_system.get_vector_store()
        
        # Create temporary documents for FAQ questions
        from langchain.schema import Document
        faq_docs = [Document(page_content=q, metadata={"type": "faq_question"}) for q in all_questions]
        
        # Find similar questions
        similar_docs = await vector_store.similarity_search(
            query=request.question,
            k=3,
            score_threshold=0.3
        )
        
        # Extract questions from similar documents
        related_questions = []
        for doc, score in similar_docs:
            if doc.metadata.get("type") == "faq_question":
                related_questions.append(doc.page_content)
        
        # If not enough FAQ questions found, add some random ones
        if len(related_questions) < 3:
            import random
            remaining_needed = 3 - len(related_questions)
            available_questions = [q for q in all_questions if q not in related_questions]
            if available_questions:
                additional_questions = random.sample(
                    available_questions, 
                    min(remaining_needed, len(available_questions))
                )
                related_questions.extend(additional_questions)
        
        return {
            "related_questions": related_questions[:3],
            "count": len(related_questions[:3])
        }
        
    except Exception as e:
        logger.error(f"Error getting related questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """
    Delete document from system.
    
    Args:
        filename: Filename to delete
        rag_system: RAG system dependency
        
    Returns:
        Deletion result
    """
    try:
        # Note: This is a simplified implementation
        # In a production system, you would need to:
        # 1. Remove documents from vector store
        # 2. Rebuild index
        # 3. Remove file from storage
        
        logger.info(f"Deleting document: {filename}")
        
        return {
            "message": f"Document {filename} deletion requested",
            "note": "Full deletion not implemented in this version"
        }
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
