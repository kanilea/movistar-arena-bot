#!/usr/bin/env python3
"""
Simple Iwata Asks Scraper - Version for Windows
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
import json

class SimpleIwataAsksScraper:
    def __init__(self):
        self.base_url = "https://iwataasks.nintendo.com"
        self.output_dir = "iwata_archive"
        self.session = requests.Session()
        self.interviews = []
        
    def create_directories(self):
        """Create necessary directories"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created directory: {self.output_dir}")
    
    def get_page(self, url):
        """Get page content"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Error accessing {url}: {e}")
            return None
    
    def extract_interview_links(self):
        """Extract all interview links"""
        print("Extracting interview links...")
        
        response = self.get_page(self.base_url)
        if not response:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        interview_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            if href.startswith('/interviews/') and text:
                full_url = urljoin(self.base_url, href)
                if full_url not in [i['url'] for i in interview_links]:
                    interview_links.append({
                        'url': full_url,
                        'title': text
                    })
        
        print(f"Found {len(interview_links)} interview links")
        return interview_links
    
    def extract_interview_content(self, interview):
        """Extract content from one interview"""
        print(f"Extracting: {interview['title'][:50]}...")
        
        response = self.get_page(interview['url'])
        if not response:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find title
        title = interview['title']
        title_elem = soup.find('h1')
        if title_elem:
            title = title_elem.get_text().strip()
        
        # Find content
        content = ""
        content_div = soup.find('div', class_='content')
        if content_div:
            # Remove scripts
            for script in content_div.find_all(['script', 'style']):
                script.decompose()
            content = content_div.get_text().strip()
        
        # Find images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                img_url = urljoin(interview['url'], src)
                images.append({
                    'url': img_url,
                    'alt': img.get('alt', ''),
                    'filename': img_url.split('/')[-1].split('?')[0]
                })
        
        return {
            'url': interview['url'],
            'title': title,
            'content': content,
            'images': images
        }
    
    def save_text_document(self):
        """Save as simple text document"""
        text_content = f"""IWATA ASKS COMPLETE ARCHIVE
{'='*60}

Total interviews: {len(self.interviews)}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Source: {self.base_url}

{'='*60}

"""
        
        for i, interview in enumerate(self.interviews, 1):
            text_content += f"""
{'-'*60}
INTERVIEW {i}: {interview['title']}

URL: {interview['url']}

CONTENT:
{interview['content']}

IMAGES ({len(interview['images'])}):
"""
            for img in interview['images']:
                text_content += f"- {img['alt']}: {img['url']}\n"
        
        # Save text file
        filename = f"{self.output_dir}/Iwata_Asks_Archive.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"Text document saved: {filename}")
        
        # Also save JSON
        json_filename = f"{self.output_dir}/Iwata_Asks_Data.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.interviews, f, indent=2, ensure_ascii=False)
        
        print(f"JSON data saved: {json_filename}")
        return filename, json_filename
    
    def scrape_all(self):
        """Main method"""
        print("Starting Iwata Asks scraper...")
        
        self.create_directories()
        
        # Get links
        links = self.extract_interview_links()
        if not links:
            print("No interview links found!")
            return
        
        print(f"Starting extraction of {len(links)} interviews...")
        
        # Extract each interview
        for i, link in enumerate(links, 1):
            print(f"Progress: {i}/{len(links)}")
            
            interview = self.extract_interview_content(link)
            if interview and interview['content']:
                self.interviews.append(interview)
            
            # Be respectful
            time.sleep(1)
            
            # Show progress every 10 interviews
            if i % 10 == 0:
                print(f"Completed {i} interviews, collected {len(self.interviews)} valid ones")
        
        print(f"\nExtraction complete!")
        print(f"Total interviews extracted: {len(self.interviews)}")
        
        if self.interviews:
            self.save_text_document()
            print(f"Archive saved in '{self.output_dir}' directory!")

if __name__ == "__main__":
    scraper = SimpleIwataAsksScraper()
    scraper.scrape_all()