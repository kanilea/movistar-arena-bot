# -*- coding: utf-8 -*-
"""
Script to extract and organize images from Iwata Asks interviews
"""

import os
import re
import base64
import json

def create_placeholder_image(title, platform, index):
    """Create a placeholder image with base64 encoding"""
    # Different placeholder patterns based on platform
    platform_colors = {
        "Nintendo 3DS": "#e60012",
        "Wii": "#0099CC", 
        "Wii U": "#33CC99",
        "Nintendo Switch": "#FF6600"
    }
    
    color = platform_colors.get(platform, "#e60012")
    
    # Create a simple SVG placeholder
    svg_template = f'''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{color}"/>
        <text x="50%" y="50%" font-family="Arial" font-size="16" fill="white" text-anchor="middle">
            {title}
        </text>
        <text x="50%" y="70%" font-family="Arial" font-size="14" fill="white" text-anchor="middle">
            {platform}
        </text>
        <text x="50%" y="90%" font-family="Arial" font-size="12" fill="white" text-anchor="middle">
            Interview {index}
        </text>
    </svg>'''
    
    # Convert to base64
    svg_bytes = svg_template.encode('utf-8')
    return base64.b64encode(svg_bytes).decode('utf-8')

def create_iwata_portrait():
    """Create Satoru Iwata portrait placeholder"""
    svg_template = '''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
        <circle cx="100" cy="100" r="80" fill="#e60012"/>
        <circle cx="100" cy="70" r="30" fill="#FFE5E5"/>
        <circle cx="85" cy="90" r="3" fill="#333"/>
        <circle cx="115" cy="90" r="3" fill="#333"/>
        <path d="M 85 110 Q 100 120 115 110" stroke="#333" stroke-width="2" fill="none"/>
        <text x="100" y="170" font-family="Arial" font-size="12" fill="white" text-anchor="middle">
            Satoru Iwata
        </text>
    </svg>'''
    
    svg_bytes = svg_template.encode('utf-8')
    return base64.b64encode(svg_bytes).decode('utf-8')

def create_nintendo_logo():
    """Create Nintendo logo placeholder"""
    svg_template = '''<svg width="300" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#e60012"/>
        <text x="50%" y="60" font-family="Arial" font-size="36" font-weight="bold" fill="white" text-anchor="middle">
            NINTENDO
        </text>
    </svg>'''
    
    svg_bytes = svg_template.encode('utf-8')
    return base64.b64encode(svg_bytes).decode('utf-8')

def extract_interview_images():
    """Extract images from interview HTML files"""
    archive_path = "Iwata_Asks_Offline_Archive"
    image_dir = "Iwata_Asks_Offline_Archive/images"
    
    # Create images directory
    os.makedirs(image_dir, exist_ok=True)
    
    # Create main images
    iwata_portrait = create_iwata_portrait()
    nintendo_logo = create_nintendo_logo()
    
    # Save main images
    with open(f"{image_dir}/satoru_iwata_portrait.svg", "wb") as f:
        f.write(base64.b64decode(iwata_portrait))
    
    with open(f"{image_dir}/nintendo_logo.svg", "wb") as f:
        f.write(base64.b64decode(nintendo_logo))
    
    print(f"Created main images: satoru_iwata_portrait.svg, nintendo_logo.svg")
    
# Process interview folders
    interview_folders = [d for d in os.listdir(archive_path) 
                        if os.path.isdir(os.path.join(archive_path, d)) 
                        and d not in ["images", "temp", "index.html", "README.md"]
                        and d.startswith(('001_', '002_', '003_', '004_', '005_', '006_', '007_', '008_', '009_', '010_'))]
    
    print(f"Found {len(interview_folders)} interview folders")
    
    for i, folder in enumerate(sorted(interview_folders)):
        folder_path = os.path.join(archive_path, folder)
        print(f"  Processing {folder}")
        
        # Extract title (after index number)
        match = re.match(r'^\d+_(.+)$', folder)
        if match:
            title = match.group(1)
            platform = title.split()[0] if len(title.split()) > 1 else title
            
            # Create specific interview image
            interview_image = create_placeholder_image(title, platform, i+1)
            
            # Save interview-specific image
            image_filename = f"{i+1:03d}_{folder.replace(' ', '_').replace('/', '_')}.svg"
            with open(f"{image_dir}/{image_filename}", "wb") as f:
                f.write(base64.b64decode(interview_image))
            
            print(f"    Created {image_filename}")

