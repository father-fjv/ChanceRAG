#!/usr/bin/env python3
"""Simple FastAPI server for testing."""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

# Create FastAPI app
app = FastAPI(title="ChanceRAG Test Server", version="0.1.0")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "ChanceRAG Test Server is running!", "status": "ok"}

@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "message": "Server is running"}

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Test file upload."""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-korean")
async def test_korean():
    """Test Korean tokenizer."""
    try:
        from chancerag.utils.korean_tokenizer import KoreanTokenizer
        tokenizer = KoreanTokenizer()
        tokens = tokenizer.tokenize("안녕하세요. 반갑습니다.")
        
        return {
            "message": "Korean tokenizer test",
            "input": "안녕하세요. 반갑습니다.",
            "tokens": tokens
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting ChanceRAG Test Server...")
    print("Access at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

