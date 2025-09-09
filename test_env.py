#!/usr/bin/env python3
"""Test environment variable loading."""

import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_settings():
    """Test settings loading."""
    try:
        # Set environment variables
        os.environ['OPENAI_API_KEY'] = 'test-key-12345'
        os.environ['DEBUG'] = 'true'
        os.environ['USE_OPENAI_EMBEDDINGS'] = 'false'  # Use local embeddings for testing
        
        print("🔧 환경 변수 설정:")
        print(f"  OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY', 'Not set')}")
        print(f"  DEBUG: {os.environ.get('DEBUG', 'Not set')}")
        print(f"  USE_OPENAI_EMBEDDINGS: {os.environ.get('USE_OPENAI_EMBEDDINGS', 'Not set')}")
        
        # Test settings import
        from chancerag.config.settings import get_settings
        settings = get_settings()
        
        print("\n✅ 설정 로드 성공:")
        print(f"  App Name: {settings.app_name}")
        print(f"  Debug: {settings.debug}")
        print(f"  OpenAI API Key: {settings.openai_api_key[:10]}..." if settings.openai_api_key else "Not set")
        print(f"  Use OpenAI Embeddings: {settings.use_openai_embeddings}")
        print(f"  Vector Store Path: {settings.vector_store_path}")
        print(f"  Upload Path: {settings.upload_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 환경 변수 테스트")
    print("=" * 50)
    
    if test_settings():
        print("\n✅ 환경 변수 테스트 성공!")
    else:
        print("\n❌ 환경 변수 테스트 실패!")
        sys.exit(1)

