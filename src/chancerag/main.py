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
    # Serve the static HTML file
    static_path = Path(__file__).parent / "static" / "index.html"
    if static_path.exists():
        return HTMLResponse(content=static_path.read_text(encoding="utf-8"))
    else:
        # Fallback to simple HTML if static file doesn't exist
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ChanceRAG - KOICA 해외봉사단 규정 상담 챗봇</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>ChanceRAG</h1>
            <p>웹 인터페이스를 로드하는 중...</p>
            <p><a href="/docs">API 문서</a></p>
        </body>
        </html>
        """)


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
