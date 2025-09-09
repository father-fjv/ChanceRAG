#!/usr/bin/env python3
"""Script to index PDF files using local embeddings."""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def index_pdfs_local():
    """Index all PDF files using local embeddings."""
    try:
        print("🔍 PDF 파일 인덱싱 시작 (로컬 임베딩 사용)...")
        
        # Import required modules
        from chancerag.core.document_processor import DocumentProcessor
        from chancerag.core.vector_store import FAISSVectorStore
        
        # Settings
        upload_path = Path("./data/uploads")
        vector_store_path = Path("./data/vector_store")
        chunk_size = 1000
        chunk_overlap = 100
        
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
        
        # Initialize document processor
        print("📄 문서 프로세서 초기화 중...")
        document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        
        # Initialize vector store with local embeddings
        print("🔢 벡터 저장소 초기화 중 (로컬 임베딩)...")
        vector_store = FAISSVectorStore(
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            use_openai=False,  # Use local embeddings
            index_path=str(vector_store_path),
        )
        
        # Process each PDF file
        all_documents = []
        for pdf_file in pdf_files:
            print(f"\n📄 처리 중: {pdf_file.name}")
            
            try:
                # Load and process document
                documents = document_processor.load_pdf(str(pdf_file))
                print(f"  ✓ 문서 로드 완료: {len(documents)}개 청크")
                all_documents.extend(documents)
                
            except Exception as e:
                print(f"  ❌ 오류 발생: {e}")
                continue
        
        if all_documents:
            # Add all documents to vector store
            print(f"\n💾 벡터 저장소에 추가 중... (총 {len(all_documents)}개 청크)")
            vector_store.add_documents(all_documents)
            
            # Save vector store
            print("💾 벡터 저장소 저장 중...")
            vector_store.save()
            print("✅ 인덱싱 완료!")
            
            # Show statistics
            stats = vector_store.get_stats()
            print(f"\n📊 인덱스 통계:")
            print(f"  - 총 문서 수: {stats.get('total_documents', 0)}")
            print(f"  - 총 청크 수: {stats.get('total_chunks', 0)}")
            print(f"  - 벡터 차원: {stats.get('vector_dimension', 0)}")
        else:
            print("❌ 처리할 문서가 없습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(index_pdfs_local())

