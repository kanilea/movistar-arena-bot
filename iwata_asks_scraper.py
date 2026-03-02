#!/usr/bin/env python3
"""
Iwata Asks Scraper
Download all Iwata Asks interviews from Nintendo's website with images
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin, urlparse
import markdown
from datetime import datetime

class IwataAsksScraper:
    def __init__(self):
        self.base_url = "https://iwataasks.nintendo.com"
        self.output_dir = "iwata_asks_archive"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.interviews = []
        
    def create_directories(self):
        """Create necessary directories for the archive"""
        dirs = [
            self.output_dir,
            f"{self.output_dir}/images",
            f"{self.output_dir}/interviews"
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def get_page(self, url):
        """Get page content with error handling"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Error accessing {url}: {e}")
            return None
    
    def extract_interview_links(self):
        """Extract all interview links from the main page"""
        print("Extracting interview links from main page...")
        
        response = self.get_page(self.base_url)
        if not response:
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # Find all interview links (usually in navigation or content areas)
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and 'interviews' in href or (href.startswith('/') and any(word in link.get_text().lower() for word in ['ask', 'interview', 'wii', '3ds', 'ds'])):
                full_url = urljoin(self.base_url, href)
                if full_url not in links and full_url != self.base_url:
                    links.append(full_url)
        
        print(f"Found {len(links)} potential interview links")
        return links
    
    def extract_interview_content(self, url):
        """Extract content from an individual interview page"""
        print(f"Extracting content from: {url}")
        
        response = self.get_page(url)
        if not response:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = ""
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            title = title_elem.get_text().strip()
        
        # Extract main content
        content = ""
        content_elem = soup.find('div', class_='content') or soup.find('main') or soup.find('div', id='content')
        if content_elem:
            # Remove script and style elements
            for script in content_elem(["script", "style"]):
                script.decompose()
            content = content_elem.get_text().strip()
        
        # Extract images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                img_url = urljoin(url, src)
                img_alt = img.get('alt', '')
                images.append({
                    'url': img_url,
                    'alt': img_alt,
                    'filename': os.path.basename(urlparse(img_url).path)
                })
        
        return {
            'url': url,
            'title': title,
            'content': content,
            'images': images,
            'extracted_date': datetime.now().isoformat()
        }
    
    def download_image(self, img_url, filename):
        """Download an image and save it locally"""
        try:
            response = self.get_page(img_url)
            if response:
                filepath = f"{self.output_dir}/images/{filename}"
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filepath
        except Exception as e:
            print(f"Error downloading image {img_url}: {e}")
        return None
    
    def generate_markdown_document(self):
        """Generate a markdown document with all interviews"""
        md_content = f"""# Iwata Asks - Complete Archive

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Total interviews: {len(self.interviews)}*

---

"""
        
        for i, interview in enumerate(self.interviews, 1):
            md_content += f"""## {i}. {interview['title']}

**Source:** {interview['url']}  
**Extracted:** {interview['extracted_date']}

### Content

{interview['content']}

"""
            
            if interview['images']:
                md_content += "### Images\n\n"
                for img in interview['images']:
                    if self.download_image(img['url'], img['filename']):
                        md_content += f"![{img['alt']}]({img['filename']})\n\n"
            
            md_content += "---\n\n"
        
        # Save markdown document
        md_filename = f"{self.output_dir}/Iwata_Asks_Complete_Archive.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"Markdown document saved: {md_filename}")
        return md_filename
    
    def generate_html_document(self):
        """Generate an HTML document with all interviews"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iwata Asks - Complete Archive</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ border-bottom: 2px solid #e60012; padding-bottom: 20px; margin-bottom: 30px; }}
        .interview {{ margin-bottom: 40px; border-bottom: 1px solid #ccc; padding-bottom: 30px; }}
        .interview h2 {{ color: #e60012; }}
        .interview img {{ max-width: 500px; height: auto; margin: 10px 0; }}
        .content {{ line-height: 1.6; white-space: pre-wrap; }}
        .images {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Iwata Asks - Complete Archive</h1>
        <p><strong>Generated on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total interviews:</strong> {len(self.interviews)}</p>
        <p><strong>Source:</strong> <a href="{self.base_url}">{self.base_url}</a></p>
    </div>
"""
        
        for i, interview in enumerate(self.interviews, 1):
            html_content += f"""
    <div class="interview">
        <h2>{i}. {interview['title']}</h2>
        <p><strong>Source:</strong> <a href="{interview['url']}">{interview['url']}</a></p>
        <p><strong>Extracted:</strong> {interview['extracted_date']}</p>
        
        <div class="content">{interview['content']}</div>
"""
            
            if interview['images']:
                html_content += '<div class="images"><h3>Images</h3>\n'
                for img in interview['images']:
                    if self.download_image(img['url'], img['filename']):
                        html_content += f'<img src="images/{img["filename"]}" alt="{img["alt"]}" title="{img["alt"]}"><br>\n'
                html_content += '</div>\n'
            
            html_content += '</div>\n'
        
        html_content += """
</body>
</html>"""
        
        # Save HTML document
        html_filename = f"{self.output_dir}/Iwata_Asks_Complete_Archive.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML document saved: {html_filename}")
        return html_filename
    
    def save_raw_interviews_json(self):
        """Save all interviews data as JSON"""
        import json
        
        json_filename = f"{self.output_dir}/interviews_data.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.interviews, f, indent=2, ensure_ascii=False)
        
        print(f"Raw data saved: {json_filename}")
        return json_filename
    
    def scrape_all(self):
        """Main scraping method"""
        print("Starting Iwata Asks scraper...")
        print(f"Base URL: {self.base_url}")
        print(f"Output directory: {self.output_dir}")
        
        # Create directories
        self.create_directories()
        
        # Get interview links
        links = self.extract_interview_links()
        if not links:
            print("No interview links found. Please check the website structure.")
            return
        
        print(f"Found {len(links)} interview links. Starting extraction...")
        
        # Extract content from each interview
        for i, link in enumerate(links, 1):
            print(f"Processing interview {i}/{len(links)}: {link}")
            
            interview = self.extract_interview_content(link)
            if interview and interview['content']:
                self.interviews.append(interview)
            
            # Be respectful with requests
            time.sleep(1)
        
        print(f"Successfully extracted {len(self.interviews)} interviews")
        
        # Generate documents
        if self.interviews:
            self.generate_markdown_document()
            self.generate_html_document()
            self.save_raw_interviews_json()
            
            print(f"\nArchive completed successfully!")
            print(f"Check the '{self.output_dir}' folder for all files.")
        else:
            print("No interviews were successfully extracted.")

if __name__ == "__main__":
    scraper = IwataAsksScraper()
    scraper.scrape_all()