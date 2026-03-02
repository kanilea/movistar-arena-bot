#!/usr/bin/env python3
"""
Full Content Extractor - Extract content from ALL 126 interviews
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import json
from urllib.parse import urljoin

def extract_all_content():
    """Extract content from all 126 interviews"""
    
    print("EXTRACTING COMPLETE CONTENT FROM ALL 126 INTERVIEWS")
    print("="*65)
    
    # Load the complete list
    try:
        with open("Iwata_Asks_Complete/all_126_interviews.json", 'r', encoding='utf-8') as f:
            all_interviews = json.load(f)
    except:
        print("Error: Could not load interview list. Run complete_extractor_fixed.py first.")
        return
    
    print(f"Loaded {len(all_interviews)} interviews")
    
    # Extract content for ALL interviews
    extracted_interviews = []
    
    for i, interview in enumerate(all_interviews, 1):
        title_short = interview['title'][:50] if len(interview['title']) > 50 else interview['title']
        print(f"{i:3d}/126: {title_short}...", end=" ")
        
        try:
            # Get the page
            response = requests.get(interview['url'], timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title from page
            page_title = interview['title']
            title_elem = soup.find('title') or soup.find('h1')
            if title_elem:
                page_title = title_elem.get_text().strip()
            
            # Try to extract all text content
            content = ""
            
            # Method 1: Try to find main content areas
            content_selectors = [
                'div[class*="content"]',
                'div[class*="chapter"]', 
                'div[class*="article"]',
                'div[class*="text"]',
                'div[class*="body"]',
                'div[class*="main"]',
                'main',
                'section',
                'article'
            ]
            
            best_content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    # Clean up the element
                    for unwanted in elem.find_all(['script', 'style', 'nav', 'header', 'footer', 'button']):
                        unwanted.decompose()
                    
                    text = elem.get_text().strip()
                    # Look for meaningful content (should have sentences)
                    if len(text) > len(best_content) and '.' in text:
                        best_content = text
            
            # Method 2: If no good content found, try to extract from entire page
            if len(best_content) < 500:
                # Remove unwanted elements from entire page
                for unwanted in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'button', 'input']):
                    unwanted.decompose()
                
                page_text = soup.get_text().strip()
                # Split by lines and look for interview content
                lines = page_text.split('\n')
                content_lines = []
                
                for line in lines:
                    line = line.strip()
                    # Skip very short lines and navigation elements
                    if len(line) > 20 and not any(skip in line.lower() for skip in 
                        ['home', 'nintendo', 'wii', '3ds', 'interviews', 'volumes', 'select', 'menu']):
                        content_lines.append(line)
                
                best_content = '\n'.join(content_lines[:100])  # First 100 meaningful lines
            
            # Clean up the content
            best_content = '\n'.join([line.strip() for line in best_content.split('\n') if line.strip()])
            
            # Extract images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    alt_text = img.get('alt', '')
                    img_url = urljoin(interview['url'], src)
                    if len(img_url) > 20 and not 'icon' in img_url.lower():
                        images.append({
                            'url': img_url,
                            'alt': alt_text,
                            'src': src
                        })
            
            # Update interview with extracted data
            interview['extracted_title'] = page_title
            interview['content'] = best_content[:5000]  # First 5000 chars
            interview['full_content_length'] = len(best_content)
            interview['images'] = images[:10]  # First 10 images
            interview['extraction_successful'] = len(best_content) > 100
            interview['extraction_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            if interview['extraction_successful']:
                extracted_interviews.append(interview)
                print(f"SUCCESS ({len(best_content)} chars, {len(images)} images)")
            else:
                print(f"PARTIAL ({len(best_content)} chars)")
                extracted_interviews.append(interview)  # Still save partial results
            
        except Exception as e:
            interview['error'] = str(e)
            interview['extraction_successful'] = False
            print(f"FAILED ({e})")
            extracted_interviews.append(interview)  # Still save failed attempts
        
        # Save progress every 10 interviews
        if i % 10 == 0:
            save_progress(extracted_interviews, f"progress_{i}_interviews.json")
            print(f"  [Progress saved: {i}/126]")
        
        # Respect rate limits
        time.sleep(1.5)
    
    # Final save
    save_progress(extracted_interviews, "all_126_interviews_with_content.json")
    
    # Generate final reports
    generate_final_reports(extracted_interviews)
    
    print(f"\nEXTRACTION COMPLETE!")
    print(f"Total interviews processed: {len(extracted_interviews)}")
    successful = len([i for i in extracted_interviews if i.get('extraction_successful', False)])
    print(f"Successfully extracted: {successful}")
    print(f"Failed/Partial: {len(extracted_interviews) - successful}")
    
    return extracted_interviews

def save_progress(interviews, filename):
    """Save interview progress to file"""
    filepath = f"Iwata_Asks_Complete/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(interviews, f, indent=2, ensure_ascii=False)
    print(f"Saved to: {filepath}")

def generate_final_reports(interviews):
    """Generate final comprehensive reports"""
    
    # Statistics
    total = len(interviews)
    successful = len([i for i in interviews if i.get('extraction_successful', False)])
    failed = total - successful
    
    # Group by platform
    platforms = {}
    for interview in interviews:
        platform = interview['platform']
        if platform not in platforms:
            platforms[platform] = {'total': 0, 'successful': 0, 'failed': 0}
        platforms[platform]['total'] += 1
        if interview.get('extraction_successful', False):
            platforms[platform]['successful'] += 1
        else:
            platforms[platform]['failed'] += 1
    
    # Generate comprehensive text report
    with open("Iwata_Asks_Complete/FULL_ARCHIVE_REPORT.txt", 'w', encoding='utf-8') as f:
        f.write("IWATA ASKS - COMPLETE ARCHIVE REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total Interviews: {total}\n")
        f.write(f"Successfully Extracted: {successful} ({successful/total*100:.1f}%)\n")
        f.write(f"Failed/Partial: {failed} ({failed/total*100:.1f}%)\n")
        f.write(f"Extraction Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("PLATFORM BREAKDOWN:\n")
        f.write("-" * 40 + "\n")
        for platform, stats in sorted(platforms.items()):
            success_rate = stats['successful'] / stats['total'] * 100
            f.write(f"{platform:20s}: {stats['successful']:3d}/{stats['total']:3d} ({success_rate:.1f}%)\n")
        
        f.write(f"\nDETAILED INTERVIEW LIST:\n")
        f.write("="*60 + "\n\n")
        
        for platform, items in platforms.items():
            f.write(f"\n{platform.upper()}\n")
            f.write("-" * 40 + "\n")
            
            platform_interviews = [i for i in interviews if i['platform'] == platform]
            for i, interview in enumerate(platform_interviews, 1):
                status = "✓" if interview.get('extraction_successful', False) else "✗"
                content_length = interview.get('full_content_length', 0)
                images_count = len(interview.get('images', []))
                
                f.write(f"{i:3d}. {status} {interview['title']}\n")
                f.write(f"     URL: {interview['url']}\n")
                f.write(f"     Content: {content_length} chars\n")
                f.write(f"     Images: {images_count}\n")
                if interview.get('error'):
                    f.write(f"     Error: {interview['error'][:100]}\n")
                f.write("\n")
    
    # Generate HTML summary with content previews
    html_content = generate_html_summary(interviews, platforms, successful)
    with open("Iwata_Asks_Complete/Complete_Archive_With_Content.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
# Export as markdown for documentation
    generate_markdown_archive(interviews, platforms)
    
    print(f"Generated final reports:")
    print("- FULL_ARCHIVE_REPORT.txt (comprehensive text report)")
    print("- Complete_Archive_With_Content.html (interactive with previews)")
    print("- complete_archive.md (markdown documentation)")

def generate_html_summary(interviews, platforms, successful):
    """Generate HTML summary with content previews"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iwata Asks - Complete Archive with Content</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 1600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }}
        .header {{ background: linear-gradient(135deg, #e60012, #ff3366); color: white; padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 3em; font-weight: bold; color: #e60012; margin-bottom: 10px; }}
        .platform-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .platform-card {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .platform-header {{ background: #2c3e50; color: white; padding: 20px; font-size: 1.3em; font-weight: bold; }}
        .platform-stats {{ padding: 20px; display: flex; justify-content: space-between; }}
        .stat-box {{ text-align: center; }}
        .stat-box .number {{ font-size: 1.8em; font-weight: bold; color: #e60012; }}
        .interview-list {{ padding: 0 20px 20px; }}
        .interview-item {{ border: 1px solid #e9ecef; border-radius: 5px; margin: 10px 0; padding: 15px; cursor: pointer; transition: all 0.3s; }}
        .interview-item:hover {{ background: #f8f9fa; border-color: #e60012; }}
        .interview-title {{ font-weight: bold; color: #2c3e50; margin-bottom: 8px; font-size: 1.1em; }}
        .interview-meta {{ color: #666; font-size: 0.9em; margin-bottom: 8px; }}
        .content-preview {{ background: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 0.85em; color: #495057; display: none; margin-top: 10px; }}
        .status-success {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .search-box {{ width: 100%; padding: 15px; font-size: 1.1em; border: 2px solid #e9ecef; border-radius: 8px; margin-bottom: 30px; }}
        .search-box:focus {{ outline: none; border-color: #e60012; }}
        .footer {{ text-align: center; margin-top: 50px; padding: 30px; color: #666; background: white; border-radius: 10px; }}
    </style>
    <script>
        function toggleContent(element) {{
            const preview = element.querySelector('.content-preview');
            if (preview.style.display === 'none' || preview.style.display === '') {{
                preview.style.display = 'block';
            }} else {{
                preview.style.display = 'none';
            }}
        }}
        
        function filterInterviews(element) {{
            const searchTerm = element.value.toLowerCase();
            const interviews = document.querySelectorAll('.interview-item');
            
            interviews.forEach(interview => {{
                const title = interview.querySelector('.interview-title').textContent.toLowerCase();
                const platform = interview.closest('.platform-card').querySelector('.platform-header').textContent.toLowerCase();
                const visible = title.includes(searchTerm) || platform.includes(searchTerm);
                interview.style.display = visible ? 'block' : 'none';
            }});
        }}
    </script>
</head>
<body>
    <div class="header">
        <h1>Iwata Asks - Complete Archive with Content</h1>
        <h2>All {len(interviews)} Interviews with Extracted Content</h2>
        <p><em>"Please understand that I understand."</em></p>
    </div>
    
    <input type="text" class="search-box" placeholder="Search interviews..." onkeyup="filterInterviews(this)">
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{len(interviews)}</div>
            <div>Total Interviews</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{successful}</div>
            <div>Successfully Extracted</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(platforms)}</div>
            <div>Platforms</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{successful/len(interviews)*100:.1f}%</div>
            <div>Success Rate</div>
        </div>
    </div>
    
    <div class="platform-grid">
"""
    
    for platform, stats in sorted(platforms.items()):
        platform_interviews = [i for i in interviews if i['platform'] == platform]
        
        html += f"""
        <div class="platform-card">
            <div class="platform-header">🎮 {platform}</div>
            <div class="platform-stats">
                <div class="stat-box">
                    <div class="number">{stats['total']}</div>
                    <div>Total</div>
                </div>
                <div class="stat-box">
                    <div class="number">{stats['successful']}</div>
                    <div>Success</div>
                </div>
                <div class="stat-box">
                    <div class="number">{stats['successful']/stats['total']*100:.0f}%</div>
                    <div>Rate</div>
                </div>
            </div>
            <div class="interview-list">
"""
        
        for interview in platform_interviews:
            status_class = "status-success" if interview.get('extraction_successful', False) else "status-failed"
            status_text = "✓ Extracted" if interview.get('extraction_successful', False) else "✗ Failed"
            content_length = interview.get('full_content_length', 0)
            images_count = len(interview.get('images', []))
            content_preview = interview.get('content', '')[:500] + '...' if interview.get('content') else 'No content extracted'
            
            html += f"""
                <div class="interview-item" onclick="toggleContent(this)">
                    <div class="interview-title">{interview['title']}</div>
                    <div class="interview-meta">
                        <span class="{status_class}">{status_text}</span> | 
                        {content_length} chars | {images_count} images
                    </div>
                    <div style="font-size: 0.8em; color: #6c757d; margin-top: 5px;">
                        👉 Click to preview content
                    </div>
                    <div class="content-preview">
                        <strong>Content Preview:</strong><br>
                        {content_preview.replace(chr(10), '<br>')}
                    </div>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
    
    html += f"""
    </div>
    
    <div class="footer">
        <h3>Archive Complete</h3>
        <p><strong>Total Interviews:</strong> {len(interviews)} | <strong>Extracted:</strong> {successful} | <strong>Platforms:</strong> {len(platforms)}</p>
        <p><em>Archive created for preservation. Content belongs to Nintendo Co., Ltd.</em></p>
        <p>Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>"""
    
    return html

def generate_markdown_archive(interviews, platforms):
    """Generate Markdown documentation"""
    
    markdown = f"""# Iwata Asks - Complete Archive

## Overview

This comprehensive archive contains **{len(interviews)}** Iwata Asks interviews extracted from the official Nintendo website.

- **Total Interviews:** {len(interviews)}
- **Successfully Extracted:** {len([i for i in interviews if i.get('extraction_successful', False)])}
- **Platforms:** {len(platforms)}
- **Extraction Date:** {time.strftime('%Y-%m-%d')}

## Platform Breakdown

"""
    
    for platform, stats in sorted(platforms.items()):
        success_rate = stats['successful'] / stats['total'] * 100
        markdown += f"### {platform}\n"
        markdown += f"- **Total:** {stats['total']} interviews\n"
        markdown += f"- **Extracted:** {stats['successful']} interviews\n"
        markdown += f"- **Success Rate:** {success_rate:.1f}%\n\n"
    
    markdown += "## Interview List\n\n"
    
    for platform, stats in sorted(platforms.items()):
        markdown += f"### {platform} Interviews\n\n"
        
        platform_interviews = [i for i in interviews if i['platform'] == platform]
        for i, interview in enumerate(platform_interviews, 1):
            status = "✅" if interview.get('extraction_successful', False) else "❌"
            content_length = interview.get('full_content_length', 0)
            
            markdown += f"{i}. {status} **{interview['title']}**\n"
            markdown += f"   - URL: {interview['url']}\n"
            markdown += f"   - Content: {content_length} characters\n\n"
    
    with open("Iwata_Asks_Complete/complete_archive.md", 'w', encoding='utf-8') as f:
        f.write(markdown)

if __name__ == "__main__":
    extract_all_content()