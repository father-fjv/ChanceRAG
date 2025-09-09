"""RAG generator module for answer generation."""

import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import asyncio
from concurrent.futures import ThreadPoolExecutor

from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from ..utils.streaming import stream_response

from .retriever import RAGRetriever

logger = logging.getLogger(__name__)


class RAGGenerator:
    """RAG generator for Korean answer generation."""
    
    def __init__(
        self,
        retriever: RAGRetriever,
        model_name: str = "gpt-4o",
        temperature: float = 0.1,
        max_tokens: int = 1000,
    ):
        """
        Initialize RAG generator.
        
        Args:
            retriever: RAG retriever instance
            model_name: OpenAI model name
            temperature: Model temperature
            max_tokens: Maximum tokens to generate
        """
        self.retriever = retriever
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize OpenAI chat model
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
        )
        
        # Korean-optimized system prompt
        self.system_prompt = """당신은 사내 규정을 전문적으로 해석하고 설명하는 AI 어시스턴트입니다.

주어진 규정 문서를 바탕으로 직원의 질문에 정확하고 이해하기 쉬운 답변을 제공해주세요.

답변 시 다음 사항을 준수해주세요:
1. 규정의 정확한 조항을 인용하고 출처를 명시하세요
2. 복잡한 법적 문구를 일상 언어로 쉽게 설명하세요
3. 구체적인 예시나 상황을 들어 설명하세요
4. 답변을 찾을 수 없는 경우 솔직히 말씀해주세요
5. 한국어로 자연스럽게 답변해주세요

답변 형식:
- 핵심 답변: 질문에 대한 직접적인 답변
- 근거 조항: 관련 규정 조항 인용
- 쉬운 설명: 이해하기 쉬운 추가 설명
- 출처: 문서명 및 조항 번호"""
        
        self.user_prompt_template = """다음은 사내 규정 문서에서 검색된 관련 내용입니다:

{context}

질문: {question}

위 규정 내용을 바탕으로 질문에 답변해주세요."""
    
    async def generate_answer(
        self, 
        question: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate answer for a question.
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            logger.info(f"Generating answer for question: {question}")
            
            # Retrieve relevant documents
            results = await self.retriever.retrieve(
                query=question,
                top_k=top_k,
                score_threshold=score_threshold
            )
            
            if not results:
                return {
                    "answer": "죄송합니다. 관련 규정을 찾을 수 없습니다. 다른 키워드로 검색해보시거나 HR팀에 문의해주세요.",
                    "sources": [],
                    "confidence": 0.0,
                    "metadata": {
                        "retrieved_docs": 0,
                        "question": question,
                    }
                }
            
            # Prepare context from retrieved documents
            context = self._prepare_context(results)
            
            # Generate answer
            answer = await self._generate_with_context(question, context)
            
            # Prepare sources
            sources = self._prepare_sources(results)
            
            # Calculate confidence based on retrieval scores
            confidence = self._calculate_confidence(results)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "metadata": {
                    "retrieved_docs": len(results),
                    "question": question,
                    "model": self.model_name,
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "죄송합니다. 답변 생성 중 오류가 발생했습니다. 다시 시도해주세요.",
                "sources": [],
                "confidence": 0.0,
                "metadata": {
                    "error": str(e),
                    "question": question,
                }
            }
    
    async def generate_streaming_answer(
        self, 
        question: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming answer for a question.
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score
            
        Yields:
            Streaming answer tokens
        """
        try:
            logger.info(f"Generating streaming answer for question: {question}")
            
            # Retrieve relevant documents
            results = await self.retriever.retrieve(
                query=question,
                top_k=top_k,
                score_threshold=score_threshold
            )
            
            if not results:
                yield "죄송합니다. 관련 규정을 찾을 수 없습니다. 다른 키워드로 검색해보시거나 HR팀에 문의해주세요."
                return
            
            # Prepare context from retrieved documents
            context = self._prepare_context(results)
            
            # Generate streaming answer
            async for token in self._generate_streaming_with_context(question, context):
                yield token
                
        except Exception as e:
            logger.error(f"Error generating streaming answer: {e}")
            yield "죄송합니다. 답변 생성 중 오류가 발생했습니다. 다시 시도해주세요."
    
    def _prepare_context(self, results: List[tuple]) -> str:
        """
        Prepare context from retrieved documents.
        
        Args:
            results: List of (document, score) tuples
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get("source", "Unknown")
            filename = doc.metadata.get("filename", "Unknown")
            page = doc.metadata.get("page", 0)
            
            context_parts.append(
                f"[문서 {i}] {filename} (페이지 {page})\n"
                f"관련도: {score:.2f}\n"
                f"내용: {doc.page_content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _prepare_sources(self, results: List[tuple]) -> List[Dict[str, Any]]:
        """
        Prepare sources information.
        
        Args:
            results: List of (document, score) tuples
            
        Returns:
            List of source dictionaries
        """
        sources = []
        
        for doc, score in results:
            source = {
                "content": doc.page_content,
                "source": doc.metadata.get("source", ""),
                "filename": doc.metadata.get("filename", ""),
                "page": doc.metadata.get("page", 0),
                "score": score,
            }
            sources.append(source)
        
        return sources
    
    def _calculate_confidence(self, results: List[tuple]) -> float:
        """
        Calculate confidence score based on retrieval results.
        
        Args:
            results: List of (document, score) tuples
            
        Returns:
            Confidence score between 0 and 1
        """
        if not results:
            return 0.0
        
        # Use average score of top results
        scores = [score for _, score in results]
        avg_score = sum(scores) / len(scores)
        
        # Normalize to 0-1 range (assuming scores are 0-1)
        return min(avg_score, 1.0)
    
    async def _generate_with_context(self, question: str, context: str) -> str:
        """
        Generate answer with context using OpenAI API.
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        try:
            # Prepare messages
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=self.user_prompt_template.format(
                    context=context,
                    question=question
                ))
            ]
            
            # Generate answer
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: self.llm.invoke(messages)
                )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating answer with context: {e}")
            raise
    
    async def _generate_streaming_with_context(
        self, 
        question: str, 
        context: str
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming answer with context.
        
        Args:
            question: User question
            context: Retrieved context
            
        Yields:
            Streaming answer tokens
        """
        try:
            # Prepare messages
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=self.user_prompt_template.format(
                    context=context,
                    question=question
                ))
            ]
            
            # Generate streaming response
            response = self.llm.stream(messages)
            
            # Use langchain-teddynote streaming function
            for chunk in response:
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"Error generating streaming answer: {e}")
            yield "답변 생성 중 오류가 발생했습니다."
    
    def get_generator_stats(self) -> Dict[str, Any]:
        """
        Get generator statistics.
        
        Returns:
            Dictionary with generator stats
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "retriever_stats": self.retriever.get_retrieval_stats(),
        }
