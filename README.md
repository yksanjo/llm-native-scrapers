# 🤖 LLM-Native Scrapers

> AI-Powered Web Scraping Inspired by ScrapeGraphAI

Transform natural language instructions into structured web data extraction. This project implements the "Research-y Tier" of AI-powered scrapers, featuring LLM-guided extraction that adapts to website changes automatically.

## ✨ Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **SmartScraper** | Natural language → Structured data | ✅ Ready |
| **SearchGraph** | Multi-source search & aggregation | ✅ Ready |
| **ScriptCreator** | Auto-generate scraping code | ✅ Ready |
| **Adaptive Extraction** | Self-healing when sites change | ✅ Ready |
| **SpeechGraph** | Voice-enabled scraping | 🚧 Planned |

## 🚀 Quick Start

### Installation

```bash
# Clone and enter the directory
cd llm-native-scrapers

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set your API key
export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...
```

### Basic Usage

```python
from llm_native_scrapers import smart_scraper

# Extract data using natural language
result = smart_scraper(
    prompt="Extract all product names and prices from this e-commerce page",
    source="https://example-shop.com/products"
)

print(result['data'])
```

### Using the Full API

```python
from llm_native_scrapers import ScrapeGraphAI

# Initialize
sgai = ScrapeGraphAI(api_key="your-key")

# 1. SmartScraper - Single source extraction
scraper = sgai.create_smart_scraper(
    prompt="Get the top story title and URL",
    source="https://news.ycombinator.com"
)
result = scraper.run()

# 2. SearchGraph - Multi-source aggregation
search = sgai.create_search_graph(
    prompt="Find information about AI scraping tools",
    sources=["https://site1.com", "https://site2.com"]
)
results = search.run()

# 3. ScriptCreator - Generate scraping code
creator = sgai.create_script_creator(
    prompt="Create a scraper for GitHub trending repos"
)
script = creator.run()
print(script['generated_code'])
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM-Native Scraper                            │
├─────────────────────────────────────────────────────────────────┤
│  Natural Language → LLM Understanding → Graph Execution          │
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │  Instruction │ → │  LLM Parse  │ → │  Graph Node: Fetch  │   │
│  │  "Get prices"│   │  Understand │   │  Playwright/HTTP    │   │
│  └─────────────┘   └─────────────┘   └─────────────────────┘   │
│                                               ↓                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Graph Node: Parse (BeautifulSoup/lxml)                 │    │
│  │  Clean HTML, remove scripts, structure content          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                               ↓                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Graph Node: LLM Extract                                │    │
│  │  "Given this HTML, extract product prices"              │    │
│  │  → Returns structured JSON                              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                               ↓                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Graph Node: Transform                                  │    │
│  │  Format output (JSON/CSV/Markdown)                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                               ↓                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Result: {"products": [{"name": "...", "price": "..."}]} │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Why LLM-Native Scraping?

### Traditional Scraping
```python
# Brittle - breaks when site changes CSS
price = soup.select_one('.product-card .price .amount').text

# Requires constant maintenance
# Fails on different site structures
# Doesn't understand context
```

### LLM-Native Scraping
```python
# Robust - adapts automatically
result = scraper.scrape(
    "Extract product prices from this electronics store page"
)

# LLM understands "price" concept
# Works across different layouts
# Self-healing when structure changes
```

## 📚 Examples

### Example 1: E-commerce Price Tracking

```python
from llm_native_scrapers import SmartScraperGraph

# Track product prices - works even if site redesigns
scraper = SmartScraperGraph(
    prompt="Extract product name, current price, and original price. "
           "Calculate discount percentage if on sale.",
    source="https://amazon.com/s?k=laptops"
)

result = scraper.run()
# Returns structured data regardless of HTML structure
```

### Example 2: News Aggregation

```python
from llm_native_scrapers import SearchGraph

# Aggregate news from multiple sources
search = SearchGraph(
    prompt="Find latest news about AI regulations in 2024",
    sources=[
        "https://techcrunch.com",
        "https://wired.com",
        "https://theverge.com"
    ]
)

result = search.run()
# LLM synthesizes information from all sources
```

### Example 3: Auto-Generated Scrapers

```python
from llm_native_scrapers import ScriptCreatorGraph

# Generate reusable scraping code
creator = ScriptCreatorGraph(
    prompt="Create a scraper for LinkedIn job postings. "
           "Extract title, company, location, and description. "
           "Handle pagination to get first 50 results."
)

