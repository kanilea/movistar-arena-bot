#!/usr/bin/env python3
"""
Demo Iwata Asks Scraper - Extract first 5 interviews only
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
import json

def extract_demo_interviews():
    base_url = "https://iwataasks.nintendo.com"
    
    print("DEMO: Extracting first 5 Iwata Asks interviews...")
    
    try:
        # Get main page
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find interview links
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            if href.startswith('/interviews/') and text:
                full_url = urljoin(base_url, href)
                if full_url not in [i['url'] for i in links]:
                    links.append({
                        'url': full_url,
                        'title': text
                    })
        
        # Take only first 5
        demo_links = links[:5]
        print(f"Found {len(links)} total interviews, extracting first 5 for demo...")
        
        # Extract content
        interviews = []
        
        for i, link in enumerate(demo_links, 1):
            print(f"{i}. Extracting: {link['title'][:50]}...")
            
            try:
                resp = requests.get(link['url'], timeout=10)
                s = BeautifulSoup(resp.text, 'html.parser')
                
                # Get title
                title = link['title']
                title_elem = s.find('h1')
                if title_elem:
                    title = title_elem.get_text().strip()
                
                # Get content
                content = ""
                content_div = s.find('div', class_='content')
                if content_div:
                    for script in content_div.find_all(['script', 'style']):
                        script.decompose()
                    content = content_div.get_text().strip()[:1000] + "..."  # First 1000 chars
                
                # Get images
                images = []
                for img in s.find_all('img')[:3]:  # First 3 images only
                    src = img.get('src')
                    if src:
                        img_url = urljoin(link['url'], src)
                        images.append({
                            'url': img_url,
                            'alt': img.get('alt', '')
                        })
                
                interviews.append({
                    'title': title,
                    'url': link['url'],
                    'content': content,
                    'images': images
                })
                
            except Exception as e:
                print(f"   Error extracting {link['title']}: {e}")
            
            time.sleep(1)
        
        # Save demo results
        if interviews:
            os.makedirs("demo_output", exist_ok=True)
            
            # Save as text
            with open("demo_output/Iwata_Asks_Demo.txt", 'w', encoding='utf-8') as f:
                f.write("IWATA ASKS DEMO - First 5 Interviews\n")
                f.write("="*50 + "\n\n")
                
                for i, interview in enumerate(interviews, 1):
                    f.write(f"{i}. {interview['title']}\n")
                    f.write(f"URL: {interview['url']}\n")
                    f.write(f"Content:\n{interview['content']}\n")
                    f.write(f"Images: {len(interview['images'])}\n")
                    f.write("-"*50 + "\n\n")
            
            # Save as JSON
            with open("demo_output/Iwata_Asks_Demo.json", 'w', encoding='utf-8') as f:
                json.dump(interviews, f, indent=2, ensure_ascii=False)
            
            print(f"\nDEMO COMPLETE!")
            print(f"Extracted {len(interviews)} interviews")
            print(f"Files saved in 'demo_output/' directory")
            
            # Show sample
            print(f"\nSAMPLE:")
            print(f"Interview 1: {interviews[0]['title']}")
            print(f"Content preview: {interviews[0]['content'][:200]}...")
            print(f"Images found: {len(interviews[0]['images'])}")
            
        else:
            print("No interviews extracted successfully")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_demo_interviews()