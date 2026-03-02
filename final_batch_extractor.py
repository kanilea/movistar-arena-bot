#!/usr/bin/env python3
"""
Final Batch Extractor - Extract from all 126 interviews (Windows compatible)
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import json
from urllib.parse import urljoin

def extract_all_interviews():
    """Extract content from all 126 interviews"""
    
    print("FINAL BATCH EXTRACTOR - PROCESSING ALL 126 INTERVIEWS")
    print("="*60)
    
    # Load the complete list
    try:
        with open("Iwata_Asks_Complete/all_126_interviews.json", 'r', encoding='utf-8') as f:
            all_interviews = json.load(f)
    except:
        print("Error: Could not load interview list. Run complete_extractor_fixed.py first.")
        return
    
    print(f"Loaded {len(all_interviews)} interviews")
    
    # Process all interviews
    extracted_interviews = []
    
    for i, interview in enumerate(all_interviews, 1):
        title_short = interview['title'][:40] if len(interview['title']) > 40 else interview['title']
        print(f"{i:3d}/126: {title_short}...", end=" ")
        
        try:
            response = requests.get(interview['url'], timeout=12)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract content
            content = ""
            
            # Try various selectors
            selectors = [
                'div[class*="content"]',
                'div[class*="chapter"]',
                'div[class*="article"]',
                'main',
                'section',
                'div[class*="text"]',
                'div[class*="body"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for elem in elements:
                    for unwanted in elem.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        unwanted.decompose()
                    text = elem.get_text().strip()
                    if len(text) > len(content) and '.' in text:
                        content = text
            
            # If still short, try entire page
            if len(content) < 200:
                for unwanted in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    unwanted.decompose()
                
                page_text = soup.get_text().strip()
                lines = [line.strip() for line in page_text.split('\n') 
                        if len(line.strip()) > 25 and not any(skip in line.lower() 
                        for skip in ['home', 'nintendo', 'wii', '3ds', 'interviews', 'menu'])]
                content = '\n'.join(lines[:60])
            
            # Extract images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    if len(src) > 20 and not 'icon' in src.lower():
                        img_url = urljoin(interview['url'], src)
                        images.append({
                            'url': img_url,
                            'alt': img.get('alt', ''),
                            'src': src
                        })
            
            # Update interview data
            interview['content'] = content[:2000] if len(content) > 2000 else content
            interview['full_content_length'] = len(content)
            interview['images'] = images[:5]
            interview['extraction_successful'] = len(content) > 100
            interview['extraction_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            extracted_interviews.append(interview)
            
            if interview['extraction_successful']:
                print(f"SUCCESS ({len(content)} chars)")
            else:
                print(f"PARTIAL ({len(content)} chars)")
            
        except Exception as e:
            interview['error'] = str(e)
            interview['extraction_successful'] = False
            extracted_interviews.append(interview)
            print(f"FAILED ({e[:40]})")
        
        # Save progress every 30 interviews
        if i % 30 == 0:
            save_progress(extracted_interviews, f"progress_{i}.json")
            print(f"    Progress saved: {i}/126")
        
        # Rate limiting
        time.sleep(1)
    
    # Final save
    save_progress(extracted_interviews, "ALL_126_COMPLETE_FINAL.json")
    
    # Generate reports
    generate_reports(extracted_interviews)
    
    print(f"\nEXTRACTION COMPLETE!")
    print(f"Total interviews: {len(extracted_interviews)}")
    successful = len([i for i in extracted_interviews if i.get('extraction_successful', False)])
    print(f"Successful: {successful}")
    print(f"Success rate: {successful/len(extracted_interviews)*100:.1f}%")
    
    return extracted_interviews

def save_progress(interviews, filename):
    """Save progress to file"""
    filepath = f"Iwata_Asks_Complete/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(interviews, f, indent=2, ensure_ascii=False)
    print(f"Saved: {filename}")

def generate_reports(interviews):
    """Generate comprehensive reports"""
    
    successful = len([i for i in interviews if i.get('extraction_successful', False)])
    total = len(interviews)
    
    # Platform statistics
    platforms = {}
    for interview in interviews:
        platform = interview['platform']
        if platform not in platforms:
            platforms[platform] = {'total': 0, 'successful': 0}
        platforms[platform]['total'] += 1
        if interview.get('extraction_successful', False):
            platforms[platform]['successful'] += 1
    
    # Generate comprehensive text report
    with open("Iwata_Asks_Complete/COMPLETE_FINAL_REPORT.txt", 'w', encoding='utf-8') as f:
        f.write("IWATA ASKS - COMPLETE FINAL REPORT\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total Interviews: {total}\n")
        f.write(f"Successfully Extracted: {successful} ({successful/total*100:.1f}%)\n")
        f.write(f"Failed/Partial: {total - successful} ({(total-successful)/total*100:.1f}%)\n")
        f.write(f"Extraction Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("PLATFORM BREAKDOWN:\n")
        f.write("-" * 30 + "\n")
        for platform, stats in sorted(platforms.items()):
            success_rate = stats['successful'] / stats['total'] * 100 if stats['total'] > 0 else 0
            f.write(f"{platform:15s}: {stats['successful']:3d}/{stats['total']:3d} ({success_rate:.1f}%)\n")
        
        f.write(f"\nCOMPLETE INVENTORY:\n")
        f.write("="*50 + "\n")
        
        for platform, stats in sorted(platforms.items()):
            f.write(f"\n{platform.upper()} ({stats['successful']}/{stats['total']} successful)\n")
            f.write("-" * 40 + "\n")
            
            platform_interviews = [i for i in interviews if i['platform'] == platform]
            for i, interview in enumerate(platform_interviews, 1):
                status = "OK" if interview.get('extraction_successful', False) else "FAIL"
                content_len = interview.get('full_content_length', 0)
                images_count = len(interview.get('images', []))
                
                f.write(f"{i:3d}. [{status}] {interview['title']}\n")
                f.write(f"     Content: {content_len:5d} chars | Images: {images_count:2d}\n")
                f.write(f"     URL: {interview['url']}\n")
                if interview.get('error'):
                    f.write(f"     ERROR: {interview['error'][:60]}\n")
                f.write("\n")
    
    # Generate HTML report
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Iwata Asks - Complete Final Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1400px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }}
        .header {{ background: linear-gradient(135deg, #e60012, #ff3366); color: white; padding: 40px; text-align: center; border-radius: 15px; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 25px; text-align: center; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; color: #e60012; margin-bottom: 10px; }}
        .platform-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .platform-card {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .platform-header {{ background: #2c3e50; color: white; padding: 20px; font-weight: bold; font-size: 1.2em; }}
        .interview-list {{ max-height: 600px; overflow-y: auto; }}
        .interview-item {{ padding: 15px; border-bottom: 1px solid #eee; cursor: pointer; transition: background 0.3s; }}
        .interview-item:hover {{ background: #f8f9fa; }}
        .interview-item:last-child {{ border-bottom: none; }}
        .status-success {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .search-box {{ width: 100%; padding: 15px; font-size: 1.1em; border: 2px solid #e9ecef; border-radius: 8px; margin-bottom: 30px; }}
        .search-box:focus {{ outline: none; border-color: #e60012; }}
        .footer {{ text-align: center; margin-top: 50px; padding: 30px; color: #666; background: white; border-radius: 10px; }}
    </style>
    <script>
        function filterInterviews(element) {{
            const searchTerm = element.value.toLowerCase();
            const interviews = document.querySelectorAll('.interview-item');
            
            interviews.forEach(interview => {{
                const text = interview.textContent.toLowerCase();
                const visible = text.includes(searchTerm);
                interview.style.display = visible ? 'block' : 'none';
            }});
        }}
    </script>
</head>
<body>
    <div class="header">
        <h1>Iwata Asks - Complete Archive</h1>
        <h2>All {total} Interviews Extraction Report</h2>
        <p><em>"Please understand that I understand."</em></p>
    </div>
    
    <input type="text" class="search-box" placeholder="Search interviews by title or platform..." onkeyup="filterInterviews(this)">
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{total}</div>
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
            <div class="stat-number">{successful/total*100:.1f}%</div>
            <div>Success Rate</div>
        </div>
    </div>
    
    <div class="platform-grid">
"""
    
    for platform, stats in sorted(platforms.items()):
        success_rate = stats['successful'] / stats['total'] * 100 if stats['total'] > 0 else 0
        platform_interviews = [i for i in interviews if i['platform'] == platform]
        
        html += f"""
        <div class="platform-card">
            <div class="platform-header">GAME CONSOLE: {platform}</div>
            <div style="padding: 15px; background: #f8f9fa; display: flex; justify-content: space-between;">
                <span><strong>Total:</strong> {stats['total']}</span>
                <span><strong>Success:</strong> {stats['successful']}</span>
                <span><strong>Rate:</strong> {success_rate:.0f}%</span>
            </div>
            <div class="interview-list">
"""
        
        for interview in platform_interviews:
            status_cls = "status-success" if interview.get('extraction_successful', False) else "status-failed"
            status_text = "EXTRACTED" if interview.get('extraction_successful', False) else "FAILED"
            content_len = interview.get('full_content_length', 0)
            images_count = len(interview.get('images', []))
            
            html += f"""
                <div class="interview-item">
                    <span class="{status_cls}">[{status_text}]</span>
                    <div style="font-weight: bold; margin: 5px 0; color: #2c3e50;">{interview['title']}</div>
                    <div style="font-size: 0.9em; color: #666;">
                        Content: {content_len} chars | Images: {images_count}
                    </div>
                    <div style="font-size: 0.85em; margin-top: 5px;">
                        <a href="{interview['url']}" target="_blank" style="color: #e60012; text-decoration: none;">
                            VIEW INTERVIEW
                        </a>
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
        <h3>Archive Extraction Complete</h3>
        <p><strong>Total Interviews:</strong> {total}</p>
        <p><strong>Successfully Extracted:</strong> {successful}</p>
        <p><strong>Success Rate:</strong> {successful/total*100:.1f}%</p>
        <p><strong>Platforms:</strong> {len(platforms)}</p>
        <p><em>Archive created for preservation purposes. Content belongs to Nintendo Co., Ltd.</em></p>
        <p>Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>"""
    
    with open("Iwata_Asks_Complete/COMPLETE_FINAL_REPORT.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated comprehensive reports:")
    print(f"- COMPLETE_FINAL_REPORT.txt ({total} interviews)")
    print(f"- COMPLETE_FINAL_REPORT.html (interactive)")
    print(f"- ALL_126_COMPLETE_FINAL.json (raw data)")

if __name__ == "__main__":
    extract_all_interviews()