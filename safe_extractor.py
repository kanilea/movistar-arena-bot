#!/usr/bin/env python3
"""
Safe Unicode Extractor - Extract content from all interviews safely
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import json
from urllib.parse import urljoin
import sys

def safe_print(text, end='\n'):
    """Print text safely on Windows"""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        # Replace problematic characters
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text, end=end)

def extract_all():
    """Extract content from all interviews safely"""
    
    safe_print("SAFE EXTRACTOR - PROCESSING ALL 126 INTERVIEWS")
    safe_print("=" * 55)
    
    # Load interviews
    try:
        with open("Iwata_Asks_Complete/all_126_interviews.json", 'r', encoding='utf-8') as f:
            all_interviews = json.load(f)
    except:
        safe_print("Error: Could not load interviews")
        return
    
    safe_print(f"Loaded {len(all_interviews)} interviews")
    
    extracted = []
    
    for i, interview in enumerate(all_interviews, 1):
        # Safe title display
        title = interview['title'][:30] + "..." if len(interview['title']) > 30 else interview['title']
        try:
            safe_print(f"{i:3d}/126: {title}...", end=" ")
        except:
            safe_print(f"{i:3d}/126: Interview #{i}...", end=" ")
        
        try:
            response = requests.get(interview['url'], timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract content
            content = ""
            
            # Try selectors
            for selector in ['main', 'section', 'div[class*="content"]', 'div[class*="chapter"]']:
                elements = soup.select(selector)
                for elem in elements:
                    for script in elem.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        script.decompose()
                    text = elem.get_text().strip()
                    if len(text) > len(content):
                        content = text
            
            # Fallback to entire page
            if len(content) < 100:
                for unwanted in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    unwanted.decompose()
                
                page_text = soup.get_text().strip()
                lines = [line.strip() for line in page_text.split('\n') if len(line.strip()) > 20]
                content = '\n'.join(lines[:40])
            
            # Images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    if len(src) > 15:
                        img_url = urljoin(interview['url'], src)
                        images.append({'url': img_url, 'alt': img.get('alt', '')})
            
            # Update data
            interview['content'] = content[:1000] if len(content) > 1000 else content
            interview['content_length'] = len(content)
            interview['images'] = images[:3]
            interview['success'] = len(content) > 50
            interview['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            extracted.append(interview)
            
            success = interview['success']
            safe_print(f"{'OK' if success else 'PART'} ({len(content)} chars)")
            
        except Exception as e:
            interview['error'] = str(e)
            interview['success'] = False
            extracted.append(interview)
            safe_print(f"ERR ({str(e)[:30]})")
        
        # Progress save
        if i % 25 == 0:
            save_data(extracted, f"temp_{i}.json")
            safe_print(f"    Saved: {i}/126")
        
        time.sleep(0.8)
    
    # Final save
    save_data(extracted, "FINAL_ALL_126.json")
    
    # Generate report
    generate_report(extracted)
    
    successful = len([x for x in extracted if x.get('success', False)])
    safe_print(f"\nCOMPLETE! Total: {len(extracted)}, Success: {successful}")
    
    return extracted

def save_data(data, filename):
    """Save data with encoding handling"""
    try:
        filepath = f"Iwata_Asks_Complete/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        safe_print(f"Save error: {e}")
        return False

def generate_report(interviews):
    """Generate final report"""
    total = len(interviews)
    successful = len([x for x in interviews if x.get('success', False)])
    
    # Stats by platform
    platforms = {}
    for iv in interviews:
        p = iv.get('platform', 'Unknown')
        if p not in platforms:
            platforms[p] = {'total': 0, 'success': 0}
        platforms[p]['total'] += 1
        if iv.get('success', False):
            platforms[p]['success'] += 1
    
    # Text report
    report_content = f"""IWATA ASKS - FINAL EXTRACTED ARCHIVE
{'='*50}

Total Interviews: {total}
Successfully Extracted: {successful}
Success Rate: {successful/total*100:.1f}%
Extraction Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

