import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

# TEMPORARILY DISABLED FOR TESTING
# from app.services.cloud_mcp_client import cloud_mcp_client
# from app.services.performance_monitor import performance_monitor
# from app.services.cache_service import cache_service

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Logging yapılandırması
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Rate limiting (TEMPORARILY DISABLED FOR TESTING)
# limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü yönetimi"""
    # Startup
    logger.info("Starting Trending Papers Cloud API...")
    
    try:
        # TEMPORARILY DISABLED FOR TESTING
        # Initialize performance monitoring
        # await performance_monitor.start_monitoring(interval=5.0)
        # logger.info("Performance monitoring initialized")
        
        # Test cache connection
        # await cache_service.initialize()
        # logger.info("Cache service initialized")
        
        # Test cloud services
        if os.getenv("USE_CLOUD_MCP", "false").lower() == "true":
            # async with cloud_mcp_client as client:
            #     # Test with minimal request
            #     test_result = await client.search_arxiv_papers("test", max_results=1)
            #     if test_result.get("success"):
            #         logger.info("Cloud MCP integration test successful")
            #     else:
            #         logger.warning("Cloud MCP integration test failed, using fallback")
            pass
        
        logger.info("Test server startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Continue with fallback services
    
    yield
    
    # Shutdown
    logger.info("Shutting down Trending Papers Cloud API...")
    
    try:
        # TEMPORARILY DISABLED FOR TESTING
        # await performance_monitor.stop_monitoring()
        # await cache_service.close()
        logger.info("Test shutdown completed successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# FastAPI uygulamasını oluştur
app = FastAPI(
    title=os.getenv("API_TITLE", "Trending Papers Cloud API"),
    description="Cloud-ready MCP server ile entegre çalışan araştırma paper'ları arama ve analiz API'si. Real API calls, caching, rate limiting ve performance monitoring ile optimize edilmiş.",
    version=os.getenv("API_VERSION", "2.0.0"),
    lifespan=lifespan
)

# Rate limiting middleware (TEMPORARILY DISABLED)
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router'ını ekle
from app.api.endpoints import router
app.include_router(router)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main page
@app.get("/")
async def serve_main_page():
    """Ana sayfa - HTML interface"""
    static_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    return FileResponse(static_path)

@app.get("/api")
async def api_info():
    """API bilgileri"""
    cache_stats = cache_service.get_stats() if cache_service else {}
    
    return {
        "name": os.getenv("API_TITLE", "Trending Papers Cloud API"),
        "version": os.getenv("API_VERSION", "2.0.0"),
        "description": "Cloud-ready MCP server ile entegre çalışan araştırma paper'ları arama ve analiz API'si",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "features": {
            "cloud_integration": os.getenv("USE_CLOUD_MCP", "false").lower() == "true",
            "caching": "redis" if cache_stats.get("backend") == "redis" else "memory",
            "rate_limiting": True,
            "performance_monitoring": True,
            "fallback_systems": os.getenv("ENABLE_FALLBACK_DATA", "true").lower() == "true"
        },
        "endpoints": {
            "GET /api/trending": "Trending paper'ları getirir",
            "POST /api/search": "Paper arama endpoint'i",
            "GET /api/paper/{id}": "Paper detayları",
            "POST /api/analyze": "Paper analizi",
            "GET /api/similar/{id}": "Benzer paper'lar",
            "GET /api/repositories": "GitHub repository arama",
            "GET /api/export/search": "Sonuçları export et",
            "GET /api/metrics": "Performance metrikleri",
            "GET /api/cache/stats": "Cache istatistikleri"
        },
        "cache_stats": cache_stats,
        "monitoring_enabled": os.getenv("ENABLE_METRICS", "false").lower() == "true"
    }

@app.get("/api/health")
async def health_check():
    """Detaylı sağlık kontrolü"""
    try:
        # Test services
        cache_status = "connected" if cache_service else "unavailable"
        
        # Get system stats
        system_stats = performance_monitor.get_system_stats() if performance_monitor else {}
        
        # Test cloud services
        cloud_status = "disabled"
        if os.getenv("USE_CLOUD_MCP", "false").lower() == "true":
            try:
                async with cloud_mcp_client as client:
                    test_result = await client.search_arxiv_papers("health", max_results=1)
                    cloud_status = "healthy" if test_result.get("success") else "degraded"
            except Exception as e:
                cloud_status = f"error: {str(e)}"
        
        return {
            "status": "healthy",
            "timestamp": performance_monitor.get_system_stats().get("timestamp", 0) if performance_monitor else 0,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "services": {
                "cache": cache_status,
                "cloud_mcp": cloud_status,
                "performance_monitor": "active" if performance_monitor else "inactive"
            },
            "system": system_stats,
            "version": os.getenv("API_VERSION", "2.0.0")
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": performance_monitor.get_system_stats().get("timestamp", 0) if performance_monitor else 0
        }

@app.get("/api/metrics")
async def get_performance_metrics():
    """Performance metrikleri endpoint'i"""
    if not os.getenv("ENABLE_METRICS", "false").lower() == "true":
        raise HTTPException(status_code=403, detail="Metrics disabled")
    
    try:
        metrics = performance_monitor.export_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Cache istatistikleri"""
    try:
        stats = cache_service.get_stats()
        return {
            "cache_stats": stats,
            "cache_enabled": bool(cache_service),
            "cache_backend": stats.get("backend", "unknown")
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {
            "cache_stats": {},
            "cache_enabled": False,
            "error": str(e)
        }

# Error handler'ları
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "Endpoint bulunamadı",
        "path": str(request.url.path),
        "available_endpoints": [
            "/api/trending", "/api/search", "/api/paper/{id}",
            "/api/analyze", "/api/similar/{id}", "/api/repositories",
            "/api/export/search", "/api/metrics", "/api/health"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return {
        "error": "Internal Server Error",
        "message": "Sunucu hatası oluştu",
        "path": str(request.url.path),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Cloud mode: {os.getenv('USE_CLOUD_MCP', 'false').lower() == 'true'}")
    logger.info(f"Metrics enabled: {os.getenv('ENABLE_METRICS', 'false').lower() == 'true'}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )