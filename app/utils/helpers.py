import re
import logging
from typing import List, Dict, Any
from datetime import datetime
from difflib import SequenceMatcher
import html

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Metni temizler"""
    # HTML etiketlerini temizle
    text = html.unescape(text)
    # Çoklu boşlukları tek boşluğa çevir
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_authors(text: str) -> List[str]:
    """Metinden yazarları çıkarır"""
    if not text:
        return []
    
    # Yaygın yazar ayırıcıları
    separators = [',', ' and ', ' & ', ';', '|']
    authors = [text]
    
    for sep in separators:
        for i, author in enumerate(authors):
            parts = author.split(sep)
            if len(parts) > 1:
                authors[i:i+1] = [p.strip() for p in parts if p.strip()]
    
    # Son kontrol ve temizlik
    cleaned_authors = []
    for author in authors:
        author = author.strip()
        if author and len(author) > 1:
            cleaned_authors.append(author)
    
    return cleaned_authors

def calculate_similarity(text1: str, text2: str) -> float:
    """İki metin arasındaki benzerlik skorunu hesaplar"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def filter_papers_by_relevance(papers: List[Dict], query: str, threshold: float = 0.7) -> List[Dict]:
    """Paper'ları relevance skoruna göre filtreler"""
    filtered_papers = []
    
    for paper in papers:
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        
        # Title ve abstract'e göre similarity hesapla
        title_similarity = calculate_similarity(query, title)
        abstract_similarity = calculate_similarity(query, abstract)
        
        # Ağırlıklı ortalama (title'a daha fazla ağırlık)
        relevance_score = (title_similarity * 0.7) + (abstract_similarity * 0.3)
        
        if relevance_score >= threshold:
            paper['relevance_score'] = relevance_score
            filtered_papers.append(paper)
    
    # Relevance skoruna göre sırala
    filtered_papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return filtered_papers

def create_paper_card_data(paper: Dict[str, Any]) -> Dict[str, Any]:
    """Paper verisini kart formatına çevirir"""
    return {
        "id": paper.get("id", ""),
        "title": paper.get("title", ""),
        "authors": paper.get("authors", []),
        "abstract": paper.get("abstract", "")[:500] + "..." if len(paper.get("abstract", "")) > 500 else paper.get("abstract", ""),
        "arxiv_id": paper.get("arxiv_id", ""),
        "publication_date": paper.get("publication_date"),
        "categories": paper.get("categories", []),
        "citations": paper.get("citations", 0),
        "trends_score": paper.get("trends_score", 0),
        "pdf_url": paper.get("pdf_url", ""),
        "html_url": paper.get("html_url", ""),
        "repositories": paper.get("repositories", []),
        "similar_papers": paper.get("similar_papers", [])
    }

def create_repository_card_data(repo: Dict[str, Any]) -> Dict[str, Any]:
    """Repository verisini kart formatına çevirir"""
    return {
        "id": repo.get("id", ""),
        "name": repo.get("name", ""),
        "full_name": repo.get("full_name", ""),
        "description": repo.get("description", ""),
        "url": repo.get("url", ""),
        "stars": repo.get("stars", 0),
        "forks": repo.get("forks", 0),
        "language": repo.get("language", ""),
        "updated_at": repo.get("updated_at")
    }

def format_date(date_string: str) -> str:
    """Tarih formatını düzenler"""
    try:
        if isinstance(date_string, str):
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return date_obj.strftime("%Y-%m-%d")
        return str(date_string)
    except:
        return str(date_string)

def extract_categories(text: str) -> List[str]:
    """Metinden kategorileri çıkarır"""
    if not text:
        return []
    
    # ArXiv kategorilerini ara
    category_pattern = r'\b(cs\.[a-z]{2,3}|math\.[a-z]{2,3}|stat\.[a-z]{2,3}|physics\.[a-z]{2,3}|q-bio\.[a-z]{2,3}|nlin\.[a-z]{2,3}|cond-mat\.[a-z]{2,3}|hep\.[a-z]{2,3}|gr-qc|astro-ph|math-ph)\b'
    categories = re.findall(category_pattern, text, re.IGNORECASE)
    
    return list(set(categories))  # Duplicate'ları kaldır

def validate_arxiv_id(arxiv_id: str) -> bool:
    """ArXiv ID'sinin formatını doğrular"""
    if not arxiv_id:
        return False
    
    # Yeni format: YYMM.NNNN veya YYMM.NNNNN
    new_format = re.match(r'^\d{4}\.\d{4,5}$', arxiv_id)
    # Eski format: YYMM.NNNNN
    old_format = re.match(r'^\d{7}$', arxiv_id)
    
    return bool(new_format or old_format)

def extract_year_from_arxiv_id(arxiv_id: str) -> int:
    """ArXiv ID'sinden yıl çıkarır"""
    try:
        if validate_arxiv_id(arxiv_id):
            year_part = arxiv_id[:4]
            year = int(year_part)
            # 2000'ler ve sonrası için mantıklı değerler
            if year >= 2000 and year <= 2030:
                return year
    except:
        pass
    return datetime.now().year

def sanitize_filename(filename: str) -> str:
    """Dosya adını güvenli hale getirir"""
    # Geçersiz karakterleri kaldır
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Uzunluğu sınırla
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def truncate_text(text: str, max_length: int = 200, add_ellipsis: bool = True) -> str:
    """Metni belirtilen uzunluğa kadar kısaltır"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length].strip()
    if add_ellipsis and len(text) > max_length:
        truncated += "..."
    
    return truncated

def format_number(num: int) -> str:
    """Sayıyı okunabilir formata çevirir"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)

def get_paper_summary(paper: Dict[str, Any]) -> str:
    """Paper için özet oluşturur"""
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    authors = paper.get("authors", [])
    citations = paper.get("citations", 0)
    
    # Özet metni oluştur
    summary = f"{title}. "
    
    if authors:
        author_list = ", ".join(authors[:3])  # İlk 3 yazar
        if len(authors) > 3:
            author_list += f" ve {len(authors)-3} diğer"
        summary += f"Yazarlar: {author_list}. "
    
    if abstract:
        summary += f"Özet: {truncate_text(abstract, 150)}"
    
    return summary