"""
LLM-Native Scrapers - Adapters Module

ScrapeGraphAI-style adapters for unified scraping framework.
"""

from .scrapegraphai_adapter import (
    ScrapeGraphAI,
    SmartScraperGraph,
    SearchGraph,
    ScriptCreatorGraph,
    SpeechGraph,
    SearchResult,
    smart_scraper,
    search_graph,
    script_creator,
)

__all__ = [
    'ScrapeGraphAI',
    'SmartScraperGraph',
    'SearchGraph',
    'ScriptCreatorGraph',
    'SpeechGraph',
    'SearchResult',
    'smart_scraper',
    'search_graph',
    'script_creator',
]
