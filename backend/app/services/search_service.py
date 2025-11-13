"""
Web search service for fetching latest information
"""
from typing import List, Dict, Any, Optional
from loguru import logger
import os

try:
    from langchain_community.utilities import GoogleSerperAPIWrapper
    SERPER_AVAILABLE = True
except ImportError:
    SERPER_AVAILABLE = False
    logger.warning("Serper not available")

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False
    logger.warning("DuckDuckGo search not available")

from app.config import settings


class SearchService:
    """Service for web search operations"""

    def __init__(self):
        self.serper = None
        if settings.enable_web_search and settings.serper_api_key and SERPER_AVAILABLE:
            try:
                os.environ['SERPER_API_KEY'] = settings.serper_api_key
                self.serper = GoogleSerperAPIWrapper()
                logger.info("✓ Serper search initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Serper: {e}")

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web for information

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        logger.info(f"Searching web for: {query}")

        try:
            # Try Serper first (better quality)
            if self.serper:
                return await self._search_with_serper(query, max_results)

            # Fall back to DuckDuckGo
            if DUCKDUCKGO_AVAILABLE:
                return await self._search_with_duckduckgo(query, max_results)

            logger.warning("No search provider available")
            return []

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def _search_with_serper(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Google Serper"""
        try:
            results = self.serper.results(query)

            search_results = []
            for result in results.get('organic', [])[:max_results]:
                search_results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'source': 'google'
                })

            logger.info(f"✓ Found {len(search_results)} results via Serper")
            return search_results

        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            return []

    async def _search_with_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            search_results = []
            for result in results:
                search_results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'link': result.get('href', ''),
                    'source': 'duckduckgo'
                })

            logger.info(f"✓ Found {len(search_results)} results via DuckDuckGo")
            return search_results

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []

    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into readable text

        Args:
            results: List of search results

        Returns:
            Formatted text
        """
        if not results:
            return "No search results found."

        formatted = "Web Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   Source: {result['link']}\n\n"

        return formatted
