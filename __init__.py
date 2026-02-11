"""
LLM-Native Scrapers

AI-powered web scraping inspired by ScrapeGraphAI.

Key Features:
- Natural language to structured data extraction
- LLM-guided scraping that adapts to website changes
- Graph-based processing pipelines
- Multi-source search and aggregation
- Automatic script generation

Quick Start:
    from llm_native_scrapers import smart_scraper
    
    result = smart_scraper(
        prompt="Extract all product prices",
        source="https://example-shop.com",
        api_key="your-openai-key"
    )
    
    print(result['data'])
"""

__version__ = "0.1.0"
__author__ = "AI Research Team"

from core import (
    LLMNativeScraper,
    LLMScraperConfig,
    ScrapingInstruction,
    ScrapingResult,
    SmartScraper,
)

from adapters import (
    ScrapeGraphAI,
    SmartScraperGraph,
    SearchGraph,
    ScriptCreatorGraph,
    smart_scraper,
    search_graph,
    script_creator,
)

__all__ = [
    # Core
    'LLMNativeScraper',
    'LLMScraperConfig',
    'ScrapingInstruction',
    'ScrapingResult',
    'SmartScraper',
    
    # Adapters
    'ScrapeGraphAI',
    'SmartScraperGraph',
    'SearchGraph',
    'ScriptCreatorGraph',
    'smart_scraper',
    'search_graph',
    'script_creator',
]
