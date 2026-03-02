#!/usr/bin/env python3
"""
Batch Content Extractor - Extract from all 126 interviews in batches
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import json
from urllib.parse import urljoin

def extract_batch():
    """Extract content in batches of 25 interviews"""
    
    print("BATCH EXTRACTOR - PROCESSING ALL 126 INTERVIEWS")
    print("="*55)
    
    # Load the complete list
    try:
        with open("Iwata_Asks_Complete/all_126_interviews.json", 'r', encoding='utf-8') as f:
            all_interviews = json.load(f)
    except:
        print("Error: Could not load interview list. Run complete_extractor_fixed.py first.")
        return
    
    print(f"Loaded {len(all_interviews)} interviews")
    
    # Process in batches of 25
    batch_size = 25
    all_extracted = []
    
    # Check for existing progress
    processed_count = 0
    progress_files = [f for f in os.listdir("Iwata_Asks_Complete") if f.startswith("batch_") and f.endswith(".json")]
    
    for filename in sorted(progress_files):
        try:
            with open(f"Iwata_Asks_Complete/{filename}", 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
                all_extracted.extend(batch_data)
                processed_count += len(batch_data)
            print(f"Loaded existing progress: {filename} ({len(batch_data)} interviews)")
        except:
            continue
    
    if processed_count > 0:
        print(f"Already processed {processed_count} interviews, continuing from there...")
        interviews_to_process = all_interviews[processed_count:]
    else:
        interviews_to_process = all_interviews
    
    print(f"Remaining to process: {len(interviews_to_process)}")
    
    for batch_start in range(0, len(interviews_to_process), batch_size):
        batch_end = min(batch_start + batch_size, len(interviews_to_process))
        batch_num = processed_count // batch_size + 1
        
        batch = interviews_to_process[batch_start:batch_end]
        print(f"\nPROCESSING BATCH {batch_num}: {len(batch)} interviews (#{processed_count+1}-{processed_count+len(batch)})")
        
        batch_results = []
        
        for i, interview in enumerate(batch, 1):
            global_num = processed_count + i
            title_short = interview['title'][:40] if len(interview['title']) > 40 else interview['title']
            print(f"  {global_num:3d}/126: {title_short}...", end=" ")
            
            try:
                response = requests.get(interview['url'], timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract content using multiple methods
                content = ""
                
                # Method 1: Try specific selectors
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
                        for script in elem.find_all(['script', 'style', 'nav', 'header', 'footer']):
                            script.decompose()
                        text = elem.get_text().strip()
                        if len(text) > len(content) and '.' in text:
                            content = text
                
                # Method 2: If still short, extract from entire page
                if len(content) < 200:
                    for unwanted in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        unwanted.decompose()
                    
                    page_text = soup.get_text().strip()
                    lines = [line.strip() for line in page_text.split('\n') 
                            if len(line.strip()) > 30 and not any(skip in line.lower() 
                            for skip in ['home', 'nintendo', 'wii', '3ds', 'interviews', 'menu'])]
                    content = '\n'.join(lines[:50])
                
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
                interview['content'] = content[:3000]  # First 3000 chars
                interview['full_content_length'] = len(content)
                interview['images'] = images[:8]
                interview['extraction_successful'] = len(content) > 100
                interview['extraction_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                
                batch_results.append(interview)
                
                if interview['extraction_successful']:
                    print(f"✓ ({len(content)} chars)")
                else:
                    print(f"⚠ ({len(content)} chars)")
                
            except Exception as e:
                interview['error'] = str(e)
                interview['extraction_successful'] = False
                batch_results.append(interview)
                print(f"✗ ({e[:30]}...)")
            
            time.sleep(1.2)  # Respect rate limits
        
        # Save batch
        batch_filename = f"batch_{batch_num}_interviews.json"
        with open(f"Iwata_Asks_Complete/{batch_filename}", 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, indent=2, ensure_ascii=False)
        
        all_extracted.extend(batch_results)
        processed_count += len(batch)
        
        print(f"  Batch {batch_num} completed and saved to {batch_filename}")
    
    # Save complete results
    with open("Iwata_Asks_Complete/ALL_126_COMPLETE_EXTRACTION.json", 'w', encoding='utf-8') as f:
        json.dump(all_extracted, f, indent=2, ensure_ascii=False)
    
    # Generate final summary
    generate_final_summary(all_extracted)
    
    print(f"\nALL EXTRACTION COMPLETE!")
    print(f"Total processed: {len(all_extracted)}")
    successful = len([i for i in all_extracted if i.get('extraction_successful', False)])
    print(f"Successful: {successful}")
    print(f"Success rate: {successful/len(all_extracted)*100:.1f}%")
    
    return all_extracted

def generate_final_summary(interviews):
    """Generate comprehensive final summary"""
    
    successful = len([i for i in interviews if i.get('extraction_successful', False)])
    
    # Platform breakdown
    platforms = {}
    for interview in interviews:
        platform = interview['platform']
        if platform not in platforms:
            platforms[platform] = {'total': 0, 'successful': 0}
        platforms[platform]['total'] += 1
        if interview.get('extraction_successful', False):
            platforms[platform]['successful'] += 1
    
    # Text report
    with open("Iwata_Asks_Complete/FINAL_COMPREHENSIVE_REPORT.txt", 'w', encoding='utf-8') as f:
        f.write("IWATA ASKS - FINAL COMPREHENSIVE REPORT\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total Interviews: {len(interviews)}\n")
        f.write(f"Successfully Extracted: {successful} ({successful/len(interviews)*100:.1f}%)\n")
        f.write(f"Extraction Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("PLATFORM BREAKDOWN:\n")
        f.write("-" * 30 + "\n")
        for platform, stats in sorted(platforms.items()):
            success_rate = stats['successful'] / stats['total'] * 100
            f.write(f"{platform:15s}: {stats['successful']:3d}/{stats['total']:3d} ({success_rate:.1f}%)\n")
        
        f.write(f"\nDETAILED INVENTORY:\n")
        f.write("="*50 + "\n")
        
        for platform, stats in sorted(platforms.items()):
            f.write(f"\n{platform.upper()}\n")
            f.write("-" * 40 + "\n")
            
            platform_interviews = [i for i in interviews if i['platform'] == platform]
            for i, interview in enumerate(platform_interviews, 1):
                status = "✓" if interview.get('extraction_successful', False) else "✗"
                content_len = interview.get('full_content_length', 0)
                images_count = len(interview.get('images', []))
                f.write(f"{i:3d}. {status} {interview['title'][:60]}{'...' if len(interview['title']) > 60 else ''}\n")
                f.write(f"     Content: {content_len:5d} chars | Images: {images_count:2d}\n")
                f.write(f"     URL: {interview['url']}\n\n")
    
    # HTML report
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Iwata Asks - Final Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #e60012, #ff3366); color: white; padding: 30px; text-align: center; border-radius: 10px; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .stat {{ background: white; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .stat-num {{ font-size: 2em; font-weight: bold; color: #e60012; }}
        .platform {{ background: white; margin-bottom: 20px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .platform-header {{ background: #2c3e50; color: white; padding: 15px; font-weight: bold; }}
        .interview {{ padding: 12px 15px; border-bottom: 1px solid #eee; }}
        .interview:last-child {{ border-bottom: none; }}
        .status {{ font-weight: bold; }}
        .success {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .search {{ width: 100%; padding: 12px; font-size: 1em; border: 2px solid #ddd; border-radius: 5px; margin-bottom: 20px; }}
    </style>
    <script>
        function filterInterviews(element) {{
            const term = element.value.toLowerCase();
            const interviews = document.querySelectorAll('.interview');
            interviews.forEach(iv => {{
                const text = iv.textContent.toLowerCase();
                iv.style.display = text.includes(term) ? 'block' : 'none';
            }});
        }}
    </script>
</head>
<body>
    <div class="header">
        <h1>Iwata Asks - Complete Archive</h1>
        <h2>All {len(interviews)} Interviews Extraction Report</h2>
    </div>
    
    <input type="text" class="search" placeholder="Search interviews..." onkeyup="filterInterviews(this)">
    
    <div class="stats">
        <div class="stat">
            <div class="stat-num">{len(interviews)}</div>
            <div>Total Interviews</div>
        </div>
        <div class="stat">
            <div class="stat-num">{successful}</div>
            <div>Successfully Extracted</div>
        </div>
        <div class="stat">
            <div class="stat-num">{len(platforms)}</div>
            <div>Platforms</div>
        </div>
        <div class="stat">
            <div class="stat-num">{successful/len(interviews)*100:.1f}%</div>
            <div>Success Rate</div>
        </div>
    </div>
"""
    
    for platform, stats in sorted(platforms.items()):
        platform_interviews = [i for i in interviews if i['platform'] == platform]
        success_rate = stats['successful'] / stats['total'] * 100
        
        html += f"""
    <div class="platform">
        <div class="platform-header">🎮 {platform} ({stats['successful']}/{stats['total']} - {success_rate:.0f}%)</div>
"""
        
        for interview in platform_interviews:
            status_cls = "success" if interview.get('extraction_successful', False) else "failed"
            status_text = "✓" if interview.get('extraction_successful', False) else "✗"
            content_len = interview.get('full_content_length', 0)
            images_count = len(interview.get('images', []))
            
            html += f"""
        <div class="interview">
            <span class="status {status_cls}">{status_text}</span>
            <strong>{interview['title']}</strong><br>
            <small>Content: {content_len} chars | Images: {images_count}</small><br>
            <a href="{interview['url']}" target="_blank" style="color: #e60012;">📖 View Interview</a>
        </div>
"""
        
        html += "    </div>\n"
    
    html += f"""
    <div style="text-align: center; margin-top: 30px; padding: 20px; color: #666;">
        <h3>Archive Complete</h3>
        <p>Total: {len(interviews)} | Extracted: {successful} | Success Rate: {successful/len(interviews)*100:.1f}%</p>
        <p><em>Archive created for preservation purposes. Content belongs to Nintendo Co., Ltd.</em></p>
        <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>"""
    
    with open("Iwata_Asks_Complete/FINAL_ARCHIVE_REPORT.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Final reports generated:")
    print("- FINAL_COMPREHENSIVE_REPORT.txt")
    print("- FINAL_ARCHIVE_REPORT.html")
    print("- ALL_126_COMPLETE_EXTRACTION.json")

if __name__ == "__main__":
    extract_batch()