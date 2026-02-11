#!/usr/bin/env python3
"""
ScrapeGraphAI-Style Demo

This demo showcases the LLM-Native Scraping capabilities inspired by ScrapeGraphAI:

1. SmartScraper: Natural language to structured data
2. SearchGraph: Multi-source aggregation
3. ScriptCreator: Auto-generate scraping code
4. Adaptive extraction that handles website changes

Usage:
    export OPENAI_API_KEY=sk-...
    python demo_scrapegraphai.py

Or:
    python demo_scrapegraphai.py --demo basic
    python demo_scrapegraphai.py --demo search
    python demo_scrapegraphai.py --demo script
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.scrapegraphai_adapter import (
    ScrapeGraphAI,
    SmartScraperGraph,
    SearchGraph,
    ScriptCreatorGraph,
    smart_scraper,
    search_graph,
    script_creator
)


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_result(result: Dict[str, Any], title: str = "Result"):
    """Pretty print a result"""
    print(f"\n📦 {title}:")
    print("-" * 50)
    print(json.dumps(result, indent=2, default=str))
    print()


def demo_basic_extraction():
    """
    Demo 1: Basic SmartScraper - Extract data with natural language
    
    This is the core ScrapeGraphAI feature:
    - Describe what you want in plain English
    - LLM figures out how to extract it
    - Returns structured data
    """
    print_header("Demo 1: SmartScraper - Natural Language Extraction")
    
    print("📝 Instruction: Extract the main headline and summary from Hacker News")
    print("🔗 Source: https://news.ycombinator.com")
    print()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY=sk-...")
        return
    
    try:
        # Method 1: Using the convenience function
        result = smart_scraper(
            prompt="Extract the top story title, URL, and number of points. "
                   "Also get the submission time and author.",
            source="https://news.ycombinator.com",
            api_key=api_key
        )
        
        print_result(result, "SmartScraper Result")
        
        if result.get("success"):
            print("✅ Success! The LLM extracted:")
            data = result.get("data", {})
            for key, value in data.items():
                print(f"   • {key}: {value}")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def demo_search_aggregation():
    """
    Demo 2: SearchGraph - Multi-source aggregation
    
    Search across multiple sources and let the LLM:
    - Extract relevant information from each
    - Rank and deduplicate results
    - Synthesize a coherent answer
    """
    print_header("Demo 2: SearchGraph - Multi-Source Aggregation")
    
    print("📝 Query: Find information about AI web scraping tools")
    print("🔗 Sources: Multiple documentation sites")
    print()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Example sources - in production, these would be real URLs
    sources = [
        "https://scrapegraphai.com",  # ScrapeGraphAI website
        "https://www.crummy.com/software/BeautifulSoup/bs4/doc/",
        "https://playwright.dev/python/docs/intro",
    ]
    
    print(f"📚 Will search across {len(sources)} sources")
    print("   (Note: Using example URLs - replace with real ones)")
    print()
    
    try:
        # Using the SearchGraph
        graph = SearchGraph(
            prompt="What are the key features of AI-powered web scraping tools? "
                   "Extract features, pricing, and use cases.",
            sources=sources[:1],  # Start with one for demo
            config={"llm": {"openai_api_key": api_key}}
        )
        
        result = graph.run()
        print_result(result, "SearchGraph Result")
        
    except Exception as e:
        print(f"❌ Exception: {e}")


def demo_script_generation():
    """
    Demo 3: ScriptCreator - Auto-generate scraping code
    
    Describe what you want to scrape in natural language,
    and the LLM generates complete Python code for you.
    """
    print_header("Demo 3: ScriptCreator - Auto-Generate Scraping Code")
    
    print("📝 Request: Create a scraper for GitHub trending repositories")
    print()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return
    
    try:
        # Using ScriptCreator
        graph = ScriptCreatorGraph(
            prompt="Create a scraper for GitHub trending repositories page. "
                   "Extract repository name, description, language, stars, and forks. "
                   "Handle pagination to get top 25 repositories.",
            config={"llm": {"openai_api_key": api_key}}
        )
        
        result = graph.run()
        print_result(result, "Generated Script Info")
        
        if result.get("success"):
            print("🐍 Generated Python Code:")
            print("=" * 70)
            print(result["generated_code"])
            print("=" * 70)
            print()
            
            # Option to save
            save = input("💾 Save script to file? (y/n): ").lower().strip()
            if save == 'y':
                filepath = input("Enter filepath (default: generated_scraper.py): ").strip()
                if not filepath:
                    filepath = "generated_scraper.py"
                
                graph.save_script(filepath)
                print(f"✅ Script saved to {filepath}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")


def demo_adaptive_extraction():
    """
    Demo 4: Adaptive Extraction - Handle website changes
    
    Shows how the scraper adapts when:
    - CSS selectors change
    - Page structure is modified
    - Different website layouts
    """
    print_header("Demo 4: Adaptive Extraction - Handle Website Changes")
    
    print("📝 This demo shows how the LLM-based scraper adapts to changes")
    print()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Example: Scraping product info from different e-commerce sites
    # The same natural language instruction works on different sites
    
    test_sites = [
        ("https://news.ycombinator.com", "Extract the top story title and points"),
        ("https://example.com", "Extract the page title and main heading"),
    ]
    
    sga = ScrapeGraphAI(api_key=api_key)
    
    for url, instruction in test_sites:
        print(f"\n🔗 URL: {url}")
        print(f"📝 Instruction: {instruction}")
        print("-" * 50)
        
        try:
            scraper = sga.create_smart_scraper(instruction, url)
            result = scraper.run()
            
            if result.get("success"):
                print(f"✅ Extracted: {result.get('data')}")
            else:
                print(f"⚠️  Note: {result.get('error', 'Could not extract')}")
                
        except Exception as e:
            print(f"⚠️  Error (expected for demo): {e}")


def demo_comparison():
    """
    Demo 5: Compare traditional vs LLM-native scraping
    
    Shows the difference between:
    - Traditional: Brittle CSS selectors
    - LLM-Native: Understands context and adapts
    """
    print_header("Demo 5: Traditional vs LLM-Native Scraping")
    
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    Traditional Scraping                             │
├─────────────────────────────────────────────────────────────────────┤
│  # Brittle - breaks when site changes                               │
│  price = soup.select_one('.product-price .amount').text             │
│                                                                     │
│  # Requires maintenance when CSS classes change                     │
│  # Doesn't understand context                                       │
│  # Fails on different site structures                               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    LLM-Native Scraping                              │
├─────────────────────────────────────────────────────────────────────┤
│  # Robust - adapts to changes                                       │
│  scraper.scrape("Extract the product price from amazon.com")        │
│                                                                     │
│  # LLM understands "price" concept                                  │
│  # Works across different sites                                     │
│  # Self-healing when structure changes                              │
└─────────────────────────────────────────────────────────────────────┘
    """)
    
    print("\n💡 Key Advantages of LLM-Native Scraping:")
    print("   1. Natural language instructions")
    print("   2. Adapts to website changes automatically")
    print("   3. Understands semantic meaning (not just HTML structure)")
    print("   4. Can handle complex extraction logic")
    print("   5. Self-documenting and maintainable")


