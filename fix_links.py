#!/usr/bin/env python3
"""
Fix index.html links to match actual folder names
"""

import os
import json
import re

def fix_index():
    # Read the actual folders
    archive_dir = "Iwata_Asks_Offline_Archive"
    folders = []
    for item in os.listdir(archive_dir):
        if os.path.isdir(os.path.join(archive_dir, item)) and item.startswith(("001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014", "015", "016", "017", "018", "019", "020", "021", "022", "023", "024", "025", "026", "027", "028", "029", "030", "031", "032", "033", "034", "035", "036", "037", "038", "039", "040", "041", "042", "043", "044", "045", "046", "047", "048", "049", "050", "051", "052", "053", "054", "055", "056", "057", "058", "059", "060", "061", "062", "063", "064", "065", "066", "067", "068", "069", "070", "071", "072", "073", "074", "075", "076", "077", "078", "079", "080", "081", "082", "083", "084", "085", "086", "087", "088", "089", "090", "091", "092", "093", "094", "095", "096", "097", "098", "099", "100", "101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111", "112", "113", "114", "115", "116", "117", "118", "119", "120", "121", "122", "123", "124", "125", "126")):
            folders.append(item)
    
    folders.sort()
    print(f"Found {len(folders)} folders")
    
    # Read original interviews to get titles
    try:
        with open("Iwata_Asks_Complete/FINAL_ALL_126.json", 'r', encoding='utf-8') as f:
            interviews = json.load(f)
    except:
        print("Cannot read original interviews")
        return
    
    # Group by platform
    platform_groups = {}
    for i, iv in enumerate(interviews[:126], 1):
        if not iv.get('success', False):
            continue
        p = iv.get('platform', 'Unknown')
        if p not in platform_groups:
            platform_groups[p] = []
        platform_groups[p].append({
            'folder': folders[i-1] if i-1 < len(folders) else f"{i:03d}_Unknown",
            'title': iv.get('title', 'Unknown'),
            'url': iv['url']
        })
    
    # Generate new HTML
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iwata Asks - Complete Archive</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .header { background: #e60012; color: white; padding: 30px; text-align: center; border-radius: 5px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat { background: white; padding: 15px; text-align: center; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .stat-num { font-size: 1.5em; font-weight: bold; color: #e60012; }
        .interview-list { display: grid; gap: 10px; }
        .platform-group { background: white; border-radius: 5px; overflow: hidden; margin: 10px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .platform-header { background: #333; color: white; padding: 10px; font-weight: bold; }
        .interview { padding: 10px; border-bottom: 1px solid #eee; display: flex; align-items: center; }
        .interview:last-child { border-bottom: none; }
        .interview a { color: #e60012; text-decoration: none; font-weight: bold; }
        .interview a:hover { text-decoration: underline; }
        .meta { font-size: 0.8em; color: #666; margin-left: 10px; }
        .views { display: flex; gap: 10px; margin-left: auto; }
        .view-btn { padding: 3px 8px; background: #f0f0f0; border-radius: 3px; text-decoration: none; color: #333; font-size: 0.8em; }
        .view-btn:hover { background: #e0e0e0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Iwata Asks Complete Archive</h1>
        <p>All Interviews Available Offline</p>
    </div>
    
    <div class="stats">
"""
    
    total_interviews = sum(len(items) for items in platform_groups.values())
    html += f"""
        <div class="stat"><div class="stat-num">{total_interviews}</div><div>Total</div></div>
        <div class="stat"><div class="stat-num">{len(platform_groups)}</div><div>Platforms</div></div>
        <div class="stat"><div class="stat-num">100%</div><div>Offline</div></div>
        <div class="stat"><div class="stat-num">HTML+MD</div><div>Formats</div></div>
    </div>
"""
    
    # Display interviews by platform
    for platform, items in sorted(platform_groups.items()):
        html += f"""
    <div class="platform-group">
        <div class="platform-header">{platform} ({len(items)} interviews)</div>
        <div class="interview-list">
"""
        for item in items:
            html += f"""
            <div class="interview">
                <a href="{item['folder']}/interview.html">{item['title']}</a>
                <div class="views">
                    <a href="{item['folder']}/interview.html" class="view-btn">HTML</a>
                    <a href="{item['folder']}/interview.md" class="view-btn">Markdown</a>
                </div>
            </div>
"""
        html += """
        </div>
    </div>
"""
    
    html += f"""
    <div style="text-align: center; margin: 30px; padding: 20px; background: #f9f9f9; border-radius: 5px;">
        <h3>Archive Complete</h3>
        <p>All {total_interviews} interviews downloaded for offline viewing</p>
        <p>Each interview includes HTML and Markdown formats</p>
        <p>Created: 2026-03-02 (Fixed Links Version)</p>
        <p><em>Content belongs to Nintendo Co., Ltd. Archive preserved for historical purposes.</em></p>
    </div>
</body>
</html>
"""
    
    # Save fixed index
    with open(os.path.join(archive_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Fixed index.html created!")
    print(f"Total platforms: {len(platform_groups)}")
    for platform, items in platform_groups.items():
        print(f"{platform}: {len(items)} interviews")

if __name__ == "__main__":
    fix_index()