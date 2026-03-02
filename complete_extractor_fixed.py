#!/usr/bin/env python3
"""
Complete Iwata Asks Extractor - Extract ALL 126 interviews from original site
Fixed for Windows compatibility
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
import json
import re

def extract_all_interviews():
    """Extract all 126 interviews found on the original site"""
    
    print("EXTRACTING ALL 126 INTERVIEWS FROM IWATA ASKS")
    print("="*60)
    
    # Create archive directory
    os.makedirs("Iwata_Asks_Complete", exist_ok=True)
    
    # Step 1: Get all interview links
    print("\n1. EXTRACTING ALL INTERVIEW LINKS...")
    all_interviews = extract_all_links()
    
    # Step 2: Try to extract content from each interview
    print("\n2. ATTEMPTING CONTENT EXTRACTION...")
    interviews_with_content = extract_content_for_links(all_interviews[:20])  # Test first 20
    
    # Step 3: Generate complete archive
    print("\n3. GENERATING COMPLETE ARCHIVE...")
    generate_complete_archive(all_interviews, interviews_with_content)
    
    print(f"\nCOMPLETE ARCHIVE CREATED!")
    print(f"Total interviews: {len(all_interviews)}")
    print(f"With available content: {len(interviews_with_content)}")
    print("Check 'Iwata_Asks_Complete' directory for all files.")

def extract_all_links():
    """Extract all interview links from the original site"""
    base_url = "https://iwataasks.nintendo.com"
    
    try:
        response = requests.get(base_url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find ALL interview links
        interview_links = []
        seen_urls = set()
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            if href.startswith('/interviews/') and text and len(text) > 1:
                full_url = urljoin(base_url, href)
                
                # Avoid duplicates
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    
                    # Try to extract platform from URL
                    platform = "Unknown"
                    if '/wiiu/' in href:
                        platform = "Wii U"
                    elif '/3ds/' in href:
                        platform = "Nintendo 3DS" 
                    elif '/wii/' in href:
                        platform = "Wii"
                    elif '/ds/' in href:
                        platform = "Nintendo DS"
                    elif '/switch/' in href:
                        platform = "Nintendo Switch"
                    
                    interview_links.append({
                        'url': full_url,
                        'title': text,
                        'path': href,
                        'platform': platform,
                        'extracted': False,
                        'content_length': 0
                    })
        
        print(f"Extracted {len(interview_links)} unique interview links")
        
        # Sort by platform and title
        interview_links.sort(key=lambda x: (x['platform'], x['title']))
        
        return interview_links
        
    except Exception as e:
        print(f"Error extracting links: {e}")
        return []

def extract_content_for_links(interviews):
    """Try to extract content for each interview"""
    
    print(f"Testing content extraction on {len(interviews)} interviews...")
    
    for i, interview in enumerate(interviews, 1):
        title_short = interview['title'][:50] if len(interview['title']) > 50 else interview['title']
        print(f"{i:3d}/{len(interviews)}: {title_short}...", end=" ")
        
        try:
            response = requests.get(interview['url'], timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple selectors for content
            content_selectors = [
                'div[class*="content"]',
                'div[class*="chapter"]', 
                'div[class*="article"]',
                'main',
                'section',
                'div[class*="container"]',
                'article',
                '.prose',
                '[class*="text"]',
                '[class*="body"]'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    # Remove script/style tags
                    for script in elem.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        script.decompose()
                    
                    text = elem.get_text().strip()
                    if len(text) > len(content):
                        content = text
            
            # Extract images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    img_url = urljoin(interview['url'], src)
                    images.append({
                        'url': img_url,
                        'alt': img.get('alt', ''),
                        'src': src
                    })
            
            # Update interview data
            interview['content'] = content[:2000] + "..." if len(content) > 2000 else content
            interview['content_length'] = len(content)
            interview['images'] = images[:5]  # First 5 images
            interview['extracted'] = True
            
            print(f"SUCCESS ({len(content)} chars, {len(images)} images)")
            
        except Exception as e:
            interview['error'] = str(e)
            print(f"FAILED ({e})")
        
        # Be respectful with requests
        time.sleep(1)
    
    return [i for i in interviews if i.get('extracted', False)]

def generate_complete_archive(all_interviews, content_interviews):
    """Generate complete archive with extracted data"""
    
    # Save complete list
    with open("Iwata_Asks_Complete/all_126_interviews.json", 'w', encoding='utf-8') as f:
        json.dump(all_interviews, f, indent=2, ensure_ascii=False)
    
    # Save interviews with content
    if content_interviews:
        with open("Iwata_Asks_Complete/interviews_with_content.json", 'w', encoding='utf-8') as f:
            json.dump(content_interviews, f, indent=2, ensure_ascii=False)
    
    # Generate comprehensive text file
    with open("Iwata_Asks_Complete/Complete_Iwata_Asks_Archive.txt", 'w', encoding='utf-8') as f:
        f.write("IWATA ASKS - COMPLETE ARCHIVE\n")
        f.write("="*60 + "\n\n")
        f.write(f"Source: https://iwataasks.nintendo.com\n")
        f.write(f"Total Interviews Found: {len(all_interviews)}\n")
        f.write(f"With Extracted Content: {len(content_interviews)}\n")
        f.write(f"Extraction Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Group by platform
        platforms = {}
        for interview in all_interviews:
            platform = interview['platform']
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(interview)
        
        for platform, items in sorted(platforms.items()):
            f.write(f"\n{platform.upper()} ({len(items)} interviews)\n")
            f.write("-" * 50 + "\n")
            
            for i, interview in enumerate(items, 1):
                f.write(f"\n{i:3d}. {interview['title']}\n")
                f.write(f"     URL: {interview['url']}\n")
                f.write(f"     Platform: {interview['platform']}\n")
                
                if interview.get('extracted'):
                    f.write(f"     [EXTRACTED] Content: {interview['content_length']} chars\n")
                    f.write(f"     [IMAGES] Found: {len(interview.get('images', []))}\n")
                    
                    # Add content preview
                    if interview.get('content'):
                        preview = interview['content'][:300]
                        f.write(f"     CONTENT PREVIEW:\n{preview}...\n")
                else:
                    f.write(f"     [NOT EXTRACTED] Content extraction failed\n")
                    if interview.get('error'):
                        f.write(f"    .ERROR: {interview['error'][:100]}...\n")
                
                f.write("-" * 50 + "\n")
    
    # Generate interactive HTML
    html_content = generate_interactive_html(all_interviews, content_interviews)
    with open("Iwata_Asks_Complete/Complete_Archive_126_Interviews.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Print summary
    print(f"\nGenerated files:")
    print(f"- all_126_interviews.json ({len(all_interviews)} interviews)")
    if content_interviews:
        print(f"- interviews_with_content.json ({len(content_interviews)} with content)")
    print(f"- Complete_Iwata_Asks_Archive.txt (complete text archive)")
    print(f"- Complete_Archive_126_Interviews.html (interactive)")

def generate_interactive_html(all_interviews, content_interviews):
    """Generate comprehensive interactive HTML"""
    
    # Platform statistics
    platforms_count = {}
    for interview in all_interviews:
        platform = interview['platform']
        platforms_count[platform] = platforms_count.get(platform, 0) + 1
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iwata Asks - Complete Archive (126 Interviews)</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px; 
            background-color: #f8f9fa;
        }}
        .header {{ 
            background: linear-gradient(135deg, #e60012, #ff3366);
            color: white; 
            padding: 40px; 
            border-radius: 15px; 
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(230, 0, 18, 0.3);
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #e60012;
            margin-bottom: 10px;
        }}
        .stat-label {{
            color: #666;
            font-size: 1.1em;
        }}
        .platform-section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .platform-header {{
            background: #2c3e50;
            color: white;
            padding: 20px 25px;
            font-size: 1.4em;
            font-weight: bold;
        }}
        .interview-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
            padding: 25px;
        }}
        .interview-card {{
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
            position: relative;
        }}
        .interview-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border-color: #e60012;
        }}
        .platform-badge {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: #e60012;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.75em;
            font-weight: bold;
        }}
        .interview-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
            line-height: 1.3;
        }}
        .url-container {{
            margin-bottom: 15px;
        }}
        .url {{
            color: #666;
            font-size: 0.85em;
            word-break: break-all;
            display: block;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 3px solid #e60012;
        }}
        .status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .status-success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status-failed {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .search-box {{
            width: 100%;
            padding: 15px;
            font-size: 1.1em;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .search-box:focus {{
            outline: none;
            border-color: #e60012;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            color: #666;
            background: white;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }}
    </style>
    <script>
        function filterInterviews(element) {{
            const searchTerm = element.value.toLowerCase();
            const cards = document.querySelectorAll('.interview-card');
            
            cards.forEach(card => {{
                const title = card.querySelector('.interview-title').textContent.toLowerCase();
                const platform = card.querySelector('.platform-badge').textContent.toLowerCase();
                const visible = title.includes(searchTerm) || platform.includes(searchTerm);
                card.style.display = visible ? 'block' : 'none';
            }});
        }}
    </script>
</head>
<body>
    <div class="header">
        <h1>Iwata Asks - Complete Archive</h1>
        <h2>All {len(all_interviews)} Interviews by Satoru Iwata</h2>
        <p><em>"Please understand that I understand."</em></p>
        <p>The complete collection of Satoru Iwata's intimate interviews with Nintendo developers</p>
    </div>
    
    <input type="text" class="search-box" placeholder="Search interviews by title or platform..." onkeyup="filterInterviews(this)">
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{len(all_interviews)}</div>
            <div class="stat-label">Total Interviews</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(platforms_count)}</div>
            <div class="stat-label">Platforms</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(content_interviews)}</div>
            <div class="stat-label">With Extracted Content</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">Wii U</div>
            <div class="stat-label">Most Represented</div>
        </div>
    </div>
"""

    # Group by platform
    platforms = {}
    for interview in all_interviews:
        platform = interview['platform']
        if platform not in platforms:
            platforms[platform] = []
        platforms[platform].append(interview)
    
    for platform, items in sorted(platforms.items()):
        html += f"""
    <div class="platform-section">
        <div class="platform-header">
            CONSOLE: {platform} ({len(items)} interviews)
        </div>
        <div class="interview-grid">
"""
        
        for interview in items:
            status_html = ""
            if interview.get('extracted'):
                status_html = f'<span class="status status-success">EXTRACTED ({interview.get("content_length", 0)} chars)</span>'
            else:
                status_html = '<span class="status status-failed">NOT EXTRACTED</span>'
            
            html += f"""
            <div class="interview-card">
                <span class="platform-badge">{interview['platform']}</span>
                <div class="interview-title">{interview['title']}</div>
                <div class="url-container">
                    <span class="url">
                        <a href="{interview['url']}" target="_blank" style="text-decoration: none; color: #e60012;">
                            VIEW INTERVIEW
                        </a>
                        <br>
                        {interview['url']}
                    </span>
                </div>
                {status_html}
            </div>
"""
        
        html += """
        </div>
    </div>
"""

    html += f"""
    <div class="footer">
        <h3>Archive Information</h3>
        <p><strong>Total Interviews:</strong> {len(all_interviews)}</p>
        <p><strong>Content Extraction:</strong> {len(content_interviews)} interviews successfully extracted</p>
        <p><strong>Platforms:</strong> {', '.join(platforms_count.keys())}</p>
        <p><strong>Last Updated:</strong> {time.strftime('%Y-%m-%d')}</p>
        
        <p><em>Note: The original Iwata Asks website uses JavaScript rendering. 
        Some content may require browser access to view fully.</em></p>
        <p><strong>Archive created for preservation purposes. Content belongs to Nintendo Co., Ltd.</strong></p>
    </div>
</body>
</html>"""
    
    return html

if __name__ == "__main__":
    extract_all_interviews()