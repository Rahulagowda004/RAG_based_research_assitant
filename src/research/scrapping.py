import asyncio
from typing import List # This can be removed if not used elsewhere
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
# requests and xml.etree.ElementTree are no longer needed for this version
# import requests
# from xml.etree import ElementTree
import re, os # Moved imports to the top

async def crawl_single_url(url: str): # Renamed and changed parameter
    print(f"\n=== Crawling Single URL: {url} ===")

    browser_config = BrowserConfig(
        headless=True,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = "session1" # You can keep or remove session_id if only one URL
        result = await crawler.arun(
            url=url,
            config=crawl_config,
            session_id=session_id
        )
        if result.success:
            print(f"Successfully crawled: {url}")
            safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', url.replace('https://', '').replace('http://', ''))
            output_dir = "scraped_markdown"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"{safe_filename}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.markdown.raw_markdown)
            print(f"Saved markdown to {file_path}")
        else:
            print(f"Failed: {url} - Error: {result.error_message}")
    finally:
        await crawler.close()

# Removed get_pydantic_ai_docs_urls function

async def main():
    # Define the single URL you want to crawl
    target_url = "https://en.wikipedia.org/wiki/Attention_Is_All_You_Need" # Replace with your desired URL
    if target_url:
        print(f"Attempting to crawl: {target_url}")
        await crawl_single_url(target_url) # Call the modified function
    else:
        print("No URL provided to crawl")

if __name__ == "__main__":
    asyncio.run(main())