"""
LLM-Native Scraper Core

AI-powered scraper that uses LLMs to understand natural language instructions
and automatically generate scraping logic - inspired by ScrapeGraphAI.
"""

import json
import logging
from abc import abstractmethod
from typing import Optional, Dict, Any, List, Type, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Try to import LLM libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class LLMScraperConfig:
    """Configuration for LLM-powered scraper"""
    # LLM Settings
    llm_provider: str = "openai"  # openai, anthropic
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4000
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Browser Settings
    headless: bool = True
    browser_timeout: int = 30000
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.0.36"
    
    # Scraping Behavior
    max_pages: int = 10
    respect_robots_txt: bool = True
    delay_between_requests: float = 1.0
    
    # Output
    output_format: str = "json"  # json, csv, markdown
    
    def __post_init__(self):
        if self.llm_provider == "openai" and not self.openai_api_key:
            import os
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        elif self.llm_provider == "anthropic" and not self.anthropic_api_key:
            import os
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")


@dataclass
class ScrapingInstruction:
    """Natural language instruction for scraping"""
    description: str  # "Get all product prices from this e-commerce page"
    url: str
    expected_output: Optional[Dict[str, Any]] = None  # Schema hint
    context: Optional[str] = None  # Additional context


@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    success: bool
    data: Any
    source_url: str
    instruction: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class LLMClient:
    """Unified interface for different LLM providers"""
    
    def __init__(self, config: LLMScraperConfig):
        self.config = config
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate LLM client"""
        if self.config.llm_provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
            self.client = openai.OpenAI(api_key=self.config.openai_api_key)
        elif self.config.llm_provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
            self.client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)
        else:
            raise ValueError(f"Unknown LLM provider: {self.config.llm_provider}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using the configured LLM"""
        if self.config.llm_provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=self.config.llm_temperature,
                max_tokens=self.config.llm_max_tokens
            )
            return response.choices[0].message.content
        
        elif self.config.llm_provider == "anthropic":
            response = self.client.messages.create(
                model=self.config.llm_model,
                max_tokens=self.config.llm_max_tokens,
                temperature=self.config.llm_temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text


class GraphNode:
    """Node in the scraping graph"""
    def __init__(self, name: str, node_type: str, config: Dict[str, Any] = None):
        self.name = name
        self.node_type = node_type  # fetch, parse, extract, transform
        self.config = config or {}
        self.next_nodes: List['GraphNode'] = []
        self.prev_nodes: List['GraphNode'] = []
    
    def connect_to(self, node: 'GraphNode'):
        """Connect this node to another node"""
        self.next_nodes.append(node)
        node.prev_nodes.append(self)


class ScrapingGraph:
    """
    Graph-based scraping pipeline
    
    Inspired by ScrapeGraphAI's graph logic - represents scraping
    as a directed graph of operations.
    """
    
    def __init__(self, name: str = "scraping_graph"):
        self.name = name
        self.nodes: Dict[str, GraphNode] = {}
        self.entry_node: Optional[GraphNode] = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the default scraping graph"""
        # Create nodes
        fetch_node = GraphNode("fetch", "fetch")
        parse_node = GraphNode("parse", "parse")
        extract_node = GraphNode("extract", "extract")
        transform_node = GraphNode("transform", "transform")
        
        # Connect nodes
        fetch_node.connect_to(parse_node)
        parse_node.connect_to(extract_node)
        extract_node.connect_to(transform_node)
        
        # Store nodes
        self.nodes = {
            "fetch": fetch_node,
            "parse": parse_node,
            "extract": extract_node,
            "transform": transform_node
        }
        self.entry_node = fetch_node
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the graph with given context"""
        current = self.entry_node
        state = context.copy()
        
        while current:
            logger.info(f"Executing node: {current.name}")
            
            if current.node_type == "fetch":
                state = self._execute_fetch(state)
            elif current.node_type == "parse":
                state = self._execute_parse(state)
            elif current.node_type == "extract":
                state = self._execute_extract(state)
            elif current.node_type == "transform":
                state = self._execute_transform(state)
            
            # Move to next node
            current = current.next_nodes[0] if current.next_nodes else None
        
        return state
    
    def _execute_fetch(self, state: Dict) -> Dict:
        """Fetch the webpage"""
        # Implemented by subclass
        return state
    
    def _execute_parse(self, state: Dict) -> Dict:
        """Parse the HTML"""
        # Implemented by subclass
        return state
    
    def _execute_extract(self, state: Dict) -> Dict:
        """Extract data using LLM guidance"""
        # Implemented by subclass
        return state
    
    def _execute_transform(self, state: Dict) -> Dict:
        """Transform extracted data to desired format"""
        # Implemented by subclass
        return state


class LLMNativeScraper:
    """
    AI-powered scraper that understands natural language instructions.
    
    Key features (inspired by ScrapeGraphAI):
    - Natural language to scraping logic
    - LLM-guided data extraction
    - Graph-based processing pipeline
    - Automatic adaptation to website changes
    """
    
    SYSTEM_PROMPT = """You are an expert web scraping AI. Your task is to:
1. Analyze the provided HTML content
2. Extract specific data based on the user's natural language instruction
3. Return ONLY valid JSON with the extracted data

Rules:
- Be precise and extract exactly what was asked
- Handle missing data gracefully (use null)
- Return structured JSON that matches the expected output schema if provided
- If pagination is needed, identify the next page link
- Adapt to different website structures automatically"""

    def __init__(self, config: Optional[LLMScraperConfig] = None):
        self.config = config or LLMScraperConfig()
        self.llm = LLMClient(self.config)
        self.graph = ScrapingGraph()
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
    
    def _init_browser(self):
        """Initialize Playwright browser"""
        if self._browser is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=self.config.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self._page = self._browser.new_page(
                user_agent=self.config.user_agent
            )
            self._page.set_default_timeout(self.config.browser_timeout)
    
    def scrape(self, instruction: Union[str, ScrapingInstruction]) -> ScrapingResult:
        """
        Main scraping method - accepts natural language instructions.
        
        Args:
            instruction: Natural language description of what to scrape
                        e.g., "Get all product prices from amazon.com"
        
        Returns:
            ScrapingResult with extracted data
        """
        if isinstance(instruction, str):
            # Parse simple string instruction
            instruction = self._parse_instruction(instruction)
        
        try:
            self._init_browser()
            
            # Execute the scraping graph
            context = {
                "instruction": instruction,
                "url": instruction.url,
                "page": self._page
            }
            
            result = self._execute_scraping(context)
            
            return ScrapingResult(
                success=True,
                data=result.get("data"),
                source_url=instruction.url,
                instruction=instruction.description,
                metadata=result.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return ScrapingResult(
                success=False,
                data=None,
                source_url=instruction.url if isinstance(instruction, ScrapingInstruction) else "",
                instruction=instruction.description if isinstance(instruction, ScrapingInstruction) else str(instruction),
                error=str(e)
            )
    
    def _parse_instruction(self, instruction_str: str) -> ScrapingInstruction:
        """Parse a natural language instruction string"""
        # Simple parsing - extract URL and description
        # In production, could use LLM to parse more complex instructions
        
        words = instruction_str.split()
        url = None
        description = instruction_str
        
        for word in words:
            if word.startswith("http"):
                url = word
                description = instruction_str.replace(word, "").strip()
                break
        
        if not url:
            raise ValueError("No URL found in instruction. Please include a URL starting with http")
        
        return ScrapingInstruction(
            description=description,
            url=url
        )
    
    def _execute_scraping(self, context: Dict) -> Dict:
        """Execute the full scraping pipeline"""
        # Step 1: Fetch
        logger.info(f"Fetching: {context['url']}")
        self._page.goto(context['url'], wait_until="networkidle")
        html_content = self._page.content()
        
        # Step 2: Parse
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Clean up HTML for LLM (remove scripts, styles)
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        
        # Truncate if too long
        cleaned_html = str(soup)[:15000]  # Limit context window
        
        # Step 3: Extract using LLM
        instruction = context['instruction']
        prompt = self._build_extraction_prompt(
            instruction.description,
            cleaned_html,
            instruction.expected_output
        )
        
        logger.info("Extracting data using LLM...")
        llm_response = self.llm.generate(prompt, self.SYSTEM_PROMPT)
        
        # Parse LLM response
        try:
            extracted_data = json.loads(llm_response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', llm_response, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group(1))
            else:
                extracted_data = {"raw_response": llm_response}
        
        # Step 4: Transform
        return {
            "data": extracted_data,
            "metadata": {
                "url": context['url'],
                "instruction": instruction.description,
                "html_length": len(html_content)
            }
        }
    
    def _build_extraction_prompt(
        self, 
        description: str, 
        html_content: str,
        expected_schema: Optional[Dict] = None
    ) -> str:
        """Build the LLM prompt for data extraction"""
        prompt = f"""Instruction: {description}

HTML Content:
```html
{html_content}
```

"""
        if expected_schema:
            prompt += f"""Expected output format:
```json
{json.dumps(expected_schema, indent=2)}
```

"""
        
        prompt += """Extract the requested data and return ONLY valid JSON.
If data is missing or not found, use null values.
Do not include any explanation, only the JSON response."""
        
        return prompt
    
    def close(self):
        """Clean up resources"""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class SmartScraper(LLMNativeScraper):
    """
    Smart scraper that adapts to website changes automatically.
    
    This is the flagship feature - it uses LLM reasoning to:
    1. Understand the website structure
    2. Identify the right selectors even when they change
    3. Adapt extraction logic based on context
    """
    
    def scrape_with_adaptation(
        self, 
        instruction: ScrapingInstruction,
        previous_selectors: Optional[Dict] = None
    ) -> ScrapingResult:
        """
        Scrape with automatic adaptation.
        
        If previous_selectors are provided and fail, the scraper
        will use LLM reasoning to find alternative selectors.
        """
        # Try with previous selectors first (fast path)
        if previous_selectors:
            try:
                result = self._scrape_with_selectors(instruction, previous_selectors)
                if result.success:
                    return result
            except Exception as e:
                logger.warning(f"Previous selectors failed: {e}. Adapting...")
        
        # Fall back to LLM-based extraction (adaptive path)
        return self.scrape(instruction)
    
    def _scrape_with_selectors(
        self, 
        instruction: ScrapingInstruction,
        selectors: Dict[str, str]
    ) -> ScrapingResult:
        """Scrape using predefined CSS/XPath selectors"""
        self._init_browser()
        self._page.goto(instruction.url, wait_until="networkidle")
        
        data = {}
        for key, selector in selectors.items():
            element = self._page.query_selector(selector)
            if element:
                data[key] = element.inner_text()
        
        return ScrapingResult(
            success=True,
            data=data,
            source_url=instruction.url,
            instruction=instruction.description
        )
