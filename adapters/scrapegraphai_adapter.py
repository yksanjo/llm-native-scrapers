"""
ScrapeGraphAI-style Adapter

This adapter provides a ScrapeGraphAI-like interface for the unified scraper framework.
It implements:
- SmartScraper: Natural language to data extraction
- SearchGraph: Multi-source search and aggregation
- SpeechGraph: Voice-enabled scraping (stub)
- ScriptCreator: Automatic scraper generation
"""

import json
import logging
from typing import Optional, Dict, Any, List, Union, Iterator
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from core.llm_scraper import (
    LLMNativeScraper, 
    LLMScraperConfig, 
    ScrapingInstruction,
    ScrapingResult,
    LLMClient
)

try:
    from playwright.sync_api import Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from a search operation"""
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float = 0.0


class SmartScraperGraph:
    """
    SmartScraper - The core ScrapeGraphAI feature
    
    Converts natural language instructions into structured data extraction.
    Uses a graph-based pipeline: Fetch → Parse → LLM Extract → Validate
    """
    
    def __init__(self, prompt: str, source: str, config: Optional[Dict] = None):
        """
        Args:
            prompt: Natural language instruction (e.g., "Extract all product prices")
            source: URL or search query
            config: Optional configuration dict
        """
        self.prompt = prompt
        self.source = source
        self.config = config or {}
        self.scraper_config = LLMScraperConfig(**self.config.get('llm', {}))
        self._scraper = LLMNativeScraper(self.scraper_config)
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the scraping graph and return results.
        
        Returns:
            Dict with extracted data
        """
        instruction = ScrapingInstruction(
            description=self.prompt,
            url=self.source
        )
        
        result = self._scraper.scrape(instruction)
        
        if result.success:
            return {
                "success": True,
                "data": result.data,
                "source": result.source_url,
                "timestamp": result.timestamp.isoformat()
            }
        else:
            return {
                "success": False,
                "error": result.error,
                "source": self.source
            }
    
    def close(self):
        """Clean up resources"""
        self._scraper.close()


class SearchGraph:
    """
    SearchGraph - Multi-source search and aggregation
    
    Performs searches across multiple sources and aggregates results
    using LLM to rank and deduplicate.
    """
    
    def __init__(
        self, 
        prompt: str,
        sources: Optional[List[str]] = None,
        config: Optional[Dict] = None
    ):
        """
        Args:
            prompt: Search query in natural language
            sources: List of source URLs to search (if None, uses web search)
            config: Optional configuration
        """
        self.prompt = prompt
        self.sources = sources or []
        self.config = config or {}
        self.scraper_config = LLMScraperConfig(**self.config.get('llm', {}))
        self._llm = LLMClient(self.scraper_config)
    
    def run(self) -> Dict[str, Any]:
        """
        Execute search across sources and aggregate results.
        
        Returns:
            Dict with aggregated search results
        """
        all_results = []
        
        # If no sources provided, simulate web search
        if not self.sources:
            logger.info("No sources provided, would use web search API")
            # In production, integrate with SerpAPI, Bing API, etc.
            return {
                "success": False,
                "error": "Web search not implemented. Please provide source URLs."
            }
        
        # Scrape each source
        scraper = LLMNativeScraper(self.scraper_config)
        
        for source in self.sources:
            try:
                instruction = ScrapingInstruction(
                    description=f"Search for: {self.prompt}. Extract relevant information.",
                    url=source
                )
                
                result = scraper.scrape(instruction)
                
                if result.success:
                    all_results.append({
                        "source": source,
                        "data": result.data
                    })
                    
            except Exception as e:
                logger.error(f"Failed to scrape {source}: {e}")
        
        scraper.close()
        
        # Use LLM to aggregate and rank results
        if all_results:
            aggregated = self._aggregate_results(all_results)
            return {
                "success": True,
                "query": self.prompt,
                "results_count": len(all_results),
                "aggregated_data": aggregated
            }
        else:
            return {
                "success": False,
                "query": self.prompt,
                "error": "No results found"
            }
    
    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """Use LLM to aggregate and synthesize results from multiple sources"""
        prompt = f"""Query: {self.prompt}

Results from {len(results)} sources:
{json.dumps(results, indent=2)}

Synthesize these results into a coherent answer. 
Identify consensus information and note any contradictions.
Return as JSON with:
- summary: Brief synthesis
- key_findings: List of main points
- sources_consensus: What sources agree on
- contradictions: Any conflicting information"""

        response = self._llm.generate(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"summary": response, "raw_results": results}


