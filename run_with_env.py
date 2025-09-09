#!/usr/bin/env python3
"""Run server with environment variables."""

import os
import sys
from pathlib import Path

# Set environment variables
os.environ['OPENAI_API_KEY'] = 'your_actual_openai_api_key_here'  # 실제 API 키로 변경하세요
os.environ['DEBUG'] = 'true'
os.environ['USE_OPENAI_EMBEDDINGS'] = 'false'  # 로컬 임베딩 사용
os.environ['HOST'] = '0.0.0.0'
os.environ['PORT'] = '8000'

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    print("🚀 ChanceRAG 서버 시작 중...")
    print("=" * 50)
    print("📋 환경 설정:")
    print(f"  OpenAI API Key: {os.environ.get('OPENAI_API_KEY', 'Not set')[:10]}...")
    print(f"  Debug Mode: {os.environ.get('DEBUG', 'false')}")
    print(f"  Use OpenAI Embeddings: {os.environ.get('USE_OPENAI_EMBEDDINGS', 'true')}")
    print(f"  Host: {os.environ.get('HOST', '0.0.0.0')}")
    print(f"  Port: {os.environ.get('PORT', '8000')}")
    print("=" * 50)
    
    try:
        from chancerag.main import main
        main()
    except KeyboardInterrupt:
        print("\n👋 서버가 중지되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

