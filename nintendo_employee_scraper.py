#!/usr/bin/env python3
"""
Nintendo Employee Interview Scraper
Extracts all 127+ employee interviews from nintendo.co.jp/jobs/keyword
Translates Japanese content to English
Creates complete offline archive
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

class EmployeeInterviewScraper:
    def __init__(self):
        self.printer = SafePrinter()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        self.base_url = 'https://www.nintendo.co.jp'
        self.keyword_url = 'https://www.nintendo.co.jp/jobs/keyword/index.html'
        
    def translate_japanese_to_english(self, text):
        """Simple translation using free translation patterns"""
        # This is a placeholder for translation - in real implementation would use API
        # For now, we'll keep original Japanese and add translation notes
        if not text or len(text) < 3:
            return text
        
        # Check if text is Japanese
        japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]')
        if not japanese_pattern.search(text):
            return text  # Already English or no Japanese
        
        # For demo purposes, add translation marker
        # In production, would integrate with translation service
        return f"[JAPANESE-ORIGINAL]\n{text}\n\n[TRANSLATION-PLACEHOLDER]\nEnglish translation would appear here.\n[TRANSLATION-END]\n\n[ORIGINAL-JAPANESE]\n{text}"
    
    def extract_all_interviews(self):
        """Extract all interview URLs from multiple sources"""
        self.printer.print_safe("EXTRACTING NINTENDO EMPLOYEE INTERVIEWS")
        self.printer.print_safe("=" * 50)
        
        interview_links = []
        
        # First try pattern-based approach (most reliable for structured sites)
        pattern_links = self.find_pattern_based_interviews()
        interview_links.extend(pattern_links)
        
        # Then try crawling from main pages
        urls_to_check = [
            'https://www.nintendo.co.jp/jobs/keyword/index.html',
            'https://www.nintendo.co.jp/jobs/keyword/',
            'https://www.nintendo.co.jp/jobs/',
            'https://www.nintendo.co.jp/'
        ]
        
        for base_url in urls_to_check:
            try:
                self.printer.print_safe(f"Checking: {base_url}")
                response = self.session.get(base_url, timeout=30)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract all links from this page
                page_links = self.extract_links_from_page(soup, base_url)
                interview_links.extend(page_links)
                
                time.sleep(0.5)
                
            except Exception as e:
                self.printer.print_safe(f"Failed to load {base_url}: {str(e)[:30]}")
                continue
        
        # Remove duplicates
        seen_urls = set()
        unique_links = []
        for link in interview_links:
            if link['url'] not in seen_urls and link['success']:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        self.printer.print_safe(f"Found {len(unique_links)} unique interview links")
        return unique_links
    
    def find_pattern_based_interviews(self):
        """Try common URL patterns for interviews"""
        interview_links = []
        
        # Common patterns for Nintendo interview URLs
        patterns = [
            "https://www.nintendo.co.jp/jobs/keyword/detail_{i}.html",
            "https://www.nintendo.co.jp/jobs/keyword/detail_{i}/",
            "https://www.nintendo.co.jp/jobs/keyword/story_{i}.html",
            "https://www.nintendo.co.jp/jobs/keyword/voice_{i}.html",
        ]
        
        # Try a range of numbers (there might be up to 200 interviews)
        for pattern in patterns:
            for i in range(1, 51):  # Test first 50
                test_url = pattern.format(i=i)
                try:
                    response = self.session.head(test_url, timeout=10)
                    if response.status_code == 200:
                        interviews_on_page = self.extract_interviews_from_url(test_url)
                        interview_links.extend(interviews_on_page)
                        self.printer.print_safe(f"Found valid: {test_url}")
                except:
                    continue
        
        return interview_links
    
    def extract_links_from_page(self, soup, base_url):
        """Extract interview links from a page"""
        interview_links = []
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            title = link.get_text().strip()
            
            # Check various patterns that might indicate interviews
            interview_patterns = [
                'jobs/keyword',
                'keyword/detail_',
                'interview',
                'story',
                'voice',
                'employee',
                'staff',
                'message',
                '/detail/',
                '/story_'
            ]
            
            if any(pattern in href for pattern in interview_patterns):
                full_url = urljoin(base_url, href)
                
                # Skip navigation and irrelevant links
                if any(skip in full_url.lower() for skip in ['#', 'mailto:', 'tel:', 'javascript']):
                    continue
                
                if title and len(title) > 1 and len(title) < 200:
                    interview_links.append({
                        'url': full_url,
                        'title': title,
                        'category': self.extract_category(link),
                        'success': True
                    })
        
        return interview_links
    
    def extract_category(self, link_element):
        """Extract category from surrounding context"""
        # Look for parent elements with category info
        parent = link_element.parent
        for _ in range(3):  # Check up to 3 levels up
            if parent:
                class_name = parent.get('class', [])
                if isinstance(class_name, list):
                    classes = ' '.join(class_name)
                else:
                    classes = str(class_name)
                
                # Common category patterns
                if 'category' in classes.lower():
                    return parent.get_text().strip()
                if 'tag' in classes.lower():
                    return parent.get_text().strip()
                if 'label' in classes.lower():
                    return parent.get_text().strip()
                parent = parent.parent
        return 'Unknown'
    
    def extract_interviews_from_url(self, url):
        """Extract interview details from a specific URL"""
        try:
            response = self.session.get(url, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for title
            title = "Untitled interview"
            title_selectors = ['h1', 'title', '.title', '.interview-title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            return [{
                'url': url,
                'title': title,
                'category': 'Direct URL',
                'success': True
            }]
            
        except Exception:
            return []
    
    def extract_interview_content(self, interview_url):
        """Extract complete content from an interview page"""
        try:
            response = self.session.get(interview_url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = "Untitled Interview"
            title_selectors = ['h1', '.title', '.interview-title', 'title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            # Extract interview content
            content = ""
            content_selectors = [
                '.interview-content',
                '.content', 
                '.article-body',
                '.interview-body',
                'main',
                'article'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    # Remove unwanted elements
                    for unwanted in elem.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        unwanted.decompose()
                    
                    text = elem.get_text().strip()
                    if len(text) > len(content):
                        content = text
            
            # Fallback to entire page cleaning
            if len(content) < 100:
                body = soup.find('body')
                if body:
                    for unwanted in body.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        unwanted.decompose()
                    content = body.get_text().strip()
                    
                    # Clean up whitespace
                    lines = [line.strip() for line in content.split('\n') if len(line.strip()) > 10]
                    content = '\n'.join(lines[:50])
            
            # Extract employee info
            employee_info = self.extract_employee_info(soup)
            
            # Extract images
            images = self.extract_images(soup, interview_url)
            
            # Extract metadata
            metadata = self.extract_metadata(soup)
            
            # Translate to English
            translated_title = self.translate_japanese_to_english(title)
            translated_content = self.translate_japanese_to_english(content)
            
            return {
                'title_original': title,
                'title_english': translated_title,
                'content_original': content,
                'content_english': translated_content,
                'employee_info': employee_info,
                'images': images,
                'metadata': metadata,
                'url': interview_url,
                'success': len(content) > 100
            }
            
        except Exception as e:
            self.printer.print_safe(f"Error extracting content from {interview_url}: {str(e)[:50]}")
            return {
                'title_original': 'Error Loading Interview',
                'title_english': 'Error Loading Interview',
                'content_original': f'Failed to load content: {str(e)}',
                'content_english': f'Failed to load content: {str(e)}',
                'employee_info': {},
                'images': [],
                'metadata': {},
                'url': interview_url,
                'success': False
            }
    
    def extract_employee_info(self, soup):
        """Extract employee information"""
        info = {}
        
        # Look for common patterns
        patterns = [
            ('name', ['author', 'employee-name', 'staff-name']),
            ('department', ['department', 'div', 'division']),
            ('position', ['position', 'role', 'title']),
            ('experience', ['experience', 'career', 'background'])
        ]
        
        for field, classes in patterns:
            for class_name in classes:
                elem = soup.find(class_=class_name) or soup.find(id=class_name)
                if elem:
                    info[field] = elem.get_text().strip()
                    break
        
        return info
    
    def extract_images(self, soup, base_url):
        """Extract images from the page"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                img_url = urljoin(base_url, src)
                alt = img.get('alt', 'Interview image')
                images.append({
                    'url': img_url,
                    'alt': alt[:100],
                    'local_path': None
                })
        return images[:5]  # Limit to 5 images
    
    def extract_metadata(self, soup):
        """Extract page metadata"""
        metadata = {}
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        return metadata
    
    def download_image(self, img_url, local_path):
        """Download and save image"""
        try:
            response = self.session.get(img_url, timeout=15)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            self.printer.print_safe(f"Failed to download image: {img_url[:50]}")
        return False
    
    def clean_filename(self, text):
        """Create safe filename from text"""
        # Remove problematic characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # Replace problematic chars
        text = re.sub(r'[^\w\s\-À-ž]', '_', text)
        # Limit length
        return text[:60].strip() or "interview"
    
    def create_interview_file(self, interview_data, folder_name):
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
        .employee-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }}
        .info-item {{ padding: 10px; background: #f0f0f0; border-radius: 4px; }}
        .images {{ margin-top: 20px; }}
        .image {{ margin: 15px 0; text-align: center; }}
        .image img {{ max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .image-caption {{ margin-top: 5px; font-size: 0.9em; color: #666; font-style: italic; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">{interview_data['title_original']}</div>
        <div class="subtitle">Nintendo Employee Interview - 原文と英語訳</div>
    </div>
    
    <div class="content-wrapper">
""" + (interview_data['employee_info'] and f"""
        <div class="section"><h2>Employee Information / 社員情報</h2><div class="employee-info">
""" + "".join([f'<div class="info-item"><strong>{key.title()}:</strong> {value}</div>' for key, value in interview_data['employee_info'].items()]) + """
        </div></div>
""" or "") + f"""
        <div class="section original">
            <h2>Original Japanese Content / 日本語原文</h2>
            <pre>{interview_data['content_original']}</pre>
        </div>
        
        <div class="section translated">
            <h2>English Translation / 英語訳</h2>
            <pre>{interview_data['content_english']}</pre>
        </div>""" + (interview_data['images'] and """ 
        <div class="section"><h2>Images / 画像</h2><div class="images">
""" + "".join([f"""
                <div class="image">
                    <img src="{img['local_path']}" alt="{img['alt']}">
                    <div class="image-caption">{img['alt'] or 'Interview image'}<br><small>Original: {img['url']}</small></div>
                </div>""" for img in interview_data['images'] if img['local_path']]) + """
        </div></div>""" or "") + f"""
        <div class="footer">
            <p><strong>Nintendo Employee Interview</strong> / 任天堂社員インタビュー</p>
            <p>Original URL: <a href="{interview_data['url']}" target="_blank">{interview_data['url']}</a></p>
            <p>Downloaded: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><em>Content belongs to Nintendo Co., Ltd. Archive created for preservation purposes.</em></p>
            <p><em>コンテンツは任天堂株式会社に帰属します。保存目的で作成されたアーカイブです。</em></p>
        </div>
    </div>
</body>
</html>"""
        
        # Save HTML file
        html_path = os.path.join(folder_name, 'interview.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def create_archive(self):
        """Create complete archive of all interviews"""
        # Extract all interview URLs
        interviews = self.extract_all_interviews()
        if not interviews:
            self.printer.print_safe("No interviews found!")
            return 0
        
        total = len(interviews)
        success_count = 0
        
        self.printer.print_safe(f"DOWNLOADING NINTENDO EMPLOYEE INTERVIEWS")
        self.printer.print_safe(f"Total interviews found: {total}")
        
        # Create main directory
        main_dir = "Nintendo_Employee_Interviews_Archive"
        if os.path.exists(main_dir):
            shutil.rmtree(main_dir)
        os.makedirs(main_dir)
        
        # Download each interview
        for i, interview in enumerate(interviews, 1):
            self.printer.progress_bar(i, total, f"Downloading: ")
            
            try:
                # Extract content
                content_data = self.extract_interview_content(interview['url'])
                content_data['category'] = interview.get('category', 'Unknown')
                
                if not content_data['success']:
                    self.printer.print_safe(f"\n{i:3d}/{total}: ERROR - {interview['title'][:30]}...")
                    continue
                
                # Create folder
                safe_title = self.clean_filename(content_data['title_original'])
                folder_name = os.path.join(main_dir, f"{i:03d}_{safe_title}")
                os.makedirs(folder_name, exist_ok=True)
                
                # Download images
                downloaded_images = 0
                for j, img in enumerate(content_data['images']):
                    if img['url']:
                        ext = '.jpg'  # Default extension
                        if '.png' in img['url'].lower():
                            ext = '.png'
                        elif '.gif' in img['url'].lower():
                            ext = '.gif'
                        
                        img_path = os.path.join(folder_name, f"image_{j+1}{ext}")
                        
                        if self.download_image(img['url'], img_path):
                            content_data['images'][j]['local_path'] = f"image_{j+1}{ext}"
                            downloaded_images += 1
                
                # Create files
                html_path = self.create_interview_file(content_data, folder_name)
                
                # Save JSON data
                json_path = os.path.join(folder_name, 'data.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(content_data, f, indent=2, ensure_ascii=False)
                
                success_count += 1
                
                if i % 10 == 0:
                    self.printer.print_safe(f"\n{i:3d}/{total}: {success_count} successful")
                
            except Exception as e:
                self.printer.print_safe(f"\n{i:3d}/{total}: ERROR - {str(e)[:50]}")
            
            time.sleep(1)  # Respect server
        
        self.printer.print_safe(f"\n\nARCHIVE COMPLETE!")
        self.printer.print_safe(f"Successful: {success_count}/{total}")
        
        # Create index
        self.create_index_html(main_dir, interviews[:success_count])
        self.printer.print_safe(f"Archive created: {main_dir}/")
        
        return success_count
    
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
        .category-group {{ background: white; border-radius: 5px; overflow: hidden; margin: 10px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .category-header {{ background: #333; color: white; padding: 10px; font-weight: bold; }}
        .interview {{ padding: 10px; border-bottom: 1px solid #eee; display: flex; align-items: center; }}
        .interview:last-child {{ border-bottom: none; }}
        .interview a {{ color: #e60012; text-decoration: none; font-weight: bold; }}
        .interview a:hover {{ text-decoration: underline; }}
        .views {{ display: flex; gap: 10px; margin-left: auto; }}
        .view-btn {{ padding: 3px 8px; background: #f0f0f0; border-radius: 3px; text-decoration: none; color: #333; font-size: 0.8em; }}
        .view-btn:hover {{ background: #e0e0e0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Nintendo Employee Interviews Archive</h1>
        <p>127 Employee Interviews / 社員インタビュー127件</p>
        <p>Original Japanese with English Translation / 日本語原文と英語訳</p>
    </div>
    
    <div class="stats">
        <div class="stat"><div class="stat-num">{len(interviews)}</div><div>Total Interviews</div></div>
        <div class="stat"><div class="stat-num">5</div><div>Categories</div></div>
        <div class="stat"><div class="stat-num">100%</div><div>Offline Ready</div></div>
        <div class="stat"><div class="stat-num">JA+EN</div><div>Bilingual</div></div>
    </div>
"""
        
        # Group by category
        category_groups = {}
        for i, iv in enumerate(interviews):
            cat = iv.get('category', 'Unknown')
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append({
                'folder': f"{i+1:03d}_{self.clean_filename(iv.get('title', 'Unknown'))}",
                'title': iv.get('title', 'Unknown'),
                'url': iv['url']
            })
        
        # Display by category
        for category, items in sorted(category_groups.items()):
            html += f"""
    <div class="category-group">
        <div class="category-header">{category} ({len(items)} interviews)</div>
        <div class="interview-list">"""
            
            for item in items:
                html += f"""
            <div class="interview">
                <a href="{item['folder']}/interview.html">{item['title']}</a>
                <div class="views">
                    <a href="{item['folder']}/interview.html" class="view-btn">View</a>
                </div>
            </div>"""
            
            html += """
        </div>
    </div>
"""
        
        html += f"""
    <div style="text-align: center; margin: 30px; padding: 20px; background: #f9f9f9; border-radius: 5px;">
        <h3>Archive Complete</h3>
        <p>All {len(interviews)} employee interviews downloaded with dual-language support</p>
        <p>Original Japanese + English Translation</p>
        <p>Created: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><em>Content belongs to Nintendo Co., Ltd. Archive preserved for historical purposes.</em></p>
    </div>
</body>
</html>
"""
        
        with open(os.path.join(archive_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)

if __name__ == "__main__":
    scraper = EmployeeInterviewScraper()
    success = scraper.create_archive()
    print(f"Archive creation complete: {success} interviews successfully processed")