class ScriptCreatorGraph:
    """
    ScriptCreator - Automatically generates scraping scripts
    
    Takes a natural language description and generates executable
    Python code for scraping.
    """
    
    SCRIPT_SYSTEM_PROMPT = """You are an expert Python web scraping developer.
Generate clean, robust scraping code based on the user's requirements.

Guidelines:
- Use Playwright for JavaScript-heavy sites
- Include proper error handling
- Add rate limiting and respectful delays
- Include comments explaining the logic
- Make the code modular and reusable
- Follow PEP 8 style guidelines

Output only the Python code, no explanations."""

    def __init__(self, prompt: str, config: Optional[Dict] = None):
        """
        Args:
            prompt: Description of what the scraper should do
            config: Optional configuration
        """
        self.prompt = prompt
        self.config = config or {}
        self.scraper_config = LLMScraperConfig(**self.config.get('llm', {}))
        self._llm = LLMClient(self.scraper_config)
    
    def run(self) -> Dict[str, Any]:
        """
        Generate a scraping script based on the prompt.
        
        Returns:
            Dict with generated code and metadata
        """
        code_prompt = f"""Create a Python web scraper that does the following:
{self.prompt}

Requirements:
1. Use Playwright for browser automation
2. Include type hints
3. Add docstrings
4. Handle errors gracefully
5. Return data as structured JSON
6. Include a main() function with example usage

Generate the complete Python script:"""

        generated_code = self._llm.generate(code_prompt, self.SCRIPT_SYSTEM_PROMPT)
        
        # Clean up the response (remove markdown code blocks if present)
        if '```python' in generated_code:
            generated_code = generated_code.split('```python')[1].split('```')[0].strip()
        elif '```' in generated_code:
            generated_code = generated_code.split('```')[1].split('```')[0].strip()
        
        return {
            "success": True,
            "prompt": self.prompt,
            "generated_code": generated_code,
            "language": "python",
            "dependencies": ["playwright", "beautifulsoup4", "lxml"]
        }
    
    def save_script(self, filepath: str) -> bool:
        """Save the generated script to a file"""
        result = self.run()
        
        if result["success"]:
            with open(filepath, 'w') as f:
                f.write(result["generated_code"])
            logger.info(f"Script saved to {filepath}")
            return True
        return False


class SpeechGraph:
    """
    SpeechGraph - Voice-enabled scraping (stub)
    
    This is a placeholder for voice-enabled scraping functionality.
    In a full implementation, this would:
    - Accept voice commands
    - Convert speech to text
    - Execute scraping based on voice instructions
    - Provide voice feedback
    """
    
    def __init__(self, prompt: str, source: str, config: Optional[Dict] = None):
        self.prompt = prompt
        self.source = source
        self.config = config or {}
    
    def run(self) -> Dict[str, Any]:
        """Stub implementation"""
        return {
            "success": False,
            "error": "SpeechGraph not implemented. Requires speech recognition libraries.",
            "note": "Install speech_recognition and pyttsx3 for voice functionality"
        }


class ScrapeGraphAI:
    """
    Main interface mimicking the ScrapeGraphAI library.
    
    Provides a unified API for all graph types:
    - SmartScraperGraph: Single-source extraction
    - SearchGraph: Multi-source search
    - ScriptCreatorGraph: Code generation
    - SpeechGraph: Voice interface
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize ScrapeGraphAI interface.
        
        Args:
            api_key: OpenAI or Anthropic API key
            model: LLM model to use
        """
        self.config = {
            "llm": {
                "llm_provider": "openai",
                "llm_model": model,
                "openai_api_key": api_key
            }
        }
    
    def create_smart_scraper(self, prompt: str, source: str) -> SmartScraperGraph:
        """Create a SmartScraperGraph instance"""
        return SmartScraperGraph(prompt, source, self.config)
    
    def create_search_graph(
        self, 
        prompt: str, 
        sources: Optional[List[str]] = None
    ) -> SearchGraph:
        """Create a SearchGraph instance"""
        return SearchGraph(prompt, sources, self.config)
    
    def create_script_creator(self, prompt: str) -> ScriptCreatorGraph:
        """Create a ScriptCreatorGraph instance"""
        return ScriptCreatorGraph(prompt, self.config)
    
    def create_speech_graph(self, prompt: str, source: str) -> SpeechGraph:
        """Create a SpeechGraph instance"""
        return SpeechGraph(prompt, source, self.config)


# Convenience functions (similar to ScrapeGraphAI API)
def smart_scraper(prompt: str, source: str, api_key: Optional[str] = None) -> Dict:
    """
    Quick function to run a SmartScraperGraph.
    
    Args:
        prompt: Natural language instruction
        source: URL to scrape
        api_key: LLM API key (or set OPENAI_API_KEY env var)
    
    Returns:
        Dict with extraction results
    """
    config = {"llm": {"openai_api_key": api_key}}
    graph = SmartScraperGraph(prompt, source, config)
    try:
        return graph.run()
    finally:
        graph.close()


def search_graph(
    prompt: str, 
    sources: List[str],
    api_key: Optional[str] = None
) -> Dict:
    """
    Quick function to run a SearchGraph.
    
    Args:
        prompt: Search query
        sources: List of URLs to search
        api_key: LLM API key
    
    Returns:
        Dict with aggregated search results
    """
    config = {"llm": {"openai_api_key": api_key}}
    graph = SearchGraph(prompt, sources, config)
    return graph.run()


def script_creator(prompt: str, api_key: Optional[str] = None) -> Dict:
    """
    Quick function to generate a scraping script.
    
    Args:
        prompt: Description of what to scrape
        api_key: LLM API key
    
    Returns:
        Dict with generated code
    """
    config = {"llm": {"openai_api_key": api_key}}
    graph = ScriptCreatorGraph(prompt, config)
    return graph.run()