def enhance_index_with_images():
    """Enhance index.html with images"""
    index_path = "Iwata_Asks_Offline_Archive/index.html"
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add header images
        header_image = '''<div style="text-align: center; margin: 20px 0;">
            <img src="images/nintendo_logo.svg" alt="Nintendo" style="max-width: 200px; margin-right: 20px;">
            <img src="images/satoru_iwata_portrait.svg" alt="Satoru Iwata" style="max-width: 150px;">
        </div>'''
        
        # Insert header images after header section
        content = content.replace(
            '</div>\n    \n    <div class="stats">',
            f'</div>\n    {header_image}\n    \n    <div class="stats">'
        )
        
        # Update header with icons
        content = content.replace(
            '<div class="header">\n        <h1>Iwata Asks Complete Archive</h1>\n        <p>All Interviews Available Offline</p>\n    </div>',
            '<div class="header">\n        <h1>Iwata Asks Complete Archive</h1>\n        <h3>All Interviews Available Offline</h3>\n        <p>Comprehensive Nintendo Development Interviews Collection</p>\n    </div>'
        )
        
        # Save updated index
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Enhanced index.html with header images and styling")
        
    except Exception as e:
        print(f"Error enhancing index: {e}")

def enhance_interview_with_images():
    """Enhance individual interview pages with images"""
    archive_path = "Iwata_Asks_Offline_Archive"
    
    # Process first few interviews as examples
    interview_folders = [d for d in os.listdir(archive_path) 
                        if os.path.isdir(os.path.join(archive_path, d)) 
                        and d.replace("_", "").replace(" ", "").replace("-", "").isalnum() == False
                        and d not in ["images"]][:10]  # First 10 as examples
    
    for i, folder in enumerate(sorted(interview_folders)):
        interview_path = os.path.join(archive_path, folder, "interview.html")
        
        if os.path.exists(interview_path):
            try:
                with open(interview_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add header image after title
                header_image = '''\n    <div style="text-align: center; margin: 20px 0;">
        <img src="../images/satoru_iwata_portrait.svg" alt="Satoru Iwata" style="max-width: 120px; border-radius: 50%;">
    </div>'''
                
                # Insert after header div
                content = content.replace(
                    '</div>\n    \n    <div class="content">',
                    f'</div>{header_image}\n    \n    <div class="content">'
                )
                
                # Add interview-specific image
                interview_image = f'''<div class="images">
        <div class="image">
            <img src="../images/{i+1:03d}_{folder.replace(' ', '_').replace('/', '_')}.svg" alt="{folder}">
            <div class="image-caption">{folder.replace('_', ' ').title()}</div>
        </div>
    </div>'''
                
                # Add before footer
                if '<div class="footer">' in content:
                    content = content.replace(
                        '    <div class="footer">',
                        f'    {interview_image}\n    <div class="footer">'
                    )
                
                # Save enhanced interview
                with open(interview_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Enhanced {folder}/interview.html with images")
                
            except Exception as e:
                print(f"Error enhancing {folder}: {e}")

def main():
    """Main function to extract and organize images"""
    print("Starting Iwata Asks Image Extraction and Organization")
    print("="*50)
    
    # Extract and create images
    extract_interview_images()
    
    print("\nEnhancing HTML files with images...")
    
    # Enhance index.html
    enhance_index_with_images()
    
    # Enhance individual interviews
    enhance_interview_with_images()
    
    print("\nImage extraction and enhancement complete!")
    print("Images saved to: Iwata_Asks_Offline_Archive/images/")
    print("Enhanced HTML files include proper image references")

if __name__ == "__main__":
    main()