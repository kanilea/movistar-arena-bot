#!/usr/bin/env python3
"""
Modern Iwata Asks Scraper - For JavaScript-rendered websites
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
import json
import re

def get_wikipedia_list():
    """Get the complete list from Wikipedia since the original site is modern JS"""
    url = "https://en.wikipedia.org/wiki/List_of_Iwata_Asks_interviews"
    
    print("Getting Iwata Asks list from Wikipedia...")
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"Wikipedia page loaded - Length: {len(response.text)}")
        
        # Find interview lists (usually in tables or lists)
        interviews = []
        
        # Look for tables with interview data
        tables = soup.find_all('table', {'class': ['wikitable', 'sortable']})
        
        for i, table in enumerate(tables):
            print(f"Processing table {i+1}...")
            
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    title = cols[0].get_text().strip()
                    platform = cols[1].get_text().strip() if len(cols) > 1 else ""
                    
                    if title and len(title) > 3:  # Valid entry
                        interviews.append({
                            'title': title,
                            'platform': platform,
                            'table_index': i
                        })
        
        print(f"Found {len(interviews)} interviews from Wikipedia")
        
        # Also look for lists
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            for item in items:
                text = item.get_text().strip()
                if any(keyword in text.lower() for keyword in ['wii', '3ds', 'ds', 'switch']):
                    # Extract game title (usually first part)
                    title = text.split('–')[0].split('-')[0].strip()
                    if title and len(title) > 3 and title not in [i['title'] for i in interviews]:
                        interviews.append({
                            'title': title,
                            'platform': 'Unknown',
                            'source': 'list'
                        })
        
        print(f"Total interviews found: {len(interviews)}")
        
        # Remove duplicates
        unique_interviews = []
        seen_titles = set()
        
        for interview in interviews:
            title = interview['title'].lower().strip()
            if title not in seen_titles:
                seen_titles.add(title)
                unique_interviews.append(interview)
        
        print(f"After removing duplicates: {len(unique_interviews)}")
        
        # Save the list
        os.makedirs("iwata_archive", exist_ok=True)
        
        # Save as structured JSON
        with open("iwata_archive/interview_list.json", 'w', encoding='utf-8') as f:
            json.dump(unique_interviews, f, indent=2, ensure_ascii=False)
        
        # Save as formatted text
        with open("iwata_archive/Iwata_Asks_Complete_List.txt", 'w', encoding='utf-8') as f:
            f.write("COMPLETE LIST OF IWATA ASKS INTERVIEWS\n")
            f.write("="*60 + "\n\n")
            f.write("Source: Wikipedia - List of Iwata Asks interviews\n")
            f.write(f"Total: {len(unique_interviews)} interviews\n\n")
            
            # Group by platform
            platforms = {}
            for interview in unique_interviews:
                platform = interview.get('platform', 'Unknown')
                if platform not in platforms:
                    platforms[platform] = []
                platforms[platform].append(interview)
            
            for platform, items in sorted(platforms.items()):
                f.write(f"\n{platform.upper()} ({len(items)} interviews)\n")
                f.write("-" * 40 + "\n")
                
                for i, interview in enumerate(items, 1):
                    f.write(f"{i:2d}. {interview['title']}\n")
        
        print(f"Files saved to 'iwata_archive/' directory")
        
        # Show sample
        print(f"\nSAMPLE INTERVIEWS:")
        for i, interview in enumerate(unique_interviews[:10], 1):
            print(f"{i:2d}. {interview['title']} ({interview.get('platform', 'Unknown')})")
        
        if len(unique_interviews) > 10:
            print(f"... and {len(unique_interviews) - 10} more")
        
        # Try to create links to original interviews
        print(f"\nGenerating interview links...")
        generate_interview_links(unique_interviews)
        
        return unique_interviews
        
    except Exception as e:
        print(f"Error accessing Wikipedia: {e}")
        return []

def generate_interview_links(interviews):
    """Generate potential links to original Iwata Asks interviews"""
    base_url = "https://iwataasks.nintendo.com/interviews"
    
    platform_mapping = {
        'Wii U': 'wiiu',
        'Nintendo 3DS': '3ds', 
        'Wii': 'wii',
        'Nintendo DS': 'ds'
    }
    
    with open("iwata_archive/interview_links.txt", 'w', encoding='utf-8') as f:
        f.write("POTENTIAL IWATA ASKS INTERVIEW LINKS\n")
        f.write("="*50 + "\n\n")
        
        for interview in interviews:
            title = interview['title']
            platform = interview.get('platform', '')
            
            # Try to construct URL based on title
            platform_path = platform_mapping.get(platform, 'wiiu') if platform in platform_mapping else 'wiiu'
            
            # Clean title for URL
            title_slug = title.lower()
            title_slug = re.sub(r'[^a-z0-9\s-]', '', title_slug)
            title_slug = re.sub(r'\s+', '-', title_slug).strip('-')
            
            potential_url = f"{base_url}/{platform_path}/{title_slug}/0/0/"
            
            f.write(f"{title}\n")
            f.write(f"Platform: {platform}\n")
            f.write(f"Potential URL: {potential_url}\n")
            f.write("-" * 50 + "\n")
    
    print(f"Potential interview links saved to 'iwata_archive/interview_links.txt'")

if __name__ == "__main__":
    interviews = get_wikipedia_list()
    
    if interviews:
        print(f"\nSUCCESS: Retrieved {len(interviews)} Iwata Asks interviews from Wikipedia!")
        print("Files created:")
        print("- iwata_archive/Iwata_Asks_Complete_List.txt")
        print("- iwata_archive/interview_list.json") 
        print("- iwata_archive/interview_links.txt")
        print("\nThe original Nintendo site uses JavaScript rendering,")
        print("so Wikipedia provides the most reliable complete list.")
    else:
        print("FAILED: Could not retrieve interview list")