def main():
    parser = argparse.ArgumentParser(
        description="ScrapeGraphAI-style LLM-Native Scraping Demo"
    )
    parser.add_argument(
        "--demo",
        choices=["basic", "search", "script", "adaptive", "compare", "all"],
        default="all",
        help="Which demo to run"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║           🤖 LLM-Native Scraping Demo                             ║
    ║           Inspired by ScrapeGraphAI                               ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  This demo showcases AI-powered web scraping that:               ║
    ║                                                                  ║
    ║  ✓ Understands natural language instructions                     ║
    ║  ✓ Adapts to website changes automatically                       ║
    ║  ✓ Uses LLMs for intelligent data extraction                     ║
    ║  ✓ Generates scraping code from descriptions                     ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Run selected demos
    demos = {
        "basic": demo_basic_extraction,
        "search": demo_search_aggregation,
        "script": demo_script_generation,
        "adaptive": demo_adaptive_extraction,
        "compare": demo_comparison,
    }
    
    if args.demo == "all":
        for name, demo_func in demos.items():
            try:
                demo_func()
            except KeyboardInterrupt:
                print("\n\n⛔ Demo interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Demo '{name}' failed: {e}")
                continue
            
            if name != list(demos.keys())[-1]:
                input("\n⏎ Press Enter to continue to next demo...")
    else:
        demos[args.demo]()
    
    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("""
📚 Next Steps:
   1. Explore the code in llm-native-scrapers/
   2. Try with your own URLs and instructions
   3. Integrate with the unified-scraper framework
   4. Build custom graphs for your use case

🔗 Resources:
   - ScrapeGraphAI: https://scrapegraphai.com
   - Playwright: https://playwright.dev
   - OpenAI API: https://platform.openai.com
    """)


if __name__ == "__main__":
    main()
