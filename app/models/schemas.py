from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PaperBase(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    arxiv_id: str
    publication_date: datetime
    categories: List[str]
    pdf_url: str
    html_url: str

class Paper(PaperBase):
    id: str
    citations: int
    trends_score: float
    repositories: List['Repository'] = []
    similar_papers: List['Paper'] = []

class Repository(BaseModel):
    id: str
    name: str
    full_name: str
    description: str
    url: str
    stars: int
    forks: int
    language: str
    updated_at: datetime

class SearchFilters(BaseModel):
    categories: List[str] = []
    date_range: Optional[tuple[datetime, datetime]] = None
    min_citations: Optional[int] = 0
    max_results: int = 50
    sort_by: str = "relevance"

class SearchRequest(BaseModel):
    query: str
    filters: SearchFilters
    similarity_threshold: float = 0.7

class SearchResponse(BaseModel):
    papers: List[Paper]
    total_count: int
    search_time: float
    query: str

class TrendingResponse(BaseModel):
    trending_papers: List[Paper]
    total_count: int

class AnalysisRequest(BaseModel):
    paper_ids: List[str]
    analysis_type: str = "summary"

class AnalysisResponse(BaseModel):
    paper_id: str
    analysis_results: Dict[str, Any]
    generated_at: float

# Forward references'ları çöz
Paper.model_rebuild()
Repository.model_rebuild()