PLATFORM BREAKDOWN:
{'-'*30}
"""
    
    for platform, stats in sorted(platforms.items()):
        rate = stats['success']/stats['total']*100 if stats['total'] > 0 else 0
        report_content += f"{platform:15s}: {stats['success']:3d}/{stats['total']:3d} ({rate:.1f}%)\n"
    
    report_content += f"\nDETAILED LIST:\n{'='*30}\n"
    
    for platform, stats in sorted(platforms.items()):
        platform_interviews = [iv for iv in interviews if iv.get('platform') == platform]
        report_content += f"\n{platform.upper()}\n{'-'*40}\n"
        
        for i, iv in enumerate(platform_interviews, 1):
            status = "OK" if iv.get('success', False) else "FAIL"
            title = iv.get('title', 'Unknown')[:60]
            content_len = iv.get('content_length', 0)
            images_count = len(iv.get('images', []))
            
            report_content += f"{i:3d}. [{status}] {title}\n"
            report_content += f"     Content: {content_len} chars | Images: {images_count}\n"
            report_content += f"     URL: {iv['url']}\n\n"
    
    # Save reports
    save_data_content(report_content, "FINAL_EXTRACTED_REPORT.txt")
    
    # HTML report
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Iwata Asks - Final Archive</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
.header {{ background: #e60012; color: white; padding: 30px; text-align: center; border-radius: 10px; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
.stat {{ background: white; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
.stat-num {{ font-size: 2em; font-weight: bold; color: #e60012; }}
.platform {{ background: white; margin: 15px 0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
.platform-header {{ background: #333; color: white; padding: 15px; font-weight: bold; }}
.interview {{ padding: 12px 15px; border-bottom: 1px solid #eee; }}
.interview:last-child {{ border-bottom: none; }}
.ok {{ color: #28a745; }}
.fail {{ color: #dc3545; }}
</style></head><body>
<div class="header">
<h1>Iwata Asks Complete Archive</h1>
<h2>All {total} Interviews Extracted</h2>
</div>

<div class="stats">
<div class="stat"><div class="stat-num">{total}</div><div>Total</div></div>
<div class="stat"><div class="stat-num">{successful}</div><div>Successful</div></div>
<div class="stat"><div class="stat-num">{len(platforms)}</div><div>Platforms</div></div>
<div class="stat"><div class="stat-num">{successful/total*100:.1f}%</div><div>Success Rate</div></div>
</div>
"""
    
    for platform, stats in sorted(platforms.items()):
        platform_interviews = [iv for iv in interviews if iv.get('platform') == platform]
        rate = stats['success']/stats['total']*100 if stats['total'] > 0 else 0
        
        html += f"""
<div class="platform">
<div class="platform-header">{platform} ({stats['success']}/{stats['total']} - {rate:.0f}%)</div>
"""
        for iv in platform_interviews:
            status_cls = "ok" if iv.get('success', False) else "fail"
            status_text = "EXTRACTED" if iv.get('success', False) else "FAILED"
            content_len = iv.get('content_length', 0)
            images_count = len(iv.get('images', []))
            
            html += f"""
<div class="interview">
<span class="{status_cls}">[{status_text}]</span><br>
<strong>{iv.get('title', 'Unknown')}</strong><br>
<small>Content: {content_len} chars | Images: {images_count}</small><br>
<a href="{iv['url']}" target="_blank" style="color: #e60012;">View Interview</a>
</div>
"""
        html += "</div>"
    
    html += f"""
<div style="text-align: center; margin: 30px; padding: 20px; color: #666;">
<h3>Archive Complete</h3>
<p>Total: {total} | Success: {successful} | Success Rate: {successful/total*100:.1f}%</p>
<p>Archive created for preservation. Content belongs to Nintendo Co., Ltd.</p>
<p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
</body></html>"""
    
    save_data_content(html, "FINAL_ARCHIVE_REPORT.html")
    
    safe_print("Generated reports:")
    safe_print("- FINAL_EXTRACTED_REPORT.txt")
    safe_print("- FINAL_ARCHIVE_REPORT.html") 
    safe_print("- FINAL_ALL_126.json")

def save_data_content(content, filename):
    """Save text/HTML content"""
    try:
        filepath = f"Iwata_Asks_Complete/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        safe_print(f"Save error: {e}")
        return False

if __name__ == "__main__":
    extract_all()