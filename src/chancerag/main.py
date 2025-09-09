"""Main FastAPI application."""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from .config import get_settings
from .api.routes import router
from .api.dependencies import get_rag_system

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Korean RAG system for company regulations using OpenAI and FAISS",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Serve static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main page."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ChanceRAG - KOICA 해외봉사단 규정 상담 챗봇</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .description {
                color: #666;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            .api-links {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }
            .api-link {
                display: inline-block;
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            .api-link:hover {
                background-color: #0056b3;
            }
            .features {
                margin-top: 40px;
            }
            .feature {
                margin-bottom: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
            .feature h3 {
                margin-top: 0;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ChanceRAG</h1>
            <p class="description">
                사내 직원이 규정을 빠르게 찾아보고 이해할 수 있도록, PDF 규정을 RAG로 검색·답변해 주는 웹 기반 챗봇입니다.
            </p>
            
            <div class="api-links">
                <a href="/docs" class="api-link">📚 API 문서</a>
                <a href="/redoc" class="api-link">📖 ReDoc</a>
                <a href="/api/v1/health" class="api-link">💚 상태 확인</a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🔍 지능형 검색</h3>
                    <p>FAISS 벡터 데이터베이스를 활용한 의미적 문서 검색으로 정확한 규정 조항을 찾아드립니다.</p>
                </div>
                
                <div class="feature">
                    <h3>🤖 AI 답변 생성</h3>
                    <p>OpenAI GPT-4를 활용하여 복잡한 규정을 이해하기 쉬운 언어로 설명해드립니다.</p>
                </div>
                
                <div class="feature">
                    <h3>🇰🇷 한국어 최적화</h3>
                    <p>Kiwi 형태소 분석기를 활용한 한국어 텍스트 처리로 더 정확한 검색 결과를 제공합니다.</p>
                </div>
                
                <div class="feature">
                    <h3>⚡ 실시간 스트리밍</h3>
                    <p>답변을 실시간으로 스트리밍하여 빠른 응답 속도를 제공합니다.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Create necessary directories
    Path(settings.data_path).mkdir(exist_ok=True)
    Path(settings.upload_path).mkdir(exist_ok=True)
    Path(settings.vector_store_path).mkdir(parents=True, exist_ok=True)
    
    # Initialize RAG system
    try:
        rag_system = await get_rag_system().__anext__()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        # Don't raise exception to allow server to start


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down ChanceRAG")


def main():
    """Run the application."""
    uvicorn.run(
        "chancerag.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
