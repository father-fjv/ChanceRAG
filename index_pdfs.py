#!/usr/bin/env python3
"""Script to index PDF files in the uploads directory."""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def index_pdfs():
    """Index all PDF files in the uploads directory."""
    try:
        # Import required modules
        from chancerag.config import get_settings
        from chancerag.core.document_processor import DocumentProcessor
        from chancerag.core.vector_store import FAISSVectorStore
        from chancerag.api.dependencies import get_rag_system
        
        print("🔍 PDF 파일 인덱싱 시작...")
        
        # Get settings
        settings = get_settings()
        upload_path = Path(settings.upload_path)
        
        # Check if upload directory exists
        if not upload_path.exists():
            print(f"❌ 업로드 디렉토리가 존재하지 않습니다: {upload_path}")
            return
        
        # Find PDF files
        pdf_files = list(upload_path.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ PDF 파일을 찾을 수 없습니다: {upload_path}")
            return
        
        print(f"📁 발견된 PDF 파일: {len(pdf_files)}개")
        for pdf_file in pdf_files:
            print(f"  - {pdf_file.name}")
        
        # Initialize RAG system
        print("🚀 RAG 시스템 초기화 중...")
        rag_system = await get_rag_system().__anext__()
        
        # Get components
        document_processor = rag_system.get_document_processor()
        vector_store = rag_system.get_vector_store()
        
        # Process each PDF file
        for pdf_file in pdf_files:
            print(f"\n📄 처리 중: {pdf_file.name}")
            
            try:
                # Load and process document
                documents = document_processor.load_pdf(str(pdf_file))
                print(f"  ✓ 문서 로드 완료: {len(documents)}개 청크")
                
                # Add to vector store
                vector_store.add_documents(documents)
                print(f"  ✓ 벡터 저장소에 추가 완료")
                
            except Exception as e:
                print(f"  ❌ 오류 발생: {e}")
                continue
        
        # Save vector store
        print("\n💾 벡터 저장소 저장 중...")
        vector_store.save()
        print("✅ 인덱싱 완료!")
        
        # Show statistics
        stats = vector_store.get_stats()
        print(f"\n📊 인덱스 통계:")
        print(f"  - 총 문서 수: {stats.get('total_documents', 0)}")
        print(f"  - 총 청크 수: {stats.get('total_chunks', 0)}")
        print(f"  - 벡터 차원: {stats.get('vector_dimension', 0)}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(index_pdfs())
