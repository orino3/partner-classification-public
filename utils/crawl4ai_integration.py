from crawl4ai import AsyncWebCrawler
import asyncio
from urllib.parse import urlparse, urljoin
import logging
from typing import Set, Optional, Dict, List
import re
from dataclasses import dataclass
from heapq import heappush, heappop

logger = logging.getLogger(__name__)

@dataclass
class PageScore:
    url: str
    score: float
    depth: int

    def __lt__(self, other):
        return (-self.score, self.depth) < (-other.score, other.depth)

def score_url(url: str) -> float:
    """Score URL relevance for business partner evaluation"""
    url_lower = url.lower()
    
    # High priority pages
    if any(x in url_lower for x in [
        'about', 'company', 'team', 'partner', 'client', 
        'service', 'product', 'solution', 'integration',
        'enterprise', 'business', 'pricing', 'plan',
        'technology', 'platform', 'developer', 'api',
        'security', 'compliance', 'legal', 'privacy',
        'contact', 'support'
    ]):
        return 1.0
        
    # Medium priority pages    
    if any(x in url_lower for x in [
        'feature', 'resource', 'blog', 'news',
        'case-study', 'success-story', 'testimonial',
        'documentation', 'guide', 'help'
    ]):
        return 0.6
        
    # Low priority pages
    if any(x in url_lower for x in [
        'career', 'job', 'press', 'media',
        'event', 'webinar', 'download'
    ]):
        return 0.3
    
    return 0.1  # Default score

async def scrape_content(url: str, timeout: int = 30, max_pages: int = 5) -> Optional[str]:
    """
    Scrape website content using Crawl4AI.
    Returns cleaned content in Markdown format.
    
    Args:
        url: Website URL to scrape
        timeout: Timeout in seconds (default 30)
        max_pages: Maximum number of pages to scrape (default 5)
    """
    # Ensure URL has scheme
    if not urlparse(url).scheme:
        url = "https://" + url
    
    base_domain = urlparse(url).netloc
    visited_urls: Set[str] = set()
    all_content: List[str] = []
    page_queue: List[PageScore] = []  # Priority queue
    
    # Start with homepage
    heappush(page_queue, PageScore(url=url, score=1.0, depth=0))

    while page_queue and len(visited_urls) < max_pages:
        current_page = heappop(page_queue)
        current_url = current_page.url
        
        if current_url in visited_urls:
            continue
            
        visited_urls.add(current_url)
        logger.info(f"Scraping page {len(visited_urls)}/{max_pages} (score: {current_page.score:.2f}): {current_url}")

        try:
            async with AsyncWebCrawler() as crawler:
                task = asyncio.create_task(crawler.arun(url=current_url))
                try:
                    result = await asyncio.wait_for(task, timeout=timeout)
                    if result:
                        if result.markdown:
                            # Add page title/url as context
                            page_content = f"# {current_url}\n\n{result.markdown}"
                            all_content.append(page_content)
                        
                        # Extract and score new URLs
                        if result.links:
                            for link in result.links:
                                # Normalize URL
                                full_url = urljoin(current_url, link)
                                # Only queue internal links
                                if urlparse(full_url).netloc == base_domain and full_url not in visited_urls:
                                    score = score_url(full_url)
                                    heappush(page_queue, PageScore(
                                        url=full_url,
                                        score=score,
                                        depth=current_page.depth + 1
                                    ))
                                    
                except asyncio.TimeoutError:
                    logger.error(f"Timeout scraping {current_url} after {timeout} seconds")
                    
        except Exception as e:
            logger.error(f"Error scraping {current_url}: {str(e)}")

    if all_content:
        return "\n\n---\n\n".join(all_content)
    return None 