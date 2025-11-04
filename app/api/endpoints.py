import time
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..models.schemas import SearchRequest, SearchResponse, TrendingResponse, AnalysisRequest, AnalysisResponse, SearchFilters
from ..services.mcp_client import MCPClient, MockMCPClient
from ..utils.helpers import filter_papers_by_relevance, create_paper_card_data, create_repository_card_data

logger = logging.getLogger(__name__)

# Router tanımla
router = APIRouter(prefix="/api", tags=["papers"])

# Global client instance
_mcp_client = None

def get_mcp_client():
    """MCP client singleton"""
    global _mcp_client
    if _mcp_client is None:
        # Her zaman mock client kullan (gerçek MCP server için ayrı yapılandırma gerekli)
        _mcp_client = MockMCPClient()
        logger.info("Using mock MCP client for development")
    return _mcp_client

@router.get("/")
async def root():
    """API sağlık kontrolü"""
    return {"message": "Trending Papers API", "status": "healthy", "version": "1.0.0"}

@router.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "mcp_client": "connected"
        }
    }

@router.get("/trending", response_model=TrendingResponse)
async def get_trending_papers(
    limit: int = Query(20, ge=1, le=100, description="Getirilecek paper sayısı"),
    refresh: bool = Query(False, description="Verileri yenile")
):
    """Trending paper'ları getirir"""
    start_time = time.time()
    
    try:
        mcp_client = get_mcp_client()
        result = await mcp_client.get_trending_papers(limit=limit)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        papers_data = result.get("papers", [])
        
        # Veriyi kart formatına çevir
        trending_papers = []
        for paper in papers_data:
            paper_card = create_paper_card_data(paper)
            trending_papers.append(paper_card)
        
        # Trending papers'ı trends skoruna göre sırala
        trending_papers.sort(key=lambda x: x.get('trends_score', 0), reverse=True)
        
        response_time = time.time() - start_time
        
        return TrendingResponse(
            trending_papers=trending_papers,
            total_count=len(trending_papers)
        )
    
    except Exception as e:
        logger.error(f"Trending papers error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """Paper arama endpoint'i"""
    start_time = time.time()
    
    try:
        # Sorguyu doğrula
        if not request.query or len(request.query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        mcp_client = get_mcp_client()
        
        # Filtreleri hazırla
        filters = {
            "max_results": request.filters.max_results,
            "sort_by": request.filters.sort_by
        }
        
        if request.filters.categories:
            filters["categories"] = request.filters.categories
        
        if request.filters.date_range:
            filters["date_range"] = request.filters.date_range
        
        if request.filters.min_citations:
            filters["min_citations"] = request.filters.min_citations
        
        # Arama yap
        result = await mcp_client.search_arxiv_papers(
            query=request.query,
            filters=filters
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        papers_data = result.get("papers", [])
        
        # Relevans filtreleme
        if request.similarity_threshold > 0:
            papers_data = filter_papers_by_relevance(
                papers_data, 
                request.query, 
                request.similarity_threshold
            )
        
        # Repository bilgilerini ekle (paralel)
        papers_with_repos = []
        for paper in papers_data:
            paper_card = create_paper_card_data(paper)
            
            # Repository'leri paralel olarak getir
            try:
                repo_result = await mcp_client.find_code_repositories(
                    query=paper.get("title", ""),
                    limit=5
                )
                
                if "repositories" in repo_result:
                    repositories = [
                        create_repository_card_data(repo) 
                        for repo in repo_result["repositories"]
                    ]
                    paper_card["repositories"] = repositories
                else:
                    paper_card["repositories"] = []
            except Exception as e:
                logger.warning(f"Repository fetch failed for paper {paper.get('id')}: {str(e)}")
                paper_card["repositories"] = []
            
            papers_with_repos.append(paper_card)
        
        response_time = time.time() - start_time
        
        return SearchResponse(
            papers=papers_with_repos,
            total_count=len(papers_with_repos),
            search_time=response_time,
            query=request.query
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/paper/{paper_id}")
async def get_paper_details(paper_id: str):
    """Paper detaylarını getirir"""
    try:
        mcp_client = get_mcp_client()
        result = await mcp_client.get_paper_details(paper_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Paper details error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_papers(request: AnalysisRequest):
    """Paper analizi endpoint'i"""
    try:
        if not request.paper_ids:
            raise HTTPException(status_code=400, detail="No paper IDs provided")
        
        mcp_client = get_mcp_client()
        result = await mcp_client.analyze_papers(
            paper_ids=request.paper_ids,
            analysis_type=request.analysis_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnalysisResponse(
            paper_id=request.paper_ids[0],  # İlk paper ID'si
            analysis_results=result.get("analyses", {}),
            generated_at=time.time()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/similar/{paper_id}")
async def get_similar_papers(
    paper_id: str,
    limit: int = Query(5, ge=1, le=20, description="Benzer paper sayısı")
):
    """Benzer paper'ları getirir"""
    try:
        mcp_client = get_mcp_client()
        result = await mcp_client.get_similar_papers(
            paper_id=paper_id,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        similar_papers = result.get("similar_papers", [])
        return {
            "paper_id": paper_id,
            "similar_papers": similar_papers,
            "total_count": len(similar_papers)
        }
    
    except Exception as e:
        logger.error(f"Similar papers error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/repositories")
async def search_repositories(
    query: str = Query(..., description="Arama terimi"),
    limit: int = Query(10, ge=1, le=50, description="Repository sayısı")
):
    """GitHub repository'lerini arar"""
    try:
        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        mcp_client = get_mcp_client()
        result = await mcp_client.find_code_repositories(
            query=query,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        repositories = result.get("repositories", [])
        formatted_repos = [create_repository_card_data(repo) for repo in repositories]
        
        return {
            "repositories": formatted_repos,
            "total_count": len(formatted_repos),
            "query": query
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Repository search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/export/search")
async def export_search_results(
    format: str = Query("json", pattern="^(json|csv)$", description="Export formatı"),
    query: str = Query(..., description="Arama terimi"),
    limit: int = Query(50, ge=1, le=500, description="Sonuç sayısı")
):
    """Arama sonuçlarını export eder"""
    try:
        # Arama yap
        search_request = SearchRequest(
            query=query,
            filters=SearchFilters(
                max_results=limit,
                sort_by="relevance"
            ),
            similarity_threshold=0.7
        )
        
        search_response = await search_papers(search_request)
        
        if format == "json":
            # JSON export - Pydantic modellerini doğru şekilde serialize et
            papers_data = []
            for paper in search_response.papers:
                # Pydantic'in model_dump(mode='json') metodunu kullan - datetime'ları otomatik serialize eder
                paper_dict = paper.model_dump(mode='json') if hasattr(paper, 'model_dump') else paper.dict()
                papers_data.append(paper_dict)
            
            return JSONResponse(content={
                "query": query,
                "total_results": search_response.total_count,
                "papers": papers_data,
                "exported_at": time.time()
            })
        
        elif format == "csv":
            # CSV export
            csv_data = "Title,Authors,ArXiv ID,Citations,Categories\n"
            for paper in search_response.papers:
                title = f'"{paper.title.replace("\"", "\"\"\"")}"'
                authors = f'"{", ".join(paper.authors).replace("\"", "\"\"\"")}"'
                csv_data += f"{title},{authors},{paper.arxiv_id},{paper.citations}," + ", ".join(paper.categories) + "\n"
            
            return JSONResponse(
                content={"csv": csv_data},
                media_type="application/json"
            )
    
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/stats")
async def get_api_stats():
    """API istatistiklerini getirir"""
    return {
        "endpoints": {
            "/api/trending": "Trending papers",
            "/api/search": "Search papers",
            "/api/paper/{id}": "Paper details",
            "/api/analyze": "Analyze papers",
            "/api/similar/{id}": "Similar papers",
            "/api/repositories": "Search repositories",
            "/api/export/search": "Export results"
        },
        "features": [
            "Real-time search",
            "Relevance filtering",
            "Repository integration",
            "Paper analysis",
            "Export functionality"
        ],
        "version": "1.0.0"
    }