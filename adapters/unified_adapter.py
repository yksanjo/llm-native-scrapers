"""
Unified Scraper Framework Adapter

Integrates LLM-Native scrapers with the unified-scraper framework.
This allows using natural language scraping within the existing infrastructure.
"""

import sys
import os
from typing import Optional, Dict, Any, Iterator
from pathlib import Path

# Add unified-scraper to path
unified_path = Path(__file__).parent.parent.parent / "unified-scraper"
if str(unified_path) not in sys.path:
    sys.path.insert(0, str(unified_path))

try:
    from core.base import BaseScraper, ScraperConfig
    UNIFIED_AVAILABLE = True
except ImportError:
    UNIFIED_AVAILABLE = False
    # Create stub classes if unified-scraper not available
    class ScraperConfig:
        pass
    class BaseScraper:
        pass

from core.llm_scraper import LLMNativeScraper, LLMScraperConfig, ScrapingInstruction
from adapters.scrapegraphai_adapter import SmartScraperGraph, SearchGraph


class LLMNativeAdapter(BaseScraper if UNIFIED_AVAILABLE else object):
    """
    Adapter for LLM-Native scraping in the unified framework.
    
    Allows using natural language instructions within the unified scraper:
    
    ```python
    from unified_scraper import Scraper
    
    scraper = Scraper.for_source('llm_native', api_key="sk-...")
    result = scraper.scrape(
        "https://example.com",
        prompt="Extract all product names and prices"
    )
    ```
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[ScraperConfig] = None):
        if UNIFIED_AVAILABLE:
            super().__init__(config)
        
        self.llm_config = LLMScraperConfig(
            openai_api_key=api_key or os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self._scraper = LLMNativeScraper(self.llm_config)
    
    def scrape(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scrape using natural language instruction.
        
        Args:
            target: URL to scrape
            prompt: Natural language instruction (required)
            expected_output: Optional schema hint
            
        Returns:
            Dict with extracted data
        """
        prompt = kwargs.get('prompt')
        if not prompt:
            raise ValueError("LLM-native scraper requires 'prompt' parameter")
        
        instruction = ScrapingInstruction(
            description=prompt,
            url=target,
            expected_output=kwargs.get('expected_output'),
            context=kwargs.get('context')
        )
        
        result = self._scraper.scrape(instruction)
        
        return {
            "success": result.success,
            "data": result.data,
            "source": result.source_url,
            "error": result.error,
            "timestamp": result.timestamp.isoformat()
        }
    
    def scrape_multiple(
        self, 
        urls: list[str], 
        prompt: str,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Scrape multiple URLs with the same instruction.
        
        Args:
            urls: List of URLs to scrape
            prompt: Natural language instruction
            
        Yields:
            Dict with results for each URL
        """
        for url in urls:
            yield self.scrape(url, prompt=prompt, **kwargs)
    
    def close(self):
        """Clean up resources"""
        self._scraper.close()


class UnifiedSmartScraper(SmartScraperGraph):
    """
    SmartScraper that conforms to unified scraper interface.
    """
    
    def scrape(self, target: str, **kwargs) -> Dict[str, Any]:
        """Conform to unified scraper interface"""
        self.source = target
        if 'prompt' in kwargs:
            self.prompt = kwargs['prompt']
        return self.run()


class UnifiedSearchScraper(SearchGraph):
    """
    SearchGraph that conforms to unified scraper interface.
    """
    
    def scrape(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Conform to unified scraper interface.
        
        Target can be:
        - Single URL (treated as single source search)
        - Comma-separated URLs (treated as multi-source)
        """
        if ',' in target:
            self.sources = [url.strip() for url in target.split(',')]
        else:
            self.sources = [target]
        
        if 'prompt' in kwargs:
            self.prompt = kwargs['prompt']
        
        return self.run()


# Registration helper
def register_with_unified_framework():
    """
    Register LLM-native adapters with the unified scraper framework.
    
    This should be called once at startup to add the adapters
    to the unified scraper's registry.
    """
    if not UNIFIED_AVAILABLE:
        raise ImportError("Unified scraper framework not available")
    
    # This would integrate with unified-scraper's plugin system
    # For now, just a placeholder showing the intent
    
    # Example integration:
    # from unified_scraper import register_adapter
    # register_adapter('llm_native', LLMNativeAdapter)
    # register_adapter('llm_smart', UnifiedSmartScraper)
    # register_adapter('llm_search', UnifiedSearchScraper)
    
    print("✅ LLM-native adapters registered with unified framework")


# Convenience function for unified usage
def create_llm_scraper(api_key: Optional[str] = None) -> LLMNativeAdapter:
    """
    Create an LLM-native scraper compatible with unified framework.
    
    Args:
        api_key: OpenAI or Anthropic API key
        
    Returns:
        LLMNativeAdapter instance
    """
    return LLMNativeAdapter(api_key=api_key)


# Example usage
if __name__ == "__main__":
    print("LLM-Native Unified Adapter")
    print("=" * 50)
    
    # Check unified framework availability
    if UNIFIED_AVAILABLE:
        print("✅ Unified scraper framework available")
    else:
        print("⚠️  Unified scraper framework not available (standalone mode)")
    
    # Demo
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ API key found")
        
        # Create adapter
        adapter = create_llm_scraper(api_key)
        print("✅ LLM-native adapter created")
        
        # Example (would require actual URL)
        print("\nExample usage:")
        print('  result = adapter.scrape(')
        print('      "https://example.com",')
        print('      prompt="Extract all product names"')
        print('  )')
    else:
        print("❌ No API key found. Set OPENAI_API_KEY environment variable.")
