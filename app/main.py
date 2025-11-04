import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.api.endpoints import router
from app.services.mcp_client import MCPClient, MockMCPClient

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü yönetimi"""
    # Startup
    logger.info("Starting Trending Papers API...")
    
    # MCP client test - her zaman mock data kullan
    try:
        # Mock data ile test yap
        from app.services.mcp_client import MockMCPClient
        async with MockMCPClient() as client:
            result = await client.get_trending_papers(limit=1)
            logger.info("Mock data test successful")
    except:
        logger.warning("Mock data test failed")
    
    logger.info("Using mock data for development")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Trending Papers API...")

# FastAPI uygulamasını oluştur
app = FastAPI(
    title="Trending Papers API",
    description="MCP server ile entegre çalışan araştırma paper'ları arama ve analiz API'si",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gradio interface için
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router'ını ekle
app.include_router(router)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main page
@app.get("/")
async def serve_main_page():
    """Ana sayfa - HTML interface"""
    import os
    static_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    return FileResponse(static_path)

@app.get("/api")
async def api_info():
    """API bilgileri"""
    return {
        "name": "Trending Papers API",
        "version": "1.0.0",
        "description": "MCP server ile entegre çalışan araştırma paper'ları arama ve analiz API'si",
        "endpoints": {
            "GET /api/trending": "Trending paper'ları getirir",
            "POST /api/search": "Paper arama endpoint'i",
            "GET /api/paper/{id}": "Paper detayları",
            "POST /api/analyze": "Paper analizi",
            "GET /api/similar/{id}": "Benzer paper'lar",
            "GET /api/repositories": "GitHub repository arama",
            "GET /api/export/search": "Sonuçları export et"
        },
        "features": [
            "Real-time paper search",
            "ArXiv integration",
            "GitHub repository discovery",
            "Paper analysis and insights",
            "Relevance filtering",
            "Export functionality (JSON/CSV)"
        ]
    }

# Error handler'ları
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "Endpoint bulunamadı",
        "path": str(request.url.path)
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return {
        "error": "Internal Server Error",
        "message": "Sunucu hatası oluştu",
        "path": str(request.url.path)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )