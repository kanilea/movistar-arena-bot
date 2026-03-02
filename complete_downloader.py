#!/usr/bin/env python3
"""
Complete Iwata Asks Archive Downloader
Download complete content and images for offline viewing
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import json
from urllib.parse import urljoin
import re
import shutil

class SafePrinter:
    def print_safe(self, text, end='\n'):
        try:
            print(text, end=end)
        except UnicodeEncodeError:
            safe_text = text.encode('ascii', 'ignore').decode('ascii')
            print(safe_text, end=end)
    
    def progress_bar(self, current, total, prefix=''):
        percent = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * percent // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        self.print_safe(f'\r{prefix}{current:3d}/{total}: [{percent:5.1f}%] {bar}', end='')

class InterviewDownloader:
    def __init__(self):
        self.printer = SafePrinter()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = 'https://iwataasks.nintendo.com'
        
    def load_interviews(self):
        """Load interview list"""
        try:
            with open("Iwata_Asks_Complete/FINAL_ALL_126.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            self.printer.print_safe("Error: Cannot load FINAL_ALL_126.json")
            return []
    
    def clean_filename(self, text):
        """Create safe filename from text"""
        # Remove invalid characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # Replace problematic chars
        text = re.sub(r'[^\w\s\-À-ž]', '_', text)
        # Limit length
        return text[:60].strip() or "interview"
    
    def extract_full_content(self, url):
        """Extract complete content from interview"""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = "Unknown Interview"
            title_elem = soup.find('h1') or soup.find('title') or soup.find('meta', {'property': 'og:title'})
            if title_elem:
                title = title_elem.get_text().strip()
            
            # Extract main content - try multiple selectors
            content = ""
            content_selectors = [
                'main',
                'article', 
                'section[class*="content"]',
                'div[class*="content"]',
                'div[class*="chapter"]',
                'div[class*="article"]',
                '.post-content',
                '.entry-content'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    # Clean up each element
                    for elem in elements:
                        # Remove unwanted tags but keep structure
                        for unwanted in elem.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                            unwanted.decompose()
                        
                        # Get text preserving paragraphs
                        elem_content = self.extract_structured_text(elem)
                        if len(elem_content) > len(content):
                            content = elem_content
            
            # Fallback to body
            if len(content) < 100:
                body = soup.find('body')
                if body:
                    for tag in body.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        tag.decompose()
                    content = self.extract_structured_text(body)
            
            # Extract images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    img_url = urljoin(url, src)
                    alt = img.get('alt', '')
                    images.append({
                        'url': img_url,
                        'alt': alt[:100],
                        'local_path': None
                    })
            
            return {
                'title': title,
                'content': content,
                'images': images[:10],  # Limit to 10 images
                'success': len(content) > 200
            }
            
        except Exception as e:
            self.printer.print_safe(f"Content extraction error: {str(e)[:50]}")
            return {
                'title': 'Error',
                'content': f'Error loading content: {str(e)}',
                'images': [],
                'success': False
            }
    
    def extract_structured_text(self, element):
        """Extract text preserving some structure"""
        # Convert to text while preserving paragraphs
        text_parts = []
        
        for child in element.children:
            if hasattr(child, 'name'):
                if child.name in ['p', 'div', 'section', 'article']:
                    text_parts.append('\n' + child.get_text().strip() + '\n')
                elif child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    text_parts.append('\n' + child.get_text().strip().upper() + '\n')
                elif child.name in ['br']:
                    text_parts.append('\n')
                elif child.name in ['q', 'blockquote']:
                    text_parts.append('\n"' + child.get_text().strip() + '"\n')
                else:
                    text_parts.append(child.get_text() + ' ')
            else:
                text_parts.append(str(child))
        
        # Clean up
        full_text = ''.join(text_parts)
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        
        # Remove duplicate empty lines
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            if line:
                cleaned_lines.append(line)
                prev_empty = False
            elif not prev_empty:
                cleaned_lines.append('')
                prev_empty = True
        
        return '\n'.join(cleaned_lines)
    
    def download_image(self, img_url, local_path):
        """Download and save image"""
        try:
            response = self.session.get(img_url, timeout=15)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            self.printer.print_safe(f"Image download error: {str(e)[:30]}")
        return False
    
    def create_html_interview(self, interview_data, folder_name):
        """Create complete HTML file for interview"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{interview_data['title']} - Iwata Asks</title>
    <style>
        body {{
            font-family: Georgia, serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #fafafa;
        }}
        .header {{
            background: #e60012;
            color: white;
            padding: 20px;
            text-align: center;
            margin: -20px -20px 30px;
            border-radius: 0;
        }}
        .title {{
            font-size: 2.2em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            opacity: 0.9;
            font-style: italic;
        }}
        .content {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            white-space: pre-wrap;
        }}
        .images {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        .image {{
            margin: 15px 0;
            text-align: center;
        }}
        .image img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .image-caption {{
            margin-top: 5px;
            font-size: 0.9em;
            color: #666;
            font-style: italic;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">{interview_data['title']}</div>
        <div class="subtitle">Iwata Asks Interview Series</div>
    </div>
    
    <div class="content">{interview_data['content']}</div>
"""
        
        # Add images if any
        if interview_data['images']:
            html_content += '<div class="images"><h3>Images</h3>'
            for i, img in enumerate(interview_data['images']):
                if img['local_path']:
                    html_content += f"""
    <div class="image">
        <img src="{img['local_path']}" alt="{img['alt']}">
        <div class="image-caption">{img['alt'] or 'Interview Image'}<br><small>Original: {img['url']}</small></div>
    </div>
"""
            html_content += '</div>'
        
        html_content += f"""
    <div class="footer">
        <p><strong>Iwata Asks</strong> - Interview Archive</p>
        <p>Original URL: <a href="{interview_data['url']}" target="_blank">{interview_data['url']}</a></p>
        <p>Downloaded: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><em>Content belongs to Nintendo Co., Ltd. This archive is for preservation purposes.</em></p>
    </div>
</body>
</html>
"""
        
        # Save HTML file
        html_path = os.path.join(folder_name, 'interview.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def create_markdown_interview(self, interview_data, folder_name):
        """Create markdown file for interview"""
        md_content = f"""# {interview_data['title']}

**Iwata Asks Interview Series**

---

{interview_data['content']}

---

## Images

"""
        
        for img in interview_data['images']:
            if img['local_path']:
                md_content += f"![{img['alt']}]({img['local_path']})\n\n"
        
        md_content += f"""
---

## Interview Info

- **Title:** {interview_data['title']}
- **URL:** {interview_data['url']}
- **Downloaded:** {time.strftime('%Y-%m-%d %H:%M:%S')}

---

*Iwata Asks © Nintendo Co., Ltd. Archive created for preservation purposes.*
"""
        
        # Save markdown file
        md_path = os.path.join(folder_name, 'interview.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return md_path
    
    def download_all_interviews(self):
        """Download complete content for all interviews"""
        interviews = self.load_interviews()
        if not interviews:
            return
        
        total = len(interviews)
        success_count = 0
        
        self.printer.print_safe(f"DOWNLOADING COMPLETE IWATA ASKS ARCHIVE")
        self.printer.print_safe("=" * 50)
        self.printer.print_safe(f"Total interviews: {total}")
        self.printer.print_safe("Creating offline archive...\n")
        
        # Create main directory
        main_dir = "Iwata_Asks_Offline_Archive"
        if os.path.exists(main_dir):
            shutil.rmtree(main_dir)
        os.makedirs(main_dir)
        
        # Download each interview
        for i, interview in enumerate(interviews, 1):
            self.printer.progress_bar(i, total, f"Downloading: ")
            
            try:
                # Extract content
                content_data = self.extract_full_content(interview['url'])
                content_data['url'] = interview['url']
                content_data['platform'] = interview.get('platform', 'Unknown')
                
                if not content_data['success']:
                    self.printer.print_safe(f"\n{i:3d}/{total}: ERROR - {interview['title'][:30]}...")
                    continue
                
                # Create folder
                safe_title = self.clean_filename(content_data['title'])
                folder_name = os.path.join(main_dir, f"{i:03d}_{safe_title}")
                os.makedirs(folder_name, exist_ok=True)
                
                # Download images
                downloaded_images = 0
                for j, img in enumerate(content_data['images']):
                    if img['url']:
                        # Create image filename
                        ext = '.jpg'  # Default extension
                        if '.png' in img['url'].lower():
                            ext = '.png'
                        elif '.gif' in img['url'].lower():
                            ext = '.gif'
                        
                        img_path = os.path.join(folder_name, f"image_{j+1}{ext}")
                        
                        if self.download_image(img['url'], img_path):
                            content_data['images'][j]['local_path'] = f"image_{j+1}{ext}"
                            downloaded_images += 1
                
                # Create files
                html_path = self.create_html_interview(content_data, folder_name)
                md_path = self.create_markdown_interview(content_data, folder_name)
                
                # Save JSON data
                json_path = os.path.join(folder_name, 'data.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(content_data, f, indent=2, ensure_ascii=False)
                
                success_count += 1
                
                if i % 10 == 0:
                    self.printer.print_safe(f"\n{i:3d}/{total}: {success_count} successful")
                
            except Exception as e:
                self.printer.print_safe(f"\n{i:3d}/{total}: ERROR - {str(e)[:50]}")
            
            time.sleep(1)  # Respect server
        
        self.printer.print_safe(f"\n\nDOWNLOAD COMPLETE!")
        self.printer.print_safe(f"Successful: {success_count}/{total}")
        
        # Create index
        self.create_index_html(main_dir, interviews[:success_count])
        self.printer.print_safe(f"Archive created in: {main_dir}/")
        
        return success_count
    
    def create_index_html(self, archive_dir, interviews):
        """Create index page for archive"""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iwata Asks - Complete Archive</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .header { background: #e60012; color: white; padding: 30px; text-align: center; border-radius: 5px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat { background: white; padding: 15px; text-align: center; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .stat-num { font-size: 1.5em; font-weight: bold; color: #e60012; }
        .interview-list { display: grid; gap: 10px; }
        .platform-group { background: white; border-radius: 5px; overflow: hidden; margin: 10px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .platform-header { background: #333; color: white; padding: 10px; font-weight: bold; }
        .interview { padding: 10px; border-bottom: 1px solid #eee; display: flex; align-items: center; }
        .interview:last-child { border-bottom: none; }
        .interview a { color: #e60012; text-decoration: none; font-weight: bold; }
        .interview a:hover { text-decoration: underline; }
        .meta { font-size: 0.8em; color: #666; margin-left: 10px; }
        .views { display: flex; gap: 10px; margin-left: auto; }
        .view-btn { padding: 3px 8px; background: #f0f0f0; border-radius: 3px; text-decoration: none; color: #333; font-size: 0.8em; }
        .view-btn:hover { background: #e0e0e0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Iwata Asks Complete Archive</h1>
        <p>All Interviews Available Offline</p>
    </div>
    
    <div class="stats">
"""
        
        # Count by platform
        platforms = {}
        for iv in interviews:
            p = iv.get('platform', 'Unknown')
            if iv.get('success', False):
                platforms[p] = platforms.get(p, 0) + 1
        
        html += f"""
        <div class="stat"><div class="stat-num">{len(interviews)}</div><div>Total</div></div>
        <div class="stat"><div class="stat-num">{len(platforms)}</div><div>Platforms</div></div>
        <div class="stat"><div class="stat-num">100%</div><div>Offline</div></div>
        <div class="stat"><div class="stat-num">HTML+MD</div><div>Formats</div></div>
    </div>
"""
        
        # Group by platform
        platform_groups = {}
        for i, iv in enumerate(interviews, 1):
            p = iv.get('platform', 'Unknown')
            if iv.get('success', False):
                if p not in platform_groups:
                    platform_groups[p] = []
                
                safe_title = self.clean_filename(iv.get('title', 'Unknown'))
                folder_name = f"{i:03d}_{safe_title}"
                platform_groups[p].append({
                    'folder': folder_name,
                    'title': iv.get('title', 'Unknown'),
                    'url': iv['url']
                })
        
        # Display interviews by platform
        for platform, items in sorted(platform_groups.items()):
            html += f"""
    <div class="platform-group">
        <div class="platform-header">{platform} ({len(items)} interviews)</div>
        <div class="interview-list">
"""
            for item in items:
                html += f"""
            <div class="interview">
                <a href="{item['folder']}/interview.html">{item['title']}</a>
                <div class="views">
                    <a href="{item['folder']}/interview.html" class="view-btn">HTML</a>
                    <a href="{item['folder']}/interview.md" class="view-btn">Markdown</a>
                </div>
            </div>
"""
            html += """
        </div>
    </div>
"""
        
        html += f"""
    <div style="text-align: center; margin: 30px; padding: 20px; background: #f9f9f9; border-radius: 5px;">
        <h3>Archive Complete</h3>
        <p>All {len(interviews)} interviews downloaded for offline viewing</p>
        <p>Each interview includes HTML and Markdown formats</p>
        <p>Created: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><em>Content belongs to Nintendo Co., Ltd. Archive preserved for historical purposes.</em></p>
    </div>
</body>
</html>
"""
        
        with open(os.path.join(archive_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)

if __name__ == "__main__":
    downloader = InterviewDownloader()
    downloader.download_all_interviews()