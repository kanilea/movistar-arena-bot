#!/usr/bin/env python3
"""
Improved Iwata Asks Scraper - Better content extraction
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
import json

def extract_one_interview():
    """Test extracting just one interview to understand the structure"""
    test_url = "https://iwataasks.nintendo.com/interviews/wiiu/splatoon/0/0/"
    
    print(f"Testing extraction of single interview: {test_url}")
    
    try:
        response = requests.get(test_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"Page loaded successfully - Length: {len(response.text)}")
        
        # Extract title
        title = ""
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            title = title_elem.get_text().strip()
        print(f"Title: {title}")
        
        # Extract text content from different possible containers
        content_selectors = [
            'div.content',
            'div.main-content', 
            'div.article',
            'div.post',
            'section',
            'main',
            'div.container'
        ]
        
        content = ""
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                # Remove unwanted elements
                for script in elem.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    script.decompose()
                
                content = elem.get_text().strip()
                if len(content) > 200:  # We found substantial content
                    print(f"Found content using selector: {selector}")
                    break
        
        print(f"Content length: {len(content)} characters")
        if content:
            print(f"Content preview: {content[:300]}...")
        else:
            print("No substantial content found")
        
        # Extract all images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                img_url = urljoin(test_url, src)
                images.append({
                    'url': img_url,
                    'alt': img.get('alt', ''),
                    'src': src
                })
        
        print(f"Found {len(images)} images")
        for i, img in enumerate(images[:3], 1):
            print(f"  {i}. {img['alt']} -> {img['url']}")
        
        # Show page structure
        print("\nPage structure (main elements):")
        for elem in soup.find_all(['div', 'section', 'article'])[:10]:
            classes = elem.get('class', [])
            id_attr = elem.get('id', '')
            if classes or id_attr:
                class_str = ' '.join(classes) if classes else ''
                id_str = f"#{id_attr}" if id_attr else ''
                print(f"  {elem.name}{id_str}.{class_str}")
        
        return {
            'title': title,
            'content': content,
            'images': images,
            'has_content': len(content) > 200
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = extract_one_interview()
    
    if result and result['has_content']:
        print("\nSUCCESS: Content extraction works!")
        
        # Save test result
        os.makedirs("test_output", exist_ok=True)
        
        with open("test_output/single_interview.txt", 'w', encoding='utf-8') as f:
            f.write(f"Title: {result['title']}\n\n")
            f.write(f"Content:\n{result['content']}\n\n")
            f.write(f"Images ({len(result['images'])}):\n")
            for img in result['images']:
                f.write(f"- {img['alt']}: {img['url']}\n")
        
        print("Test result saved to test_output/single_interview.txt")
    else:
        print("FAILED: Could not extract substantial content")