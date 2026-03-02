#!/usr/bin/env python3
"""
Iwata Asks Test - Quick version to extract interview list
"""

import requests
from bs4 import BeautifulSoup

def test_iwata_asks_connection():
    base_url = "https://iwataasks.nintendo.com"
    
    print("Testing connection to Iwata Asks...")
    
    try:
        response = requests.get(base_url, timeout=10)
        print(f"Connected successfully!")
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)} characters")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            if href and len(text) > 0:
                links.append({
                    'url': href,
                    'text': text
                })
        
        print(f"\nFound {len(links)} links total:")
        
        # Filter potentially interview-related links
        interview_links = []
        for link in links:
            text_lower = link['text'].lower()
            if any(keyword in text_lower for keyword in ['wii', '3ds', 'ds', 'game', 'nintendo', 'interview', 'ask']):
                interview_links.append(link)
        
        print(f"\nPotentially interview-related links ({len(interview_links)}):")
        for i, link in enumerate(interview_links[:20], 1):  # Show first 20
            print(f"{i:2d}. {link['text'][:50]:<50} -> {link['url']}")
        
        if len(interview_links) > 20:
            print(f"... and {len(interview_links) - 20} more")
        
        return len(interview_links) > 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_iwata_asks_connection()
    if success:
        print("\nTest completed successfully!")
        print("You can now run the full scraper.")
    else:
        print("\nTest failed. Check your connection or the website status.")