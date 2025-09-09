#!/usr/bin/env python3
"""Simple test server to diagnose issues."""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test all imports."""
    try:
        print("Testing imports...")
        
        # Test basic imports
        from chancerag.utils.korean_tokenizer import KoreanTokenizer
        print("✓ Korean tokenizer imported")
        
        from chancerag.utils.streaming import stream_response
        print("✓ Streaming utilities imported")
        
        from chancerag.core.document_processor import DocumentProcessor
        print("✓ Document processor imported")
        
        from chancerag.core.vector_store import FAISSVectorStore
        print("✓ Vector store imported")
        
        from chancerag.core.retriever import RAGRetriever
        print("✓ Retriever imported")
        
        from chancerag.core.generator import RAGGenerator
        print("✓ Generator imported")
        
        from chancerag.config.settings import get_settings
        print("✓ Settings imported")
        
        print("\nAll imports successful!")
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality."""
    try:
        print("\nTesting basic functionality...")
        
        # Test Korean tokenizer
        from chancerag.utils.korean_tokenizer import KoreanTokenizer
        tokenizer = KoreanTokenizer()
        tokens = tokenizer.tokenize("안녕하세요. 반갑습니다.")
        print(f"✓ Korean tokenizer works: {tokens}")
        
        # Test settings
        from chancerag.config.settings import get_settings
        settings = get_settings()
        print(f"✓ Settings loaded: {settings.app_name}")
        
        print("\nBasic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("ChanceRAG Diagnostic Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed!")
        sys.exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Functionality test failed!")
        sys.exit(1)
    
    print("\n✅ All tests passed! System is ready.")

