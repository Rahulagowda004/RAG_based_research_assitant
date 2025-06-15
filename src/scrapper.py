from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import base64
from datetime import datetime
import requests
from pathlib import Path
from urllib.parse import urlparse

load_dotenv()

def extract_page_identifier(url: str) -> str:
    """
    Extract the page identifier from transformer-circuits.pub URLs.
    
    Args:
        url: URL like 'https://transformer-circuits.pub/2025/attribution-graphs/biology.html'
    
    Returns:
        str: The page identifier (e.g., 'biology')
    """
    try:
        # Parse the URL to get the path
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Extract filename from path
        filename = Path(path).name
        
        # Remove .html extension if present
        if filename.endswith('.html'):
            filename = filename[:-5]
        
        return filename
    
    except Exception as e:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return timestamp

def scrape_url(url, output_dir=r"R:\TAZMIC\artifacts\research_papers"):
    app = FirecrawlApp(api_key=os.getenv('firecrawl_api_key'))

    result = app.scrape_url(
        'https://transformer-circuits.pub/2025/attribution-graphs/biology.html',
        formats=['markdown', 'screenshot', 'links']
    )

    page_identifier = extract_page_identifier(url)
    
    output_dir = f"{output_dir}/{page_identifier}"
    
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/content.md", 'w', encoding='utf-8') as f:
        f.write(result.markdown)

    if hasattr(result, 'screenshot') and result.screenshot:
        try:
            screenshot_data = result.screenshot
            
            if screenshot_data.startswith('http'):
                print(f"Downloading screenshot from: {screenshot_data}")
                response = requests.get(screenshot_data)
                response.raise_for_status()
                
                with open(f"{output_dir}/screenshot.png", 'wb') as f:
                    f.write(response.content)
                print("Screenshot downloaded and saved successfully")
                
            elif screenshot_data.startswith('data:image'):
                screenshot_data = screenshot_data.split(',')[1]
                
                def fix_base64_padding(data):
                    missing_padding = len(data) % 4
                    if missing_padding:
                        data += '=' * (4 - missing_padding)
                    return data
                
                screenshot_data = fix_base64_padding(screenshot_data)
                
                with open(f"{output_dir}/screenshot.png", 'wb') as f:
                    f.write(base64.b64decode(screenshot_data))
                print("Screenshot decoded and saved successfully")
            else:
                print(f"Unknown screenshot format: {screenshot_data[:50]}...")
                
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            with open(f"{output_dir}/screenshot_debug.txt", 'w') as f:
                f.write(f"Screenshot data length: {len(result.screenshot)}\n")
                f.write(f"First 100 chars: {result.screenshot[:100]}\n")
                f.write(f"Raw data: {result.screenshot}")
    else:
        print("No screenshot data available")

    print(f"Data saved to directory: {output_dir}")
    print(f"Content size: {len(result.markdown)} characters")
    print(f"Links found: {len(result.links) if hasattr(result, 'links') and result.links else 0}")
    print(f"Screenshot: {'Available' if hasattr(result, 'screenshot') and result.screenshot else 'Not available'}")
    
    return output_dir, page_identifier
