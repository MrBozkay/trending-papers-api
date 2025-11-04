import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

class MCPClient:
    """MCP Server istemcisi"""
    
    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _ensure_session(self):
        """Ensure session is initialized"""
        if self.session is None:
            import asyncio
            # For synchronous usage, create a new session
            self.session = aiohttp.ClientSession()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP server tool'unu çağırır"""
        try:
            self._ensure_session()
            async with self.session.post(
                f"{self.server_url}/tools/{tool_name}",
                json=arguments,
                timeout=30
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"MCP server error: {response.status}")
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"MCP client error: {str(e)}")
            return {"error": str(e)}
    
    async def get_trending_papers(self, limit: int = 20) -> Dict[str, Any]:
        """Trending paper'ları getirir"""
        return await self.call_tool("get_trending_papers", {"limit": limit})
    
    async def search_arxiv_papers(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """ArXiv'te paper arar"""
        return await self.call_tool("search_arxiv_papers", {
            "query": query,
            "filters": filters
        })
    
    async def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """Paper detaylarını getirir"""
        return await self.call_tool("get_paper_details", {"paper_id": paper_id})
    
    async def get_similar_papers(self, paper_id: str, limit: int = 5) -> Dict[str, Any]:
        """Benzer paper'ları getirir"""
        return await self.call_tool("get_similar_papers", {
            "paper_id": paper_id,
            "limit": limit
        })
    
    async def find_code_repositories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """GitHub repository'lerini bulur"""
        return await self.call_tool("find_code_repositories", {
            "query": query,
            "limit": limit
        })
    
    async def analyze_papers(self, paper_ids: List[str], analysis_type: str) -> Dict[str, Any]:
        """Paper'ları analiz eder"""
        return await self.call_tool("analyze_papers", {
            "paper_ids": paper_ids,
            "analysis_type": analysis_type
        })

class MockMCPClient:
    """Mock MCP client - test ve development için"""
    
    def __init__(self):
        self.mock_data = self._load_mock_data()
    
    def _load_mock_data(self):
        """Mock data'yı yükler"""
        try:
            with open("data/sample_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            # Varsayılan mock data
            return {
                "papers": [
                    {
                        "id": "mock-1",
                        "title": "Attention Is All You Need",
                        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
                        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
                        "arxiv_id": "1706.03762",
                        "publication_date": "2017-06-12T00:00:00",
                        "categories": ["cs.CL", "cs.LG", "cs.NE"],
                        "citations": 95000,
                        "trends_score": 95.5,
                        "pdf_url": "https://arxiv.org/pdf/1706.03762",
                        "html_url": "https://arxiv.org/abs/1706.03762"
                    },
                    {
                        "id": "mock-2",
                        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                        "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
                        "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
                        "arxiv_id": "1810.04805",
                        "publication_date": "2018-10-11T00:00:00",
                        "categories": ["cs.CL", "cs.LG"],
                        "citations": 72000,
                        "trends_score": 92.3,
                        "pdf_url": "https://arxiv.org/pdf/1810.04805",
                        "html_url": "https://arxiv.org/abs/1810.04805"
                    },
                    {
                        "id": "mock-3",
                        "title": "GPT-3: Language Models are Few-Shot Learners",
                        "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah"],
                        "abstract": "We show that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches. Specifically, we present GPT-3, an autoregressive language model with 175 billion parameters, 10x more than any previous non-sparse language model.",
                        "arxiv_id": "2005.14165",
                        "publication_date": "2020-05-28T00:00:00",
                        "categories": ["cs.CL", "cs.LG", "cs.NE"],
                        "citations": 18000,
                        "trends_score": 88.7,
                        "pdf_url": "https://arxiv.org/pdf/2005.14165",
                        "html_url": "https://arxiv.org/abs/2005.14165"
                    }
                ]
            }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def get_trending_papers(self, limit: int = 20) -> Dict[str, Any]:
        """Mock trending papers"""
        await asyncio.sleep(0.1)  # Simulate delay
        papers = self.mock_data["papers"][:limit]
        return {"papers": papers, "total": len(papers)}
    
    async def search_arxiv_papers(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock paper search"""
        await asyncio.sleep(0.2)  # Simulate delay
        
        # Simple mock search
        papers = [p for p in self.mock_data["papers"] 
                 if query.lower() in p["title"].lower() or query.lower() in p["abstract"].lower()]
        
        # Apply filters
        max_results = filters.get("max_results", 50)
        if filters.get("min_citations"):
            papers = [p for p in papers if p["citations"] >= filters["min_citations"]]
        
        return {"papers": papers[:max_results], "total": len(papers[:max_results])}
    
    async def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """Mock paper details"""
        await asyncio.sleep(0.1)
        paper = next((p for p in self.mock_data["papers"] if p["id"] == paper_id), None)
        if paper:
            return paper
        return {"error": "Paper not found"}
    
    async def get_similar_papers(self, paper_id: str, limit: int = 5) -> Dict[str, Any]:
        """Mock similar papers"""
        await asyncio.sleep(0.15)
        papers = self.mock_data["papers"][1:limit+1]  # Exclude the first paper
        return {"similar_papers": papers, "total": len(papers)}
    
    async def find_code_repositories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Mock GitHub repositories"""
        await asyncio.sleep(0.25)
        repositories = [
            {
                "id": f"repo-{i}",
                "name": f"{query.lower().replace(' ', '-')}-implementation-{i}",
                "full_name": f"user/repo-{i}",
                "description": f"Implementation of {query} algorithm in Python",
                "url": f"https://github.com/user/repo-{i}",
                "stars": 100 + i * 10,
                "forks": 20 + i * 5,
                "language": "Python",
                "updated_at": "2024-01-01T00:00:00"
            }
            for i in range(1, min(limit + 1, 6))
        ]
        return {"repositories": repositories, "total": len(repositories)}
    
    async def analyze_papers(self, paper_ids: List[str], analysis_type: str) -> Dict[str, Any]:
        """Mock paper analysis"""
        await asyncio.sleep(0.3)
        analyses = {
            "summary": "This paper presents significant contributions to the field with novel approaches and experimental validation.",
            "key_findings": ["Method shows 15% improvement", "Scalable to large datasets", "Reproducible results"],
            "methodology": "The authors use a combination of theoretical analysis and experimental validation.",
            "limitations": "Dataset size may limit generalizability", "Computational requirements are high"
        }
        return {"analyses": analyses}