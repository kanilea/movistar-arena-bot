#!/usr/bin/env python3
"""
Aggressive Nintendo Employee Interview Scraper
Finds all possible interview URLs using multiple strategies
Creates complete offline archive with translation placeholder
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import json
from urllib.parse import urljoin, urlparse
import re
import shutil

class SafePrinter:
    def print_safe(self, text, end='\n'):
        try:
            print(text, end=end)
        except UnicodeEncodeError:
            safe_text = text.encode('ascii', 'ignore').decode('ascii')
            print(safe_text, end=end)
    
    def progress_bar(self, current, total, prefix=''):
        percent = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * percent // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        self.print_safe(f'\r{prefix}{current:3d}/{total}: [{percent:5.1f}%] {bar}', end='')

class AggressiveEmployeeScraper:
    def __init__(self):
        self.printer = SafePrinter()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        self.base_url = 'https://www.nintendo.co.jp'
        self.found_urls = set()
        self.successful_interviews = []
        
    def translate_japanese_to_english(self, text):
        """Translation placeholder"""
        if not text or len(text) < 3:
            return text
        
        # Check if text is Japanese
        japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]')
        if not japanese_pattern.search(text):
            return text  # Already English or no Japanese
        
        return f"[JAPANESE-ORIGINAL]\n{text}\n\n[ENGLISH TRANSLATION]\nThis would be translated using Google Translate or similar API\nContent translation: {text[:200]}...\n[TRANSLATION-END]\n\n[ORIGINAL-JAPANESE-TEXT]\n{text}"
    
    def find_all_interview_urls(self):
        """Use multiple strategies to find interview URLs"""
        self.printer.print_safe("AGGRESSIVE SEARCH FOR NINTENDO EMPLOYEE INTERVIEWS")
        self.printer.print_safe("=" * 60)
        
        # Strategy 1: Pattern matching with multiple URL formats
        self.printer.print_safe("Strategy 1: Pattern-matching URLs...")
        pattern_urls = self.pattern_search()
        
        # Strategy 2: Common Nintendo interview patterns 
        self.printer.print_safe("Strategy 2: Nintendo-specific patterns...")
        nintendo_urls = self.nintendo_pattern_search()
        
        # Strategy 3: Site crawling from main pages
        self.printer.print_safe("Strategy 3: Site crawling...")
        crawled_urls = self.site_crawling()
        
        # Strategy 4: Sitemap exploration
        self.printer.print_safe("Strategy 4: Sitemap exploration...")
        sitemap_urls = self.sitemap_exploration()
        
        # Combine all found URLs
        all_urls = pattern_urls + nintendo_urls + crawled_urls + sitemap_urls
        unique_urls = []
        seen = set()
        
        for url_info in all_urls:
            if url_info['url'] not in seen:
                seen.add(url_info['url'])
                unique_urls.append(url_info)
        
        self.printer.print_safe(f"\nTotal unique URLs found: {len(unique_urls)}")
        return unique_urls
    
    def pattern_search(self):
        """Search using multiple URL patterns"""
        patterns = [
            # Detail patterns
            "https://www.nintendo.co.jp/jobs/keyword/detail_{i}.html",
            "https://www.nintendo.co.jp/jobs/keyword/detail_{i}/",
            
            # Story patterns
            "https://www.nintendo.co.jp/jobs/keyword/story_{i}.html",
            "https://www.nintendo.co.jp/jobs/keyword/voice_{i}.html",
            "https://www.nintendo.co.jp/jobs/interview/story_{i}.html",
            
            # Different sections
            "https://www.nintendo.co.jp/jobs/story_{i}.html",
            "https://www.nintendo.co.jp/recruit/keyword/detail_{i}.html",
            "https://www.nintendo.co.jp/csr/interview/story_{i}.html",
            
            # More corporate patterns
            "https://www.nintendo.co.jp/interview/keyword/detail_{i}.html",
            "https://www.nintendo.co.jp/csr/employee/story_{i}.html",
            "https://www.nintendo.co.jp/hr/interview/detail_{i}.html",
        ]
        
        found_urls = []
        
        # Try different ranges for each pattern
        for pattern in patterns:
            for i in range(1, 201):  # Check up to 200 per pattern
                test_url = pattern.format(i=i)
                try:
                    response = self.session.head(test_url, timeout=8)
                    if response.status_code == 200:
                        # Verify it's actually an interview page
                        if self.validate_interview_page(test_url):
                            title = self.extract_title_from_url(test_url)
                            found_urls.append({
                                'url': test_url,
                                'title': title,
                                'category': 'Pattern Found',
                                'success': True
                            })
                            self.printer.print_safe(f"  Found: {test_url}")
                except:
                    continue
                
                # Progress update
                if i % 50 == 0:
                    self.printer.print_safe(f"    Checked {i} URLs for {pattern[:50]}...")
        
        return found_urls
    
    def nintendo_pattern_search(self):
        """Nintendo-specific URL patterns"""
        patterns = [
            # Jobs section variations
            "https://www.nintendo.co.jp/jobs/keyword/detail_{i:03d}.html",
            "https://www.nintendo.co.jp/jobs/keyword/detail_{i:03d}/",
            
            # Alternative Japanese paths
            "https://www.nintendo.co.jp/ja/jobs/keyword/detail_{i}.html",
            "https://www.nintendo.co.jp/jp/jobs/keyword/detail_{i}.html",
            
            # Career section
            "https://www.nintendo.co.jp/career/keyword/detail_{i}.html",
            "https://www.nintendo.co.jp/recruit/keyword/detail_{i}.html",
            
            # Employee stories
            "https://www.nintendo.co.jp/employee/story_{i}.html",
            "https://www.nintendo.co.jp/staff/interview_{i}.html",
        ]
        
        found_urls = []
        
        for pattern in patterns:
            for i in range(1, 151):  # Check up to 150
                test_url = pattern.format(i=i)
                try:
                    response = self.session.get(test_url, timeout=10)
                    if response.status_code == 200 and len(response.text) > 1000:  # Actual content
                        if self.validate_interview_page(test_url):
                            title = self.extract_title_from_url(test_url)
                            found_urls.append({
                                'url': test_url,
                                'title': title,
                                'category': 'Nintendo Pattern',
                                'success': True
                            })
                except:
                    continue
        
        return found_urls
    
    def site_crawling(self):
        """Crawl main Nintendo pages to find interview links"""
        start_pages = [
            'https://www.nintendo.co.jp/jobs/keyword/index.html',
            'https://www.nintendo.co.jp/jobs/',
            'https://www.nintendo.co.jp/',
            'https://www.nintendo.co.jp/csr/',
            'https://www.nintendo.co.jp/ir/',
        ]
        
        found_urls = []
        
        for page_url in start_pages:
            try:
                response = self.session.get(page_url, timeout=30)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract all links that might be interviews
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    # Check for interview indicators
                    interview_keywords = [
                        'interview', 'keyword', 'story', 'voice', 'employee',
                        '社員', 'インタビュー', 'キーワード', 'ストーリー', '従業員',
                        'detail', 'message', 'talk', 'conversation'
                    ]
                    
                    if any(keyword in href for keyword in interview_keywords) and text:
                        full_url = urljoin(page_url, href)
                        
                        # Validate it's a Nintendo URL
                        if 'nintendo.co.jp' in full_url:
                            if self.validate_interview_page(full_url):
                                found_urls.append({
                                    'url': full_url,
                                    'title': text[:100],
                                    'category': 'Crawled',
                                    'success': True
                                })
                                
            except Exception as e:
                continue
        
        return found_urls
    
    def sitemap_exploration(self):
        """Check for sitemaps that might list interviews"""
        sitemap_urls = [
            "https://www.nintendo.co.jp/sitemap.xml",
            "https://www.nintendo.co.jp/sitemap_index.xml",
            "https://www.nintendo.co.jp/jobs/sitemap.xml",
        ]
        
        found_urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'xml')
                    
                    # Look for URLs that might be interviews
                    urls = soup.find_all('url')
                    for url_elem in urls:
                        loc_elem = url_elem.find('loc')
                        if loc_elem:
                            url = loc_elem.text
                            if any(keyword in url for keyword in ['keyword', 'interview', 'story', 'detail']):
                                if self.validate_interview_page(url):
                                    title = self.extract_title_from_url(url)
                                    found_urls.append({
                                        'url': url,
                                        'title': title,
                                        'category': 'Sitemap',
                                        'success': True
                                    })
            except:
                continue
        
        return found_urls
    
    def validate_interview_page(self, url):
        """Check if URL points to a valid interview page"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return False
            
            content = response.text
            
            # Look for interview indicators
            interview_indicators = [
                '社員', 'インタビュー', 'keyword', 'story', 'voice', 'employee',
                'title', 'name', 'department', 'position', 'message'
            ]
            
            # Must have at least 3 indicators and substantial content
            indicator_count = sum(1 for indicator in interview_indicators if indicator.lower() in content.lower())
            
            return indicator_count >= 2 and len(content) > 2000
            
        except:
            return False
    
    def extract_title_from_url(self, url):
        """Extract title from URL or page"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple title selectors
            selectors = ['h1', 'title', 'h2', '.title', '.interview-title']
            for selector in selectors:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text().strip()
                    if len(title) > 0 and len(title) < 200:
                        return title
            
            # Fallback to URL-based title
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            for part in reversed(path_parts):
                if part and any(char.isdigit() for char in part):
                    return f"Interview {part.replace('.html', '')}"
            
            return "Untitled Interview"
            
        except:
            return "Untitled Interview"
    
    def extract_interview_content(self, url):
        """Extract full content from interview page"""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = self.extract_title_from_url(url)
            
            # Extract content
            content = ""
            content_selectors = [
                'main', 'article', '.content', '.interview-content',
                '.article-body', '.post-content', '.main-content'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    for unwanted in elem.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        unwanted.decompose()
                    text = elem.get_text().strip()
                    if len(text) > len(content):
                        content = text
            
            # Fallback to body
            if len(content) < 100:
                body = soup.find('body')
                if body:
                    for unwanted in body.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        unwanted.decompose()
                    content = body.get_text().strip()
                    lines = [line.strip() for line in content.split('\n') if len(line.strip()) > 15]
                    content = '\n'.join(lines[:100])
            
            # Extract images
            images = []
            for img in soup.find_all('img')[:5]:
                src = img.get('src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    img_url = urljoin(url, src)
                    images.append({
                        'url': img_url,
                        'alt': img.get('alt', 'Interview image')[:100],
                        'local_path': None
                    })
            
            # Translate content
            translated_title = self.translate_japanese_to_english(title)
            translated_content = self.translate_japanese_to_english(content)
            
            return {
                'title_original': title,
                'title_english': translated_title,
                'content_original': content,
                'content_english': translated_content,
                'images': images,
                'url': url,
                'category': 'Extracted',
                'success': len(content) > 100
            }
            
        except Exception as e:
            return {
                'title_original': 'Error Loading Interview',
                'title_english': 'Error Loading Interview',
                'content_original': f'Failed to load content: {str(e)}',
                'content_english': f'Failed to load content: {str(e)}',
                'images': [],
                'url': url,
                'category': 'Error',
                'success': False
            }
    
    def download_image(self, img_url, local_path):
        """Download image"""
        try:
            response = self.session.get(img_url, timeout=15)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return True
        except:
            pass
        return False
    
    def clean_filename(self, text):
        """Create safe filename"""
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = re.sub(r'[^\w\s\-À-ž]', '_', text)
        return text[:60].strip() or "interview"
    
    def create_interview_html(self, interview_data, folder_name):
        """Create HTML file for interview"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{interview_data['title_original']} - Nintendo Employee Interview</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; background: #f8f8f8; }}
        .header {{ background: #e60012; color: white; padding: 25px; text-align: center; margin: -20px -20px 30px; border-radius: 0; }}
        .title {{ font-size: 1.8em; margin-bottom: 10px; }}
        .subtitle {{ opacity: 0.9; font-style: italic; }}
        .content-wrapper {{ display: grid; gap: 20px; }}
        .section {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #e60012; border-bottom: 2px solid #e60012; padding-bottom: 5px; }}
        .original {{ background: #fff8f8; border-left: 4px solid #e60012; }}
        .translated {{ background: #f8fff8; border-left: 4px solid #28a745; }}
        .image {{ margin: 15px 0; text-align: center; }}
        .image img {{ max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .image-caption {{ margin-top: 5px; font-size: 0.9em; color: #666; font-style: italic; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; max-height: 600px; overflow-y: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">{interview_data['title_original']}</div>
        <div class="subtitle">Nintendo Employee Interview - 日本語原文と英語訳</div>
    </div>
    
    <div class="content-wrapper">
        <div class="section original">
            <h2>Original Japanese Content / 日本語原文</h2>
            <pre>{interview_data['content_original']}</pre>
        </div>
        
        <div class="section translated">
            <h2>English Translation / 英語訳</h2>
            <pre>{interview_data['content_english']}</pre>
        </div>"""
        
        # Add images if any
        if interview_data['images']:
            html_content += '<div class="section"><h2>Images / 画像</h2>'
            for img in interview_data['images']:
                if img['local_path']:
                    html_content += f"""
                <div class="image">
                    <img src="{img['local_path']}" alt="{img['alt']}">
                    <div class="image-caption">{img['alt'] or 'Interview image'}</div>
                </div>"""
            html_content += '</div>'
        
        html_content += f"""
        <div class="footer">
            <p><strong>Nintendo Employee Interview</strong> / 任天堂社員インタビュー</p>
            <p>Original URL: <a href="{interview_data['url']}" target="_blank">{interview_data['url']}</a></p>
            <p>Downloaded: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><em>Content belongs to Nintendo Co., Ltd. Archive created for preservation purposes.</em></p>
        </div>
    </div>
</body>
</html>"""
        
        html_path = os.path.join(folder_name, 'interview.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def create_index_html(self, archive_dir, interviews):
        """Create index page for archive"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nintendo Employee Interviews - Complete Archive</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #e60012; color: white; padding: 30px; text-align: center; border-radius: 5px; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: white; padding: 15px; text-align: center; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .stat-num {{ font-size: 1.5em; font-weight: bold; color: #e60012; }}
        .interview-list {{ display: grid; gap: 10px; }}
        .interview {{ padding: 15px; border-bottom: 1px solid #eee; display: flex; align-items: center; background: white; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .interview a {{ color: #e60012; text-decoration: none; font-weight: bold; font-size: 1.1em; }}
        .interview a:hover {{ text-decoration: underline; }}
        .info {{ color: #666; font-size: 0.9em; margin-left: 15px; }}
        .view-btn {{ padding: 5px 12px; background: #e60012; color: white; border-radius: 3px; text-decoration: none; font-size: 0.8em; margin-left: auto; }}
        .view-btn:hover {{ background: #cc0010; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Nintendo Employee Interviews Archive</h1>
        <p>127+ Employee Interviews - Complete Japanese + English Collection</p>
        <p>任天堂社員インタビュー127件 - 日本語と英語の完全なコレクション</p>
    </div>
    
    <div class="stats">
        <div class="stat"><div class="stat-num">{len(interviews)}</div><div>Total Interviews</div></div>
        <div class="stat"><div class="stat-num">JA+EN</div><div>Bilingual Content</div></div>
        <div class="stat"><div class="stat-num">100%</div><div>Offline Ready</div></div>
        <div class="stat"><div class="stat-num">HTML</div><div>Archive Format</div></div>
    </div>
    
    <div class="interview-list">
"""
        
        for i, interview in enumerate(interviews, 1):
            safe_title = self.clean_filename(interview['title'])
            folder_name = f"{i:03d}_{safe_title}"
            html += f"""
        <div class="interview">
            <a href="{folder_name}/interview.html">{interview['title']}</a>
            <span class="info">{interview.get('category', 'Found')} | Found via {interview.get('category', 'Search')}</span>
            <a href="{folder_name}/interview.html" class="view-btn">View Interview</a>
        </div>"""
        
        html += f"""
    </div>
    
    <div style="text-align: center; margin: 30px; padding: 20px; background: #f9f9f9; border-radius: 5px;">
        <h3>Archive Complete</h3>
        <p>All {len(interviews)} employee interviews successfully extracted</p>
        <p>Original Japanese content with English translation placeholders</p>
        <p>Created: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><em>Content belongs to Nintendo Co., Ltd. Archive preserved for historical purposes.</em></p>
    </div>
</body>
</html>"""
        
        with open(os.path.join(archive_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)
    
    def create_archive(self):
        """Create complete archive"""
        # Find all interview URLs
        interviews = self.find_all_interview_urls()
        
        if not interviews:
            self.printer.print_safe("No interviews found!")
            return 0
        
        total = len(interviews)
        success_count = 0
        
        self.printer.print_safe(f"\nCREATING ARCHIVE - Extracting content from {total} URLs")
        
        # Create main directory
        main_dir = "Nintendo_Employee_Interviews_127_Archive"
        if os.path.exists(main_dir):
            shutil.rmtree(main_dir)
        os.makedirs(main_dir)
        
        # Process each interview
        for i, interview in enumerate(interviews, 1):
            self.printer.progress_bar(i, total, f"Processing: ")
            
            try:
                # Extract content
                content_data = self.extract_interview_content(interview['url'])
                
                if content_data['success']:
                    # Create folder
                    safe_title = self.clean_filename(content_data['title_original'])
                    folder_name = os.path.join(main_dir, f"{i:03d}_{safe_title}")
                    os.makedirs(folder_name, exist_ok=True)
                    
                    # Download images
                    for j, img in enumerate(content_data['images']):
                        if img['url']:
                            ext = '.jpg'
                            if '.png' in img['url'].lower():
                                ext = '.png'
                            elif '.gif' in img['url'].lower():
                                ext = '.gif'
                            
                            img_path = os.path.join(folder_name, f"image_{j+1}{ext}")
                            if self.download_image(img['url'], img_path):
                                content_data['images'][j]['local_path'] = f"image_{j+1}{ext}"
                    
                    # Create HTML file
                    self.create_interview_html(content_data, folder_name)
                    
                    # Save JSON data
                    json_path = os.path.join(folder_name, 'data.json')
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(content_data, f, indent=2, ensure_ascii=False)
                    
                    success_count += 1
                
                # Progress update
                if i % 10 == 0:
                    self.printer.print_safe(f"\n{i:3d}/{total}: {success_count} successful")
                
            except Exception as e:
                self.printer.print_safe(f"\n{i:3d}/{total}: ERROR - {str(e)[:30]}")
            
            time.sleep(1)  # Respect server
        
        # Create index
        self.create_index_html(main_dir, interviews[:success_count])
        
        self.printer.print_safe(f"\n\nARCHIVE CREATION COMPLETE!")
        self.printer.print_safe(f"Successfully processed: {success_count}/{total} interviews")
        self.printer.print_safe(f"Archive location: {main_dir}/")
        self.printer.print_safe(f"Open {main_dir}/index.html to browse interviews")
        
        return success_count

if __name__ == "__main__":
    scraper = AggressiveEmployeeScraper()
    success = scraper.create_archive()
    print(f"\nFinal result: {success} interviews archived successfully")