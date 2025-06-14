import os
import base64
from pathlib import Path
from model import llm

def get_image_info(image_path: Path) -> dict:
    try:
        content_file = image_path.parent / "content.md"
        png_files = [file for file in os.listdir(image_path.parent) if file.endswith(".png")]

        if not png_files:
            print("No PNG files found in the directory")
        else:
            # Open the content.md file in append mode
            with open(content_file, "a", encoding="utf-8") as md_file:
                md_file.write("\n\n## Image Descriptions\n\n")
                
                for file in png_files:
                    file_path = Path(image_path.parent, file)
                    print(f"Found: {file_path}")
                    
                    if file_path.exists():
                        print(f"Processing: {file_path.name}")
                        
                        try:
                            # Read and encode the image as base64
                            with open(file_path, "rb") as image_file:
                                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                            
                            # Determine the MIME type
                            mime_type = "image/png"
                            
                            # Create the message with base64 data URL
                            message = {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Describe the image in detail."},
                                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}}
                                ]
                            }
                            
                            response = llm.invoke([message])
                            print(f'Response for {file}: {response.content}')
                            
                            # Write to markdown file
                            md_file.write(f"### {file}\n\n")
                            md_file.write(f"{response.content}\n\n")
                            md_file.write("-" * 50 + "\n\n")
                            
                        except Exception as e:
                            print(f"Error processing {file}: {e}")
                            md_file.write(f"### {file}\n\n")
                            md_file.write(f"Error processing image: {e}\n\n")
                            md_file.write("-" * 50 + "\n\n")
                    else:
                        print(f"File not found: {file_path}")

    except FileNotFoundError:
        print(f"Directory not found: {biology_dir}")
    except Exception as e:
        print(f"Error accessing directory: {e}")