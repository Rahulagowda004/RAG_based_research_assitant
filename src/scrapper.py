from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import base64
from datetime import datetime
import requests

load_dotenv()

def scrape_url(url, output_dir=None):
    app = FirecrawlApp(api_key=os.getenv('firecrawl_api_key'))

    result = app.scrape_url(
        'https://transformer-circuits.pub/2025/attribution-graphs/biology.html',
        formats=['markdown', 'screenshot', 'links']
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"artifacts/scraped_data_{timestamp}"
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