result = creator.run()
# Returns complete Python script with Playwright

# Save and use the generated script
creator.save_script("linkedin_scraper.py")
```

## 🛠️ Configuration

### LLM Providers

```python
from llm_native_scrapers import LLMScraperConfig

# OpenAI (default)
config = LLMScraperConfig(
    llm_provider="openai",
    llm_model="gpt-4",
    openai_api_key="sk-..."
)

# Anthropic Claude
config = LLMScraperConfig(
    llm_provider="anthropic",
    llm_model="claude-3-opus-20240229",
    anthropic_api_key="sk-ant-..."
)

scraper = LLMNativeScraper(config)
```

### Browser Settings

```python
config = LLMScraperConfig(
    headless=False,           # Show browser window
    browser_timeout=60000,    # 60 second timeout
    user_agent="CustomBot/1.0",
    max_pages=5,              # Limit pages per scrape
    delay_between_requests=2  # Be respectful
)
```

## 🧪 Running the Demo

```bash
# Run all demos
python examples/demo_scrapegraphai.py

# Run specific demo
python examples/demo_scrapegraphai.py --demo basic
python examples/demo_scrapegraphai.py --demo search
python examples/demo_scrapegraphai.py --demo script
python examples/demo_scrapegraphai.py --demo adaptive

# With explicit API key
python examples/demo_scrapegraphai.py --demo all --api-key sk-...
```

## 📁 Project Structure

```
llm-native-scrapers/
├── core/
│   ├── __init__.py
│   └── llm_scraper.py          # Core LLM scraper classes
├── adapters/
│   ├── __init__.py
│   └── scrapegraphai_adapter.py # ScrapeGraphAI-style API
├── examples/
│   └── demo_scrapegraphai.py   # Comprehensive demo
├── tests/
│   └── (test files)
├── docs/
│   └── (documentation)
├── requirements.txt
├── .env.example
├── README.md
└── __init__.py
```

## 🔌 Integration with Unified Scraper

This project is designed to integrate with the `unified-scraper` framework:

```python
# Add to unified-scraper/adapters/llm_native.py
from llm_native_scrapers import ScrapeGraphAI

class LLMNativeAdapter(BaseScraper):
    """Adapter for LLM-native scraping in unified framework"""
    
    def scrape(self, target: str, **kwargs) -> Dict:
        sgai = ScrapeGraphAI(api_key=self.config.api_key)
        scraper = sgai.create_smart_scraper(
            prompt=kwargs.get('prompt'),
            source=target
        )
        return scraper.run()
```

## 💰 Business Model (Like ScrapeGraphAI)

This open-source implementation can be paired with a SaaS offering:

| Tier | Price | Features |
|------|-------|----------|
| **Open Source** | Free | Self-hosted, bring your own API keys |
| **Starter** | $19/mo | 1,000 requests/mo, shared infrastructure |
| **Pro** | $49/mo | 10,000 requests/mo, priority speed |
| **Enterprise** | Custom | Unlimited, dedicated instances, SLA |

## 🎯 Use Cases

1. **Price Monitoring** - Track competitor prices without brittle selectors
2. **Content Aggregation** - Build news feeds from multiple sources
3. **Lead Generation** - Extract contact info from business directories
4. **Research** - Gather data for market analysis
5. **Monitoring** - Watch for changes on websites

## 🛡️ Ethical Considerations

- Always respect `robots.txt`
- Implement rate limiting
- Don't overload servers
- Check website Terms of Service
- Consider using official APIs when available

## 🔮 Future Roadmap

- [ ] SpeechGraph - Voice-enabled scraping
- [ ] Vision capabilities - Handle image-based content
- [ ] Auto-pagination detection
- [ ] JavaScript execution planning
- [ ] Multi-step form handling
- [ ] Scheduled/automated scraping
- [ ] Data validation schemas
- [ ] Real-time change detection

## 📖 References

- [ScrapeGraphAI](https://scrapegraphai.com) - The inspiration
- [Playwright](https://playwright.dev) - Browser automation
- [OpenAI API](https://platform.openai.com) - LLM provider
- [Anthropic Claude](https://anthropic.com) - Alternative LLM

## 📄 License

MIT License - See LICENSE file for details.

---

<p align="center">
  Built with 🤖 + 🧠 + 🕷️
</p>
